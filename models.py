from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Stations(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String, unique=True, index=True)
    base_tax = Column(Float)

class Artists(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    origin = Column(String)

class SongPlays(Base):
    __tablename__ = "song_plays"
    id = Column(Integer, primary_key=True, index=True)
    played_at = Column(DateTime, default=datetime.now)
    title = Column(String)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    artist = relationship("Artists")
    station_id = Column(Integer, ForeignKey("stations.id"))
    station = relationship("Stations")

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    station_id = Column(Integer, ForeignKey("stations.id"))
    station = relationship("Stations")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, default=datetime.now)

class Payments(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    payment_date = Column(DateTime, default=datetime.now)
    method = Column(String)
    status = Column(String)
    foreign_percentage = Column(Float)
    local_percentage = Column(Float)
    user = relationship("Users")

class ScanLogs(Base):
    __tablename__ = "scan_logs"
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"))
    scan_time = Column(DateTime, default=datetime.now)
    status = Column(String)
    station = relationship("Stations")
    