import requests
from spotipy import Spotify, SpotifyOAuth
from bs4 import BeautifulSoup
import datetime
import os
import logging


class SpotifyPlaylistCreator:
    """
    A class to create Spotify playlists based on Billboard Hot 100 charts for a given date.
    """
    
    def __init__(self) -> None:
        """
        Initializes the SpotifyPlaylistCreator with necessary variables.
        """
        
        self.CACHE_ID = ""
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = "https://example.com"
        self.SCOPE = "playlist-modify-private"
        self.music_list = []
        self.track_names = []
        self.artist_names = []
        self.untrimmed_artists = []
        self.uri_tracks = []
        self.playlist_url = ""
        self.playlist_name = ""
        self.playlist_ID = ""


    def get_data(self,users_date):
        """
        Fetches song and artist data from the Billboard Hot 100 chart for a given date.

        Args:
            users_date (str): The date for which the Billboard data is to be fetched, in 'Day.Month.Year' format.
        """
        
        logging.info("Starting get_data")

        # user_date = input("What's the date for the billboard top 100?\nType in the form 'Day Month Year'\n")
        user_date = users_date
        formatted_date = datetime.datetime.strptime(user_date, "%d.%m.%Y")
        user_date = datetime.datetime.strftime(formatted_date, "%Y-%m-%d")
        self.playlist_name = datetime.datetime.strftime(formatted_date, "%d %m %Y")
        
        response = requests.get(f"https://www.billboard.com/charts/hot-100/{user_date}")
        soup = BeautifulSoup(response.text, "html.parser")

        data = soup.find_all("div", class_="o-chart-results-list-row-container")
        x = 1

        for item in data:
            songs = item.find('h3', {'id': 'title-of-a-story'})
            artists = item.find("span",{'class': 'a-font-primary-s'})

            if songs:
                title_text = songs.get_text().strip()
            else:
                title_text = "Couldn't be found"

            if artists:
                artists_text = artists.get_text().strip()
            else:
                artists_text = "Couldn't be found"

            self.music_list.append(f"{x}. {title_text} --- {artists_text}")
            self.track_names.append(title_text)
            trimmed_artist = artists_text.split("Featuring")[0].strip()
            self.artist_names.append(trimmed_artist)
            self.untrimmed_artists.append(artists_text.strip())
            x += 1
        logging.info(f"Fetched data for date: {users_date}")


    def spotipy_auth(self):
        """
        Authenticates with Spotify and creates a playlist with tracks obtained from the Billboard Hot 100 chart.
        """
             
        logging.info("Starting spotipy_auth")
        spoti = SpotifyOAuth(client_id=self.CLIENT_ID,
                             client_secret=self.CLIENT_SECRET,
                             redirect_uri=self.REDIRECT_URI,
                             scope=self.SCOPE)
        access_token_info = spoti.get_cached_token()

        if not access_token_info:
            # Authenticate if no token is found
            access_token_info = spoti.get_access_token()
        elif spoti.is_token_expired(access_token_info):
            # Refresh the token if it's expired
            access_token_info = spoti.refresh_access_token(access_token_info['refresh_token'])
            
        self.CACHE_ID = access_token_info['access_token']

        sp = Spotify(auth=access_token_info['access_token'])
        
        current_user = sp.current_user()
        user_id = current_user['id']

        for x in range(len(self.track_names)):
            artist = sp.search(q=f"track:{self.track_names[x]} artist:{self.artist_names[x]}", type="track")
            try:
                uri = artist['tracks']['items'][0]['uri']
                self.uri_tracks.append(uri)
            except IndexError:
                artist_secondary = sp.search(q=f"{self.track_names[x]} {self.untrimmed_artists[x]}", type="track")
                try:
                    uri_secondary = artist_secondary['tracks']['items'][0]['uri']
                    self.uri_tracks.append(uri_secondary)
                except IndexError:
                    logging.error(f"Could not find track: {self.track_names[x]} by {self.untrimmed_artists[x]}")

        playlist_data = sp.user_playlist_create(user_id, self.playlist_name, public=False)
        # Process the result of the synchronous operation
        playlist_link = playlist_data["external_urls"]["spotify"]
        self.playlist_url = playlist_link
        self.playlist_ID = playlist_data["id"]


    def add_songs(self):
        """
        Adds songs to the Spotify playlist.

        Returns:
            str: The URL of the created Spotify playlist.
        """
        
        logging.info("Starting add_songs")
        for uri in self.uri_tracks:
            body = {"uris": [uri]}
            header = {
                "Authorization": f"Bearer {self.CACHE_ID}",
                "Content-Type": "application/json"
            }
            response = requests.post(url=f"https://api.spotify.com/v1/playlists/{self.playlist_ID}/tracks", json=body, headers=header)
            response_json = response.json()
            if response.status_code not in range(200, 299):
                logging.error(f"Failed to add track URI {uri}: {response_json}")
        return self.playlist_url
