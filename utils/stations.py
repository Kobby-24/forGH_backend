from fastapi import HTTPException
from sqlalchemy import func, case
from datetime import datetime
from typing import List
from database import SessionLocal
import models
from schemas import Station


def create_station(station: Station):
    db = SessionLocal()
    existing_station = (
        db.query(models.Stations)
        .filter(models.Stations.name == station.name)
        .first()
    )
    if existing_station:
        raise HTTPException(status_code=400, detail="Station with this name already exists")
    new_station = models.Stations(
        name=station.name, url=station.url, base_tax=station.base_tax
    )
    db.add(new_station)
    db.commit() 
    db.refresh(new_station)
    return new_station


def format_iso(dt):
    return dt.isoformat() if dt else None



def get_station_export(station_id: int):
    db = SessionLocal()
    try:
        station = db.get(models.Stations, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # Recent contentLog (limit to N latest plays)
        rows = (
            db.query(
                models.SongPlays.played_at,
                models.SongPlays.title,
                models.Artists.name.label("artist"),
                models.Artists.origin,
            )
            .join(models.Artists, models.SongPlays.artist_id == models.Artists.id)
            .filter(models.SongPlays.station_id == station_id)
            .order_by(models.SongPlays.played_at.desc())
            .limit(200)
            .all()
        )
        content_log = [
            {
                "timestamp": format_iso(r.played_at),
                "title": r.title,
                "artist": r.artist,
                "origin": r.origin,
            }
            for r in rows
        ]

        # Monthly historical aggregates (periodId 'YYYY-MM') — Postgres uses to_char
        period_expr = func.to_char(models.SongPlays.played_at, "YYYY-MM").label(
            "periodId"
        )

        period_agg = (
            db.query(
                period_expr,
                func.count().label("total"),
                func.sum(case((models.Artists.origin == "Foreign", 1), else_=0)).label(
                    "foreign_count"
                ),
                func.max(models.SongPlays.played_at).label("paid_on_candidate"),
            )
            .join(models.Artists, models.SongPlays.artist_id == models.Artists.id)
            .filter(models.SongPlays.station_id == station_id)
            .group_by(period_expr)
            .order_by(period_expr.desc())
            .all()
        )

        historical = []
        for p in period_agg:
            total = p.total or 0
            foreign = p.foreign_count or 0
            foreign_pct = (foreign / total * 100) if total else 0.0

            # example business logic for surcharge/totalTax (replace with your rules)
            surcharge = round(max(0, (foreign_pct - 30.0) * 10.0), 2)  # placeholder
            total_tax = float(station.base_tax or 0) + surcharge

            # fetch full contentLog for this period
            period_start = f"{p.periodId}-01"
            rows_period = (
                db.query(
                    models.SongPlays.played_at,
                    models.SongPlays.title,
                    models.Artists.name.label("artist"),
                    models.Artists.origin,
                )
                .join(models.Artists)
                .filter(models.SongPlays.station_id == station_id)
                .filter(
                    func.to_char(models.SongPlays.played_at, "YYYY-MM") == p.periodId
                )
                .order_by(models.SongPlays.played_at)
                .all()
            )
            content_period = [
                {
                    "timestamp": format_iso(r.played_at),
                    "title": r.title,
                    "artist": r.artist,
                    "origin": r.origin,
                }
                for r in rows_period
            ]

            historical.append(
                {
                    "period": datetime.strptime(
                        p.periodId + "-01", "%Y-%m-%d"
                    ).strftime("%B %Y"),
                    "periodId": p.periodId,
                    "status": "Paid" if p.paid_on_candidate else "Due",  # example
                    "summary": {
                        "foreignPercentage": round(foreign_pct, 2),
                        "surcharge": surcharge,
                        "totalTax": total_tax,
                        "paidOn": (
                            format_iso(p.paid_on_candidate)
                            if p.paid_on_candidate
                            else None
                        ),
                    },
                    "contentLog": content_period,
                }
            )

        response = {
            "id": station.id,
            "name": station.name,
            "streamUrl": station.url,
            "baseTax": station.base_tax,
            "contentLog": content_log,
            "historicalRecords": historical,
        }
        return response
    finally:
        db.close()

def get_station_export_for_today(station_id: int):
    db = SessionLocal()
    try:
        station = db.get(models.Stations, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        rows = (
            db.query(
                models.SongPlays.played_at,
                models.SongPlays.title,
                models.Artists.name.label("artist"),
                models.Artists.origin,
            )
            .join(models.Artists, models.SongPlays.artist_id == models.Artists.id)
            .filter(models.SongPlays.station_id == station_id)
            .filter(func.to_char(models.SongPlays.played_at, "YYYY-MM-DD") == today_str)
            .order_by(models.SongPlays.played_at.desc())
            .all()
        )
        content_log = [
            {
                "timestamp": format_iso(r.played_at),
                "title": r.title,
                "artist": r.artist,
                "origin": r.origin,
            }
            for r in rows
        ]

        response = {
            "id": station.id,
            "name": station.name,
            "streamUrl": station.url,
            "baseTax": station.base_tax,
            "contentLog": content_log,
        }
        return response
    finally:
        db.close()

def get_all_stations():
    db = SessionLocal()
    try:
        stations = db.query(models.Stations).all()
        return [get_station_export(s.id) for s in stations]
    finally:
        db.close()

def stations_list():
    db = SessionLocal()
    try:
        stations = db.query(models.Stations).all()
        return [{"id": s.id, "name": s.name} for s in stations]
    finally:
        db.close()

def get_station_history(station_id: int, period: str):
    """
    Fetch a specific historical record for a station by period (YYYY-MM format).
    period format: "2025-11"
    """
    db = SessionLocal()
    try:
        station = db.get(models.Stations, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Validate period format
        try:
            datetime.strptime(period, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period format. Use YYYY-MM")
        
        # Query aggregates for this specific period
        period_agg = (
            db.query(
                func.count().label("total"),
                func.sum(case((models.Artists.origin == "Foreign", 1), else_=0)).label(
                    "foreign_count"
                ),
                func.max(models.SongPlays.played_at).label("paid_on_candidate"),
            )
            .join(models.Artists, models.SongPlays.artist_id == models.Artists.id)
            .filter(models.SongPlays.station_id == station_id)
            .filter(
                func.to_char(models.SongPlays.played_at, "YYYY-MM") == period
            )
            .first()
        )
        
        if not period_agg or not period_agg.total:
            raise HTTPException(status_code=404, detail="No data found for this period")
        
        total = period_agg.total or 0
        foreign = period_agg.foreign_count or 0
        foreign_pct = (foreign / total * 100) if total else 0.0
        
        # Calculate surcharge/totalTax
        surcharge = round(max(0, (foreign_pct - 30.0) * 10.0), 2)
        total_tax = float(station.base_tax or 0) + surcharge
        
        # Fetch full contentLog for this period
        rows_period = (
            db.query(
                models.SongPlays.played_at,
                models.SongPlays.title,
                models.Artists.name.label("artist"),
                models.Artists.origin,
            )
            .join(models.Artists)
            .filter(models.SongPlays.station_id == station_id)
            .filter(
                func.to_char(models.SongPlays.played_at, "YYYY-MM") == period
            )
            .order_by(models.SongPlays.played_at)
            .all()
        )
        
        content_period = [
            {
                "timestamp": format_iso(r.played_at),
                "title": r.title,
                "artist": r.artist,
                "origin": r.origin,
            }
            for r in rows_period
        ]
        
        response = {
            "periodId": period,
            "period": datetime.strptime(period + "-01", "%Y-%m-%d").strftime("%B %Y"),
            "status": "paid" if period_agg.paid_on_candidate else "due",
            "summary": {
                "foreignPercentage": round(foreign_pct, 2),
                "surcharge": surcharge,
                "totalTax": total_tax,
                "paidOn": (
                    format_iso(period_agg.paid_on_candidate)
                    if period_agg.paid_on_candidate
                    else None
                ),
            },
            "contentLog": content_period,
        }
        return response
    finally:
        db.close()


def dashboard_stations_summary():
    db = SessionLocal()
    try:
        from datetime import datetime, date
        today = date.today()
        current_month_start = datetime(today.year, today.month, 1)
        
        stations = db.query(models.Stations).all()
        result = []
        
        for s in stations:
            # Get all song plays for current month
            plays_this_month = (
                db.query(models.SongPlays)
                .filter(
                    models.SongPlays.station_id == s.id,
                    models.SongPlays.played_at >= current_month_start
                )
                .all()
            )
            
            total_content_logs = len(plays_this_month)
            
            # Calculate foreign percentage
            foreign_count = 0
            if total_content_logs > 0:
                play_ids = [p.id for p in plays_this_month]
                foreign_count = (
                    db.query(models.SongPlays)
                    .join(models.Artists, models.SongPlays.artist_id == models.Artists.id)
                    .filter(
                        models.SongPlays.id.in_(play_ids),
                        models.Artists.origin == "Foreign"
                    )
                    .count()
                )
            
            foreign_percentage = round((foreign_count / total_content_logs * 100), 2) if total_content_logs > 0 else 0.0
            
            result.append({
                "id": s.id,
                "name": s.name,
                "streamUrl": s.url,
                "baseTax": s.base_tax,
                "status": "active",
                "foreignPercentage": foreign_percentage,
                "totalContentLogs": total_content_logs,
            })
        
        return result
    finally:
        db.close()

