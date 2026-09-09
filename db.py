"""
Módulo de conexión a la base de datos mediante SQLAlchemy.
Incluye soporte para Modo Demostración / Fallback automático en memoria (SQLite)
cuando el servidor de base de datos institucional no está accesible (ej. fuera de VPN).
"""

import os
import random
from datetime import date, datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import streamlit as st

# Cargar variables de entorno desde .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_VIEW = os.getenv("DB_VIEW", "vista_matriculas")
DB_PAGOS_VIEW = os.getenv("DB_PAGOS_VIEW", "vw_pagos_recientes")
FORCE_DEMO = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

_ENGINE = None
_IS_DEMO = False
_CONNECTION_STATUS = "Desconectado"


def _create_synthetic_dataset(num_rows: int = 850) -> pd.DataFrame:
    """
    Genera un conjunto de datos sintético y realista basado exactamente
    en las características descritas en la sección 2.1 del MVP.
    """
    random.seed(42)

    ciclos = ["ORD_2026_II", "ESP_2026_II", "SUP_2027_I"]
    ciclo_weights = [0.65, 0.25, 0.10]

    locales = [
        "CIUDAD UNIVERSITARIA",
        "SEDE SAN JUAN DE LURIGANCHO",
        "SEDE NORTE (LOS OLIVOS)",
        "SEDE SUR (SAN JUAN DE MIRAFLORES)",
        "SEDE CENTRAL",
        "SEDE COLONIAL",
        "SEDE MIRAFLORES",
        "SEDE CALLAO",
        "SEDE ATE VITARTE",
        "SEDE HUARAL",
    ]

    turnos = ["MAÑANA", "TARDE"]
    turno_weights = [0.58, 0.42]

    areas_carreras = {
        "A": [  # Ciencias de la Salud
            "MEDICINA HUMANA", "ENFERMERÍA", "FARMACIA Y BIOQUÍMICA",
            "ODONTOLOGÍA", "OBSTETRICIA", "NUTRICIÓN", "TECNOLOGÍA MÉDICA",
            "MEDICINA VETERINARIA", "PSICOLOGÍA"
        ],
        "B": [  # Ciencias Básicas
            "CIENCIAS BIOLÓGICAS", "GENÉTICA Y BIOTECNOLOGÍA", "MICROBIOLOGÍA",
            "QUÍMICA", "FÍSICA", "MATEMÁTICA", "ESTADÍSTICA", "INVESTIGACIÓN OPERATIVA"
        ],
        "C": [  # Ingenierías
            "INGENIERÍA DE SISTEMAS", "INGENIERÍA DE SOFTWARE", "INGENIERÍA INDUSTRIAL",
            "INGENIERÍA ELECTRÓNICA", "INGENIERÍA CIVIL", "INGENIERÍA MECÁNICA DE FLUIDOS",
            "INGENIERÍA QUÍMICA", "INGENIERÍA METALÚRGICA", "INGENIERÍA DE MINAS",
            "INGENIERÍA GEOLÓGICA", "INGENIERÍA GEOGRÁFICA", "INGENIERÍA AMBIENTAL",
            "INGENIERÍA TELECOMUNICACIONES", "INGENIERÍA BIOMÉDICA", "CIENCIA DE LA COMPUTACIÓN"
        ],
        "D": [  # Ciencias Económicas y de la Gestión
            "ADMINISTRACIÓN", "ADMINISTRACIÓN DE TURISMO", "ADMINISTRACIÓN DE NEGOCIOS INTERNACIONALES",
            "CONTABILIDAD", "AUDITORÍA EMPRESARIAL", "GESTIÓN TRIBUTARIA",
            "ECONOMÍA", "ECONOMÍA PÚBLICA", "ECONOMÍA INTERNACIONAL"
        ],
        "E": [  # Humanidades y Ciencias Jurídicas y Sociales
            "DERECHO", "CIENCIA POLÍTICA", "COMUNICACIÓN SOCIAL", "LITERATURA",
            "FILOSOFÍA", "LINGÜÍSTICA", "HISTORIA", "SOCIOLOGÍA", "ANTROPOLOGÍA",
            "ARQUEOLOGÍA", "TRABAJO SOCIAL", "EDUCACIÓN SECUNDARIA", "EDUCACIÓN PRIMARIA"
        ],
    }

    # Distribución de fechas de matrícula (últimos 30 días hasta hoy)
    today = date.today()
    start_date = today - timedelta(days=28)

    records = []
    for i in range(num_rows):
        codigo = 210000 + i + 1
        ciclo = random.choices(ciclos, weights=ciclo_weights)[0]
        local = random.choice(locales)
        turno = random.choices(turnos, weights=turno_weights)[0]
        area = random.choice(list(areas_carreras.keys()))
        carrera = random.choice(areas_carreras[area])
        aula = random.randint(1, 45)

        # Probabilidad de matrícula en días recientes (con mayor pico hoy y ayer)
        days_offset = int(random.triangular(0, 28, 28))
        f_matricula = start_date + timedelta(days=days_offset)
        
        # Hora de matrícula
        hour = random.randint(8, 19)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        h_matricula = f"{hour:02d}:{minute:02d}:{second:02d}"

        records.append({
            "CICLO": ciclo,
            "CODIGO": codigo,
            "APE_PATERNO": f"APELLIDO_{i+1}",
            "APE_MATERNO": f"MATERNO_{i+1}",
            "NOMBRES": f"ESTUDIANTE {i+1}",
            "LOCAL": local,
            "TURNO": turno,
            "AULA": aula,
            "AREA": area,
            "CARRERA": carrera,
            "fecha_matricula": f_matricula.strftime("%Y-%m-%d"),
            "hora_matricula": h_matricula,
        })

    return pd.DataFrame(records)


from sqlalchemy.pool import StaticPool

DEMO_DB_PATH = os.path.join(os.path.dirname(__file__), "demo_data.sqlite")

def _create_synthetic_pagos_dataset() -> pd.DataFrame:
    """
    Genera un conjunto de datos sintético para vw_pagos_recientes
    con la misma estructura y ciclos observados en producción.
    """
    today = date.today()
    records = [
        # ORD_2026_II (9 pagos x S/ 2,700)
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": today.strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": today.strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"idproducto": 2, "anio_prod": 2026, "pago_ciclo": "ORD_2026_II", "monto_pago": 2700.0, "fecha_pago": (today - timedelta(days=2)).strftime("%Y-%m-%d")},
        # ESP_2026_II (1 pago x S/ 1,430)
        {"idproducto": 5, "anio_prod": 2026, "pago_ciclo": "ESP_2026_II", "monto_pago": 1430.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
        # SUP_2027_I (4 pagos x S/ 385)
        {"idproducto": 81, "anio_prod": 2026, "pago_ciclo": "SUP_2027_I", "monto_pago": 385.0, "fecha_pago": today.strftime("%Y-%m-%d")},
        {"idproducto": 81, "anio_prod": 2026, "pago_ciclo": "SUP_2027_I", "monto_pago": 385.0, "fecha_pago": today.strftime("%Y-%m-%d")},
        {"idproducto": 81, "anio_prod": 2026, "pago_ciclo": "SUP_2027_I", "monto_pago": 385.0, "fecha_pago": today.strftime("%Y-%m-%d")},
        {"idproducto": 81, "anio_prod": 2026, "pago_ciclo": "SUP_2027_I", "monto_pago": 385.0, "fecha_pago": (today - timedelta(days=1)).strftime("%Y-%m-%d")},
    ]
    return pd.DataFrame(records)


def _init_demo_engine():
    """
    Crea una base de datos SQLite persistente para modo demostración
    con pool estático para soportar múltiples hilos y recargas de Streamlit.
    """
    engine = create_engine(
        f"sqlite:///{DEMO_DB_PATH}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    # Verificar si ambas tablas ya existen y tienen registros
    try:
        with engine.connect() as conn:
            res_view = conn.execute(text(f"SELECT COUNT(*) FROM {DB_VIEW}")).scalar()
            res_pagos = conn.execute(text(f"SELECT COUNT(*) FROM {DB_PAGOS_VIEW}")).scalar()
            if res_view and res_view > 0 and res_pagos and res_pagos > 0:
                return engine
    except Exception:
        pass

    # Generar y persistir dataset de matrículas
    df = _create_synthetic_dataset(920)
    df.to_sql(DB_VIEW, con=engine, if_exists="replace", index=False)

    # Generar y persistir dataset de pagos recientes
    df_pagos = _create_synthetic_pagos_dataset()
    df_pagos.to_sql(DB_PAGOS_VIEW, con=engine, if_exists="replace", index=False)

    return engine


def get_db_engine():
    """
    Retorna el engine de SQLAlchemy para conectarse a la base de datos.
    Si FORCE_DEMO está activo o la conexión a la base de datos no responde,
    activa el fallback automático con datos de prueba realistas.
    """
    global _ENGINE, _IS_DEMO, _CONNECTION_STATUS

    if _ENGINE is not None:
        return _ENGINE, _IS_DEMO, _CONNECTION_STATUS

    if FORCE_DEMO or not DB_HOST or not DB_NAME or not DB_USER:
        _ENGINE = _init_demo_engine()
        _IS_DEMO = True
        _CONNECTION_STATUS = "Modo Demostración (Datos de simulación activos)"
        return _ENGINE, _IS_DEMO, _CONNECTION_STATUS

    # Intentar conexión real a la base de datos
    try:
        from sqlalchemy import URL
        url_obj = URL.create(
            "mysql+pymysql",
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=int(DB_PORT) if DB_PORT else 3306,
            database=DB_NAME,
            query={"charset": "utf8mb4"},
        )
        engine = create_engine(
            url_obj,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 5},
        )
        
        # Prueba de conexión rápida
        with engine.connect() as conn:
            conn.execute(text(f"SELECT 1 FROM {DB_VIEW} LIMIT 1"))

        _ENGINE = engine
        _IS_DEMO = False
        _CONNECTION_STATUS = f"En Vivo (Servidor: {DB_HOST}/{DB_NAME})"
        return _ENGINE, _IS_DEMO, _CONNECTION_STATUS

    except Exception as err:
        # Si falla la conexión (ej. sin VPN o BD apagada), fallback seguro
        _ENGINE = _init_demo_engine()
        _IS_DEMO = True
        _CONNECTION_STATUS = (
            f"Modo Demostración (No se pudo conectar al servidor: {type(err).__name__}). "
            f"Mostrando datos de simulación."
        )
        return _ENGINE, _IS_DEMO, _CONNECTION_STATUS


def get_view_name() -> str:
    """Retorna el nombre de la vista en la base de datos."""
    return DB_VIEW


def get_pagos_view_name() -> str:
    """Retorna el nombre de la vista de pagos recientes en la base de datos."""
    return DB_PAGOS_VIEW
