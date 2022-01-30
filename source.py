import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date, datetime, timedelta
import pandas as pd

load_dotenv()

cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred, {
    'projectId': os.environ['GCP_PROJECT_ID']
})

db = firestore.client()

doc_ref = db.collection('users').document(os.environ['USER'])

artist_uris = doc_ref.get(field_paths = ['artists_uri']).to_dict()["artists_uri"]

spotify_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(cache_handler=spotipy.MemoryCacheHandler()))

# Calculate the date cut off - 7 days from before. This could be modified to be more variable
date_cutoff = date.today() - timedelta(days = 7)

recent_album_df = pd.DataFrame(columns = ["name", "artist", "release_date"])

for artist_uri in artist_uris:
    # Get list of albums 
    album_list = spotify_client.artist_albums(artist_uri, album_type = "album")["items"]

    # Check if artist has any albums
    if len(album_list) != 0:
        # Get latest album
        latest_album = album_list[0]
        # Need to extract a release date. How this is done depends on the release date precision
        if latest_album["release_date_precision"] == "day" :
            # If we've got precision to a single day, extract in ISO format (yyyy-mm-dd)
            album_release_date = date.fromisoformat(latest_album["release_date"])
        if latest_album["release_date_precision"] == "month":
            # If its to months, extract in the form yyyy-mm
            album_release_date = datetime.strptime(latest_album["release_date"], "%Y-%m").date()
        if latest_album["release_date_precision"] == "year":
            # If only to year, extract in the form yyyy
            album_release_date = datetime.strptime(latest_album["release_date"], "%Y").date()

        # Check if the album was released since the predefined date cut off
        if album_release_date >= date_cutoff:
            # Get the album name
            album_name = latest_album["name"]
            # Get the artist
            album_artist = latest_album["artists"][0]["name"]
            # Create a row to append in the form of a data frame
            album_to_append_df = pd.DataFrame(
                [[album_name, album_artist, album_release_date]],
                columns = ["name", "artist", "release_date"])
            # Append the row to the maste dataframe
            recent_album_df = recent_album_df.append(album_to_append_df)
            # Save album

print(recent_album_df)