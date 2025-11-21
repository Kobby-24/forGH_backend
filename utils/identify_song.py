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


def identify_song(file_path: str):
    """Send file to Audd.io for recognition"""
    try:
        with open(file_path, "rb") as f:
            data = {"api_token": AUDD_API_TOKEN, "return": "spotify,timecode"}
            files = {"file": f}
            result = requests.post("https://api.audd.io/", data=data, files=files)
            response = result.json()
            print("Audd.io response:", response)
            return response.get("result")
    except Exception as e:
        print("Error identifying song:", e)
        return None
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

