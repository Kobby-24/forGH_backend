# app/main.py
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
from database import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
import models
from utils import scan_station
from routers import stations, users



app = FastAPI()

origin = [
    "http://localhost:3000",
    "https://radio-frontend-two.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stations.router)
app.include_router(users.router)

# def scan_all_stations():
#     """Fetches all station IDs and runs the scanner for each concurrently."""
#     print("--- Starting concurrent scheduled scan ---")
#     db = SessionLocal()
#     try:
#         # We only need the station IDs to pass to the threads
#         station_ids = [s.id for s in db.query(models.Stations.id).all()]

#         if not station_ids:
#             print("No stations found in the database. Add a station to begin scanning.")
#             return

#         # Use a ThreadPoolExecutor to run scans for all stations at the same time
#         with ThreadPoolExecutor(max_workers=len(station_ids)) as executor:
#             print(station_ids)
#             # executor.map will call scan_station.scan_station for each id in station_ids
#             executor.map(scan_station.scan_station, station_ids)

#     finally:
#         db.close()
#     print("--- Concurrent scheduled scan finished ---")


# @app.on_event("startup")
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     # Schedule the job to run every 60 seconds
#     scheduler.add_job(scan_all_stations, "interval", seconds=60)
#     scheduler.start()
#     print("Scheduler started. First scan will run shortly.")


@app.get("/")
def read_root():
    return {"message": "Radio Scanner API is running."}
