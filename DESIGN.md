---
name: "Dashboard de Métricas de Matrícula"
description: "Sistema visual ejecutivo de alta fidelidad para el monitoreo en tiempo real del avance de matrícula universitaria"
colors:
  primary: "#1E40AF"
  primary-hover: "#1D4ED8"
  secondary: "#0284C7"
  indigo: "#6366F1"
  emerald: "#059669"
  amber: "#D97706"
  crimson: "#E11D48"
  slate: "#475569"
  canvas-dark: "#0B0F19"
  canvas-light: "#F8FAFC"
  surface-dark: "#152238"
  surface-light: "#FFFFFF"
  bezel-outer-dark: "#131C31"
  bezel-outer-light: "#FFFFFF"
  border-dark: "rgba(59, 130, 246, 0.85)"
  border-light: "#E2E8F0"
  text-dark-primary: "#F8FAFC"
  text-dark-secondary: "#CBD5E1"
  text-dark-muted: "#94A3B8"
  text-light-primary: "#0F172A"
  text-light-secondary: "#475569"
  text-light-muted: "#64748B"
typography:
  display:
    fontFamily: "Outfit, sans-serif"
    fontSize: "clamp(2rem, 3.5vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.1
  headline:
    fontFamily: "Outfit, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 600
    lineHeight: 1.25
  title:
    fontFamily: "Outfit, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "0.925rem"
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.4
  label:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  bezel-inner: "12px"
  bezel-outer: "18px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  card-kpi:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.text-dark-primary}"
    rounded: "{rounded.bezel-outer}"
    padding: "16px 20px"
  card-graph:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.text-dark-primary}"
    rounded: "{rounded.bezel-outer}"
    padding: "20px 24px"
  badge-live:
    backgroundColor: "{colors.bezel-outer-dark}"
    textColor: "{colors.text-dark-primary}"
    rounded: "{rounded.sm}"
    padding: "4px 10px"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text-dark-primary}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
---

# Design System: Dashboard de Métricas de Matrícula

## Overview

**Creative North Star: "El Observatorio Académico de Élite (The Executive Academic Observatory)"**

El Observatorio Académico de Élite está concebido para conferir a los directivos y coordinadores una visión diáfana, soberana y en tiempo real del avance del proceso de matrícula estudiantil. La interfaz prescinde del ruido ornamental para abrazar una densidad analítica impecable, donde cada cifra posee peso de decisión y cada visualización responde a una pregunta operativa concreta. El sistema opera como un instrumento de precisión institucional: sereno, autoritativo y matemáticamente riguroso.

La atmósfera equilibra la sobriedad académica con un refinamiento contemporáneo inspirado en interfaces de alta ingeniería. En modo oscuro, el lienzo azul abisal profundo (`#0B0F19`) evoca un centro de mando con paneles retroiluminados; en modo claro, el fondo alabastro puro (`#F8FAFC`) proporciona una legibilidad cristalina ideal para auditorías y presentaciones ejecutivas matutinas. La arquitectura de doble bisel (*Double-Bezel*) otorga a cada tarjeta de KPI y gráfico una presencia táctil tridimensional que flota con elegancia sobre el lienzo.

**Key Characteristics:**
- **Claridad Jerárquica Absoluta:** Los totales y ratios de cumplimiento capturan la mirada en el primer milisegundo mediante cifras en escala display con números tabulares.
- **Doble Bisel Anidado (Double-Bezel):** Un marco exterior protector aloja un contenedor interior biselado con gradiente sutil y realce de luz especular superior.
- **Tipografía Bipolar Calibrada:** *Outfit* comanda la escena analítica para titulares y números de alto impacto, mientras *Plus Jakarta Sans* gestiona el ritmo de lectura y microcopias.
- **Gráficos Transparentes Integrados:** Los gráficos Plotly se funden con el fondo del contenedor, eliminando bordes internos y cajas duras.

## Colors

El espectro cromático combina tonos institucionales de zafiro y cerúleo con acentos temáticos desaturados que clasifican de inmediato turnos y áreas académicas sin saturar la atención.

### Primary
- **Azul Zafiro Institucional** (`#1E40AF` / hover `#1D4ED8`): Identidad primaria del sistema, utilizado para elementos de mando directivo, barra de progreso principal de matrícula y botones primarios.

### Secondary
- **Cerúleo Refinado** (`#0284C7`): Tono de apoyo para métricas de proyección, acentos interactivos y gráficos secundarios.

### Tertiary (Acentos Temáticos)
- **Ámbar Ocre** (`#D97706`): Reservado para el turno Tarde, metas de advertencia y Área D (Ciencias Económicas y Gestión).
- **Rosa Carmesí** (`#E11D48`): Reservado para Área A (Ciencias de la Salud) y alertas de umbral crítico.
- **Esmeralda Profundo** (`#059669`): Indicador de avance completado, estado en vivo (pulsing dot) y Área B (Ciencias Básicas).
- **Iris Índigo / Violeta** (`#6366F1` / `#7C3AED`): Identificador del turno Noche y Área E (Humanidades y Ciencias Sociales).

### Neutral
- **Abisal Profundo (Dark Canvas)** (`#0B0F19`): Fondo principal inmersivo en modo oscuro.
- **Alabastro Fresco (Light Canvas)** (`#F8FAFC`): Fondo diurno de alto contraste en modo claro.
- **Superficie Marina (Dark Surface)** (`#152238`): Relleno de tarjetas y paneles en modo oscuro.
- **Blanco Puro (Light Surface)** (`#FFFFFF`): Relleno de tarjetas y paneles en modo claro.
- **Borde de Zafiro Lúcido** (`rgba(59, 130, 246, 0.85)` en oscuro, `#E2E8F0` en claro): Frontera estructural de contenedores.
- **Texto Principal** (`#F8FAFC` en oscuro, `#0F172A` en claro): Máxima nitidez para datos y etiquetas.
- **Texto Secundario / Muted** (`#CBD5E1` / `#94A3B8` en oscuro, `#64748B` / `#94A3B8` en claro): Metadatos y contexto.

### Named Rules
**The Strict Data Tint Rule.** Los colores de acento (`#E11D48`, `#059669`, `#D97706`) están estrictamente restringidos a codificar datos reales (áreas, turnos, metas de progreso). Ningún contenedor estático ni adorno tipográfico puede emplearlos sin un significado analítico subyacente.

**The Contrast Floor Rule.** Todo texto secundario y etiqueta numérica debe sostener un ratio de contraste mínimo de 4.5:1 contra su superficie inmediata, tanto en modo oscuro como en modo claro.

## Typography

**Display Font:** Outfit (fallback: sans-serif)  
**Body Font:** Plus Jakarta Sans (fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif)  
**Numeric Mode:** `tabular-nums` obligatorio en todos los valores numéricos y tablas.

**Character:** La combinación contrasta la geometría limpia y amplia de *Outfit* en cifras de gran tamaño con la legibilidad compacta y neutral de *Plus Jakarta Sans* para controles e interfaces de datos densos.

### Hierarchy
- **Display** (Bold 700, `clamp(2rem, 3.5vw, 2.75rem)`, line-height 1.1): Valores principales de KPI e indicadores magnos de avance de meta. Siempre con números tabulares.
- **Headline** (SemiBold 600, `1.35rem`, line-height 1.25): Títulos de sección analítica, nombres de bloques y encabezados de página.
- **Title** (SemiBold 600, `1.1rem`, line-height 1.3): Títulos de gráficos enmarcados y encabezados de tarjetas individuales.
- **Body** (Regular 400, `0.925rem`, line-height 1.5): Textos explicativos, nombres de carreras en listas y descripciones operativas.
- **Label / Eyebrow** (SemiBold 600, `0.75rem`, letter-spacing `0.05em`, uppercase): Etiquetas de categoría sobre tarjetas KPI y cabeceras de columnas en tablas.

### Named Rules
**The Tabular Integrity Rule.** Todo número que exprese una cantidad de alumnos, vacantes, porcentajes o fechas debe renderizarse con la propiedad CSS `font-variant-numeric: tabular-nums` para garantizar alineación vertical perfecta entre filas y evitar oscilaciones visuales al refrescar datos.

## Layout

El layout utiliza un sistema de contenedor centrado con ancho máximo de `1440px`, protegido por un acolchado horizontal fluido (`2.5rem` en escritorio, `1.25rem` en móvil). 

- **Espaciado Vertical:** Ritmo estricto de módulo 8px (`8px`, `16px`, `24px`, `32px`). La separación entre filas principales de métricas es de `24px`.
- **Rejilla KPI (Top Tier):** 3 a 4 columnas simétricas de tarjetas métricas con altura uniforme y distribución flexible.
- **Rejilla Gráfica (Middle & Lower Tier):** Filas de dos columnas (`1:1`) para comparativas correlativas (ej. distribución de turnos vs. sedes), o filas de ancho completo (`1fr`) para rankings detallados de carreras y tablas consolidadas.
- **Sidebar Ejecutivo:** Panel lateral colapsable (`#0D1322` en oscuro, `#FFFFFF` en claro) de ancho fijo de 320px que agrupa los filtros multidimensionales (Ciclo, Sede, Turno, Área, Rango de Fechas) sin contaminar el área de visualización.

## Elevation & Depth

La profundidad en el sistema no depende de sombras oscuras pesadas, sino de una arquitectura de **Doble Bisel Anidado (Double-Bezel)** complementada con un resplandor ambiental sutil.

### Shadow Vocabulary
- **Ambient Bezel Drop** (`0 4px 16px rgba(0, 0, 0, 0.55)` en oscuro, `0 4px 14px -2px rgba(15, 23, 42, 0.04)` en claro): Sostiene la tarjeta flotando sobre el lienzo principal.
- **Specular Inset Highlight** (`inset 0 1px 0 rgba(255, 255, 255, 0.08)` en oscuro, `inset 0 1px 0 rgba(255, 255, 255, 0.9)` en claro): Línea de luz superior en el bisel interior que simula un corte biselado de cristal técnico.
- **Hover Luminescence** (`0 8px 28px rgba(0, 0, 0, 0.7), 0 0 0 2px rgba(96, 165, 250, 0.50)` en oscuro): Respuesta al cursor en tarjetas interactivas mediante un halo suave de luz cerúlea perimetral.

### Named Rules
**The Double-Bezel Anatomy Rule.** Todo contenedor principal de métrica o gráfico se compone de dos niveles: un marco exterior (`bezel-outer`) con borde exterior y sombra difusa, y un marco interior (`bezel-inner`) con relleno de gradiente sutil de 180° y bisel de luz interior.

## Shapes

- **Bisel Exterior (Outer Bezel):** Radio de `18px` (`border-radius: 18px`).
- **Bisel Interior (Inner Bezel):** Radio de `12px` (`border-radius: 12px`), manteniendo una concentricidad geométrica exacta con el marco exterior.
- **Píldoras y Chips (Badges & Eyebrows):** Radio completamente redondeado (`border-radius: 9999px`) o `6px` para etiquetas de estado rectangulares.
- **Controles y Botones:** Radio de curvatura suave de `10px` (`rounded.md`).

## Components

### Tarjeta de KPI (Double-Bezel KPI Card)
- **Marco Exterior:** Fondo `#131C31` (oscuro) / `#FFFFFF` (claro), borde `rgba(255,255,255,0.14)` / `rgba(226,232,240,0.9)`, radio 18px, padding 4px.
- **Marco Interior:** Gradiente `180deg, #18233D 0%, #11182B 100%`, radio 12px, padding 18px.
- **Eyebrow:** Píldora con fondo `rgba(37,99,235,0.22)`, texto `#93C5FD`, tipografía label 0.75rem.
- **Métrica Central:** Tipografía display *Outfit* 2.4rem, peso 700, números tabulares.
- **Context Tag:** Etiqueta inferior con texto secundario `#94A3B8` indicando base de cálculo o tendencia.

### Marco de Gráfico Unificado (Chart Wrapper Card)
- **Estructura:** Contenedor unificado (`stVerticalBlockBorderWrapper`) que encierra el título del gráfico y la figura Plotly en un solo marco continuo.
- **Comportamiento:** En hover, transiciona el borde a Cerúleo Refinado (`#93C5FD`) con curva `cubic-bezier(0.16, 1, 0.3, 1)`.

### Badge "En Vivo" (Live Indicator)
- **Estructura:** Chip de estado con indicador luminoso verde (`#10B981`) que pulsa mediante animación `@keyframes pulse-green` continua, confirmando conexión directa a la base de datos de producción.

### Barra de Progreso de Meta (Goal Progress Bar)
- **Pista:** Fondo neutro tenue con radio de 9999px y altura de 8px.
- **Relleno:** Gradiente continuo desde Azul Zafiro (`#1E40AF`) hasta Cerúleo (`#0284C7`), con porcentaje numérico anclado a la derecha.

### Tabla de Datos Ejecutiva (Ranking Grid)
- **Encabezados:** Fondo sutil con texto en mayúsculas `0.75rem` en Azul Zafiro (`#60A5FA` / `#1D4ED8`).
- **Filas:** Separadores de 1px con transición de iluminación suave al posar el cursor (`rgba(255,255,255,0.04)`).
- **Fila Totalizadora (Footer):** Borde superior reforzado de 2px con texto en negrita semi-extendida.

## Do's and Don'ts

### Do:
- **Do** utilizar siempre `font-variant-numeric: tabular-nums` en toda cifra métrica y columna de total.
- **Do** mantener el fondo de las figuras Plotly en transparencia total (`rgba(0,0,0,0)`) para que adopten el color y bisel del contenedor subyacente.
- **Do** preservar la arquitectura de doble bisel (`18px` exterior, `12px` interior) en todas las tarjetas de métricas nuevas.
- **Do** respetar el mapeo semántico estricto de colores para turnos (Mañana: azul, Tarde: ámbar, Noche: violeta) y áreas académicas.

### Don't:
- **Don't** exponer jamás nombres, apellidos o códigos de alumnos en tablas, gráficos, subtítulos ni tooltips.
- **Don't** emplear bordes duros de color saturado puro sin transparencia o gradiente de bisel.
- **Don't** mezclar tipografías ajenas a *Outfit* y *Plus Jakarta Sans*.
- **Don't** utilizar sombras negras opacas y pesadas que manchen el lienzo; utilizar sombras difusas con resplandor cerúleo en hover.
