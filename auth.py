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

    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        cookie_key=cookie_key,
        cookie_expiry_days=cookie_expiry_days,
        auto_hash=False
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
        # Estructura centrada de alta calidad visual
        col1, col2, col3 = st.columns([1, 1.6, 1])
        with col2:
            st.markdown(
                """
                <div style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;">
                    <div style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: #1D4ED8; background: #EFF6FF; padding: 4px 12px; border-radius: 9999px; border: 1px solid #DBEAFE; margin-bottom: 0.75rem;">
                        <span>🏛️</span> SISTEMA DE ADMISIÓN Y MATRÍCULA
                    </div>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.1rem; font-weight: 700; letter-spacing: -0.035em; color: #0F172A; margin: 0;">
                        Portal de Monitoreo
                    </h2>
                    <p style="color: #64748B; font-size: 0.92rem; margin-top: 0.35rem;">
                        Acceso restringido para el seguimiento ejecutivo en tiempo real
                    </p>
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
                        "Login": "Ingresar al Tablero"
                    }
                )
            except Exception as e:
                st.error(f"Error en el sistema de autenticación: {e}")

            auth_status = st.session_state.get("authentication_status")

            if auth_status is False:
                st.error("Credenciales incorrectas. Verifique su usuario y contraseña.")
            elif auth_status is None:
                st.info("🔒 Ingrese con su cuenta autorizada institucional para acceder.")
                
                with st.expander("ℹ️ Cuentas de Acceso Predefinidas", expanded=False):
                    st.markdown("""
                    - **`admin`** *(Administrador del Sistema)*
                    - **`jperez`** *(Juan Pérez - Analista)*
                    - **`directivo`** *(Dirección Académica)*
                    """)

        # Detener la ejecución del dashboard hasta que la autenticación sea exitosa
        st.stop()

    user_name = st.session_state.get("name", "Usuario")
    username = st.session_state.get("username", "")

    return authenticator, username, user_name
