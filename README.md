# Spotify Playlist Extractor

## Descripción

Herramienta para extraer playlists desde Spotify y YouTube Music, y guardarlas en un archivo JSON centralizado.

---

## 1. Parser HTML de Spotify

### Descripción

Extrae canciones de un archivo HTML exportado desde Spotify.

### Parámetros

| Parámetro      | Tipo       | Obligatorio | Por defecto      | Descripción                                                         |
| -------------- | ---------- | ----------- | ---------------- | ------------------------------------------------------------------- |
| `html_file`    | posicional | No          | `08 - 84.html`   | Ruta del archivo HTML de Spotify a procesar                         |
| `-o, --output` | opcional   | No          | `../tracks.json` | Ruta del archivo JSON de salida (se guarda en la raíz del proyecto) |
| `--print`      | flag       | No          | N/A              | Imprime el JSON generado en pantalla además de guardarlo            |

### Uso

**Ejemplo básico (usa archivo HTML por defecto):**

```powershell
cd jsonGenerator
python spotify_html_playlist_parser.py
```

**Especificar un archivo HTML diferente:**

```powershell
python spotify_html_playlist_parser.py "mi_playlist.html"
```

**Especificar ruta de salida personalizada:**

```powershell
python spotify_html_playlist_parser.py "mi_playlist.html" -o "salida/tracks.json"
```

**Imprimir resultado en pantalla:**

```powershell
python spotify_html_playlist_parser.py "mi_playlist.html" --print
```

**Todos los parámetros:**

```powershell
python spotify_html_playlist_parser.py "mi_playlist.html" -o "../tracks.json" --print
```

### Salida (JSON)

```json
{
  "tracks": [
    {
      "track_number": "1",
      "title": "Blackbird - Remastered 2009",
      "artist": "The Beatles",
      "album": "The Beatles (Remastered)"
    },
    {
      "track_number": "2",
      "title": "Something",
      "artist": "The Beatles",
      "album": "Abbey Road"
    }
  ]
}
```

---

## 2. Parser HTML de YouTube Music

### Descripción

Extrae canciones de un archivo HTML exportado desde YouTube Music.

### Parámetros

| Parámetro      | Tipo       | Obligatorio | Por defecto      | Descripción                                                         |
| -------------- | ---------- | ----------- | ---------------- | ------------------------------------------------------------------- |
| `html_file`    | posicional | No          | `ytmusic.html`   | Ruta del archivo HTML de YouTube Music a procesar                   |
| `-o, --output` | opcional   | No          | `../tracks.json` | Ruta del archivo JSON de salida (se guarda en la raíz del proyecto) |
| `--print`      | flag       | No          | N/A              | Imprime el JSON generado en pantalla además de guardarlo            |

### Uso

**Ejemplo básico (usa archivo HTML por defecto):**

```powershell
cd jsonGenerator
python ytmusic_html_playlist_parser.py
```

**Especificar un archivo HTML diferente:**

```powershell
python ytmusic_html_playlist_parser.py "mi_playlist_ytmusic.html"
```

**Especificar ruta de salida personalizada:**

```powershell
python ytmusic_html_playlist_parser.py "mi_playlist_ytmusic.html" -o "salida/tracks.json"
```

**Imprimir resultado en pantalla:**

```powershell
python ytmusic_html_playlist_parser.py "mi_playlist_ytmusic.html" --print
```

**Todos los parámetros:**

```powershell
python ytmusic_html_playlist_parser.py "mi_playlist_ytmusic.html" -o "../tracks.json" --print
```

### Salida (JSON)

```json
{
  "tracks": [
    {
      "track_number": "1",
      "title": "Blinding Lights",
      "artist": "The Weeknd",
      "album": "After Hours"
    },
    {
      "track_number": "2",
      "title": "As It Was",
      "artist": "Harry Styles",
      "album": "Harry's House"
    }
  ]
}
```

---

## 3. Comportamiento de Actualización

Ambos parsers **anexan** nuevas canciones al `tracks.json` existente en lugar de sobrescribirlo:

- ✅ Lee las canciones existentes en `tracks.json`
- ✅ Agrega solo las canciones nuevas (deduplicadas por `title` y `artist`)
- ✅ Evita canciones repetidas
- ✅ Guarda el resultado actualizado en `tracks.json`

**Ejemplo de ejecución secuencial:**

```powershell
# Primera ejecución: crea tracks.json con 10 canciones
python spotify_html_playlist_parser.py "playlist1.html"

# Segunda ejecución: agrega 5 canciones nuevas (total: 15)
python spotify_html_playlist_parser.py "playlist2.html"

# Tercera ejecución: agrega 3 canciones nuevas de YouTube Music (total: 18)
python ytmusic_html_playlist_parser.py "ytmusic_playlist.html"
```

---

## 4. Parser API de Spotify

### Descripción

Extrae canciones de Spotify usando la API oficial (requiere credenciales).

### Setup

```powershell
$env:SPOTIPY_CLIENT_ID="tu_client_id"
$env:SPOTIPY_CLIENT_SECRET="tu_client_secret"
$env:SPOTIPY_REDIRECT_URI="http://127.0.0.1:8888/callback"
$env:SPOTIPY_PLAYLIST_ID="tu_playlist_id"
```

### Uso

```powershell
cd jsonGenerator
python playlistExtrator.py
```

### Salida (JSON)

```json
[
  {
    "id": "spotify_track_id",
    "title": "Blackbird - Remastered 2009",
    "artist": "The Beatles",
    "album": "The Beatles (Remastered)",
    "duration_ms": 240000
  }
]
```

---

## 5. Comparar librería local con `tracks.json`

### Descripción

`missingTracks/check_music.py` compara las canciones registradas en `tracks.json` con los archivos `.mp3` existentes en una carpeta local.

El script normaliza nombres y busca coincidencias entre:

- artista + título
- título + artista
- título solo

Si no encuentra un archivo local coincidente, registra la pista como faltante en `missingTracks/missing_tracks.json`.

### Uso

```powershell
cd missingTracks
python check_music.py "E:\Music\Spotify\misc"
```

### Resultado

- `missing_tracks.json` se guarda en `missingTracks/`
- El archivo contiene una lista de todas las pistas de `tracks.json` que no se detectaron como archivos `.mp3` en la carpeta local

### Ejemplo de salida en pantalla

```text
Scanning directory: E:\Music\Spotify\misc

Analysis completed:
- Total in JSON: 954
- Total files found on disk: 1200
- Missing tracks identified: 82
Result saved to: missing_tracks.json
```

### Nota

- El script asume que los archivos locales son `.mp3`
- Si deseas usar otra carpeta, reemplaza la ruta en el argumento del script
