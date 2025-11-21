from sqlalchemy.orm import Session
import os
import models
from .record_stream import record_stream
from .identify_song import identify_song
from .log_result import log_song_play
from database import SessionLocal


def scan_station(station_id: int):
    """Runs the full scan-and-log process for a single station id."""
    # get_db() in `database.py` is a FastAPI dependency generator (it yields a session)
    # here we need a real Session instance for standalone/background use, so create one
    db = SessionLocal()
    try:
        # SQLAlchemy 1.4+ supports Session.get
        station = None
        try:
            station = db.get(models.Stations, station_id)
        except Exception:
            # fallback for older APIs
            station = (
                db.query(models.Stations)
                .filter(models.Stations.id == station_id)
                .first()
            )

        if not station:
            print(f"Station with id={station_id} not found.")
            return

        print(f"Recording from {station.name}...")
        file_path = record_stream(station_name=station.name, stream_url=station.url)

        if (
            not file_path
            or not os.path.exists(file_path)
            or os.path.getsize(file_path) == 0
        ):
            print("Recording failed or created an empty file.")
            return

        print("Identifying song...")
        song_info = identify_song(file_path)
        print("Song info received:", song_info)

        if song_info:
            title = song_info.get("title", "Unknown Title")
            artist = song_info.get("artist", "Unknown Artist")
            log_song_play(db, station, title, artist)
        else:
            print("No song detected.")
    finally:
        db.close()
