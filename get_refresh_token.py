"""
Ejecutar UNA SOLA VEZ, en tu computadora local (NO en GitHub Actions),
para obtener el refresh_token que después se guarda como GitHub Secret.

Pasos previos:
1. Ir a https://console.cloud.google.com/ y crear un proyecto.
2. Habilitar la API "YouTube Data API v3" (menú APIs & Services > Library).
3. En "APIs & Services > Credentials", crear credenciales OAuth 2.0
   de tipo "Aplicación de escritorio" (Desktop app).
4. Descargar el JSON de esas credenciales y guardarlo en esta misma
   carpeta con el nombre client_secret.json.
5. Instalar dependencias:  pip install google-auth-oauthlib
6. Ejecutar:  python get_refresh_token.py
   Se va a abrir el navegador para iniciar sesión con la cuenta de
   Google/YouTube donde querés publicar los videos.

El script imprime tres valores. Esos tres van como GitHub Secrets
del repositorio (Settings > Secrets and variables > Actions):
  YT_CLIENT_ID
  YT_CLIENT_SECRET
  YT_REFRESH_TOKEN
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
credenciales = flow.run_local_server(port=0)

print("\n--- Guardá estos 3 valores como GitHub Secrets ---")
print(f"YT_CLIENT_ID={credenciales.client_id}")
print(f"YT_CLIENT_SECRET={credenciales.client_secret}")
print(f"YT_REFRESH_TOKEN={credenciales.refresh_token}")
