# MVP — Dashboard de Métricas de Matrícula

Aplicación web desarrollada en **Python + Streamlit** para el monitoreo en tiempo real de métricas de matrícula de estudiantes, consultando directamente la vista de base de datos institucional (con soporte para modo demostración / fallback local para desarrollo y pruebas).

---

## 🚀 Características Principales

- **Autenticación Previa (Login seguro):** Acceso restringido mediante `streamlit-authenticator` con contraseñas cifradas en **bcrypt**, sesiones mediante cookie firmada (expiración configurable de ~8 horas) y bloqueo tras 3 intentos consecutivos.
- **Consultas en Tiempo Real:** Agregaciones SQL directas (`GROUP BY`, `COUNT`) optimizadas en el motor de base de datos con `@st.cache_data(ttl=30)`.
- **4 Tarjetas KPI Resumen con Doble Bisel:**
  - Total de matriculados activos según filtros.
  - Locales activos con matrícula.
  - Carreras con al menos un matriculado.
  - Matriculados del día actual (`fecha_matricula = CURDATE()`).
- **6 Gráficos Plotly Interactivos (Cuadrícula Bento):**
  1. *Matriculados por Ciclo* (Barras con totales).
  2. *Matriculados por Turno* (Gráfico de Dona con número central).
  3. *Matriculados por Área* (Distribución en áreas A, B, C, D, E).
  4. *Top 15 Carreras con Mayor Matrícula* (Ranking horizontal ordenado).
  5. *Matriculados por Local / Sede* (Distribución en las 10 sedes).
  6. *Evolución Cronológica de Matrículas* (Volumen diario + curva acumulada).
  7. *Cruce Local × Turno* (Barras apiladas informativas).
- **Tabla Resumen Consolidada (Ciclo × Local × Turno):** Matriz detallada con encabezados en azul, conteo exacto por local y turno, fila de **TOTAL GENERAL** al pie de tabla, opción de explorador interactivo y exportación directa a CSV.
- **Filtros Globales Dinámicos:** Ciclo, Local, Turno, Área y Rango de Fechas sincronizados en todo el tablero con botones de *Restablecer* y *Refrescar*.
- **Privacidad Estricta:** Ninguna columna con datos personales del estudiante (`APE_PATERNO`, `APE_MATERNO`, `NOMBRES`, `CODIGO`) se extrae ni se expone en la interfaz gráfica.
- **Resiliencia / Modo Demostración:** Si el servidor de base de datos no está accesible (por ejemplo, fuera de la VPN institucional), el sistema inicia automáticamente en *Modo Demostración* con datos sintéticos basados en la especificación, permitiendo pruebas inmediatas.

---

## 📁 Estructura del Proyecto

```
mvp-dashboard-matriculas/
├── app.py                   # UI principal, layout Bento, filtros y gráficos Plotly
├── auth.py                  # Flujo de autenticación y control de acceso
├── db.py                    # Conexión SQLAlchemy a la base de datos + fallback en memoria
├── queries.py               # Consultas SQL agregadas y parametrizadas
├── styles.py                # Estilos CSS ejecutivos (Outfit, Plus Jakarta Sans, Double-Bezel)
├── generate_keys.py         # Utilidad CLI para generar hashes de contraseñas
├── credentials.yaml         # Usuarios autorizados y claves cifradas (ignorado en git)
├── credentials.yaml.example # Plantilla de configuración de usuarios
├── .env                     # Credenciales de conexión (ignorado en git)
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt         # Lista de dependencias del proyecto
├── .gitignore               # Archivos protegidos y exclusiones
└── README.md                # Documentación del proyecto
```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio y crear entorno virtual

```bash
cd d:/pra/dashboard_matriculados
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar conexión a la base de datos (`.env`)

Copie la plantilla y defina los datos del usuario de solo lectura:

```bash
cp .env.example .env
```

Edite el archivo `.env`:

```env
DB_HOST=172.16.245.13    # Dirección del servidor en la VPN
DB_PORT=3306
DB_NAME=bd_matricula
DB_USER=usuario_reporte
DB_PASSWORD='contraseña_segura'
DB_VIEW=nombre_de_la_vista
DEMO_MODE=false          # Cambiar a true si desea forzar datos de prueba
```

### 4. Configurar usuarios y contraseñas (`credentials.yaml`)

El sistema incluye usuarios predefinidos en `credentials.yaml`:

| Usuario | Nombre | Contraseña inicial |
|---|---|---|
| `admin` | Administrador del Sistema | `admin2026` |
| `jperez` | Juan Pérez | `jperez2026` |
| `directivo` | Dirección Académica | `directivo2026` |

Para generar un nuevo hash bcrypt para una contraseña personalizada, ejecute:

```bash
python generate_keys.py "MiNuevaClave2026!"
```

Pegue el hash resultante en el archivo `credentials.yaml`.

---

## 🖥️ Ejecución del Dashboard

Para iniciar el servidor local en red interna / VPN:

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Acceda desde el navegador a:
- Local: `http://localhost:8501`
- Red Interna: `http://<IP_DE_TU_MAQUINA>:8501`

---

## 🔒 Seguridad y Buenas Prácticas

1. **Parámetros Vinculados:** Todas las consultas en `queries.py` utilizan parámetros `:param` para prevenir cualquier riesgo de inyección SQL.
2. **Caché Eficiente:** Se utiliza `@st.cache_data(ttl=30)` para evitar saturar la base de datos con consultas redundantes en recargas continuas.
3. **No Exposición de Secretos:** Tanto `.env` como `credentials.yaml` están registrados en `.gitignore` para evitar filtraciones accidentales al repositorio.
