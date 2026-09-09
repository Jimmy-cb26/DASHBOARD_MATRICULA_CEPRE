"""
==============================================================================
Dashboard Ejecutivo de Métricas de Matrícula (Awwwards / Linear Tier)
==============================================================================
Desarrollado con Streamlit y Plotly aplicando principios de alta fidelidad:
- Arquitectura Double-Bezel (Doppelrand) para componentes clave
- Tipografía Display Outfit y Sans Plus Jakarta Sans con números tabulares
- Cuadrícula Asimétrica Bento-Box
- Micro-interacciones hápticas y pulso en tiempo real para conexión institucional
- Respeto absoluto a la confidencialidad de datos estudiantiles
"""

from datetime import datetime, date
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard de Métricas de Matrícula",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from auth import load_authenticator, setup_auth_flow
from db import get_db_engine, get_view_name
import queries
from styles import (
    inject_custom_css,
    create_kpi_card_html,
    create_executive_table_html,
    apply_plotly_theme,
    COLOR_PALETTE,
    TURNO_COLORS,
    AREA_COLORS,
    AREA_LABELS,
)


# 1. Inicialización de tema y estilos
if "theme" not in st.session_state:
    st.session_state.theme = "light"

inject_custom_css(theme=st.session_state.theme)
is_dark = (st.session_state.theme == "dark")

# 2. Control previo de acceso (Login Gate)
authenticator = load_authenticator()
authenticator, username, user_name = setup_auth_flow(authenticator)

# Feedback sensorial (Delight): notificación de acciones ejecutadas
if "toast_msg" in st.session_state:
    toast_text = st.session_state.pop("toast_msg", "")
    toast_icon = st.session_state.pop("toast_icon", "🏛️")
    try:
        st.toast(toast_text, icon=toast_icon)
    except Exception:
        st.toast(toast_text, icon="🏛️")

# 3. Conexión a la base de datos (En vivo o Fallback persistente)
engine, is_demo, conn_status = get_db_engine()
view_name = get_view_name()

# 4. Barra Lateral (Sidebar): Perfil y Filtros Globales
with st.sidebar:
    # Avatar monograma con las iniciales del usuario
    user_initials = "".join([part[0].upper() for part in user_name.split()[:2]]) or "U"
    
    st.markdown(
        f"""
        <div class="sidebar-identity">
            <div class="identity-user">
                <div class="identity-avatar">{user_initials}</div>
                <div>
                    <div class="identity-info-name">{user_name}</div>
                    <div class="identity-info-sub">
                        <span style="font-family: monospace;">@{username}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Selector de Tema (Claro / Oscuro)
    st.markdown(
        """
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 0.35rem;">
            Apariencia
        </div>
        """,
        unsafe_allow_html=True,
    )
    theme_choice = st.radio(
        "Tema",
        options=["☀️ Claro", "🌙 Oscuro"],
        index=0 if st.session_state.theme == "light" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="theme_radio",
    )
    new_theme = "dark" if theme_choice == "🌙 Oscuro" else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    # Botón de cierre de sesión
    authenticator.logout("Cerrar Sesión", location="sidebar")
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 0.5rem;">
            Filtros Globales
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Carga de opciones dinámicas desde la BD
    filter_options = queries.get_distinct_filter_values()

    min_date = filter_options["min_fecha"]
    max_date = filter_options["max_fecha"]

    ciclos_disponibles = filter_options["ciclos"]
    default_ciclo = "ORD_2026_II" if "ORD_2026_II" in ciclos_disponibles else (ciclos_disponibles[0] if ciclos_disponibles else "")

    # Inicialización de estado para filtros (claves exactas de widgets)
    if "sb_ciclo" not in st.session_state:
        st.session_state.sb_ciclo = default_ciclo
    if "sb_local" not in st.session_state:
        st.session_state.sb_local = "Todos los locales"
    if "sb_turno" not in st.session_state:
        st.session_state.sb_turno = "Todos los turnos"
    if "sb_area" not in st.session_state:
        st.session_state.sb_area = "Todas las áreas"
    if "date_start" not in st.session_state:
        st.session_state.date_start = min_date
    if "date_end" not in st.session_state:
        st.session_state.date_end = max_date

    def reset_filters_callback():
        st.session_state.sb_ciclo = default_ciclo
        st.session_state.sb_local = "Todos los locales"
        st.session_state.sb_turno = "Todos los turnos"
        st.session_state.sb_area = "Todas las áreas"
        st.session_state.date_start = min_date
        st.session_state.date_end = max_date
        st.session_state["toast_msg"] = "Filtros restablecidos a la vista general"
        st.session_state["toast_icon"] = "🔄"

    def format_ciclo_label(c: str) -> str:
        """Traduce códigos técnicos como ORD_2026_II a nombres institucionales claros."""
        if not c:
            return ""
        parts = c.split("_")
        if len(parts) >= 3:
            tipo_map = {"ORD": "Ordinario", "ESP": "Especial", "SUP": "Superintensivo"}
            tipo = tipo_map.get(parts[0], parts[0])
            año = parts[1]
            romano = parts[2]
            return f"{tipo} {año}-{romano} ({c})"
        return c

    # Selector de Ciclo Académico (Ciclo único, sin opción 'Todos los ciclos', ORD_2026_II por defecto)
    selected_ciclo = st.selectbox(
        "Ciclo Académico",
        options=ciclos_disponibles,
        format_func=format_ciclo_label,
        key="sb_ciclo",
    )
    selected_ciclos = [selected_ciclo] if selected_ciclo else []

    # Selector de Local / Sede (Cierra automáticamente al seleccionar opción)
    local_options = ["Todos los locales"] + filter_options["locales"]
    selected_local = st.selectbox(
        "Local / Sede",
        options=local_options,
        key="sb_local",
    )
    selected_locales = [selected_local] if selected_local != "Todos los locales" else []

    # Selector de Turno (Cierra automáticamente al seleccionar opción)
    turno_options = ["Todos los turnos"] + filter_options["turnos"]
    selected_turno = st.selectbox(
        "Turno",
        options=turno_options,
        key="sb_turno",
    )
    selected_turnos = [selected_turno] if selected_turno != "Todos los turnos" else []

    area_labels = {
        "Todas las áreas": "Todas las áreas",
        **AREA_LABELS,
    }
    area_options = ["Todas las áreas"] + filter_options["areas"]
    selected_area = st.selectbox(
        "Área Académica",
        options=area_options,
        format_func=lambda x: area_labels.get(x, f"Área {x}"),
        key="sb_area",
    )
    selected_areas = [selected_area] if selected_area != "Todas las áreas" else []

    # Rango de fechas separado: Fecha Inicio y Fecha Fin independientes
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            min_value=min_date if min_date else None,
            max_value=max_date if max_date else None,
            key="date_start",
        )
    with col_d2:
        fecha_fin = st.date_input(
            "Fecha Fin",
            min_value=min_date if min_date else None,
            max_value=max_date if max_date else None,
            key="date_end",
        )

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        st.warning("⚠️ El rango de fechas seleccionado se ajustó automáticamente.")
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.button(
            "Restablecer",
            use_container_width=True,
            help="Limpiar todos los filtros y restaurar valores por defecto",
            on_click=reset_filters_callback,
        )

    with col_btn2:
        if st.button("Actualizar", use_container_width=True, help="Consultar los datos más recientes de matrícula"):
            st.cache_data.clear()
            st.session_state["toast_msg"] = "Base de datos sincronizada: datos de matrícula al día"
            st.session_state["toast_icon"] = "⚡"
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Estado de la conexión con indicador de pulso adaptado al tema
    if is_demo:
        badge_bg = "rgba(245, 158, 11, 0.12)" if is_dark else "#FFFBEB"
        badge_border = "rgba(245, 158, 11, 0.35)" if is_dark else "#FDE68A"
        badge_title_color = "#FBBF24" if is_dark else "#B45309"
        badge_sub_color = "#FDE68A" if is_dark else "#92400E"
        st.markdown(
            f"""
            <div style="background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 10px; padding: 10px 12px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.875rem; color: {badge_title_color};">
                    <span class="pulse-demo"></span> Modo Demostración
                </div>
                <div style="font-size: 0.75rem; color: {badge_sub_color}; margin-top: 4px;">
                    Datos sintéticos activos. Configure <code>.env</code> para conectar a la base de datos en vivo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        badge_bg = "rgba(16, 185, 129, 0.12)" if is_dark else "#F0FDF4"
        badge_border = "rgba(16, 185, 129, 0.35)" if is_dark else "#BBF7D0"
        badge_title_color = "#34D399" if is_dark else "#15803D"
        badge_sub_color = "#A7F3D0" if is_dark else "#166534"
        st.markdown(
            f"""
            <div style="background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 10px; padding: 10px 12px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.875rem; color: {badge_title_color};">
                    <span class="pulse-live"></span> Conectado en Vivo
                </div>
                <div style="font-size: 0.75rem; color: {badge_sub_color}; margin-top: 4px; font-family: monospace;">
                    Servidor de Datos Institucional
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Diccionario de filtros activos
current_filters = {
    "ciclos": selected_ciclos,
    "locales": selected_locales,
    "turnos": selected_turnos,
    "areas": selected_areas,
    "fecha_inicio": fecha_inicio,
    "fecha_fin": fecha_fin,
}

# Conteo de filtros aplicados (distintos a la vista base por defecto)
active_filters_count = sum([
    bool(selected_ciclo and selected_ciclo != default_ciclo),
    bool(selected_locales),
    bool(selected_turnos),
    bool(selected_areas),
    bool(fecha_inicio and min_date and fecha_inicio > min_date),
    bool(fecha_fin and max_date and fecha_fin < max_date),
])

# 5. Cabecera Ejecutiva de Alto Impacto
header_col1, header_col2 = st.columns([3.2, 1.3])

with header_col1:
    ciclo_display = format_ciclo_label(selected_ciclo) if selected_ciclo else ""
    filter_tag_html = (
        f"<span style='color: #2563EB; font-weight: 700;'>• {active_filters_count} filtro(s) activo(s)</span>"
        if active_filters_count > 0 else f"<span style='color: var(--text-secondary);'>• {ciclo_display}</span>"
    )
    st.markdown(
        f"""
        <div>
            <div class="brand-eyebrow">
                <span>🏛️</span> ADMISIÓN Y MATRÍCULA {filter_tag_html}
            </div>
            <h1 class="header-title">
                Monitoreo Ejecutivo de Matrículas
            </h1>
            <p class="header-subtitle">
                Monitoreo en tiempo real del proceso de admisión, ritmo de inscripciones y distribución territorial
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    status_dot_class = "pulse-demo" if is_demo else "pulse-live"
    status_text = "Modo Demo" if is_demo else "Producción en Vivo"
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: flex-end; justify-content: center; height: 100%; padding-top: 0.5rem;">
            <div class="live-badge-container">
                <span class="{status_dot_class}"></span>
                <span>{status_text}</span>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 6px; font-variant-numeric: tabular-nums;">
                Última sincronización: <b>{datetime.now().strftime('%H:%M:%S')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# 6. Tarjetas KPI con Arquitectura Double-Bezel
kpi_data = queries.get_kpis(current_filters)
pagos_data = queries.get_pagos_pendientes(current_filters)

kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

with kpi_c1:
    st.markdown(
        create_kpi_card_html(
            title="Total Matriculados",
            value=f"{kpi_data['total_matriculados']:,}",
            subtitle="Estudiantes confirmados",
            icon="👥",
            accent_color="#1D4ED8",
            icon_bg="rgba(29, 78, 216, 0.08)",
        ),
        unsafe_allow_html=True,
    )

with kpi_c2:
    matriculados_hoy = kpi_data["matriculados_hoy"]
    subt_hoy = "Inscripciones registradas hoy" if matriculados_hoy > 0 else "Sin nuevas inscripciones hoy"
    accent_hoy = "#059669" if matriculados_hoy > 0 else "#64748B"
    icon_bg_hoy = "rgba(5, 150, 105, 0.08)" if matriculados_hoy > 0 else "rgba(100, 116, 139, 0.08)"
    badge_hoy = "● Ritmo activo" if matriculados_hoy > 0 else None
    
    st.markdown(
        create_kpi_card_html(
            title="Matriculados Hoy",
            value=f"{matriculados_hoy:,}",
            subtitle=subt_hoy,
            icon="📅",
            accent_color=accent_hoy,
            icon_bg=icon_bg_hoy,
            badge=badge_hoy,
            badge_bg="rgba(5, 150, 105, 0.12)",
            badge_color="#059669",
        ),
        unsafe_allow_html=True,
    )

with kpi_c3:
    total_pagos = pagos_data["total_pagos"]
    subt_pagos = "En espera de inscripción" if total_pagos > 0 else "Sin pagos pendientes"
    accent_pagos = "#D97706" if total_pagos > 0 else "#64748B"
    icon_bg_pagos = "rgba(217, 119, 6, 0.08)" if total_pagos > 0 else "rgba(100, 116, 139, 0.08)"
    badge_pagos = "● Pendientes" if total_pagos > 0 else None
    badge_bg_pagos = "rgba(217, 119, 6, 0.12)" if total_pagos > 0 else "rgba(100, 116, 139, 0.12)"
    badge_color_pagos = "#D97706" if total_pagos > 0 else "#64748B"

    st.markdown(
        create_kpi_card_html(
            title="Pagos por Matricular",
            value=f"{total_pagos:,}",
            subtitle=subt_pagos,
            icon="💳",
            accent_color=accent_pagos,
            icon_bg=icon_bg_pagos,
            badge=badge_pagos,
            badge_bg=badge_bg_pagos,
            badge_color=badge_color_pagos,
        ),
        unsafe_allow_html=True,
    )

with kpi_c4:
    st.markdown(
        create_kpi_card_html(
            title="Locales Activos",
            value=str(kpi_data["locales_activos"]),
            subtitle="Sedes con postulantes registrados",
            icon="🏫",
            accent_color="#0284C7",
            icon_bg="rgba(2, 132, 199, 0.08)",
        ),
        unsafe_allow_html=True,
    )

with kpi_c5:
    st.markdown(
        create_kpi_card_html(
            title="Carreras Activas",
            value=str(kpi_data["carreras_activas"]),
            subtitle="Programas académicos solicitados",
            icon="🎓",
            accent_color="#6366F1",
            icon_bg="rgba(99, 102, 241, 0.08)",
        ),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Validación de filtros vacíos
if kpi_data["total_matriculados"] == 0:
    empty_bg = "rgba(239, 68, 68, 0.12)" if is_dark else "#FEF2F2"
    empty_border = "rgba(239, 68, 68, 0.35)" if is_dark else "#FECACA"
    empty_title = "#FCA5A5" if is_dark else "#991B1B"
    empty_text = "#FEE2E2" if is_dark else "#B91C1C"
    st.markdown(
        f"""
        <div style="background: {empty_bg}; border: 1px solid {empty_border}; border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1rem 0;">
            <div style="font-size: 1.35rem; margin-bottom: 0.5rem;">🔍</div>
            <div style="font-weight: 700; color: {empty_title}; font-size: 1.1rem;">No se encontraron registros coincidentes</div>
            <p style="color: {empty_text}; font-size: 0.875rem; margin-top: 0.25rem;">
                Modifique los filtros en la barra lateral o presione el botón inferior para regresar a la vista general.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_empty_left, col_empty_btn, col_empty_right = st.columns([1.5, 1, 1.5])
    with col_empty_btn:
        if st.button(
            "↺ Restablecer todos los filtros",
            key="btn_reset_empty",
            on_click=reset_filters_callback,
            type="primary",
            use_container_width=True,
        ):
            st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# 7. CUADRÍCULA BENTO 1: Matriculados por Ciclo, Local y Turno + Sede × Turno
# -----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns([1.45, 1.25])

with row1_col1:
    with st.container(border=True, key="card_ciclo_local_turno"):
        st.markdown(
            """
            <div class="chart-header-row">
                <div>
                    <div class="chart-title-main">Matriculados por Ciclo, Local y Turno</div>
                    <div class="chart-desc">Distribución consolidada de postulantes por sede institucional y turno</div>
                </div>
                <span class="chart-tag">Matriz Consolidada</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_resumen = queries.get_resumen_ciclo_local_turno(current_filters)

        if not df_resumen.empty:
            total_matriculados_tabla = int(df_resumen["MATRICULADOS"].sum())

            # Renderizado directo de la tabla ejecutiva solicitada
            st.markdown(
                create_executive_table_html(
                    df_resumen,
                    is_dark=is_dark,
                    pagos_pendientes=pagos_data["total_pagos"],
                ),
                unsafe_allow_html=True,
            )

            # Barra de resumen y descarga ejecutiva
            col_act1, col_act2 = st.columns([1.3, 1.3])
            with col_act1:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 8px; padding: 0.35rem 0; font-size: 0.875rem; color: var(--text-secondary); flex-wrap: wrap;">
                        <span>📌 Registros: <b>{len(df_resumen)} sedes/turnos</b></span>
                        <span>•</span>
                        <span>Total: <b style="color: var(--text-primary); font-size: 0.95rem; font-variant-numeric: tabular-nums;">{total_matriculados_tabla:,}</b></span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_act2:
                # Formato plano detallado con total y pagos al pie tal como se visualiza en la tabla
                df_plano_export = df_resumen.copy()
                total_plano_row = pd.DataFrame([{
                    "CICLO": "",
                    "LOCAL": "",
                    "TURNO": "TOTAL GENERAL",
                    "MATRICULADOS": total_matriculados_tabla,
                }])
                pagos_plano_row = pd.DataFrame([{
                    "CICLO": "",
                    "LOCAL": "",
                    "TURNO": "PAGOS QUE TODAVIA NO SE MATRICULAN:",
                    "MATRICULADOS": pagos_data["total_pagos"],
                }])
                df_plano_export = pd.concat([df_plano_export, total_plano_row, pagos_plano_row], ignore_index=True)
                csv_plano = df_plano_export.to_csv(index=False).encode("utf-8-sig")

                st.download_button(
                    label="📥 Exportar Matriz",
                    data=csv_plano,
                    file_name=f"matriculados_detalle_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Descargar listado detallado con Ciclo, Sede, Turno y Matriculados",
                )
        else:
            st.info("No se encontraron registros con los filtros seleccionados.")

with row1_col2:
    with st.container(border=True, key="card_sede_turno"):
        st.markdown(
            """
            <div class="chart-header-row">
                <div>
                    <div class="chart-title-main">Matriculados por Sede y Turno</div>
                    <div class="chart-desc">Distribución territorial de estudiantes desglosada por turno</div>
                </div>
                <span class="chart-tag">Sedes × Turno</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_cruce = queries.get_cruce_local_turno(current_filters)
        if not df_cruce.empty:
            # Calcular el total por sede para ordenar de mayor a menor
            total_por_local = df_cruce.groupby("LOCAL")["total"].sum().reset_index(name="local_total")
            local_order = total_por_local.sort_values(by="local_total", ascending=True)["LOCAL"].tolist()
            max_total = total_por_local["local_total"].max()

            fig_cruce = px.bar(
                df_cruce,
                y="LOCAL",
                x="total",
                color="TURNO",
                orientation="h",
                barmode="stack",
                color_discrete_map=TURNO_COLORS,
                category_orders={"LOCAL": local_order},
                text="total",
            )
            fig_cruce.update_traces(
                texttemplate="%{text:,}",
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=10.5, color="#FFFFFF", family="Plus Jakarta Sans", weight="bold"),
                hovertemplate="<b>%{y}</b><br>Turno %{data.name}: <b>%{x:,}</b> matriculados<extra></extra>",
                marker=dict(line=dict(color="#131C31" if is_dark else "#FFFFFF", width=1.5)),
            )

            # Anotaciones de total general al final de cada barra
            for _, r in total_por_local.iterrows():
                fig_cruce.add_annotation(
                    x=r["local_total"],
                    y=r["LOCAL"],
                    text=f"<b>{r['local_total']:,}</b>",
                    showarrow=False,
                    xshift=14,
                    font=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold"),
                )

            fig_cruce = apply_plotly_theme(fig_cruce, height=480, is_dark=is_dark)
            fig_cruce.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#F8FAFC" if is_dark else "#0F172A", size=11, family="Plus Jakarta Sans")),
                xaxis_title="",
                yaxis_title="",
                margin=dict(l=10, r=35, t=30, b=10),
                yaxis=dict(tickfont=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold")),
                xaxis=dict(range=[0, max(max_total * 1.14, max_total + 2)], showgrid=True, gridcolor="rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0", tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569", family="Plus Jakarta Sans")),
            )
            st.plotly_chart(fig_cruce, use_container_width=True, config={"displayModeBar": False})

# -----------------------------------------------------------------------------
# 8. CUADRÍCULA BENTO 2: Distribución por Turno & Área Académica (Segunda Fila)
# -----------------------------------------------------------------------------
row2_col1, row2_col2 = st.columns([1.15, 1.45])

with row2_col1:
    with st.container(border=True, key="card_dist_turno"):
        st.markdown(
            """
            <div class="chart-header-row">
                <div>
                    <div class="chart-title-main">Distribución por Turno</div>
                    <div class="chart-desc">Proporción porcentual y distribución por turno</div>
                </div>
                <span class="chart-tag">Proporción</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_turno = queries.get_matriculados_por_turno(current_filters)
        if not df_turno.empty:
            fig_turno = px.pie(
                df_turno,
                names="TURNO",
                values="total",
                hole=0.68,
                color="TURNO",
                color_discrete_map=TURNO_COLORS,
            )
            total_turno = df_turno["total"].sum()
            fig_turno.update_traces(
                textinfo="percent",
                textfont=dict(size=12, color="#FFFFFF", family="Plus Jakarta Sans", weight="bold"),
                hovertemplate="<b>Turno %{label}</b><br>Matriculados: <b>%{value:,}</b> (%{percent})<extra></extra>",
                marker=dict(line=dict(color="#131C31" if is_dark else "#FFFFFF", width=3)),
            )
            fig_turno = apply_plotly_theme(fig_turno, height=400, is_dark=is_dark)
            fig_turno.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(color="#F8FAFC" if is_dark else "#0F172A", size=11, family="Plus Jakarta Sans")),
                margin=dict(l=10, r=10, t=20, b=30),
                annotations=[
                    dict(
                        text=f"<span style='font-size:2rem; font-weight:800; color:{'#F8FAFC' if is_dark else '#0F172A'}; font-family:Outfit;'>{total_turno:,}</span><br><span style='font-size:0.75rem; color:{'#CBD5E1' if is_dark else '#475569'}; text-transform:uppercase; letter-spacing:0.08em; font-weight:600;'>Total</span>",
                        x=0.5, y=0.5,
                        font_size=13,
                        showarrow=False,
                    )
                ]
            )
            st.plotly_chart(fig_turno, use_container_width=True, config={"displayModeBar": False})

with row2_col2:
    with st.container(border=True, key="card_dist_area"):
        st.markdown(
            """
            <div class="chart-header-row">
                <div>
                    <div class="chart-title-main">Matriculados por Área Académica</div>
                    <div class="chart-desc">Postulantes agrupados por área de conocimiento institucional</div>
                </div>
                <span class="chart-tag">Áreas</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_area = queries.get_matriculados_por_area(current_filters)
        if not df_area.empty:
            df_area_sorted = df_area.sort_values(by="total", ascending=True).copy()
            df_area_sorted["AREA_LABEL"] = df_area_sorted["AREA"].apply(lambda a: AREA_LABELS.get(a, f"Área {a}"))
            fig_area = px.bar(
                df_area_sorted,
                x="total",
                y="AREA_LABEL",
                orientation="h",
                text="total",
                color="AREA",
                color_discrete_map=AREA_COLORS,
                hover_data={"AREA_LABEL": False, "AREA": False, "total": ":,"},
            )
            max_area = int(df_area_sorted["total"].max()) if not df_area_sorted.empty else 0
            fig_area.update_traces(
                texttemplate="%{text:,}",
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold"),
                hovertemplate="<b>%{y}</b><br>Matriculados: <b>%{x:,}</b><extra></extra>",
                marker=dict(line=dict(width=0)),
            )
            fig_area = apply_plotly_theme(fig_area, height=400, is_dark=is_dark)
            fig_area.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="",
                margin=dict(l=10, r=40, t=10, b=10),
                xaxis=dict(range=[0, max(max_area * 1.15, max_area + 2)], tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569", family="Plus Jakarta Sans")),
                yaxis=dict(tickfont=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold")),
            )
            st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})

# -----------------------------------------------------------------------------
# 9. CUADRÍCULA BENTO 3: Evolución Cronológica de Matrículas (Ancho Completo)
# -----------------------------------------------------------------------------
with st.container(border=True, key="card_evolucion_temporal"):
    st.markdown(
        """
        <div class="chart-header-row">
            <div>
                <div class="chart-title-main">Evolución Cronológica de Matrículas</div>
                <div class="chart-desc">Comportamiento diario de inscripciones y curva de avance acumulado</div>
            </div>
            <span class="chart-tag">Tendencia</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    df_evolucion = queries.get_evolucion_temporal(current_filters)
    if not df_evolucion.empty:
        fig_evolucion = go.Figure()

        daily_bar_color = "rgba(96, 165, 250, 0.45)" if is_dark else "rgba(30, 64, 175, 0.40)"
        spline_color = "#38BDF8" if is_dark else "#1D4ED8"
        marker_color = "#60A5FA" if is_dark else "#1E40AF"

        # Barras de matrículas diarias
        fig_evolucion.add_trace(
            go.Bar(
                x=df_evolucion["fecha_matricula"],
                y=df_evolucion["total"],
                name="Inscripciones Diarias",
                marker_color=daily_bar_color,
                marker_line_width=0,
                hovertemplate="<b>Fecha: %{x|%d %b %Y}</b><br>Inscripciones del día: <b>%{y:,}</b><extra></extra>",
            )
        )

        # Curva de avance acumulado suave
        fig_evolucion.add_trace(
            go.Scatter(
                x=df_evolucion["fecha_matricula"],
                y=df_evolucion["total_acumulado"],
                name="Total Acumulado",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=spline_color, width=2.5, shape="spline"),
                marker=dict(size=5, color=marker_color, line=dict(color="#FFFFFF", width=1.5)),
                hovertemplate="<b>Total acumulado: %{y:,}</b><extra></extra>",
            )
        )

        # Identificar y destacar el hito del día récord de matrículas (Delight analítico)
        if not df_evolucion.empty and df_evolucion["total"].max() > 0:
            idx_max = df_evolucion["total"].idxmax()
            pico_row = df_evolucion.loc[idx_max]
            fig_evolucion.add_annotation(
                x=pico_row["fecha_matricula"],
                y=pico_row["total"],
                text=f"⭐ Pico: {int(pico_row['total']):,} inscritos",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#38BDF8" if is_dark else "#1D4ED8",
                ax=0,
                ay=-26,
                bgcolor="rgba(15, 23, 42, 0.85)" if is_dark else "rgba(255, 255, 255, 0.95)",
                bordercolor="rgba(56, 189, 248, 0.45)" if is_dark else "rgba(29, 78, 216, 0.35)",
                borderwidth=1,
                borderpad=4,
                font=dict(size=10, color="#38BDF8" if is_dark else "#1D4ED8", family="Plus Jakarta Sans", weight="bold"),
            )

        fig_evolucion = apply_plotly_theme(fig_evolucion, height=360, is_dark=is_dark)
        fig_evolucion.update_layout(
            yaxis=dict(title="Diario", title_font=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A"), tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569")),
            yaxis2=dict(
                title="Acumulado",
                title_font=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A"),
                tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569"),
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            xaxis=dict(title="", tickformat="%d %b", tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569")),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(color="#F8FAFC" if is_dark else "#0F172A")),
            margin=dict(l=10, r=10, t=32, b=15),
        )
        st.plotly_chart(fig_evolucion, use_container_width=True, config={"displayModeBar": False})

# -----------------------------------------------------------------------------
# 10. CUADRÍCULA BENTO 4: Top 15 Carreras con Mayor Demanda (Ancho Completo)
# -----------------------------------------------------------------------------
with st.container(border=True, key="card_top_carreras"):
    st.markdown(
        """
        <div class="chart-header-row">
            <div>
                <div class="chart-title-main">Top 15 Carreras con Mayor Demanda</div>
                <div class="chart-desc">Programas académicos ordenados por volumen absoluto de estudiantes</div>
            </div>
            <span class="chart-tag">Ranking</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    df_todas_carreras = queries.get_top_carreras(current_filters, limit=100)
    if not df_todas_carreras.empty:
        df_carreras = df_todas_carreras.head(15).copy()
        df_carreras_sorted = df_carreras.sort_values(by="total", ascending=True).copy()
        max_carreras = int(df_carreras_sorted["total"].max()) if not df_carreras_sorted.empty else 0
        
        # Formato de barra con escala cromática adaptativa
        c_scale = [[0, "#1E3A8A"], [0.5, "#3B82F6"], [1, "#60A5FA"]] if is_dark else [[0, "#93C5FD"], [0.5, "#3B82F6"], [1, "#1D4ED8"]]
        fig_carreras = px.bar(
            df_carreras_sorted,
            x="total",
            y="CARRERA",
            orientation="h",
            text="total",
            color="total",
            color_continuous_scale=c_scale,
        )
        fig_carreras.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold"),
            hovertemplate="<b>%{y}</b><br>Matriculados: <b>%{x:,}</b><extra></extra>",
            marker=dict(line=dict(width=0)),
        )
        fig_carreras = apply_plotly_theme(fig_carreras, height=480, is_dark=is_dark)
        fig_carreras.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title="",
            margin=dict(l=10, r=40, t=10, b=10),
            yaxis=dict(tickfont=dict(size=11, color="#F8FAFC" if is_dark else "#0F172A", family="Plus Jakarta Sans", weight="bold")),
            xaxis=dict(range=[0, max(max_carreras * 1.15, max_carreras + 2)], showgrid=True, gridcolor="rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0", tickfont=dict(size=10.5, color="#CBD5E1" if is_dark else "#475569", family="Plus Jakarta Sans")),
        )
        st.plotly_chart(fig_carreras, use_container_width=True, config={"displayModeBar": False})

        # Barra de acciones y descarga para ranking de carreras
        col_car_info, col_car_btn = st.columns([1.5, 1])
        with col_car_info:
            total_top15 = int(df_carreras["total"].sum())
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 8px; padding: 0.35rem 0; font-size: 0.875rem; color: var(--text-secondary); flex-wrap: wrap;">
                    <span>🏆 <b>Top 15 Programas</b></span>
                    <span>•</span>
                    <span>Subtotal Top 15: <b style="color: var(--text-primary); font-size: 0.95rem; font-variant-numeric: tabular-nums;">{total_top15:,}</b></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_car_btn:
            df_carreras_export = df_todas_carreras.copy()
            df_carreras_export["RANKING"] = range(1, len(df_carreras_export) + 1)
            total_carreras_sum = df_carreras_export["total"].sum()
            if total_carreras_sum > 0:
                df_carreras_export["PORCENTAJE"] = (df_carreras_export["total"] / total_carreras_sum * 100).round(2).astype(str) + "%"
            else:
                df_carreras_export["PORCENTAJE"] = "0.00%"
            df_carreras_export = df_carreras_export[["RANKING", "CARRERA", "total", "PORCENTAJE"]]
            df_carreras_export.rename(columns={"total": "MATRICULADOS"}, inplace=True)
            csv_carreras = df_carreras_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Exportar Ranking de Carreras",
                data=csv_carreras,
                file_name=f"ranking_carreras_matricula_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Descargar listado con todas las carreras ordenadas por demanda de postulantes",
            )


# 11. Pie de Página de Alto Nivel
st.markdown(
    """
    <div class="footer-minimal">
        🔒 Sistema Ejecutivo de Métricas de Matrícula — Monitoreo Oficial en Tiempo Real<br>
        Uso interno y confidencial • Datos agregados con estricto apego a políticas de privacidad
    </div>
    """,
    unsafe_allow_html=True,
)
