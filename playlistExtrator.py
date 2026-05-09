import argparse
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Cargar credenciales desde variables de entorno
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

if not client_id or not client_secret:
    raise SystemExit(
        "Faltan credenciales de Spotify. Define SPOTIPY_CLIENT_ID y SPOTIPY_CLIENT_SECRET."
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Exporta una playlist de Spotify a JSON usando credenciales de entorno.")
    parser.add_argument(
        "playlist_id",
        nargs="?",
        default=os.getenv("SPOTIPY_PLAYLIST_ID"),
        help="ID de la playlist de Spotify. Si no se pasa, se usa SPOTIPY_PLAYLIST_ID.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=os.getenv("SPOTIPY_OUTPUT_FILE", "playlist_misc.json"),
        help="Archivo JSON de salida.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    playlist_id = args.playlist_id
    if not playlist_id:
        raise SystemExit(
            "Falta el ID de la playlist. Define SPOTIPY_PLAYLIST_ID o pásalo como argumento."
        )

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-read-private"
    ))

    results = sp.playlist_items(playlist_id, additional_types=["track"])
    tracks = []

    while results:
        for item in results["items"]:
            track = item.get("track")
            if track:
                tracks.append({
                    "id": track.get("id"),
                    "title": track.get("name"),
                    "artist": ", ".join([artist.get("name") for artist in track.get("artists", []) if artist.get("name")]),
                    "album": track.get("album", {}).get("name"),
                    "duration_ms": track.get("duration_ms"),
                })
        if results.get("next"):
            results = sp.next(results)
        else:
            results = None

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(tracks, f, ensure_ascii=False, indent=2)

    print(f"Exportadas {len(tracks)} canciones a {args.output}")


if __name__ == "__main__":
    main()
