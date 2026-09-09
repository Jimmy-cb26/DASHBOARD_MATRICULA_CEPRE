# Guía para Agentes de IA — Dashboard de Métricas de Matrícula

Este documento establece las directrices, arquitectura técnica, restricciones de seguridad y reglas de desarrollo para cualquier agente de IA que trabaje en el repositorio **`dashboard_matriculados`**.

---

## 1. Visión General del Proyecto

- **Propósito:** Tablero ejecutivo para el monitoreo en tiempo real del proceso de matrícula de estudiantes, consultando directamente la vista de la base de datos de producción (configurable vía `DB_VIEW`).
- **Acceso:** Limitado a la red interna / VPN de la institución (máximo 5 usuarios internos autorizados).
- **Filosofía:** Visualizaciones agregadas en tiempo real sin ETL intermedias, con experiencia de usuario moderna, fluida y con estricto apego a la privacidad de datos estudiantiles.

---

## 2. Stack Tecnológico

- **Lenguaje:** Python 3.12+
- **Framework de UI:** [Streamlit](https://streamlit.io/) (1.37+)
- **Motor de Gráficos:** [Plotly Express](https://plotly.com/python/) y `plotly.graph_objects`
- **Capa de Datos:** [SQLAlchemy](https://www.sqlalchemy.org/) (2.0+)
- **Autenticación y Seguridad:** `streamlit-authenticator` (0.4+) con contraseñas encriptadas en **bcrypt**
- **Configuración:** `python-dotenv` y `PyYAML`

---

## 3. Estructura del Código y Responsabilidades

```
d:\pra\dashboard_matriculados/
├── app.py                   # Entrada principal, flujo de interfaz, filtros y gráficos Plotly
├── auth.py                  # Autenticación, control previo de acceso y manejo de sesiones
├── db.py                    # Engine SQLAlchemy (en vivo vía URL.create + fallback SQLite)
├── queries.py               # Consultas SQL parametrizadas y cacheadas (@st.cache_data(ttl=30))
├── styles.py                # CSS personalizado (Outfit, Plus Jakarta Sans, double-bezel) y temas Plotly
├── generate_keys.py         # Utilidad CLI para hashear contraseñas con bcrypt
├── credentials.yaml         # Credenciales cifradas de usuarios autorizados (IGNORADO EN GIT)
├── credentials.yaml.example # Plantilla para configuración de usuarios
├── .env                     # Variables de conexión a base de datos (IGNORADO EN GIT)
├── .env.example             # Plantilla de variables de conexión
├── demo_data.sqlite         # Base de datos SQLite local para modo demo/offline (IGNORADO EN GIT)
├── requirements.txt         # Dependencias exactas del proyecto
├── test_app.py              # Suite de 7 pruebas unitarias automáticas
├── MVP_Dashboard_Matriculas.md # Especificación funcional original
├── AGENTS.md                # Directrices operativas para agentes de IA (este archivo)
└── README.md                # Documentación para usuarios y administradores
```

---

## 4. Reglas Críticas para Agentes

### 4.1. Privacidad y Confidencialidad de Datos (MANDATORIO)
- **Columnas Prohibidas en UI:** Las columnas `APE_PATERNO`, `APE_MATERNO`, `NOMBRES` y `CODIGO` **NUNCA** deben ser consultadas para visualización, ni expuestas en gráficos, tablas, tooltips o exportaciones.
- Todas las consultas deben operar exclusivamente a nivel **agregado** (`COUNT(*)`, `COUNT(DISTINCT ...)`, `GROUP BY`).
- Las pruebas en `test_app.py::test_07_privacy_compliance` validan esta regla en cada cambio.

### 4.2. Prevención de Inyecciones SQL
- **NUNCA** concatenar valores de filtros directamente en sentencias SQL (`f"... WHERE CICLO = '{ciclo}'"` está **estrictamente prohibido**).
- Usar siempre consultas parametrizadas con placeholders `:param_name` y diccionarios de parámetros a través de `text(...)` de SQLAlchemy.

### 4.3. Resiliencia de Base de Datos y Modo Demo
- La capa `db.py` detecta automáticamente si el servidor de base de datos está accesible.
- Se utiliza `sqlalchemy.URL.create(...)` para evitar que caracteres especiales en contraseñas (ej. `#`, `$`, `@`, `/`) corrompan la URI de conexión de SQLAlchemy.
- Fuera de la VPN o cuando `DEMO_MODE=true`, se activa el **Modo Demostración** respaldado por un archivo SQLite persistente (`demo_data.sqlite`) configurado con `StaticPool` y `check_same_thread=False` para soportar la concurrencia multihilo de Streamlit sin pérdida de datos.
- Cualquier nueva consulta debe ser compatible con la sintaxis estándar ANSI SQL soportada tanto por el motor relacional en producción como por SQLite.

### 4.4. Manejo de Credenciales en `.env`
- **Contraseñas con caracteres especiales:** Si la contraseña contiene caracteres como `#` o `$`, **DEBE ir entre comillas simples** en `.env` (ej. `DB_PASSWORD='...'`) para evitar que `python-dotenv` corte el valor al encontrar un `#` (interpretándolo como comentario) o intente interpolar `$`.
- Tanto `.env` como `credentials.yaml` y `demo_data.sqlite` están excluidos en `.gitignore`.

### 4.5. Rendimiento y Caché
- Usar decoradores `@st.cache_data(ttl=30)` para consultas a la base de datos para amortiguar la carga sin desactualizar la percepción de tiempo real del usuario.
- Evitar cargar datos fila a fila a DataFrames cuando se puedan calcular las sumatorias o conteos directamente en el motor SQL.

### 4.6. Estética y Diseño Visual
- Mantener la línea visual ejecutiva de alta fidelidad definida en `styles.py`:
  - Tipografías `Outfit` (display) y `Plus Jakarta Sans` (interfaz) con números tabulares (`tabular-nums`)
  - Tarjetas KPI con arquitectura **Double-Bezel** (doble bisel anidado), resplandor ambiental y elevación en hover
  - Gráficos con fondo transparente (`rgba(0,0,0,0)`), tooltips oscuros tipo pastilla y paletas cromáticas institucionales (`COLOR_PALETTE`, `TURNO_COLORS`, `AREA_COLORS`).

---

## 5. Esquema de Datos de la Vista Institucional

> **Nota de Configuración:** El nombre de la vista autorizada se configura dinámicamente en la variable `DB_VIEW` dentro del archivo `.env`.

| Columna | Tipo | Descripción | Uso en Dashboard |
|---|---|---|---|
| `CICLO` | varchar(50) | Ciclo académico (ej. `ESP_2026_II`, `ORD_2026_II`, `SUP_2027_I`) | Filtro y Gráfico de Barras |
| `CODIGO` | int(11) | Código del alumno | **SOLO TRAZABILIDAD (NO EXPONER)** |
| `APE_PATERNO` | varchar(200) | Apellido paterno | **PROHIBIDO EXPONER EN UI** |
| `APE_MATERNO` | varchar(200) | Apellido materno | **PROHIBIDO EXPONER EN UI** |
| `NOMBRES` | varchar(300) | Nombres | **PROHIBIDO EXPONER EN UI** |
| `LOCAL` | varchar(200) | Sede institucional (10 sedes) | Filtro, Barras y Cruce |
| `TURNO` | varchar(50) | `MAÑANA`, `TARDE` | Filtro, Gráfico de Dona y Cruce |
| `AULA` | int(11) | Código de aula asignada | Opcional / Métricas futuras |
| `AREA` | varchar(50) | Área académica (`A` a `E`) | Filtro y Gráfico de Barras |
| `CARRERA` | varchar(200) | Carrera profesional (70 carreras) | Ranking Top 15 Carreras |
| `fecha_matricula`| date | Fecha de inscripción | Rango de fechas, KPIs y Evolución |
| `hora_matricula` | time | Hora de la matrícula | Opcional / Métricas futuras |

### 5.1. Datos Observados en Producción (Validado en Vivo)
- **Volumen actual:** 750+ matriculados
- **Locales activos (10):** `C.U. (LOCAL CENTRAL)`, `CIUDAD UNIVERSITARIA`, `JESUS MARIA`, `SAN JUAN DE LURIGANCHO`, `SAN JUAN DE MIRAFLORES`, `SAN MARTIN DE PORRES`, `SANTA ANITA`, `VILLA MARIA DEL TRIUNFO`, `VIRTUAL`, `ZAPALLAL`
- **Carreras registradas:** 70 carreras profesionales (con Medicina Humana y Derecho liderando volumen)
- **Ciclos vigentes:** `ESP_2026_II`, `ORD_2026_II`, `SUP_2027_I`

### 5.2. Vista de Pagos Recientes (`vw_pagos_recientes` / `DB_PAGOS_VIEW`)

| Columna | Tipo | Descripción | Uso en Dashboard |
|---|---|---|---|
| `idproducto` | int(11) | Identificador del producto bancario | Mapeo de ciclo (2: ORD, 5: ESP, 81: SUP) |
| `anio_prod` | int(11) | Año del producto | Trazabilidad de año académico |
| `pago_ciclo` | varchar(11) | Ciclo (`ORD_2026_II`, `ESP_2026_II`, `SUP_2027_I`) | Filtro dinámico con selector de ciclo |
| `monto_pago` | double | Monto recaudado del pago | Sumatoria agregada en tarjeta KPI |
| `fecha_pago` | date | Fecha de recepción en banco | Trazabilidad reciente (últimos 3 días) |

---

## 6. Comandos Operativos Clave

### Ejecutar Servidor Streamlit
```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Ejecutar Pruebas Automatizadas
```bash
python test_app.py
```

### Generar Hashes de Nuevas Contraseñas
```bash
python generate_keys.py "MiPasswordSeguro2026!"
```

---

## 7. Usuarios Autorizados Predefinidos

| Usuario | Clave inicial | Nombre |
|---|---|---|
| `admin` | `admin2026` | Administrador del Sistema |
| `jperez` | `jperez2026` | Juan Pérez |
| `directivo` | `directivo2026` | Dirección Académica |
