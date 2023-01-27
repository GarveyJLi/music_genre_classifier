import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from lyricsgenius import Genius
import requests


class MusicClassifier:

    #Class Attributes
    __client_credentials_manager = None
    __genius = None
    sp = None
    total_genres = set()
    reduced_genres = {}
    playist_track_info = []
    playlist_df = None
    
    
    def __init__(self, SPOTIFY_CID, SPOTIFY_CS, \
        GENIUS_CID, GENIUS_CS, GENIUS_TOKEN):
        """
        Initializer for MusicClassifier. 

        Parameters:
            SPOTIFY_CLIENT_ID (str): User Spotify API client id
            SPOTIFY_CLIENT_SECRET (str): User Sporify API client secret
            GENIUS_CID (str): User LyricsGenius API client id
            GENIUS_CS (str): User LyricsGenius API client secret
            GENIUS_TOKEN (str): User LyricsGenius Access Token
        """
        
        self.__client_credentials_manager \
            = SpotifyClientCredentials(client_id=SPOTIFY_CID, \
                client_secret=SPOTIFY_CS)
        self.sp = spotipy.Spotify(client_credentials_manager \
            = self.__client_credentials_manager)
        self.__genius = Genius(GENIUS_TOKEN)

    def get_track_list(self, playlist_url):
        """
        Creates and returns a list of tracks with all of the songs from a 
        Spotify playlist

        Parameters:
            playlist_url (str): Spotify playlist url
        """
        results = self.sp.user_playlist_tracks(self.__client_credentials_manager, playlist_url)
        tracks = results['items']
        #Had to do this to get all songs, otherwise would only get first 100(?)
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks

    def get_track_uri(track):
        """
        Returns a tracks uri as a string

        Parameters:
            track (dict): Track information from Spotify as a dictionary

        """
        return track['track']['uri']

    def get_usable_track(self, track_uri):
        """
        Returns a single track's information as a dictionary

        Parameters:
            track_uri (str): A Spotify track's uri

        """
        return self.sp.track(track_uri)

    def get_track_name(usable_track):
        """
        Returns a tracks name as a string

        Parameters:
            usable_track (dict): A single Spotify track's information
        """
        return usable_track['name']

    def get_track_artists(usable_track):
        """
        Returns a list of a track's artist(s)

        Parameters:
            usable_track (dict): A single Spotify track's information

        """
        return [usable_track['artists'][i]['name'] 
                for i in range(len(usable_track['artists']))]

    def get_track_artists_ids(usable_track):
        """
        Returns a list of ids for a track's artist(s)

        Parameters:
            usable_track (dict): A single Spotify track's information
        """
        return [usable_track['artists'][i]['uri'] 
                for i in range(len(usable_track['artists']))]
            
    def get_artist_genres(self, artist_id):
        """
        Returns a list of genres associated with an artist

        Parameters:
            artist_id (str): Artist's id
        """
        return self.sp.artist(artist_id)['genres']

    def get_lyric_url(artists, track_name):
        """
        Returns the url for a webpage containing lyrics for a track as a string

        Parameters:
            artists (list): ALL artists listed on the track on Spotify
            track_name (str): Track name (As is on Spotify)
        """
        return ('https://genius.com/' + ' and '.join(artists) \
                + track_name + ' lyrics').replace(' ', '-')

    def get_lyrics(self, track_name, artist_name):
        """
        Returns a string containing the lyrics of a track

        Parameters:
            track_name (str): Name of the track
            artist_name (str): Name of the track's artist 
                (or the first artist that is listed)

        Returns: A string containing the lyrics of a track

        """
        #Used LyricsGenius API to get lyrics instead of webscraping the website
        #because (1)the html retrieved by BS4 was before the page fully loaded
        #and (2)might get flagged for requesting too many songs
        return self.__genius.search_song(track_name, artist_name)     

    def get_playlist_df(self):
        """
        Returns the input playlists information as a pandas dataframe

        Returns: Pandas df with playlist info
        """
        return self.playlist_df if self.playlist_df != None \
            else "Please run create_playlist_track_info() first!"

    def genre_reduce(self, total_genres, reduced_genres):
        """
        Groups together genres from a set into a dictionary

        Parameters: 
            total_genres (set): A comprehensive list of all genres from the 
                input playlist
            reduced_genres(dict): A dictionary of genres condensed from 
                total_genres
        """
        for genre in total_genres:
            if ' ' not in genre: #or genre == "hip hop"
                reduced_genres[genre] = []

        for genre in total_genres:
            base_genre = genre
            if ' ' in genre:
                for key in reduced_genres.keys():
                    if key in genre:
                        base_genre = key
            if base_genre not in reduced_genres:
                reduced_genres[base_genre] = []
            else:
                reduced_genres[base_genre].append(genre) 
    

    def create_playlist_track_info(self, track_list):
        """
        Takes a list of track information and returns a more condensed 
        dictionary of data that can be analyzed.

        Parameters:
            track_list (list): List of track information

        Returns: 
            track_features (list): List of track data that can be analyzed
        """
        for track in track_list:
            track_uri=self.get_track_uri(track)
            usable_track=self.get_usable_track(track_uri)

            track_features = {}
            track_name = self.get_track_name(usable_track)
            track_features['name'] = track_name
            artists = self.get_track_artists(usable_track)
            track_features['artist(s)'] = artists

            #lyric_url = self.get_lyric_url(artists, track_name)
            track_lyrics = self.get_lyrics(track_name, artists[0])
            

            artist_ids = self.get_track_artists_ids(usable_track)
            genres = [self.get_artist_genres(artist) for artist in artist_ids]
            track_features['genres'] = genres
            track_features['lyrics'] = track_lyrics
            [self.total_genres.update(genre) for genre in genres]

            self.playist_track_info.append(track_features)

        self.genre_reduce(self.total_genres, self.reduced_genres)
        self.playlist_df = pd.DataFrame.from_dict(self.playist_track_info)

        return track_features

    
