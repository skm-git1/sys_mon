from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SystemState(Base):
    __tablename__ = "system_states"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    platform = Column(String)
    hostname = Column(String)
    
    # Security states
    disk_encryption_enabled = Column(Boolean)
    disk_encryption_type = Column(String)
    
    updates_available = Column(Boolean)
    os_version = Column(String)
    
    antivirus_installed = Column(Boolean)
    antivirus_running = Column(Boolean)
    antivirus_name = Column(String)
    
    sleep_timeout = Column(Integer)  # in minutes
    sleep_compliant = Column(Boolean)
    
    # Store full check results
    raw_check_results = Column(JSON)
