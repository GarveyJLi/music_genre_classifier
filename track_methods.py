import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests

class MusicClassifier:

    client_credentials_manager = None
    sp = None
    total_genres = set()
    reduced_genres = {}
    playist_track_info = []
    playlist_df = None
    

    def __init__(self, client_id, client_secret):
        client_credentials_manager \
            = SpotifyClientCredentials(client_id=client_id, \
                client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager \
            = client_credentials_manager)

    
    def get_all_tracks(self, user_id, playlist_url):
        results = self.sp.user_playlist_tracks(user_id, playlist_url)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks

    def get_track_uri(track):
        return track['track']['uri']

    def get_usable_track(self, track_uri):
        return self.sp.track(track_uri)

    def get_track_name(usable_track):
        return usable_track['name']

    def get_track_artists(usable_track):
        return [usable_track['artists'][i]['name'] 
                for i in range(len(usable_track['artists']))]

    def get_track_artists_ids(usable_track):
        return [usable_track['artists'][i]['uri'] 
                for i in range(len(usable_track['artists']))]
            
    def get_artist_genres(self, artist_id):
        return self.sp.artist(artist_id)['genres']

    def get_lyric_url(artists, track_name):
        return ('https://genius.com/' + ' and '.join(artists) \
                + track_name + ' lyrics').replace(' ', '-')

    def get_lyrics(lyric_url):
        lyrics = ''
        genius_html = requests.get(lyric_url)
        soup = BeautifulSoup(genius_html, 'lxml')

        return lyrics
        
    

    def create_playlist_track_info(self, track_list):
        for track in track_list:
            track_uri=self.get_track_uri(track)
            usable_track=self.get_usable_track(track_uri)

            track_features = {}
            track_name = self.get_track_name(usable_track)
            track_features['name'] = track_name
            artists = self.get_track_artists(usable_track)
            track_features['artist(s)'] = artists

            lyric_url = self.get_lyric_url(artists, track_name)
            track_lyrics = self.get_lyrics(lyric_url)
            

            artist_ids = self.get_track_artists_ids(usable_track)
            genres = [self.get_artist_genres(artist) for artist in artist_ids]
            track_features['genres'] = genres
            [self.total_genres.update(genre) for genre in genres]

            self.playist_track_info.append(track_features)

        for genre in self.total_genres:
            if ' ' not in genre or genre == "hip hop":
                self.reduced_genres[genre] = []

        for genre in self.total_genres:
            base_genre = genre
            if ' ' in genre:
                for key in self.reduced_genres.keys():
                    if key in genre:
                        base_genre = key
            if base_genre not in self.reduced_genres:
                self.reduced_genres[base_genre] = []
            else:
                self.reduced_genres[base_genre].append(genre)
        
        self.playlist_df = pd.DataFrame.from_dict(self.playist_track_info)

    
