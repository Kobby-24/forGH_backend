import os
import time
import csv
import datetime
import requests
import dotenv

dotenv.load_dotenv()

# --- CONSTANTS ---
STREAM_URL = os.getenv("STREAM_URL")
STATION_NAME = os.getenv("STATION_NAME")
AUDD_API_TOKEN = os.getenv("AUDD_API_TOKEN")
ghanaian_artists = os.getenv("GHANAIAN_ARTISTS_FILE").split(",")



def classify_song(artist):
    """Classify song as Local or Foreign"""
    if artist and artist.strip().title() in ghanaian_artists:
        return "Local"
    return "Foreign"