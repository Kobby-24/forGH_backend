from sqlalchemy.orm import Session
import models


def get_or_create_artist(db: Session, artist_name: str):
    """Finds an artist by name or creates a new one if not found."""
    # A simple classification for demonstration
    ghanaian_artists = {"Sarkodie", "Stonebwoy", "Shatta Wale", "King Promise", "Efya", "Kuami Eugene"}
    
    artist = db.query(models.Artists).filter(models.Artists.name == artist_name).first()
    if not artist:
        origin = "Ghanaian" if artist_name.strip().title() in ghanaian_artists else "Foreign"
        artist = models.Artists(name=artist_name, origin=origin)
        db.add(artist)
        db.commit()
        db.refresh(artist)
    return artist