"""
Genera un YouTube Short (video vertical 1080x1920, <60s) mostrando una
tabla de la sucesión de Fibonacci, con narración por voz (TTS).

Cada corrida arma una tabla con una cantidad de términos al azar
(entre MIN_TERMINOS y MAX_TERMINOS), para que no sea siempre el mismo
video.

Salida:
  output/short_<fecha>.mp4
  output/metadata.txt   -> ruta_video / titulo / descripcion (lo usa upload_youtube.py)
"""
import os
import random
from datetime import datetime

from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
OUTPUT_DIR = "output"
MIN_TERMINOS = 8
MAX_TERMINOS = 12

# Ruta relativa a la fuente empaquetada en el repo (carpeta fonts/),
# así funciona igual en Windows local y en el runner de GitHub Actions (Ubuntu).
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_TITULO = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")
FONT_TABLA = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")


def generar_fibonacci(cantidad):
    secuencia = [0, 1]
    while len(secuencia) < cantidad:
        secuencia.append(secuencia[-1] + secuencia[-2])
    return secuencia[:cantidad]


def crear_fondo_degradado(color_inicio=(10, 15, 35), color_fin=(20, 60, 90)):
    fondo = Image.new("RGB", (WIDTH, HEIGHT), color_inicio)
    draw = ImageDraw.Draw(fondo)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(color_inicio[0] + (color_fin[0] - color_inicio[0]) * t)
        g = int(color_inicio[1] + (color_fin[1] - color_inicio[1]) * t)
        b = int(color_inicio[2] + (color_fin[2] - color_inicio[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return fondo


def dibujar_tabla_fibonacci(fondo, secuencia):
    draw = ImageDraw.Draw(fondo)
    fuente_titulo = ImageFont.truetype(FONT_TITULO, 66)
    fuente_tabla = ImageFont.truetype(FONT_TABLA, 54)

    titulo = "Sucesión de Fibonacci"
    bbox = draw.textbbox((0, 0), titulo, font=fuente_titulo)
    x_titulo = (WIDTH - (bbox[2] - bbox[0])) // 2
    draw.text((x_titulo + 3, 143), titulo, font=fuente_titulo, fill=(0, 0, 0))
    draw.text((x_titulo, 140), titulo, font=fuente_titulo, fill=(255, 255, 255))

    # geometría de la tabla: dos columnas (n, F(n)) centradas
    filas = len(secuencia) + 1  # + encabezado
    alto_fila = 100
    ancho_col_n = 220
    ancho_col_valor = 420
    ancho_tabla = ancho_col_n + ancho_col_valor
    x_tabla = (WIDTH - ancho_tabla) // 2
    y_tabla = 320
    alto_tabla = alto_fila * filas

    # borde exterior
    draw.rectangle(
        [x_tabla, y_tabla, x_tabla + ancho_tabla, y_tabla + alto_tabla],
        outline=(255, 255, 255),
        width=4,
    )
    # línea divisoria entre columnas
    draw.line(
        [(x_tabla + ancho_col_n, y_tabla), (x_tabla + ancho_col_n, y_tabla + alto_tabla)],
        fill=(255, 255, 255),
        width=3,
    )

    def escribir_centrado(texto, x_col_izq, ancho_col, y_fila, color):
        bbox = draw.textbbox((0, 0), texto, font=fuente_tabla)
        ancho_texto = bbox[2] - bbox[0]
        alto_texto = bbox[3] - bbox[1]
        x = x_col_izq + (ancho_col - ancho_texto) // 2
        y = y_fila + (alto_fila - alto_texto) // 2 - bbox[1]
        draw.text((x, y), texto, font=fuente_tabla, fill=color)

    # encabezado
    y_fila = y_tabla
    draw.rectangle(
        [x_tabla, y_fila, x_tabla + ancho_tabla, y_fila + alto_fila],
        fill=(255, 255, 255),
    )
    escribir_centrado("n", x_tabla, ancho_col_n, y_fila, (10, 15, 35))
    escribir_centrado("F(n)", x_tabla + ancho_col_n, ancho_col_valor, y_fila, (10, 15, 35))

    # filas de datos (se ven sobre el degradado de fondo, sin relleno propio)
    for i, valor in enumerate(secuencia):
        y_fila = y_tabla + alto_fila * (i + 1)
        # líneas horizontales
        draw.line(
            [(x_tabla, y_fila), (x_tabla + ancho_tabla, y_fila)],
            fill=(255, 255, 255),
            width=2,
        )
        escribir_centrado(str(i), x_tabla, ancho_col_n, y_fila, (255, 255, 255))
        escribir_centrado(str(valor), x_tabla + ancho_col_n, ancho_col_valor, y_fila, (255, 255, 255))

    return fondo


def construir_narracion(secuencia):
    numeros = ", ".join(str(v) for v in secuencia[:-1]) + f" y {secuencia[-1]}"
    return (
        "La sucesión de Fibonacci empieza en cero y uno. "
        "Cada término siguiente es la suma de los dos anteriores. "
        f"Los primeros {len(secuencia)} términos son: {numeros}."
    )


def generar_narracion(texto, ruta_audio):
    tts = gTTS(text=texto, lang="es")
    tts.save(ruta_audio)


def generar_short():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cantidad = random.randint(MIN_TERMINOS, MAX_TERMINOS)
    secuencia = generar_fibonacci(cantidad)
    print(f"Tabla de Fibonacci ({cantidad} términos): {secuencia}")

    texto_narracion = construir_narracion(secuencia)
    audio_path = os.path.join(OUTPUT_DIR, "narracion.mp3")
    generar_narracion(texto_narracion, audio_path)
    audio_clip = AudioFileClip(audio_path)
    duracion = min(audio_clip.duration + 1.5, 59)  # los Shorts deben durar <60s

    imagen = crear_fondo_degradado()
    imagen = dibujar_tabla_fibonacci(imagen, secuencia)
    imagen_path = os.path.join(OUTPUT_DIR, "frame.png")
    imagen.save(imagen_path)

    clip = ImageClip(imagen_path).set_duration(duracion)
    clip = clip.set_audio(audio_clip.set_start(0.5))
    clip = clip.fadein(0.4).fadeout(0.4)

    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    video_path = os.path.join(OUTPUT_DIR, f"short_{fecha}.mp4")
    clip.write_videofile(video_path, fps=30, codec="libx264", audio_codec="aac")

    titulo = f"Tabla de Fibonacci: los primeros {cantidad} términos"
    with open(os.path.join(OUTPUT_DIR, "metadata.txt"), "w", encoding="utf-8") as f:
        f.write(f"{video_path}\n{titulo}\n{texto_narracion}")

    return video_path, titulo, texto_narracion


if __name__ == "__main__":
    ruta, titulo, texto = generar_short()
    print(f"Video generado en: {ruta}")
