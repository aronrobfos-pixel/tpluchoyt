# Short automático a YouTube — Tablas de Fibonacci

Genera un video vertical (1080x1920) mostrando una tabla de la
sucesión de Fibonacci (columnas n / F(n)), con narración en español,
y lo sube a YouTube como "no listado", todo automático vía GitHub
Actions, todos los días a las 22:00 (hora Argentina).

## Cómo funciona

1. `generate_short.py` calcula una tabla de Fibonacci con una
   cantidad de términos al azar (entre 8 y 12, así no es siempre el
   mismo video), la dibuja como tabla sobre un fondo degradado, genera
   una narración en español (gTTS) que explica la sucesión y lee los
   términos, y arma el video con moviepy.
2. `upload_youtube.py` sube ese video a YouTube como **no listado**
   usando la YouTube Data API v3.
3. El workflow de GitHub Actions (`.github/workflows/publish_short.yml`)
   corre ambos scripts todos los días a las 22:00 (ART) mediante un
   cron scheduled trigger.

> **Nota sobre "programado" en YouTube:** la función nativa de YouTube
> para programar una publicación (`publishAt`) solo funciona si el video
> se sube como **"privado"** y pasa a ser **público** en la fecha elegida;
> no existe una versión "programado → no listado" del lado de YouTube.
> Por eso este proyecto resuelve el "a las 22:00" con el disparador
> `cron` de GitHub Actions: el video se genera y se sube directamente
> como no listado a esa hora, sin pasar por el mecanismo de scheduling
> de YouTube. Si en algún momento preferís que se vuelva **público**
> automáticamente en vez de no listado, es cambiar una línea (te lo
> indico más abajo).

## Configuración (una sola vez)

1. **Crear credenciales de Google:**
   - Entrá a [console.cloud.google.com](https://console.cloud.google.com/),
     creá un proyecto y habilitá **YouTube Data API v3**.
   - En *Credentials*, creá un OAuth Client ID de tipo **Desktop app**
     y descargá el JSON como `client_secret.json`.

2. **Obtener el refresh token (en tu PC, no en GitHub):**
   ```bash
   pip install google-auth-oauthlib
   python get_refresh_token.py
   ```
   Iniciá sesión con la cuenta de YouTube donde querés publicar.
   El script te va a imprimir tres valores.

3. **Cargar los secrets en GitHub:**
   En el repo: *Settings → Secrets and variables → Actions → New repository secret*.
   Cargá estos tres, con los valores que imprimió el paso anterior:
   - `YT_CLIENT_ID`
   - `YT_CLIENT_SECRET`
   - `YT_REFRESH_TOKEN`

4. **Subir este código a tu repositorio de GitHub**, respetando la
   carpeta `.github/workflows/` (así GitHub reconoce el workflow).

5. Listo. Todos los días a las 22:00 (ART) se va a generar y publicar
   un Short nuevo con una tabla de Fibonacci de largo aleatorio (entre
   8 y 12 términos), para que no sea siempre el mismo video.

## Probar sin esperar a las 22:00

En la pestaña **Actions** del repo, abrí el workflow "Publicar Short
en YouTube" y usá el botón **Run workflow** (esto funciona porque el
workflow también tiene `workflow_dispatch` habilitado).

## Si en vez de "no listado" querés que se haga público solo a las 22:00

En `upload_youtube.py`, cambiá `privacidad="unlisted"` por
`privacidad="private"` y agregá `"publishAt": "<fecha ISO 8601>"` dentro
de `body["status"]`. En ese caso el trigger de GitHub Actions puede
correr en cualquier momento (por ejemplo apenas termine de generarse
el contenido), y es YouTube quien se encarga de hacerlo público a la
hora indicada.
