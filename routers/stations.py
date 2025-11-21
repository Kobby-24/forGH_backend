from fastapi import APIRouter
from utils.stations import get_station_export, get_all_stations, create_station
from schemas import Station


router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)

@router.get("/{station_id}/export")
def station_export(station_id: int):
    return get_station_export(station_id)

@router.get("/")
def all_stations():
    return get_all_stations()

@router.post("/")
def add_station(station: Station):
    return create_station(station)
