import os
import time
import csv
import datetime
import requests
import dotenv
from shazamio import Shazam

dotenv.load_dotenv()

# --- CONSTANTS ---
STREAM_URL = os.getenv("STREAM_URL")
STATION_NAME = os.getenv("STATION_NAME")
AUDD_API_TOKEN = os.getenv("AUDD_API_TOKEN")


async def identify_song(file_path: str):
    shazam = Shazam()
    """Send file to Audd.io for recognition"""
    try:
        out = await shazam.recognize_song(file_path)
        if 'track' in out:
            track_info = out['track']
            return {
                "title": track_info.get("title"),
                "artist": track_info.get("subtitle"),
                "url": track_info.get("url")
            }
    except Exception as e:
        print("Error identifying song:", e)
        return None
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

