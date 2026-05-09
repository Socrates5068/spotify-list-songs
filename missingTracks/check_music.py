import json
import os
import sys

# Default configuration
INPUT_JSON_FILE = "../tracks.json"
OUTPUT_JSON_FILE = "missing_tracks.json"

def normalize_name(text):
    """Removes non-alphanumeric characters to simplify comparison"""
    return "".join(filter(str.isalnum, str(text))).lower()

def generate_missing_tracks_list(target_directory):
    # 1. Load the JSON file
    if not os.path.exists(INPUT_JSON_FILE):
        print(f"Error: {INPUT_JSON_FILE} not found in current directory.")
        return

    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        playlist = data.get('tracks', [])

    # 2. Scan local files in the provided directory
    if not os.path.exists(target_directory):
        print(f"Error: The directory '{target_directory}' is not accessible.")
        return

    print(f"Scanning directory: {target_directory}")
    
    # Create a list of normalized local filenames
    local_files = [normalize_name(os.path.splitext(f)[0]) 
                   for f in os.listdir(target_directory) 
                   if f.lower().endswith(".mp3")]

    # 3. Compare and find missing tracks
    missing_tracks = []
    
    for track in playlist:
        title = track.get('title', '')
        artist = track.get('artist', '')
        
        # Search variants
        v1 = normalize_name(f"{artist}{title}")  # ArtistTitle
        v2 = normalize_name(f"{title}{artist}")  # TitleArtist
        v3 = normalize_name(title)                # Title only

        found = False
        for local_name in local_files:
            if v1 in local_name or v2 in local_name or v3 in local_name:
                found = True
                break
        
        if not found:
            missing_tracks.append(track)

    # 4. Save results
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump({"missing_tracks": missing_tracks}, f, indent=4, ensure_ascii=False)

    print(f"\nAnalysis completed:")
    print(f"- Total in JSON: {len(playlist)}")
    print(f"- Total files found on disk: {len(local_files)}")
    print(f"- Missing tracks identified: {len(missing_tracks)}")
    print(f"Result saved to: {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    # Check if the directory argument was provided
    if len(sys.argv) > 1:
        directory_argument = sys.argv[1]
        generate_missing_tracks_list(directory_argument)
    else:
        print("Usage: python check_music.py \"C:\\Path\\To\\Music\"")
        # Optional: you can set a fallback path here if no argument is given
        # generate_missing_tracks_list(r"E:\Music\Spotify\misc")