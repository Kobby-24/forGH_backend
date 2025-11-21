import os

import time

import csv

import datetime

import requests



# --- CONFIG ---

AUDD_API_TOKEN = "a694da5f14eb71f2906fcf81082df988"  # Replace with your key

STREAM_URL = "https://mmg.streamguys1.com/HitzFM-mp3?aw_0_req.gdpr=true?us_privacy=1YYN"

STATION_NAME = "Hitz FM"

ghanaian_artists = {"Sarkodie", "Stonebwoy", "Shatta Wale", "King Promise", "Efya", "Kuami Eugene"}


# --- FUNCTIONS ---



def record_stream(duration=30):

    """Record audio snippet from radio stream"""

    filename = f"recordings/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

    os.system(f'ffmpeg -y -i "{STREAM_URL}" -t {duration} -acodec copy {filename}')

    return filename



def identify_song(file_path):

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



def classify_song(artist):

    """Classify song as Local or Foreign"""

    if artist and artist.strip().title() in ghanaian_artists:

        return "Local"

    return "Foreign"



def log_result(station, title, artist, origin):

    """Save to CSV"""

    with open("log.csv", "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([datetime.datetime.now(), station, title, artist, origin])



# --- MAIN LOOP ---

def main():

    while True:

        print("Recording...")

        file = record_stream(duration=30)

        print("Detecting song...")

        song_info = identify_song(file)



        if song_info:

            title = song_info.get("title", "Unknown")

            artist = song_info.get("artist", "Unknown")

            origin = classify_song(artist)

            log_result(STATION_NAME, title, artist, origin)

            print(f"{title} by {artist} → {origin}")

        else:

            print("No song detected.")



        time.sleep(60)  # Wait 1 min before next scan



if __name__ == "__main__":

    main()