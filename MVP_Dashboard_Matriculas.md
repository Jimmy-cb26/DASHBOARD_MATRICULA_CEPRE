# MVP — Dashboard de Métricas de Matrícula

## 1. Objetivo del proyecto

Construir una aplicación web (MVP) que muestre en tiempo real métricas de matrícula de estudiantes, consultando directamente una vista ya existente en la base de datos institucional. El dashboard debe permitir al equipo interno visualizar volúmenes de matriculados y sus distribuciones por ciclo, local, turno, área y carrera.

## 2. Contexto y fuente de datos

- **Motor de base de datos:** Relacional (SQL)
- **Fuente:** vista `vw_matriculados` (ya creada en la BD)
- **Usuario de conexión:** ya existe y tiene permisos de solo lectura sobre la vista. No se requiere crear un nuevo usuario ni modificar permisos.
- **Modo de actualización:** tiempo real — cada interacción del usuario (cambio de filtro, recarga de página) debe consultar la vista directamente, sin ETL ni tablas intermedias.

### 2.1 Estructura de la vista `vw_matriculados`

| Columna | Tipo (inferido) | Descripción | Ejemplo |
|---|---|---|---|
| `CICLO` | varchar | Ciclo académico (formato `TIPO_AÑO_ROMANO`) | `ORD_2026_II` |
| `CODIGO` | int | Código único del alumno | `210010` |
| `APE_PATERNO` | varchar | Apellido paterno | `VASQUEZ` |
| `APE_MATERNO` | varchar | Apellido materno | `GOMEZ` |
| `NOMBRES` | varchar | Nombres del alumno | `MIA LINDSAY` |
| `LOCAL` | varchar | Sede / local donde se matriculó | `CIUDAD UNIVERSITARIA` |
| `TURNO` | varchar | Turno de estudio | `MAÑANA`, `TARDE` |
| `AULA` | int | Número/código de aula asignada | `31` |
| `AREA` | varchar | Área académica (codificada) | `A`, `B`, `C`, `D`, `E` |
| `CARRERA` | varchar | Carrera profesional | `MEDICINA HUMANA` |
| `fecha_matricula` | date | Fecha en que se realizó la matrícula | `2026-07-02` |
| `hora_matricula` | time | Hora exacta de la matrícula | `13:02:14` |

**Valores observados en la muestra actual (referencial, no exhaustivo):**
- `CICLO`: 3 valores distintos (ej. `ESP_2026_II`, `ORD_2026_II`, `SUP_2027_I`)
- `LOCAL`: 10 sedes distintas
- `TURNO`: 2 valores (`MAÑANA`, `TARDE`)
- `AREA`: 5 valores (`A` a `E`)
- `CARRERA`: ~70 carreras distintas

> Nota para el agente de desarrollo: los datos anteriores fueron levantados a partir de una muestra exportada (680 filas). Validar contra la vista real en producción antes de fijar listas de valores en el código (por ejemplo, para poblar filtros, usar `SELECT DISTINCT` en vez de hardcodear).

## 3. Alcance del MVP

### Incluido
- Ventana de login previa al dashboard (ver sección 6.4), con un máximo de 5 usuarios internos predefinidos.
- Pantalla única de dashboard con:
  - Tarjetas KPI (totales generales)
  - Gráficos de distribución por ciclo, local, turno y área
  - Ranking de carreras con más matriculados
  - Evolución de matrículas por fecha
  - Filtros interactivos (ciclo, local, turno, área)
- Conexión en tiempo real a la vista de base de datos (sin caché persistente; caché de muy corta duración aceptable solo por performance, ver sección 6).
- Despliegue accesible dentro de la red interna / VPN de la institución (no expuesto a internet público).

### Explícitamente fuera de alcance (para futuras iteraciones)
- Roles o permisos diferenciados entre usuarios (todos los usuarios autenticados ven el mismo dashboard completo)
- Recuperación de contraseña self-service (para 5 usuarios, se gestiona manualmente)
- Integración con Active Directory / LDAP / SSO institucional (no aplica: la institución no cuenta con sistema centralizado)
- Exportación a PDF/Excel desde el dashboard
- Datos de alumnos a nivel individual (nombres) en las vistas gráficas — por privacidad, no mostrar `APE_PATERNO`, `APE_MATERNO`, `NOMBRES` en gráficos ni tablas agregadas. Estas columnas solo existen en la vista por trazabilidad, no deben exponerse en el dashboard.
- Comparativas entre ciclos históricos (multi-ciclo) — el MVP puede limitarse al ciclo/ciclos vigentes.
- Alertas o notificaciones automáticas.

## 4. Métricas y KPIs requeridos

### 4.1 KPIs (tarjetas resumen)
1. Total de matriculados (según filtros aplicados)
2. Total de locales activos con matrícula
3. Total de carreras con al menos 1 matriculado
4. Matriculados del día actual (basado en `fecha_matricula = CURDATE()`)

### 4.2 Gráficos de distribución
1. **Matriculados por ciclo** — gráfico de barras
2. **Matriculados por local** — gráfico de barras horizontal (10 sedes)
3. **Matriculados por turno** — gráfico de dona/pastel (2 valores)
4. **Matriculados por área** — gráfico de barras o dona (5 valores)
5. **Top carreras con más matriculados** — barras horizontales, top 15
6. **Evolución de matrículas en el tiempo** — gráfico de línea, matriculados por `fecha_matricula`

### 4.3 Cruces útiles (opcional si el tiempo lo permite)
- Local × Turno (tabla o barras agrupadas)
- Área × Carrera (para detectar concentración dentro de un área)

## 5. Filtros requeridos

Todos los filtros deben aplicarse sobre **todas** las visualizaciones simultáneamente (filtro global, no por gráfico):

| Filtro | Tipo de control | Fuente de opciones |
|---|---|---|
| Ciclo | Multi-select | `SELECT DISTINCT CICLO FROM vw_matriculados` |
| Local | Multi-select | `SELECT DISTINCT LOCAL FROM vw_matriculados` |
| Turno | Multi-select | `SELECT DISTINCT TURNO FROM vw_matriculados` |
| Área | Multi-select | `SELECT DISTINCT AREA FROM vw_matriculados` |
| Rango de fechas | Selector de fechas (desde/hasta) | Basado en `fecha_matricula` |

## 6. Arquitectura técnica propuesta

- **Stack:** Python + Streamlit (single app, sin necesidad de backend/frontend separados para el MVP)
- **Librería de conexión a BD:** `SQLAlchemy` + driver de conexión
- **Librería de gráficos:** `plotly` (interactividad) o `altair`
- **Consultas:** agregaciones con `GROUP BY` ejecutadas directamente en la base de datos (no traer el detalle fila por fila a Python cuando el volumen crezca)
- **Caché:** usar `st.cache_data(ttl=30)` (30–60 segundos) únicamente para suavizar la carga en la BD ante múltiples usuarios simultáneos; no debe percibirse como desactualizado por el usuario final
- **Despliegue:** `streamlit run app.py --server.address 0.0.0.0 --server.port 8501`, accesible solo dentro de la red interna / VPN. No exponer a internet público en esta fase.
- **Credenciales de conexión:** manejarlas vía archivo `.env` (no hardcodear en el código), usando el usuario de solo lectura ya provisionado.

### 6.1 Diagrama de flujo

```
[Base de Datos: Vista de matrícula] 
        |  (SELECT con GROUP BY, usuario solo-lectura)
        v
[App Streamlit: db.py / queries.py]
        |  (agregaciones -> DataFrame)
        v
[App Streamlit: app.py -> componentes UI + gráficos Plotly]
        |
        v
[Usuarios internos vía navegador, dentro de VPN/red local]
```

### 6.2 Estructura de archivos sugerida

```
mvp-dashboard-matriculas/
├── app.py                # UI principal, filtros y layout del dashboard
├── db.py                 # Conexión a BD (engine SQLAlchemy)
├── queries.py             # Funciones con las consultas SQL agregadas
├── requirements.txt
├── .env.example           # Plantilla de variables de entorno (sin valores reales)
└── README.md              # Instrucciones de instalación y ejecución
```

### 6.3 Variables de entorno (`.env.example`)

```
DB_HOST=
DB_PORT=3306
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_VIEW=vw_matriculados
```

### 6.4 Autenticación (login)

Dado que no existe un sistema de cuentas centralizado (AD/LDAP/SSO) y el acceso está limitado a un máximo de 5 usuarios internos, se usará la librería **`streamlit-authenticator`** para agregar una ventana de login antes de renderizar el dashboard. No se requiere una base de datos de usuarios ni infraestructura adicional.

**Comportamiento esperado:**
1. Al abrir la URL de la app, se muestra un formulario de login (usuario + contraseña). Ningún dato ni gráfico del dashboard se renderiza antes de autenticarse.
2. Si las credenciales son correctas, se crea una sesión (cookie firmada) con expiración configurable (sugerido: 8 horas).
3. Se muestra un botón de "Cerrar sesión" visible en el sidebar del dashboard.
4. Máximo 3 intentos fallidos consecutivos antes de un breve bloqueo temporal (soportado nativamente por la librería).

**Gestión de usuarios (hasta 5, mantenimiento manual):**
- Los usuarios se definen en un archivo `credentials.yaml`, **fuera del repositorio de código** (agregado a `.gitignore`), con la siguiente estructura:

```yaml
credentials:
  usernames:
    jperez:
      name: Juan Pérez
      password: $2b$12$... # hash bcrypt, nunca texto plano
cookie:
  name: dashboard_matriculas_auth
  key: <clave_secreta_aleatoria>
  expiry_days: 0.33   # ≈ 8 horas
```

- Las contraseñas se generan una sola vez con el propio generador de hashes que trae `streamlit-authenticator` (script de línea de comandos), nunca se guardan en texto plano.
- Agregar/eliminar un usuario es una edición manual de este archivo — no se requiere UI de administración para el MVP, dado el volumen de 5 usuarios.

**Estructura de archivos actualizada:**

```
mvp-dashboard-matriculas/
├── app.py
├── db.py
├── queries.py
├── auth.py                # Carga de credentials.yaml e inicialización de streamlit-authenticator
├── credentials.yaml        # NO subir al repositorio (.gitignore)
├── requirements.txt        # incluir streamlit-authenticator
├── .env.example
├── .gitignore              # debe incluir .env y credentials.yaml
└── README.md
```

**Nota de seguridad:** dado que el dashboard además viaja dentro de la red interna/VPN, el login es una segunda capa de control (defensa en profundidad), no la única. Aun así, no debe omitirse: cualquier persona dentro de la red no debería poder ver los datos sin credenciales válidas.

## 7. Consultas SQL de referencia

```sql
-- Total matriculados (respetando filtros del usuario)
SELECT COUNT(*) AS total
FROM vw_matriculados
WHERE 1=1
  -- AND CICLO IN (...) AND LOCAL IN (...) AND TURNO IN (...) AND AREA IN (...)
  -- AND fecha_matricula BETWEEN :desde AND :hasta;

-- Matriculados por ciclo
SELECT CICLO, COUNT(*) AS total
FROM vw_matriculados
GROUP BY CICLO
ORDER BY total DESC;

-- Matriculados por local
SELECT LOCAL, COUNT(*) AS total
FROM vw_matriculados
GROUP BY LOCAL
ORDER BY total DESC;

-- Matriculados por turno
SELECT TURNO, COUNT(*) AS total
FROM vw_matriculados
GROUP BY TURNO
ORDER BY total DESC;

-- Matriculados por área
SELECT AREA, COUNT(*) AS total
FROM vw_matriculados
GROUP BY AREA
ORDER BY total DESC;

-- Top carreras con más matriculados
SELECT CARRERA, COUNT(*) AS total
FROM vw_matriculados
GROUP BY CARRERA
ORDER BY total DESC
LIMIT 15;

-- Evolución de matrículas por fecha
SELECT fecha_matricula, COUNT(*) AS total
FROM vw_matriculados
GROUP BY fecha_matricula
ORDER BY fecha_matricula;

-- Cruce Local x Turno
SELECT LOCAL, TURNO, COUNT(*) AS total
FROM vw_matriculados
GROUP BY LOCAL, TURNO
ORDER BY LOCAL, TURNO;
```

> Todas las consultas con filtros deben construirse de forma parametrizada (placeholders `:param` o `%s` según el driver) para evitar inyección SQL — nunca concatenar directamente los valores de los filtros del usuario en el string SQL.

## 8. Requisitos no funcionales

- **Rendimiento:** el dashboard debe cargar en menos de 3 segundos con el volumen actual de datos (cientos–pocos miles de filas). Si el volumen crece significativamente, evaluar índices en `CICLO`, `LOCAL`, `TURNO`, `AREA`, `fecha_matricula`.
- **Seguridad:** 
  - Usar exclusivamente el usuario de solo lectura ya provisionado.
  - Nunca exponer las columnas `APE_PATERNO`, `APE_MATERNO`, `NOMBRES` en el dashboard.
  - Credenciales solo en `.env`, nunca en el repositorio de código (agregar `.env` a `.gitignore`).
- **Disponibilidad:** acceso limitado a la red interna/VPN; no requiere alta disponibilidad para el MVP.
- **Compatibilidad:** debe funcionar correctamente en los navegadores estándar (Chrome/Edge) usados por el equipo interno.

## 9. Criterios de aceptación

1. Al abrir la app sin haber iniciado sesión, no se muestra ningún dato del dashboard — solo el formulario de login. Con credenciales inválidas, se rechaza el acceso con un mensaje de error claro.
2. Con credenciales válidas, se accede al dashboard y la sesión se mantiene activa sin pedir login nuevamente durante el periodo configurado (~8 horas) o hasta hacer clic en "Cerrar sesión".
3. Al abrir la app sin filtros, se muestran los 4 KPIs y los 6 gráficos con los totales correctos (verificables contra un `COUNT(*)` manual en el gestor de base de datos u otra herramienta).
4. Al aplicar cualquier combinación de filtros (ciclo, local, turno, área, rango de fechas), todos los gráficos y KPIs se actualizan de forma consistente entre sí.
5. Los datos reflejan cambios en la BD en tiempo real (o con un desfase máximo de ~30-60 segundos si se usa caché corta).
6. Ninguna columna con datos personales del alumno (nombres/apellidos) es visible en ninguna parte del dashboard.
7. La app es accesible desde cualquier equipo dentro de la red interna/VPN sin necesitar exponerla a internet.
8. Las credenciales de conexión (BD) y de autenticación (usuarios/contraseñas) no están hardcodeadas ni en texto plano en el código fuente.

## 10. Próximos pasos sugeridos (post-MVP)

- Agregar autenticación básica (usuario/contraseña o SSO institucional).
- Exportación de reportes (Excel/PDF).
- Histórico comparativo entre ciclos.
- Métricas adicionales: matriculados por aula (ocupación), distribución por hora del día (a partir de `hora_matricula`).
