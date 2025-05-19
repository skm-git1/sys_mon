from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class SystemStateBase(BaseModel):
    machine_id: str
    platform: str
    hostname: str
    disk_encryption_enabled: bool
    disk_encryption_type: Optional[str] = None
    updates_available: bool
    os_version: str
    antivirus_installed: bool
    antivirus_running: bool
    antivirus_name: Optional[str] = None
    sleep_timeout: Optional[int] = None
    sleep_compliant: bool
    raw_check_results: dict

class SystemStateCreate(SystemStateBase):
    pass

class SystemState(SystemStateBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemStateFilter(BaseModel):
    platform: Optional[str] = None
    has_disk_encryption: Optional[bool] = None
    has_updates: Optional[bool] = None
    has_antivirus: Optional[bool] = None
    is_sleep_compliant: Optional[bool] = None
