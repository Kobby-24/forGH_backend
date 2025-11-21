import os
import datetime




# --- FUNCTIONS ---

def record_stream(station_name: str, stream_url: str, duration: int = 30):
    """Record audio snippet from radio stream"""
    filename = f"recordings/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    os.system(f'ffmpeg -y -i "{stream_url}" -t {duration} -acodec copy {filename}')
    return filename