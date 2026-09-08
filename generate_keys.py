"""
Utilidad CLI para generar hashes de contraseñas con bcrypt y claves seguras
para el archivo credentials.yaml de la aplicación.
"""

import sys
import secrets
import streamlit_authenticator as stauth

def generate_key(length: int = 32) -> str:
    """Genera una clave secreta aleatoria y segura para la cookie."""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """Genera el hash bcrypt para una contraseña."""
    hasher = stauth.Hasher()
    return hasher.hash(password)

def main():
    print("=" * 60)
    print(" Generador de Credenciales Seguras - Dashboard de Matrículas")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
    else:
        pwd = input("Ingrese la contraseña a hashear (ej. Admin2026!): ").strip()
        if not pwd:
            print("Error: La contraseña no puede estar vacía.")
            sys.exit(1)
            
    hashed = hash_password(pwd)
    cookie_key = generate_key()
    
    print("\nResultado:")
    print(f"- Contraseña en texto plano : {pwd}")
    print(f"- Hash bcrypt generado     : {hashed}")
    print(f"- Clave segura para cookie : {cookie_key}")
    print("\nPegue el hash en su archivo credentials.yaml bajo el usuario correspondiente:")
    print(f"      password: {hashed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
