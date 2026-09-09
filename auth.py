"""
Módulo de autenticación de alta fidelidad para el Dashboard de Matrículas.
Diseñado con arquitectura Double-Bezel, tipografía Plus Jakarta Sans / Outfit,
seguridad bcrypt y manejo fluido de sesiones.
"""

import os
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.yaml")


def load_authenticator():
    """
    Carga la configuración desde credentials.yaml e inicializa el objeto Authenticate.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        st.error(
            "⚠️ Archivo `credentials.yaml` no encontrado. "
            "Cree el archivo basándose en `credentials.yaml.example`."
        )
        st.stop()

    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)

    credentials = config.get("credentials", {})
    cookie_cfg = config.get("cookie", {})
    cookie_name = cookie_cfg.get("name", "dashboard_matriculas_auth")
    cookie_key = cookie_cfg.get("key", "matriculas_secret_key_default")
    cookie_expiry_days = float(cookie_cfg.get("expiry_days", 0.33))

    import streamlit_authenticator.params as stauth_params
    stauth_params.PRE_LOGIN_SLEEP_TIME = 0.0

    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        cookie_key=cookie_key,
        cookie_expiry_days=cookie_expiry_days,
        auto_hash=False,
        login_sleep_time=0.0
    )
    return authenticator


def setup_auth_flow(authenticator):
    """
    Gestiona el flujo completo de login con estética ejecutiva:
    - Renderiza una tarjeta flotante de inicio de sesión con doble bisel.
    - Bloquea cualquier renderizado de datos del dashboard hasta autenticar.
    """
    auth_status = st.session_state.get("authentication_status")

    if not auth_status:
        # Durante el estado no autenticado, ocultar la barra lateral por completo para evitar saltos de layout
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"],
            div[data-testid="collapsedControl"] {
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        login_placeholder = st.empty()

        with login_placeholder.container():
            # Centrado con proporción áurea para tarjetas de autenticación
            col1, col2, col3 = st.columns([1, 1.3, 1])
            with col2:
                st.markdown(
                    """
                    <div class="login-wrapper">
                        <div class="login-ambient-glow"></div>
                        <div class="login-header-box">
                            <div class="login-emblem-badge">🏛️</div>
                            <div class="login-eyebrow">
                                <span>SISTEMA DE ADMISIÓN Y MATRÍCULA</span>
                            </div>
                            <h1 class="login-title">Portal de Monitoreo</h1>
                            <p class="login-subtitle">
                                Acceso restringido para el seguimiento ejecutivo en tiempo real
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Formulario de inicio de sesión
                try:
                    authenticator.login(
                        location="main",
                        max_login_attempts=3,
                        fields={
                            "Form name": "Credenciales de Acceso",
                            "Username": "Usuario",
                            "Password": "Contraseña",
                            "Login": "Ingresar al Tablero",
                        },
                    )
                except Exception as e:
                    st.error(f"Error en el sistema de autenticación: {e}")

                auth_status = st.session_state.get("authentication_status")

                if auth_status is False:
                    st.markdown(
                        """
                        <div class="login-error-card">
                            <div class="login-error-icon">⚠️</div>
                            <div class="login-error-text">
                                <strong>Credenciales incorrectas</strong>
                                <span>El usuario o la contraseña ingresados no son válidos. Por favor, verifique sus datos.</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    """
                    <div class="login-footer-info">
                        <strong>UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS</strong><br>
                        Centro Preuniversitario · Sistema de Admisión y Matrícula
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Si las credenciales fueron correctas en este ciclo, limpiar de inmediato el placeholder y reejecutar
        if auth_status is True:
            login_placeholder.empty()
            st.rerun()

        # Detener la ejecución del dashboard hasta que la autenticación sea exitosa
        st.stop()

    user_name = st.session_state.get("name", "Usuario")
    username = st.session_state.get("username", "")

    return authenticator, username, user_name
