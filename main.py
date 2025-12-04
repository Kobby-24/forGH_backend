# app/main.py
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
from database import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
import models
from utils import scan_station
from routers import stations, users
import asyncio


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

def scan_all_stations():
    """Fetches all station IDs and runs the scanner for each concurrently."""
    print("--- Starting concurrent scheduled scan ---")
    db = SessionLocal()
    try:
        station_ids = [s.id for s in db.query(models.Stations.id).all()]

        if not station_ids:
            print("No stations found in the database. Add a station to begin scanning.")
            return
        async def run_all():
            # run scan_station concurrently as coroutines
            await asyncio.gather(*(scan_station.scan_station(sid) for sid in station_ids))

        # create a fresh event loop and run all scan coroutines
        asyncio.run(run_all())

    finally:
        #log scan completion
        
        db.close()

    print("--- Concurrent scheduled scan finished ---")


@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the job to run every 60 seconds
    scheduler.add_job(scan_all_stations, "interval", seconds=60)
    scheduler.start()
    print("Scheduler started. First scan will run shortly.")


@app.get("/")
def read_root():
    return {"message": "Radio Scanner API is running."}
