"""
==============================================================================
Sistema de Diseño y Estilos de Alta Fidelidad (Awwwards / Linear Tier)
==============================================================================
Diseñado según los principios de:
- design-taste-frontend & high-end-visual-design
- Soporte completo y calibrado para Modo Claro (Light) y Modo Oscuro (Dark)
- Doble bisel (Double-Bezel architecture) con resplandor ambiental
- Marco completo para contenedores de gráficos (enmarcando título y gráfico juntos)
- Tipografía Plus Jakarta Sans + Outfit con números tabulares
- Micromovimientos con curvas cubic-bezier hápticas
- Paletas de color académicas sobrias y calibradas para Plotly
"""

import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go


# Paleta cromática curada (desaturada, de alta gama y contraste equilibrado)
COLOR_PALETTE = [
    "#1E40AF",  # Azul Zafiro Institucional
    "#0284C7",  # Cerúleo Refinado
    "#6366F1",  # Iris Índigo
    "#059669",  # Esmeralda Profundo
    "#D97706",  # Ámbar Ocre
    "#E11D48",  # Rosa Carmesí
    "#475569",  # Pizarra Neutro
    "#0D9488",  # Teal Calibrado
    "#7C3AED",  # Violeta Suave
    "#EA580C",  # Naranja Quemado
]

TURNO_COLORS = {
    "MAÑANA": "#1D4ED8",
    "TARDE": "#D97706",
    "NOCHE": "#6D28D9",
}

AREA_COLORS = {
    "A": "#E11D48",  # Ciencias de la Salud (Carmesí)
    "B": "#059669",  # Ciencias Básicas (Esmeralda)
    "C": "#1D4ED8",  # Ingenierías (Zafiro)
    "D": "#D97706",  # Ciencias Económicas y Gestión (Ámbar)
    "E": "#7C3AED",  # Humanidades y Ciencias Sociales (Violeta)
}

AREA_LABELS = {
    "A": "Área A: Ciencias de la Salud",
    "B": "Área B: Ciencias Básicas",
    "C": "Área C: Ingenierías",
    "D": "Área D: Ciencias Económicas y Gestión",
    "E": "Área E: Humanidades y Ciencias Sociales",
}



def _inject_container_js(
    card_bg: str,
    card_border: str,
    card_border_hover: str,
    card_shadow: str,
    card_shadow_hover: str,
):
    """
    Inyecta JavaScript via streamlit.components.v1.html para aplicar estilos
    en tiempo real a los marcos de contenedores (stVerticalBlockBorderWrapper).
    Usa window.parent.document para acceder al DOM principal desde el iframe.
    Un MutationObserver garantiza que los estilos se re-apliquen tras cada re-render.
    """
    js_code = f"""
    <script>
    (function() {{
        var doc = window.parent.document;
        var CARD_BG = "{card_bg}";
        var CARD_BORDER = "{card_border}";
        var CARD_BORDER_HOVER = "{card_border_hover}";
        var CARD_SHADOW = "{card_shadow}";
        var CARD_SHADOW_HOVER = "{card_shadow_hover}";

        function applyStyles() {{
            var containers = doc.querySelectorAll('div[data-testid="stVerticalBlockBorderWrapper"]');
            containers.forEach(function(el) {{
                el.style.setProperty('background-color', CARD_BG, 'important');
                el.style.setProperty('border', '2px solid ' + CARD_BORDER, 'important');
                el.style.setProperty('border-radius', '18px', 'important');
                el.style.setProperty('padding', '1.2rem 1.4rem', 'important');
                el.style.setProperty('box-shadow', CARD_SHADOW, 'important');
                el.style.setProperty('margin-bottom', '0.85rem', 'important');
                el.style.setProperty('overflow', 'visible', 'important');
                el.style.setProperty('transition', 'border-color 0.25s ease, box-shadow 0.25s ease', 'important');

                var child = el.firstElementChild;
                if (child) {{
                    child.style.setProperty('background-color', 'transparent', 'important');
                    child.style.setProperty('border', 'none', 'important');
                    child.style.setProperty('box-shadow', 'none', 'important');
                    child.style.setProperty('padding', '0', 'important');
                }}

                if (!el._marcoListening) {{
                    el._marcoListening = true;
                    el.addEventListener('mouseenter', function() {{
                        el.style.setProperty('border-color', CARD_BORDER_HOVER, 'important');
                        el.style.setProperty('box-shadow', CARD_SHADOW_HOVER, 'important');
                    }});
                    el.addEventListener('mouseleave', function() {{
                        el.style.setProperty('border-color', CARD_BORDER, 'important');
                        el.style.setProperty('box-shadow', CARD_SHADOW, 'important');
                    }});
                }}
            }});
        }}

        applyStyles();

        var observer = new MutationObserver(function(mutations) {{
            var added = false;
            mutations.forEach(function(m) {{ if (m.addedNodes.length) added = true; }});
            if (added) requestAnimationFrame(applyStyles);
        }});

        var root = doc.getElementById('root') || doc.body;
        if (root) {{
            observer.observe(root, {{ childList: true, subtree: true }});
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)


def inject_custom_css(theme: str = "light"):
    """
    Inyecta el sistema de diseño visual de élite para Streamlit,
    parametrizado de forma nativa para Modo Claro o Modo Oscuro.
    """
    is_dark = (theme == "dark")

    # Tokens de diseño según tema
    if is_dark:
        app_bg = "#0B0F19"
        sidebar_bg = "#0D1322"
        card_bg = "#152238"
        card_border = "rgba(59, 130, 246, 0.85)"
        card_border_hover = "#93C5FD"
        card_shadow = "0 4px 16px rgba(0, 0, 0, 0.55)"
        card_shadow_hover = "0 8px 28px rgba(0, 0, 0, 0.7), 0 0 0 2px rgba(96, 165, 250, 0.50)"
        text_primary = "#F8FAFC"
        text_secondary = "#CBD5E1"
        text_muted = "#94A3B8"
        divider_color = "rgba(255, 255, 255, 0.14)"
        bezel_outer_bg = "#131C31"
        bezel_outer_border = "rgba(255, 255, 255, 0.14)"
        bezel_inner_bg = "linear-gradient(180deg, #18233D 0%, #11182B 100%)"
        bezel_inner_border = "rgba(255, 255, 255, 0.08)"
        bezel_inner_shadow = "inset 0 1px 0 rgba(255, 255, 255, 0.08)"
        bezel_hover_border = "rgba(96, 165, 250, 0.4)"
        eyebrow_bg = "rgba(37, 99, 235, 0.22)"
        eyebrow_border = "rgba(59, 130, 246, 0.35)"
        eyebrow_color = "#93C5FD"
        tag_bg = "rgba(255, 255, 255, 0.08)"
        tag_color = "#CBD5E1"
        tag_border = "rgba(255, 255, 255, 0.12)"
        button_bg = "#1E293B"
        button_border = "rgba(255, 255, 255, 0.18)"
        button_color = "#F8FAFC"
        button_hover_bg = "#2A3B53"
        input_bg = "#151F33"
        input_border = "rgba(255, 255, 255, 0.18)"
        input_text = "#F8FAFC"
        live_badge_bg = "#131C31"
        live_badge_border = "rgba(255, 255, 255, 0.12)"
        live_badge_text = "#E2E8F0"
        sidebar_card_bg = "#131C31"
        sidebar_card_border = "rgba(255, 255, 255, 0.12)"
        table_th_bg = "rgba(30, 58, 138, 0.25)"
        table_th_color = "#60A5FA"
        table_border = "rgba(255, 255, 255, 0.12)"
        table_row_hover = "rgba(255, 255, 255, 0.04)"
        table_tfoot_border = "#38BDF8"
        selection_bg = "rgba(37, 99, 235, 0.45)"
        selection_color = "#FFFFFF"
        scrollbar_track = "#0B0F19"
        scrollbar_thumb = "rgba(255, 255, 255, 0.20)"
        scrollbar_thumb_hover = "rgba(96, 165, 250, 0.50)"
        focus_ring = "#3B82F6"
        caret_color = "#60A5FA"
        popover_shadow = "0 12px 32px rgba(0, 0, 0, 0.7), 0 2px 6px rgba(0, 0, 0, 0.4)"
        button_shadow = "0 1px 3px rgba(0, 0, 0, 0.4)"
        button_shadow_hover = "0 4px 12px rgba(0, 0, 0, 0.55)"
    else:
        app_bg = "#F8FAFC"
        sidebar_bg = "#FFFFFF"
        card_bg = "#FFFFFF"
        card_border = "#E2E8F0"
        card_border_hover = "#CBD5E1"
        card_shadow = "0 1px 3px rgba(15, 23, 42, 0.02), 0 4px 14px -2px rgba(15, 23, 42, 0.04)"
        card_shadow_hover = "0 8px 24px -4px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.03)"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#64748B"
        divider_color = "#E2E8F0"
        bezel_outer_bg = "#FFFFFF"
        bezel_outer_border = "rgba(226, 232, 240, 0.9)"
        bezel_inner_bg = "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)"
        bezel_inner_border = "rgba(241, 245, 249, 0.85)"
        bezel_inner_shadow = "inset 0 1px 0 rgba(255, 255, 255, 0.9)"
        bezel_hover_border = "#CBD5E1"
        eyebrow_bg = "#EFF6FF"
        eyebrow_border = "#DBEAFE"
        eyebrow_color = "#2563EB"
        tag_bg = "#F1F5F9"
        tag_color = "#475569"
        tag_border = "transparent"
        button_bg = "#FFFFFF"
        button_border = "#CBD5E1"
        button_color = "#1E293B"
        button_hover_bg = "#F8FAFC"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        input_text = "#0F172A"
        live_badge_bg = "#FFFFFF"
        live_badge_border = "#E2E8F0"
        live_badge_text = "#1E293B"
        sidebar_card_bg = "#FFFFFF"
        sidebar_card_border = "#E2E8F0"
        table_th_bg = "#EFF6FF"
        table_th_color = "#1D4ED8"
        table_border = "#CBD5E1"
        table_row_hover = "#F8FAFC"
        table_tfoot_border = "#0F172A"
        selection_bg = "rgba(147, 197, 253, 0.55)"
        selection_color = "#0F172A"
        scrollbar_track = "#F8FAFC"
        scrollbar_thumb = "rgba(15, 23, 42, 0.18)"
        scrollbar_thumb_hover = "rgba(37, 99, 235, 0.45)"
        focus_ring = "#2563EB"
        caret_color = "#1D4ED8"
        popover_shadow = "0 10px 25px -5px rgba(15, 23, 42, 0.1), 0 4px 10px -2px rgba(15, 23, 42, 0.04)"
        button_shadow = "0 1px 3px rgba(15, 23, 42, 0.06)"
        button_shadow_hover = "0 4px 12px rgba(15, 23, 42, 0.10)"

    css = f"""
    <style>
    /* Tipografías de alta gama: Plus Jakarta Sans (UI) y Outfit (Display) */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-display: 'Outfit', sans-serif;
        --ease-out-spring: cubic-bezier(0.16, 1, 0.3, 1);
        --app-bg: {app_bg};
        --sidebar-bg: {sidebar_bg};
        --card-bg: {card_bg};
        --card-border: {card_border};
        --card-border-hover: {card_border_hover};
        --card-shadow: {card_shadow};
        --card-shadow-hover: {card_shadow_hover};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --text-muted: {text_muted};
        --divider-color: {divider_color};
        --bezel-outer-bg: {bezel_outer_bg};
        --bezel-outer-border: {bezel_outer_border};
        --bezel-inner-bg: {bezel_inner_bg};
        --bezel-inner-border: {bezel_inner_border};
        --bezel-inner-shadow: {bezel_inner_shadow};
        --bezel-hover-border: {bezel_hover_border};
        --eyebrow-bg: {eyebrow_bg};
        --eyebrow-border: {eyebrow_border};
        --eyebrow-color: {eyebrow_color};
        --tag-bg: {tag_bg};
        --tag-color: {tag_color};
        --tag-border: {tag_border};
        --button-bg: {button_bg};
        --button-border: {button_border};
        --button-color: {button_color};
        --button-hover-bg: {button_hover_bg};
        --input-bg: {input_bg};
        --input-border: {input_border};
        --input-text: {input_text};
        --live-badge-bg: {live_badge_bg};
        --live-badge-border: {live_badge_border};
        --live-badge-text: {live_badge_text};
        --sidebar-card-bg: {sidebar_card_bg};
        --sidebar-card-border: {sidebar_card_border};
        --table-th-bg: {table_th_bg};
        --table-th-color: {table_th_color};
        --table-border: {table_border};
        --table-row-hover: {table_row_hover};
        --table-tfoot-border: {table_tfoot_border};
        --selection-bg: {selection_bg};
        --selection-color: {selection_color};
        --scrollbar-track: {scrollbar_track};
        --scrollbar-thumb: {scrollbar_thumb};
        --scrollbar-thumb-hover: {scrollbar_thumb_hover};
        --focus-ring: {focus_ring};
        --caret-color: {caret_color};
        --popover-shadow: {popover_shadow};
        --button-shadow: {button_shadow};
        --button-shadow-hover: {button_shadow_hover};
    }}

    /* Tratamiento integral de superficies del navegador (Craft Floor) */
    ::selection {{
        background: var(--selection-bg) !important;
        color: var(--selection-color) !important;
    }}

    * {{
        scrollbar-width: thin;
        scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
    }}

    ::-webkit-scrollbar {{
        width: 7px;
        height: 7px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--scrollbar-track);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--scrollbar-thumb);
        border-radius: 9999px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: var(--scrollbar-thumb-hover);
    }}

    input:not([role="combobox"]), textarea, [contenteditable] {{
        caret-color: var(--caret-color) !important;
    }}

    button:focus-visible,
    a:focus-visible,
    .stButton > button:focus-visible,
    div[data-testid="stRadio"] label:focus-visible {{
        outline: 2px solid var(--focus-ring) !important;
        outline-offset: 2px !important;
    }}


    /* Fondo de Lienzo y Tipografía Global */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--app-bg) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* Contenedor principal */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1440px !important;
    }}

    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}
    footer {{visibility: hidden;}}

    /* Ocultar el iframe de zero-height usado para inyección de JS */
    iframe[height="0"],
    iframe[width="0"],
    [data-testid="stCustomComponentV1"] {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }}

    /* Banner de Cabecera Ejecutiva */
    .brand-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--eyebrow-color);
        background: var(--eyebrow-bg);
        padding: 4px 11px;
        border-radius: 9999px;
        border: 1px solid var(--eyebrow-border);
        margin-bottom: 0.35rem;
    }}

    .header-title {{
        font-family: var(--font-display);
        font-size: clamp(2rem, 3.5vw, 2.75rem);
        font-weight: 700;
        letter-spacing: -0.035em;
        color: var(--text-primary);
        line-height: 1.15;
        margin: 0;
    }}

    .header-subtitle {{
        font-size: 0.925rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        letter-spacing: -0.01em;
    }}

    /* Insignia de Pulso de Conexión en Tiempo Real */
    .live-badge-container {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--live-badge-bg);
        border: 1px solid var(--live-badge-border);
        padding: 6px 14px;
        border-radius: 9999px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--live-badge-text);
    }}

    .pulse-live {{
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-ring 2s infinite cubic-bezier(0.25, 1, 0.5, 1);
    }}

    .pulse-demo {{
        width: 8px;
        height: 8px;
        background-color: #F59E0B;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
        animation: pulse-ring 2s infinite cubic-bezier(0.25, 1, 0.5, 1);
    }}

    @keyframes pulse-ring {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Soporte de Accesibilidad: Sensibilidad al movimiento (WCAG 2.1 AA) */
    @media (prefers-reduced-motion: reduce) {{
        .pulse-live, .pulse-demo {{
            animation: none !important;
            box-shadow: none !important;
        }}
        .bezel-outer {{
            transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}
        .bezel-outer:hover {{
            transform: none !important;
        }}
        .kpi-accent-glow {{
            transition: opacity 0.15s ease !important;
        }}
        .bezel-outer:hover .kpi-accent-glow {{
            transform: none !important;
        }}
        button, a, .stButton > button {{
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
            transform: none !important;
        }}
    }}

    /* ------------------------------------------------------------- */
    /* DOBLE BISEL (Double-Bezel Architecture) para Tarjetas KPI     */
    /* ------------------------------------------------------------- */
    .bezel-outer {{
        background: var(--bezel-outer-bg);
        border: 1px solid var(--bezel-outer-border);
        border-radius: 18px;
        padding: 6px;
        box-shadow: var(--card-shadow);
        transition: all 0.35s var(--ease-out-spring);
        height: 100%;
    }}

    .bezel-outer:hover {{
        transform: translateY(-3px);
        border-color: var(--bezel-hover-border);
        box-shadow: var(--card-shadow-hover);
    }}

    .bezel-inner {{
        background: var(--bezel-inner-bg);
        border: 1px solid var(--bezel-inner-border);
        border-radius: 12px;
        padding: 1.05rem 1.15rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        position: relative;
        overflow: hidden;
        box-shadow: var(--bezel-inner-shadow);
    }}

    .kpi-accent-glow {{
        position: absolute;
        top: -20px;
        right: -20px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        filter: blur(28px);
        opacity: 0.16;
        pointer-events: none;
        transition: opacity 0.35s ease, transform 0.35s ease;
    }}

    .bezel-outer:hover .kpi-accent-glow {{
        opacity: 0.38;
        transform: scale(1.18);
    }}

    .kpi-top-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }}

    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-secondary);
    }}

    .kpi-icon-pill {{
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .kpi-number {{
        font-family: var(--font-display);
        font-size: clamp(1.75rem, 2.5vw, 2.45rem);
        font-weight: 700;
        letter-spacing: -0.04em;
        color: var(--text-primary);
        line-height: 1.05;
        font-variant-numeric: tabular-nums;
        margin-bottom: 0.4rem;
    }}

    .kpi-foot {{
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    /* ------------------------------------------------------------- */
    /* MARCO COMPLETO PARA CATEGORÍAS Y GRÁFICOS (.chart-frame)     */
    /* ------------------------------------------------------------- */
    /* 
     * Clase CSS completamente controlada por nosotros.
     * Los valores de color están interpolados directamente desde Python
     * (no usan CSS variables) para evitar conflictos con la caché de Emotion/Streamlit.
     * Esta clase enmarca tanto el texto de la categoría como su gráfico respectivo.
     */
    .chart-frame {{
        background-color: {card_bg};
        border: 2px solid {card_border};
        border-radius: 18px;
        padding: 1.25rem 1.5rem;
        box-shadow: {card_shadow};
        transition: border-color 0.28s ease, box-shadow 0.28s ease, transform 0.28s ease;
        margin-bottom: 0.9rem;
        overflow: hidden;
        position: relative;
    }}

    .chart-frame:hover {{
        border-color: {card_border_hover};
        box-shadow: {card_shadow_hover};
        transform: translateY(-2px);
    }}

    /* Los bloques hijos de Streamlit dentro del marco no deben añadir estilos propios */
    .chart-frame [data-testid="stVerticalBlock"],
    .chart-frame [data-testid="element-container"],
    .chart-frame > div {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}

    /* Selector fallback para el wrapper nativo de Streamlit (en caso de que se use en otro lugar) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg} !important;
        border: 2px solid {card_border} !important;
        outline: 1px solid {card_border} !important;
        outline-offset: -1px !important;
        border-radius: 18px !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: {card_shadow}, 0 0 0 1px {card_border} !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
        margin-bottom: 0.85rem !important;
        overflow: visible !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: {card_border_hover} !important;
        outline-color: {card_border_hover} !important;
        box-shadow: {card_shadow_hover}, 0 0 0 2px {card_border_hover} !important;
    }}

    .chart-header-row {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid var(--divider-color);
        padding-bottom: 0.75rem;
    }}

    .chart-title-main {{
        font-family: var(--font-display);
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        line-height: 1.2;
    }}

    .chart-desc {{
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 3px;
        letter-spacing: -0.005em;
    }}

    .chart-tag {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--tag-color);
        background: var(--tag-bg);
        border: 1px solid var(--tag-border);
        padding: 3px 9px;
        border-radius: 6px;
        white-space: nowrap;
    }}

    /* ------------------------------------------------------------- */
    /* BARRA LATERAL (Sidebar) & Perfil                              */
    /* ------------------------------------------------------------- */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--divider-color) !important;
    }}

    .sidebar-identity {{
        background: var(--sidebar-card-bg);
        border: 1px solid var(--sidebar-card-border);
        border-radius: 14px;
        padding: 0.95rem 1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .identity-user {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .identity-avatar {{
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }}

    .identity-info-name {{
        font-size: 0.875rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }}

    .identity-info-sub {{
        font-size: 0.75rem;
        color: var(--text-secondary);
    }}

    /* ------------------------------------------------------------- */
    /* ETIQUETAS Y CONTROLES DE FORMULARIO (Alta visibilidad)        */
    /* ------------------------------------------------------------- */
    /* Etiquetas de todos los widgets (Filtros, selects, fechas) */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        letter-spacing: -0.01em !important;
    }}

    /* Selectbox y MultiSelect */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 10px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div:focus-within,
    .stMultiSelect div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {{
        border-color: var(--card-border-hover) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25) !important;
    }}

    /* Eliminar contorno azul y cursor pegado en el input interno de BaseWeb */
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] input:focus,
    div[data-baseweb="select"] input:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
        caret-color: transparent !important;
    }}

    .stSelectbox div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    .stSelectbox div[data-baseweb="select"] div[aria-selected="true"],
    .stSelectbox div[data-baseweb="select"] span {{
        color: var(--input-text) !important;
        font-weight: 500 !important;
    }}

    /* Placeholders en selectbox y multiselect */
    .stSelectbox div[data-baseweb="select"] input::placeholder,
    .stMultiSelect div[role="combobox"] input::placeholder,
    div[data-baseweb="select"] div:has(> [data-testid="stMarkdownContainer"]) {{
        color: var(--text-muted) !important;
    }}

    /* Flecha desplegable (caret) e iconos */
    .stSelectbox svg, .stMultiSelect svg {{
        fill: var(--text-secondary) !important;
        color: var(--text-secondary) !important;
    }}

    /* Tags seleccionados en MultiSelect */
    .stMultiSelect span[data-baseweb="tag"] {{
        background-color: var(--tag-bg) !important;
        border: 1px solid var(--tag-border) !important;
        border-radius: 6px !important;
    }}

    .stMultiSelect span[data-baseweb="tag"] span {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}

    /* Menús desplegables flotantes (BaseWeb Popover, Selectbox Dropdown, Menu) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"],
    div[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {{
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--popover-shadow) !important;
        overflow: hidden !important;
    }}

    li[data-baseweb="menu-item"],
    div[data-baseweb="menu-item"],
    div[role="option"],
    li[role="option"] {{
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
        cursor: pointer !important;
        transition: background 0.15s ease !important;
    }}

    li[data-baseweb="menu-item"]:hover,
    div[data-baseweb="menu-item"]:hover,
    div[role="option"]:hover,
    li[role="option"]:hover,
    li[data-baseweb="menu-item"][aria-selected="true"],
    div[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {{
        background-color: var(--button-hover-bg) !important;
        color: var(--text-primary) !important;
    }}

    /* Textos dentro de items de menú desplegable */
    li[data-baseweb="menu-item"] *,
    div[data-baseweb="menu-item"] *,
    div[role="option"] *,
    li[role="option"] * {{
        color: var(--text-primary) !important;
    }}

    /* Contenedor Date Input (elimina marcos y medialunas blancas de BaseWeb) */
    .stDateInput div[data-baseweb="input"],
    .stDateInput div[data-baseweb="base-input"],
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[data-baseweb="base-input"] {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }}

    .stDateInput input,
    div[data-testid="stDateInput"] input {{
        background-color: transparent !important;
        color: var(--input-text) !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        font-variant-numeric: tabular-nums !important;
    }}

    .stDateInput div[data-baseweb="input"] button,
    .stDateInput div[data-baseweb="input"] svg {{
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        fill: var(--text-secondary) !important;
        border: none !important;
    }}

    /* Estilo segmentado para el selector de tema */
    div[data-testid="stRadio"] > div {{
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}

    div[data-testid="stRadio"] label {{
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stRadio"] label p {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }}

    /* ------------------------------------------------------------- */
    /* BOTONES DE ACCIÓN (Restablecer, Refrescar, Cerrar Sesión)     */
    /* ------------------------------------------------------------- */
    button,
    button[kind="secondary"],
    button[kind="primary"],
    button[data-testid*="baseButton"],
    button[data-testid*="stBaseButton"],
    .stButton > button,
    div.stButton > button,
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] button[kind="secondary"],
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
        background: var(--button-bg) !important;
        background-color: var(--button-bg) !important;
        color: var(--button-color) !important;
        border: 1px solid var(--button-border) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        letter-spacing: -0.01em !important;
        padding: 0.45rem 1rem !important;
        box-shadow: var(--button-shadow) !important;
        transition: all 0.2s var(--ease-out-spring) !important;
    }}

    button p,
    button span,
    button[kind="secondary"] p,
    button[data-testid*="baseButton"] p,
    section[data-testid="stSidebar"] button p,
    section[data-testid="stSidebar"] button span {{
        color: var(--button-color) !important;
        font-weight: 600 !important;
    }}

    button:hover,
    button[kind="secondary"]:hover,
    button[data-testid*="baseButton"]:hover,
    .stButton > button:hover,
    section[data-testid="stSidebar"] button:hover {{
        background: var(--button-hover-bg) !important;
        background-color: var(--button-hover-bg) !important;
        border-color: var(--card-border-hover) !important;
        color: var(--button-color) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--button-shadow-hover) !important;
    }}

    button:active,
    .stButton > button:active {{
        transform: scale(0.97) !important;
    }}

    /* ------------------------------------------------------------- */
    /* TABLA RESUMEN EJECUTIVA (Ciclo x Local x Turno)              */
    /* ------------------------------------------------------------- */
    .table-container-responsive {{
        width: 100%;
        overflow-x: auto;
        border-radius: 12px;
        border: 1px solid var(--table-border);
        background: var(--card-bg);
        margin: 0.5rem 0 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}

    .executive-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: var(--font-sans);
        font-size: 0.875rem;
        line-height: 1.45;
        text-align: left;
    }}

    .executive-table thead th {{
        background-color: var(--table-th-bg);
        color: var(--table-th-color);
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 10px 16px;
        border-bottom: 2px solid var(--table-border);
        border-right: 1px solid var(--table-border);
    }}

    .executive-table thead th:last-child {{
        border-right: none;
        text-align: right;
    }}

    .executive-table tbody td {{
        padding: 9px 16px;
        color: var(--text-primary);
        border-bottom: 1px solid var(--table-border);
        border-right: 1px solid var(--table-border);
        font-variant-numeric: tabular-nums;
        font-size: 0.875rem;
    }}

    .executive-table tbody td:last-child {{
        border-right: none;
        text-align: right;
        font-weight: 600;
    }}

    .executive-table tbody tr:hover {{
        background-color: var(--table-row-hover);
    }}

    .executive-table tbody tr:last-child td {{
        border-bottom: 2px solid var(--table-border);
    }}

    .executive-table tfoot td {{
        padding: 10px 16px;
        font-family: var(--font-sans);
        color: var(--text-primary);
        background-color: var(--table-th-bg);
        font-weight: 700;
    }}

    .executive-table tfoot tr.total-row td {{
        border-top: 2px solid var(--table-tfoot-border);
        border-bottom: 1px solid var(--table-border);
    }}

    .executive-table tfoot tr.pagos-row td {{
        border-top: 1px solid var(--table-border);
    }}

    .executive-table tfoot tr:last-child td {{
        border-bottom: 3px double var(--table-tfoot-border);
    }}

    .executive-table tfoot td.total-label {{
        text-align: right;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-primary);
        border-right: 1px solid var(--table-border);
    }}

    .executive-table tfoot td.total-value {{
        text-align: right;
        font-size: 1.1rem;
        font-weight: 800;
        font-family: var(--font-display);
        font-variant-numeric: tabular-nums;
        color: var(--table-th-color);
        border-right: none;
    }}

    .executive-table tfoot td.pagos-label {{
        text-align: right;
        font-size: 0.85rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-primary);
        border-right: 1px solid var(--table-border);
    }}

    .executive-table tfoot td.pagos-value {{
        text-align: right;
        font-size: 1.1rem;
        font-weight: 800;
        font-family: var(--font-display);
        font-variant-numeric: tabular-nums;
        border-right: none;
    }}

    /* ------------------------------------------------------------- */
    /* SISTEMA RESPONSIVO Y ADAPTATIVO (impeccable adapt)           */
    /* ------------------------------------------------------------- */
    
    /* Momentum scroll en tablas para dispositivos móviles y tablets */
    .table-container-responsive {{
        -webkit-overflow-scrolling: touch;
    }}

    /* Tablets y Pantallas Compactas (<= 992px) */
    @media (max-width: 992px) {{
        .block-container {{
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 1rem !important;
        }}
        .header-title {{
            font-size: 1.35rem !important;
        }}
        .bezel-inner {{
            padding: 0.95rem 1rem !important;
        }}
        .kpi-number {{
            font-size: 2rem !important;
        }}
    }}

    /* Móviles y Pantallas Angostas (<= 768px) */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0.75rem !important;
        }}
        .header-title {{
            font-size: 1.1rem !important;
            letter-spacing: -0.02em !important;
        }}
        .header-subtitle {{
            font-size: 0.75rem !important;
            line-height: 1.35 !important;
        }}
        .brand-eyebrow {{
            font-size: 0.75rem !important;
            padding: 3px 8px !important;
        }}
        .bezel-outer {{
            margin-bottom: 0.5rem;
        }}
        .chart-frame,
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            padding: 0.9rem 1rem !important;
            border-radius: 14px !important;
        }}
        .executive-table thead th,
        .executive-table tbody td {{
            padding: 8px 10px !important;
            font-size: 0.75rem !important;
        }}
    }}

    /* Dispositivos Táctiles (Coarse Pointer: Touch targets 44x44px mínimos) */
    @media (pointer: coarse) {{
        button,
        button[kind="secondary"],
        button[kind="primary"],
        .stButton > button,
        section[data-testid="stSidebar"] button {{
            min-height: 44px !important;
            padding: 0.6rem 1.1rem !important;
        }}
    }}

    /* Pie de página sutil */
    .footer-minimal {{
        text-align: center;
        color: var(--text-muted);
        font-size: 0.75rem;
        margin-top: 2.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid var(--divider-color);
        letter-spacing: 0.01em;
    }}
    </style>

    """
    st.markdown(css, unsafe_allow_html=True)
    # Inject JavaScript via components.html (the only reliable way to execute JS in Streamlit)
    _inject_container_js(card_bg, card_border, card_border_hover, card_shadow, card_shadow_hover)


def create_kpi_card_html(
    title: str,
    value: str,
    subtitle: str,
    icon: str,
    accent_color: str = "#1D4ED8",
    icon_bg: str = "rgba(29, 78, 216, 0.08)",
    badge: str = None,
    badge_bg: str = "rgba(5, 150, 105, 0.12)",
    badge_color: str = "#059669",
) -> str:
    """
    Genera el HTML con arquitectura 'Double-Bezel' (Doppelrand) de alta fidelidad,
    halo ambiental, micro-badge opcional y números con tipografía Display.
    """
    title_escaped = html.escape(str(title))
    val_escaped = html.escape(str(value))
    sub_escaped = html.escape(str(subtitle))
    
    badge_html = ""
    if badge:
        badge_escaped = html.escape(str(badge))
        badge_html = (
            f'<span style="background: {badge_bg}; color: {badge_color}; '
            f'padding: 2px 7px; border-radius: 9999px; font-size: 0.75rem; '
            f'font-weight: 700; letter-spacing: 0.02em; white-space: nowrap;">'
            f'{badge_escaped}</span>'
        )

    return (
        f'<div class="bezel-outer" role="region" aria-label="Métrica {title_escaped}: {val_escaped}">'
        f'<div class="bezel-inner">'
        f'<div class="kpi-accent-glow" style="background-color: {accent_color};" aria-hidden="true"></div>'
        f'<div>'
        f'<div class="kpi-top-row">'
        f'<span class="kpi-label">{title_escaped}</span>'
        f'<div class="kpi-icon-pill" style="background-color: {icon_bg}; color: {accent_color};" aria-hidden="true">{icon}</div>'
        f'</div>'
        f'<div class="kpi-number">{val_escaped}</div>'
        f'</div>'
        f'<div class="kpi-foot" style="display: flex; align-items: center; justify-content: space-between; width: 100%;">'
        f'<span>{sub_escaped}</span>{badge_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def create_executive_table_html(
    df: pd.DataFrame,
    is_dark: bool = False,
    pagos_pendientes: int = None,
) -> str:
    """
    Genera la tabla HTML ejecutiva basada exactamente en la especificación del usuario:
    - Columnas: CICLO, LOCAL, TURNO, MATRICULADOS
    - Cabeceras en azul mayúsculas
    - Celdas con bordes definidos (gridlines estilo hoja de cálculo ejecutiva)
    - Conteo por local y turno alineado a la derecha
    - Fila de TOTAL GENERAL en el pie de tabla con número en negrita
    - Fila de PAGOS QUE TODAVIA NO SE MATRICULAN al pie de tabla
    """
    if df.empty:
        return """
        <div class="table-container-responsive" style="padding: 2rem; text-align: center; color: var(--text-muted);">
            No se encontraron registros para los filtros seleccionados.
        </div>
        """

    total_general = int(df["MATRICULADOS"].sum()) if "MATRICULADOS" in df.columns else 0

    rows_html = []
    for _, row in df.iterrows():
        ciclo = html.escape(str(row.get("CICLO", "")))
        local = html.escape(str(row.get("LOCAL", "")))
        turno = html.escape(str(row.get("TURNO", "")))
        matriculados = int(row.get("MATRICULADOS", 0))

        rows_html.append(
            f"<tr>"
            f"<td style='font-weight: 500;'>{ciclo}</td>"
            f"<td>{local}</td>"
            f"<td>{turno}</td>"
            f"<td>{matriculados:,}</td>"
            f"</tr>"
        )

    body_content = "".join(rows_html)

    pagos_row_html = ""
    if pagos_pendientes is not None:
        pagos_color = "#FBBF24" if is_dark else "#D97706"
        pagos_row_html = (
            '<tr class="pagos-row">'
            '<td colspan="3" class="pagos-label">PAGOS QUE TODAVIA NO SE MATRICULAN:</td>'
            f'<td class="pagos-value" style="color: {pagos_color};">{int(pagos_pendientes):,}</td>'
            '</tr>'
        )

    return (
        '<div class="table-container-responsive">'
        '<table class="executive-table">'
        '<thead>'
        '<tr>'
        '<th style="text-align: left;">CICLO</th>'
        '<th style="text-align: left;">LOCAL</th>'
        '<th style="text-align: left;">TURNO</th>'
        '<th style="text-align: right;">MATRICULADOS</th>'
        '</tr>'
        '</thead>'
        f'<tbody>{body_content}</tbody>'
        '<tfoot>'
        '<tr class="total-row">'
        '<td colspan="3" class="total-label">TOTAL GENERAL</td>'
        f'<td class="total-value">{total_general:,}</td>'
        '</tr>'
        f'{pagos_row_html}'
        '</tfoot>'
        '</table>'
        '</div>'
    )



def apply_plotly_theme(fig: go.Figure, height: int = 380, is_dark: bool = False) -> go.Figure:
    """
    Aplica una plantilla Plotly moderna de nivel Awwwards:
    - Soporte nativo para Modo Claro y Modo Oscuro con alto contraste en ejes y títulos
    - Tipografía Plus Jakarta Sans
    - Hoverlabels tipo pastilla con tipografía tabular
    - Fondos transparentes integrados con el marco del contenedor
    """
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    tick_color = "#CBD5E1" if is_dark else "#475569"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0"
    line_color = "rgba(255, 255, 255, 0.22)" if is_dark else "#CBD5E1"
    hover_bg = "#1E293B" if is_dark else "#0F172A"
    hover_border = "rgba(255, 255, 255, 0.25)" if is_dark else "rgba(255, 255, 255, 0.12)"
    template = "plotly_dark" if is_dark else "plotly_white"

    fig.update_layout(
        template=template,
        height=height,
        margin=dict(l=15, r=15, t=25, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, -apple-system, sans-serif",
            size=11.5,
            color=text_color,
        ),
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#F8FAFC",
            bordercolor=hover_border,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
            font=dict(size=11, color=tick_color, family="Plus Jakarta Sans"),
        ),
    )
    # Suavizar ejes de coordenadas con tipografía nítida
    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        linecolor=line_color,
        tickfont=dict(size=10.5, color=tick_color, family="Plus Jakarta Sans"),
        title_font=dict(size=11, color=text_color, family="Plus Jakarta Sans"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        linecolor=line_color,
        tickfont=dict(size=10.5, color=tick_color, family="Plus Jakarta Sans"),
        title_font=dict(size=11, color=text_color, family="Plus Jakarta Sans"),
    )
    return fig
