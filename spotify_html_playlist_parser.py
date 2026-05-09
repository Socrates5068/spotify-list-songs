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


def main():
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
        default="tracks.json",
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
    tracks = parse_spotify_track_html(html_content)

    output_data = {"tracks": tracks}
    output_path = Path(args.output)
    output_path.write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.print:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))

    print(f"Guardado {len(tracks)} canciones en {output_path}")


if __name__ == "__main__":
    main()
