import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from client_info import cid, cs as secret
import pandas as pd

#Authentication - without user
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#>=500 million plays 
#https://open.spotify.com/playlist/2YRe7HRKNRvXdJBp9nXFza?si=\198755290d2c4102

mil_playlist_url = 'https://open.spotify.com/playlist/2YRe7HRKNRvXdJBp9nXFza?si=\198755290d2c4102'

song_list = sp.playlist(mil_playlist_url)

print(song_list['items'])








