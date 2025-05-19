from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

from src.database import engine, get_db
from src import models, schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="System Monitor API",
    description="API for collecting and querying system health data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/status", response_model=schemas.SystemState)
def report_system_state(state: schemas.SystemStateCreate, db: Session = Depends(get_db)):
    """Submit a new system state report"""
    db_state = models.SystemState(
        machine_id=state.machine_id,
        platform=state.platform,
        hostname=state.hostname,
        disk_encryption_enabled=state.disk_encryption_enabled,
        disk_encryption_type=state.disk_encryption_type,
        updates_available=state.updates_available,
        os_version=state.os_version,
        antivirus_installed=state.antivirus_installed,
        antivirus_running=state.antivirus_running,
        antivirus_name=state.antivirus_name,
        sleep_timeout=state.sleep_timeout,
        sleep_compliant=state.sleep_compliant,
        raw_check_results=state.raw_check_results
    )
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

@app.get("/api/machines", response_model=List[str])
def list_machines(db: Session = Depends(get_db)):
    """Get a list of all machine IDs"""
    machines = db.query(models.SystemState.machine_id).distinct().all()
    return [machine[0] for machine in machines]

@app.get("/api/status/{machine_id}", response_model=schemas.SystemState)
def get_machine_status(machine_id: str, db: Session = Depends(get_db)):
    """Get the latest status for a specific machine"""
    status = db.query(models.SystemState)\
        .filter(models.SystemState.machine_id == machine_id)\
        .order_by(models.SystemState.timestamp.desc())\
        .first()
    if not status:
        raise HTTPException(status_code=404, detail="Machine not found")
    return status

@app.get("/api/status", response_model=List[schemas.SystemState])
def get_filtered_status(
    platform: Optional[str] = None,
    has_disk_encryption: Optional[bool] = None,
    has_updates: Optional[bool] = None,
    has_antivirus: Optional[bool] = None,
    is_sleep_compliant: Optional[bool] = None,
    time_range: Optional[int] = Query(None, description="Time range in hours to filter"),
    db: Session = Depends(get_db)
):
    """Get filtered system status for all machines"""
    query = db.query(models.SystemState)
    
    # Apply filters
    if platform:
        query = query.filter(models.SystemState.platform == platform)
    if has_disk_encryption is not None:
        query = query.filter(models.SystemState.disk_encryption_enabled == has_disk_encryption)
    if has_updates is not None:
        query = query.filter(models.SystemState.updates_available == has_updates)
    if has_antivirus is not None:
        query = query.filter(models.SystemState.antivirus_installed == has_antivirus)
    if is_sleep_compliant is not None:
        query = query.filter(models.SystemState.sleep_compliant == is_sleep_compliant)
    if time_range:
        cutoff = datetime.utcnow() - timedelta(hours=time_range)
        query = query.filter(models.SystemState.timestamp >= cutoff)
    
    # Get latest status for each machine
    subquery = db.query(
        models.SystemState.machine_id,
        models.SystemState.id.label('latest_id')
    ).group_by(
        models.SystemState.machine_id
    ).subquery()
    
    query = query.join(
        subquery,
        models.SystemState.id == subquery.c.latest_id
    )
    
    return query.all()

@app.get("/api/export/csv")
def export_to_csv(
    platform: Optional[str] = None,
    has_disk_encryption: Optional[bool] = None,
    has_updates: Optional[bool] = None,
    has_antivirus: Optional[bool] = None,
    is_sleep_compliant: Optional[bool] = None,
    time_range: Optional[int] = Query(None, description="Time range in hours to filter"),
    db: Session = Depends(get_db)
):
    """Export system status data as CSV"""
    # Reuse the filtering logic
    data = get_filtered_status(
        platform=platform,
        has_disk_encryption=has_disk_encryption,
        has_updates=has_updates,
        has_antivirus=has_antivirus,
        is_sleep_compliant=is_sleep_compliant,
        time_range=time_range,
        db=db
    )
    
    # Convert to dataframe
    records = []
    for state in data:
        record = state.__dict__
        del record['_sa_instance_state']  # Remove SQLAlchemy internal state
        del record['raw_check_results']   # Exclude complex JSON data
        records.append(record)
    
    df = pd.DataFrame.from_records(records)
    
    # Convert to CSV
    output = StringIO()
    df.to_csv(output, index=False)
    
    return {
        "filename": f"system_status_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "content": output.getvalue()
    }
