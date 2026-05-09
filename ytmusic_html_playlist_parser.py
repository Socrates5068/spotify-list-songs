import argparse
import json
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit(
        "BeautifulSoup4 no está instalado. Instala con: python -m pip install beautifulsoup4"
    )


def parse_ytmusic_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    tracks = []

    rows = soup.select("ytmusic-responsive-list-item-renderer")
    if not rows:
        rows = soup.select("div.ytmusic-responsive-list-item-renderer")

    for index, row in enumerate(rows, start=1):
        title_el = row.select_one("yt-formatted-string.title, ytmusic-formatted-string.title")
        title = None
        if title_el:
            title = title_el.get_text(strip=True)

        secondary_links = row.select(
            "div.secondary-flex-columns .flex-column yt-formatted-string a, div.secondary-flex-columns .flex-column a"
        )
        artist = None
        album = None
        if secondary_links:
            artist = secondary_links[0].get_text(strip=True)
            if len(secondary_links) > 1:
                album = secondary_links[1].get_text(strip=True)

        if not any([title, artist, album]):
            continue

        tracks.append({
            "track_number": str(index),
            "title": title,
            "artist": artist,
            "album": album,
        })

    return tracks


def main():
    parser = argparse.ArgumentParser(
        description="Extrae canciones de un HTML de YouTube Music y genera un JSON con formato de playlist."
    )
    parser.add_argument(
        "html_file",
        nargs="?",
        default="ytmusic.html",
        help="Ruta del archivo HTML de YouTube Music a procesar.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="ytmusic_tracks.json",
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
    tracks = parse_ytmusic_html(html_content)

    output_data = {"tracks": tracks}
    output_path = Path(args.output)
    output_path.write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.print:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))

    print(f"Guardado {len(tracks)} canciones en {output_path}")


if __name__ == "__main__":
    main()
