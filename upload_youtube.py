"""
Sube a YouTube el video generado por generate_short.py.

Requiere estas variables de entorno (se configuran como GitHub Secrets):
  YT_CLIENT_ID
  YT_CLIENT_SECRET
  YT_REFRESH_TOKEN

Ver get_refresh_token.py para obtener el refresh token una única vez.
"""
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def obtener_credenciales():
    return Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=SCOPES,
    )


def subir_video(ruta_video, titulo, descripcion, privacidad="unlisted", tags=None):
    creds = obtener_credenciales()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": titulo,
            "description": descripcion,
            "tags": tags or [],
            "categoryId": "22",  # People & Blogs; cambiala si querés otra categoría
        },
        "status": {
            "privacyStatus": privacidad,  # "unlisted" | "private" | "public"
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(ruta_video, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    respuesta = None
    while respuesta is None:
        estado, respuesta = request.next_chunk()
        if estado:
            print(f"Subiendo... {int(estado.progress() * 100)}%")

    print(f"Video subido correctamente. ID: {respuesta['id']}")
    print(f"https://youtube.com/shorts/{respuesta['id']}")
    return respuesta["id"]


if __name__ == "__main__":
    with open("output/metadata.txt", "r", encoding="utf-8") as f:
        ruta_video, titulo, frase = f.read().splitlines()

    descripcion = f"{frase}\n\n#Shorts\n\nVideo generado y publicado automáticamente."
    subir_video(
        ruta_video,
        titulo,
        descripcion,
        privacidad="unlisted",
        tags=["shorts"],
    )
