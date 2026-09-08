# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Directivos, directores de admisión y coordinadores académicos institucionales del CEPRE que monitorean el avance del proceso de matrícula en tiempo real. Su tarea clave es evaluar el cumplimiento de metas de captación, ajustar la capacidad instalada y decidir estratégicamente sobre vacantes, horarios y apertura o cierre de grupos por sede y turno.

## Product Purpose

Proveer un tablero de control ejecutivo de alta fidelidad para el monitoreo inmediato y estratégico de las inscripciones estudiantiles. Permite a las autoridades tomar decisiones operativas y presupuestarias oportunas sin depender de reportes estáticos ni procesos ETL intermediarios.

## Positioning

Tablero web ligero y reactivo conectado directamente a la vista de producción de la base de datos institucional (`DB_VIEW`) sobre red interna / VPN. Ofrece datos al minuto con amortiguación inteligente por caché (`@st.cache_data`), soporte para modo de demostración sin conexión (SQLite) y garantía total de confidencialidad de datos.

## Operating Context

- Entorno de red privada / VPN institucional con acceso exclusivo para usuarios autorizados autenticados con contraseñas encriptadas (bcrypt).
- Utilizado primordialmente en reuniones de comité directivo y sesiones de seguimiento de admisiones en computadoras portátiles y pantallas de escritorio.
- Pila tecnológica en producción: Python 3.12, Streamlit 1.37+, SQLAlchemy 2.0 y Plotly Express / Graph Objects.

## Capabilities and Constraints

- **Capacidades Confirmadas:** Visualización de KPIs clave (total de inscritos, avance hacia la meta, desglose por turno mañana/tarde), análisis por sedes (10 locales activos), distribución por áreas académicas (A a E), ranking Top de carreras y filtrado multidimensional cruzado por ciclo, sede, turno y rango de fechas.
- **Restricciones Mandatorias de Confidencialidad:** Las columnas `APE_PATERNO`, `APE_MATERNO`, `NOMBRES` y `CODIGO` **nunca** se consultan para visualización ni se exponen en la interfaz, gráficos ni tablas. Todas las operaciones en UI son exclusivamente agregadas (`COUNT`, `GROUP BY`).
- **Restricciones Técnicas:** Consultas SQL estrictamente parametrizadas con placeholders `:param` para eliminar cualquier vector de inyección SQL.

## Brand Commitments

- Estética visual ejecutiva de alta gama: paleta institucional sobria con contraste calibrado para modo oscuro y claro.
- Tarjetas KPI con arquitectura **Double-Bezel** (doble bisel anidado con brillo ambiental sutil y elevación hover).
- Tipografías modernas `Outfit` (titulares y valores métricos con números tabulares `tabular-nums`) y `Plus Jakarta Sans` (cuerpo y controles).
- Gráficos integrados con fondo transparente (`rgba(0,0,0,0)`) y tooltips oscuros tipo pastilla.

## Evidence on Hand

- Vista en base de datos de producción con más de 750 registros reales validados en ciclos activos (`ORD_2026_II`, `ESP_2026_II`, `SUP_2027_I`).
- 10 locales identificados y 70 carreras registradas.
- Base de datos local SQLite (`demo_data.sqlite`) con esquema idéntico para desarrollo offline y modo demostración.
- Especificación funcional en [MVP_Dashboard_Matriculas.md](file:///d:/pra/dashboard_matriculados/MVP_Dashboard_Matriculas.md) y directrices en [AGENTS.md](file:///d:/pra/dashboard_matriculados/AGENTS.md).

## Product Principles

1. **Privacidad Estricta por Diseño:** Ningún dato personal identificable de los estudiantes cruza a la capa visual; las decisiones se basan en métricas agregadas confiables.
2. **Inmediatez y Fidelidad de Datos:** Sin desfases ni transformaciones intermedias; refleja el pulso vivo de la matrícula tal como se registra en la base de datos.
3. **Escaneabilidad Ejecutiva Instantánea:** Arquitectura de información diseñada para que un directivo entienda el estado general del proceso en menos de 5 segundos.
4. **Resiliencia Operativa:** Fallback transparente a modo demo si la VPN no está conectada, garantizando continuidad de presentación en cualquier circunstancia.

## Accessibility & Inclusion

- Alto ratio de contraste en textos, tarjetas e indicadores tanto en tema claro como oscuro.
- Formato numérico tabular (`tabular-nums`) para evitar oscilaciones visuales y facilitar la comparación rápida de cifras.
- Controles de selección y filtros accesibles mediante teclado y lectores de pantalla.
