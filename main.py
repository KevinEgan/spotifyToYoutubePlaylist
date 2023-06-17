import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# enter your details here
CLIENT_ID = ""
CLIENT_SECRET = ""
YT_KEY = ""

song_ids = []

# take in user input
usr_playlist = input("Enter a playlist ID: ")
yt_playlist = input("What would you like to call the youtube playlist?: ")

# proceed once user's date is valid


# authorisation step
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                                    redirect_uri="http://example.com",
                                                    scope="playlist-modify-public user-library-modify",
                                                    show_dialog=True, cache_path="token.txt"
                                                    ))

user_id = spotify.current_user()["id"]
playlist_songs = spotify.playlist_tracks(playlist_id=usr_playlist,
                                         fields="items(track(name,artists(name)))", limit=50)

# pp = pprint.PrettyPrinter(indent=1)
# pp.pprint(playlist_songs)


song_artist_dict = {
    item['track']['name']: item['track']['artists'][0]['name'] for item in playlist_songs['items']
}

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret_16457444419-vr3hrg32sn1htlqmgmhe05nj5idck8ac.apps.googleusercontent.com.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)


credentials = flow.run_local_server()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)


def create_playlist(playlist_title=yt_playlist):
    request = youtube.playlists().insert(
        part="snippet,id",
        body={
            "snippet": {
                "title": playlist_title
            }
        }
    )
    response = request.execute()
    playlist_id = response['id']
    # print(response)
    return playlist_id


def gather_song_ids(song, artist):
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=f"{song} {artist}"
    )
    response = request.execute()
    song_id = response['items'][0]['id']['videoId']
    song_ids.append(song_id)


def add_songs_to_playlist(video_id, playlist_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
    )
    response = request.execute()

    # print(response)


playlist_id = create_playlist()
for song, artist in song_artist_dict.items():
    gather_song_ids(song, artist)

for song_id in song_ids:
    add_songs_to_playlist(video_id=song_id, playlist_id=playlist_id)


