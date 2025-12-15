from models import ScanLogs
from datetime import datetime
from database import SessionLocal
def log_scan_completion(db: SessionLocal, station_id: int, status: str):
    """Logs the completion of a scan for a given station."""
    scan_log = ScanLogs(
        station_id=station_id,
        scan_time=datetime.now(),
        status=status
    )
    db.add(scan_log)
    db.commit()