from sqlalchemy.orm import Session
import models
import requests



def get_or_create_artist(db: Session, artist_name: str):
    """Finds an artist by name or creates a new one if not found."""
    artist = db.query(models.Artists).filter(models.Artists.name == artist_name).first()
    if not artist:
        # Query TheAudioDB API for artist info
        url = f"https://www.theaudiodb.com/api/v1/json/2/search.php?s={artist_name}"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            country_code = None
            if data and data.get("artists") and data["artists"][0].get("strCountryCode"):
                country_code = data["artists"][0]["strCountryCode"]
            origin = "Local" if country_code == "GH" else "Foreign"
        except Exception:
            origin = "Foreign"  # fallback if API fails
        artist = models.Artists(name=artist_name, origin=origin)
        db.add(artist)
        db.commit()
        db.refresh(artist)
    return artist