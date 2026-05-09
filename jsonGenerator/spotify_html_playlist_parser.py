import argparse
import json
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit(
        "BeautifulSoup4 no está instalado. Instala con: python -m pip install beautifulsoup4"
    )


def parse_spotify_track_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    tracks = []

    rows = soup.select('div[role="row"] div[data-testid="tracklist-row"]')
    for row in rows:
        number_el = row.select_one('[aria-colindex="1"] span')
        title_el = row.select_one('a[data-testid="internal-track-link"] div')
        artist_cell = row.select_one('[aria-colindex="3"]')
        album_el = row.select_one('[aria-colindex="4"] a')

        number = number_el.get_text(strip=True) if number_el else None
        title = title_el.get_text(strip=True) if title_el else None
        album = album_el.get_text(strip=True) if album_el else None

        artists = []
        if artist_cell:
            artists = [a.get_text(strip=True) for a in artist_cell.select('a') if a.get_text(strip=True)]

        if not any([number, title, artists, album]):
            continue

        tracks.append({
            "track_number": number,
            "title": title,
            "artist": ", ".join(artists) if artists else None,
            "album": album,
        })

    return tracks


def load_existing_tracks(path):
    if not path.exists():
        return []

    try:
        existing_data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"El archivo existente no es un JSON válido: {path}\n{exc}")

    if not isinstance(existing_data, dict):
        raise SystemExit(f"El archivo existente debe contener un objeto JSON con una clave 'tracks': {path}")

    tracks = existing_data.get("tracks")
    if tracks is None:
        return []
    if not isinstance(tracks, list):
        raise SystemExit(f"La clave 'tracks' debe ser una lista en {path}")

    return tracks


def main():
    default_output = Path(__file__).resolve().parent.parent / "tracks.json"

    parser = argparse.ArgumentParser(
        description="Extrae canciones de un HTML de Spotify y genera un JSON de salida."
    )
    parser.add_argument(
        "html_file",
        nargs="?",
        default="08 - 84.html",
        help="Ruta del archivo HTML de Spotify a procesar.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(default_output),
        help="Ruta del archivo JSON de salida.",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Imprime el JSON generado en pantalla además de guardarlo.",
    )
    args = parser.parse_args()

    html_path = Path(args.html_file)
    if not html_path.exists():
        raise SystemExit(f"Archivo no encontrado: {html_path}")

    html_content = html_path.read_text(encoding="utf-8")
    new_tracks = parse_spotify_track_html(html_content)

    output_path = Path(args.output)
    if output_path.exists():
        existing_tracks = load_existing_tracks(output_path)
    else:
        existing_tracks = []

    existing_keys = {
        (
            (track.get("title") or "").strip().lower(),
            (track.get("artist") or "").strip().lower(),
        )
        for track in existing_tracks
    }

    appended_tracks = []
    for track in new_tracks:
        key = (
            (track.get("title") or "").strip().lower(),
            (track.get("artist") or "").strip().lower(),
        )
        if key not in existing_keys:
            existing_keys.add(key)
            appended_tracks.append(track)

    final_tracks = existing_tracks + appended_tracks
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"tracks": final_tracks}, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.print:
        print(json.dumps({"tracks": final_tracks}, ensure_ascii=False, indent=2))

    print(
        f"Guardado {len(appended_tracks)} canciones nuevas ({len(final_tracks)} en total) en {output_path}"
    )


if __name__ == "__main__":
    main()
