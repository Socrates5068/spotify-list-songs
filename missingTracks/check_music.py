import json
import os
import re
import sys
import unicodedata

INPUT_JSON_FILE = "../tracks.json"
OUTPUT_JSON_FILE = "missing_tracks.json"

def normalize_name(text):
    if text is None: return ""
    normalized = unicodedata.normalize('NFKD', str(text))
    without_accents = ''.join(c for c in normalized if not unicodedata.combining(c))
    return ''.join(filter(str.isalnum, without_accents)).lower()

def clean_extra_info(text):
    if text is None: return ""
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    return normalize_name(text)

def split_artist_names(text):
    if text is None: return []
    s = re.sub(r'\s{2,}', ',', str(text)).lower()
    patterns = [
        r'\(?feat(?:uring)?\.?\s?', r'\(?ft\.?\s?', r'\sa dueto con\s', 
        r'\swith\s', r'\sand\s', r'\sy\s', r'\scon\s', r'\svs\.?\s'
    ]
    for pattern in patterns:
        s = re.sub(pattern, ',', s)
    s = re.sub(r'[()&+/|;]', ',', s) 
    parts = [part.strip() for part in re.split(r',+', s) if part.strip()]
    return [normalize_name(part) for part in parts if normalize_name(part)]

def parse_mp3_filename(filename):
    full_name = os.path.splitext(filename)[0].strip()
    if " - " in full_name:
        parts = full_name.split(' - ', 1)
        return parts[0].strip(), parts[1].strip(), full_name
    parts = full_name.split('-', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip(), full_name
    return '', full_name, full_name

def generate_missing_tracks_list(target_directory):
    # Initial validations
    if not os.path.exists(INPUT_JSON_FILE):
        print(f"[ERROR] File not found: {INPUT_JSON_FILE}")
        return

    if not os.path.exists(target_directory):
        print(f"[ERROR] Directory not accessible: {target_directory}")
        return

    # 1. Load JSON
    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        playlist = data.get('tracks', [])

    # 2. Scan folder
    all_files = os.listdir(target_directory)
    mp3_files = [f for f in all_files if f.lower().endswith('.mp3')]
    local_data = [parse_mp3_filename(f) for f in mp3_files]

    print(f"[INFO] Starting analysis...")
    print(f"[INFO] Songs in JSON: {len(playlist)}")
    print(f"[INFO] MP3 files in folder: {len(mp3_files)}")
    print("-" * 50)

    missing_tracks = []
    found_count = 0

    # 3. Comparison with Logs
    for track in playlist:
        json_title = track.get('title', '')
        json_artist = track.get('artist', '')
        json_album = track.get('album', '')

        norm_json_title = clean_extra_info(json_title)
        json_artist_tokens = split_artist_names(json_artist)
        norm_json_album = normalize_name(json_album)

        found = False
        for mp3_artist, mp3_title, full_filename in local_data:
            # A. Full Match
            norm_full_filename = normalize_name(full_filename)
            if norm_json_title == norm_full_filename or norm_json_title in norm_full_filename:
                found = True
                break

            # B. Title Match
            norm_mp3_title = clean_extra_info(mp3_title)
            if norm_json_title not in norm_mp3_title and norm_mp3_title not in norm_json_title:
                continue

            # C. Artist/Album Match
            mp3_artist_tokens = split_artist_names(mp3_artist) + split_artist_names(mp3_title)

            # Artists
            for j_token in json_artist_tokens:
                for m_token in mp3_artist_tokens:
                    if j_token in m_token or m_token in j_token:
                        found = True
                        break
                if found: break

            # Album fallback
            if not found and norm_json_album:
                for m_token in mp3_artist_tokens:
                    if m_token in norm_json_album or norm_json_album in m_token:
                        found = True
                        break

            if found: break

        if found:
            found_count += 1
        else:
            missing_tracks.append(track)

    # 4. Save and Summary
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump({"missing_tracks": missing_tracks}, f, indent=4, ensure_ascii=False)

    print("-" * 50)
    print(f"[FINAL RESULT]")
    print(f"Total songs in JSON:  {len(playlist)}")
    print(f"Total files in folder: {len(mp3_files)}")
    print(f"Songs found:     {found_count}")
    print(f"Missing songs:       {len(missing_tracks)}")
    print(f"Missing list saved in: {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_missing_tracks_list(sys.argv[1])
    else:
        print("Usage: python script.py \"Path/To/Your/Music\"")