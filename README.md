# Spotify Playlist Extractor

Set your environment variables and run the script:

```powershell
$env:SPOTIPY_CLIENT_ID="tu_client_id"
$env:SPOTIPY_CLIENT_SECRET="tu_client_secret"
$env:SPOTIPY_REDIRECT_URI=""
$env:SPOTIPY_PLAYLIST_ID=""
python playlistExtrator.py
```
Example:
```json
{
  "tracks": [
    {
      "track_number": "523",
      "title": "Blackbird - Remastered 2009",
      "artist": "The Beatles",
      "album": "The Beatles (Remastered)"
    }
    ...
```


