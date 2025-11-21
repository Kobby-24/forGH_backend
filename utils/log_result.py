from sqlalchemy.orm import Session
import models
import datetime
from .artists import get_or_create_artist


def log_song_play(db: Session, station: models.Stations, title: str, artist_name: str):
    """Saves the identified song to the song_plays table."""
    artist = get_or_create_artist(db, artist_name)
    
    new_play = models.SongPlays(
        station_id=station.id,
        artist_id=artist.id,
        title=title,
        played_at=datetime.datetime.utcnow()
    )
    db.add(new_play)
    db.commit()
    print(f"Logged: {title} by {artist.name} ({artist.origin}) on {station.name}")