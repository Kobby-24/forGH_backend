from fastapi import APIRouter
from utils.stations import get_station_export, get_all_stations, create_station, stations_list, dashboard_stations_summary, get_station_history
from schemas import Station


router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)

@router.get("/{station_id}")
def station_export(station_id: int):
    return get_station_export(station_id)

@router.get("/{station_id}/history/{period}")
def station_history(station_id: int, period: str):
    return get_station_history(station_id, period)

@router.get("/")
def all_stations():
    return get_all_stations()

@router.post("/")
def add_station(station: Station):
    return create_station(station)

@router.get("/list")
def get_stations_list():
    return stations_list()

@router.get("/dashboard/summary")
def get_dashboard_stations_summary():
    return dashboard_stations_summary()