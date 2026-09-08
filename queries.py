"""
Módulo de consultas SQL agregadas para el Dashboard de Matrículas.
Todas las consultas ejecutan agregaciones (GROUP BY, COUNT) directamente en la BD
respetando los filtros del usuario con parámetros seguros contra inyección SQL.
Ninguna función expone datos personales de alumnos (nombres, apellidos, códigos).
"""

from datetime import date, datetime
from typing import Dict, Any, Tuple, List
import pandas as pd
from sqlalchemy import text
import streamlit as st
from db import get_db_engine, get_view_name


def _build_where_clause(filters: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Construye la cláusula WHERE y el diccionario de parámetros seguros.
    Soporta filtros para CICLO, LOCAL, TURNO, AREA y rango de fecha_matricula.
    """
    clauses = ["1=1"]
    params = {}

    # Filtro CICLO (Multi-select)
    if filters.get("ciclos"):
        placeholders = []
        for i, val in enumerate(filters["ciclos"]):
            p_name = f"ciclo_{i}"
            placeholders.append(f":{p_name}")
            params[p_name] = val
        clauses.append(f"CICLO IN ({', '.join(placeholders)})")

    # Filtro LOCAL (Multi-select)
    if filters.get("locales"):
        placeholders = []
        for i, val in enumerate(filters["locales"]):
            p_name = f"local_{i}"
            placeholders.append(f":{p_name}")
            params[p_name] = val
        clauses.append(f"LOCAL IN ({', '.join(placeholders)})")

    # Filtro TURNO (Multi-select)
    if filters.get("turnos"):
        placeholders = []
        for i, val in enumerate(filters["turnos"]):
            p_name = f"turno_{i}"
            placeholders.append(f":{p_name}")
            params[p_name] = val
        clauses.append(f"TURNO IN ({', '.join(placeholders)})")

    # Filtro AREA (Multi-select)
    if filters.get("areas"):
        placeholders = []
        for i, val in enumerate(filters["areas"]):
            p_name = f"area_{i}"
            placeholders.append(f":{p_name}")
            params[p_name] = val
        clauses.append(f"AREA IN ({', '.join(placeholders)})")

    # Filtro Rango de Fechas (desde / hasta)
    if filters.get("fecha_inicio"):
        f_ini = filters["fecha_inicio"]
        if isinstance(f_ini, date):
            f_ini = f_ini.strftime("%Y-%m-%d")
        clauses.append("fecha_matricula >= :fecha_inicio")
        params["fecha_inicio"] = f_ini

    if filters.get("fecha_fin"):
        f_fin = filters["fecha_fin"]
        if isinstance(f_fin, date):
            f_fin = f_fin.strftime("%Y-%m-%d")
        clauses.append("fecha_matricula <= :fecha_fin")
        params["fecha_fin"] = f_fin

    return " AND ".join(clauses), params


@st.cache_data(ttl=30)
def get_distinct_filter_values() -> Dict[str, Any]:
    """
    Obtiene las opciones disponibles para los filtros dinámicos (SELECT DISTINCT)
    y el rango global de fechas disponibles en la vista.
    """
    engine, _, _ = get_db_engine()
    view = get_view_name()

    with engine.connect() as conn:
        df_ciclos = pd.read_sql_query(
            text(f"SELECT DISTINCT CICLO FROM {view} WHERE CICLO IS NOT NULL ORDER BY CICLO"),
            con=conn
        )
        df_locales = pd.read_sql_query(
            text(f"SELECT DISTINCT LOCAL FROM {view} WHERE LOCAL IS NOT NULL ORDER BY LOCAL"),
            con=conn
        )
        df_turnos = pd.read_sql_query(
            text(f"SELECT DISTINCT TURNO FROM {view} WHERE TURNO IS NOT NULL ORDER BY TURNO"),
            con=conn
        )
        df_areas = pd.read_sql_query(
            text(f"SELECT DISTINCT AREA FROM {view} WHERE AREA IS NOT NULL ORDER BY AREA"),
            con=conn
        )
        df_fechas = pd.read_sql_query(
            text(f"SELECT MIN(fecha_matricula) AS min_fecha, MAX(fecha_matricula) AS max_fecha FROM {view}"),
            con=conn
        )

    min_f = df_fechas["min_fecha"].iloc[0] if not df_fechas.empty else date.today()
    max_f = df_fechas["max_fecha"].iloc[0] if not df_fechas.empty else date.today()

    # Convertir a objetos date de Python si vienen como strings
    if isinstance(min_f, str):
        min_f = datetime.strptime(min_f, "%Y-%m-%d").date()
    if isinstance(max_f, str):
        max_f = datetime.strptime(max_f, "%Y-%m-%d").date()

    return {
        "ciclos": df_ciclos["CICLO"].tolist(),
        "locales": df_locales["LOCAL"].tolist(),
        "turnos": df_turnos["TURNO"].tolist(),
        "areas": df_areas["AREA"].tolist(),
        "min_fecha": min_f,
        "max_fecha": max_f,
    }


@st.cache_data(ttl=30)
def get_kpis(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula los 4 KPIs requeridos respetando los filtros activos:
    1. Total de matriculados
    2. Locales activos con matrícula
    3. Carreras con al menos 1 matriculado
    4. Matriculados del día actual (CURDATE() o fecha máxima de matriculación)
    """
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    # Consulta consolidada de KPIs
    sql_kpis = f"""
        SELECT 
            COUNT(*) AS total_matriculados,
            COUNT(DISTINCT LOCAL) AS locales_activos,
            COUNT(DISTINCT CARRERA) AS carreras_activas
        FROM {view}
        WHERE {where_sql}
    """

    today_str = date.today().strftime("%Y-%m-%d")
    sql_hoy = f"""
        SELECT COUNT(*) AS matriculados_hoy
        FROM {view}
        WHERE {where_sql} AND fecha_matricula = :today_date
    """
    params_hoy = {**params, "today_date": today_str}

    with engine.connect() as conn:
        df_res = pd.read_sql_query(text(sql_kpis), con=conn, params=params)
        df_hoy = pd.read_sql_query(text(sql_hoy), con=conn, params=params_hoy)

    total = int(df_res["total_matriculados"].iloc[0]) if not df_res.empty else 0
    locales = int(df_res["locales_activos"].iloc[0]) if not df_res.empty else 0
    carreras = int(df_res["carreras_activas"].iloc[0]) if not df_res.empty else 0
    hoy = int(df_hoy["matriculados_hoy"].iloc[0]) if not df_hoy.empty else 0

    return {
        "total_matriculados": total,
        "locales_activos": locales,
        "carreras_activas": carreras,
        "matriculados_hoy": hoy,
        "fecha_consulta": today_str,
    }


@st.cache_data(ttl=30)
def get_matriculados_por_ciclo(filters: Dict[str, Any]) -> pd.DataFrame:
    """Distribución de matriculados por Ciclo académico."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT CICLO, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY CICLO
        ORDER BY total DESC
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_matriculados_por_local(filters: Dict[str, Any]) -> pd.DataFrame:
    """Distribución de matriculados por Local / Sede (orden descendente)."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT LOCAL, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY LOCAL
        ORDER BY total DESC
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_matriculados_por_turno(filters: Dict[str, Any]) -> pd.DataFrame:
    """Distribución de matriculados por Turno de estudio."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT TURNO, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY TURNO
        ORDER BY total DESC
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_matriculados_por_area(filters: Dict[str, Any]) -> pd.DataFrame:
    """Distribución de matriculados por Área académica."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT AREA, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY AREA
        ORDER BY total DESC
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_top_carreras(filters: Dict[str, Any], limit: int = 15) -> pd.DataFrame:
    """Top N carreras con mayor volumen de matriculados."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    # Parámetro limit seguro
    sql = f"""
        SELECT CARRERA, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY CARRERA
        ORDER BY total DESC
        LIMIT {int(limit)}
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_evolucion_temporal(filters: Dict[str, Any]) -> pd.DataFrame:
    """Evolución cronológica de matriculados por fecha_matricula."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT fecha_matricula, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY fecha_matricula
        ORDER BY fecha_matricula ASC
    """
    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql), con=conn, params=params)
    if not df.empty:
        df["fecha_matricula"] = pd.to_datetime(df["fecha_matricula"])
        # Cálculo acumulado para enriquecer la visualización de la evolución
        df["total_acumulado"] = df["total"].cumsum()
    return df


@st.cache_data(ttl=30)
def get_cruce_local_turno(filters: Dict[str, Any]) -> pd.DataFrame:
    """Cruce de distribución de matriculados por Local y Turno."""
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT LOCAL, TURNO, COUNT(*) AS total
        FROM {view}
        WHERE {where_sql}
        GROUP BY LOCAL, TURNO
        ORDER BY LOCAL, TURNO
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)


@st.cache_data(ttl=30)
def get_resumen_ciclo_local_turno(filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Resumen consolidado de matriculados agrupado por Ciclo, Local y Turno.
    Devuelve las columnas: CICLO, LOCAL, TURNO, MATRICULADOS.
    """
    engine, _, _ = get_db_engine()
    view = get_view_name()
    where_sql, params = _build_where_clause(filters)

    sql = f"""
        SELECT CICLO, LOCAL, TURNO, COUNT(*) AS MATRICULADOS
        FROM {view}
        WHERE {where_sql}
        GROUP BY CICLO, LOCAL, TURNO
        ORDER BY CICLO ASC, LOCAL ASC, TURNO ASC
    """
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), con=conn, params=params)

