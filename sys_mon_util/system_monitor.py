#!/usr/bin/env python3

import os
import sys
import time
import json
import logging
import schedule
import platform
import requests
import threading
import msvcrt
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.checkers.disk_encryption import check_disk_encryption
from src.checkers.os_updates import check_os_updates
from src.checkers.antivirus import check_antivirus
from src.checkers.sleep_settings import check_sleep_settings
from src.config import load_config
from src.daemon import setup_daemon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('system_monitor')

class SystemMonitor:
    def __init__(self):
        self.config = load_config()
        self.last_state = {}
        self.api_endpoint = self.config.get('api_endpoint', 'http://localhost:8000/api/status')
        self.check_interval = self.config.get('check_interval', 900)  # 15 minutes default
        self.display_data = self.config.get('display_data', True)  # Show data by default
        self.current_state = None
        self.running = True

    def collect_system_state(self) -> Dict[str, Any]:
        """Collect all system checks and return a dictionary formatted for the API"""
        try:
            # Get all raw check results first
            disk_enc = check_disk_encryption()
            os_upd = check_os_updates()
            av = check_antivirus()
            sleep = check_sleep_settings()

            # Format the state for API submission
            state = {
                'machine_id': platform.node(),  # Use hostname as machine ID
                'hostname': platform.node(),
                'platform': platform.system(),
                'disk_encryption_enabled': disk_enc.get('enabled', False),
                'disk_encryption_type': disk_enc.get('details'),
                'updates_available': os_upd.get('updates_available', False),
                'os_version': os_upd.get('current_version', 'unknown'),
                'antivirus_installed': av.get('installed', False),
                'antivirus_running': av.get('running', False),
                'antivirus_name': av.get('product_name'),
                'sleep_timeout': sleep.get('sleep_timeout'),
                'sleep_compliant': sleep.get('compliant', False),
                'raw_check_results': {
                    'disk_encryption': disk_enc,
                    'os_updates': os_upd,
                    'antivirus': av,
                    'sleep_settings': sleep,
                }
            }
            return state
        except Exception as e:
            logger.error(f"Error collecting system state: {e}")
            return None

    def state_changed(self, new_state: Dict[str, Any]) -> bool:
        """Compare new state with last known state"""
        if not self.last_state or not new_state:
            return True
        
        try:
            # Compare only the check results, not the timestamp
            old_check_results = {k: v for k, v in self.last_state.items() if k != 'timestamp'}
            new_check_results = {k: v for k, v in new_state.items() if k != 'timestamp'}
            return old_check_results != new_check_results
        except Exception as e:
            logger.error(f"Error comparing states: {e}")
            return True

    def display_system_state(self, state: Dict[str, Any]):
        """Display system state in a formatted way"""
        if not state:
            print("\nError: No system state available")
            return

        try:
            print("\n" + "="*50)
            print(f"System Health Check Report")
            print("="*50)
            
            # Platform info
            print(f"\nSystem: {state['platform']} on {state['hostname']}")
            
            # Disk Encryption
            print("\nDisk Encryption:")
            print(f"  Status: {'Enabled' if state['disk_encryption_enabled'] else 'Disabled'}")
            print(f"  Type: {state['disk_encryption_type'] if state['disk_encryption_type'] else 'N/A'}")
            
            # OS Updates
            print("\nOS Updates:")
            print(f"  Updates Available: {'Yes' if state['updates_available'] else 'No'}")
            print(f"  Current Version: {state['os_version']}")
            
            # Antivirus
            print("\nAntivirus:")
            print(f"  Installed: {'Yes' if state['antivirus_installed'] else 'No'}")
            print(f"  Running: {'Yes' if state['antivirus_running'] else 'No'}")
            print(f"  Product: {state['antivirus_name'] if state['antivirus_name'] else 'N/A'}")
            
            # Sleep Settings
            print("\nSleep Settings:")
            print(f"  Timeout: {state['sleep_timeout'] if state['sleep_timeout'] else 'Unknown'} minutes")
            print(f"  Compliant (time out not more than 10 minutes): {'Yes' if state['sleep_compliant'] else 'No'}")
            
            print("\n" + "="*50)
        except Exception as e:
            logger.error(f"Error displaying system state: {e}")

    def report_state(self, state: Dict[str, Any]):
        """Send state to remote API if configured"""
        if not state:
            return

        try:
            response = requests.post(
                self.api_endpoint,
                json=state,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully reported state to API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to report state to API: {e}")

    def check_and_report(self):
        """Main monitoring function that runs periodically"""
        try:
            self.current_state = self.collect_system_state()
            
            if self.state_changed(self.current_state):
                logger.info("System state changed, reporting...")
                self.report_state(self.current_state)
                self.last_state = self.current_state
            
            if self.display_data:
                self.display_system_state(self.current_state)
            
        except Exception as e:
            logger.error(f"Error during system check: {e}")

    def handle_user_input(self):
        """Handle user keyboard input"""
        print("\nKeyboard Controls:")
        print("  D: Toggle data display")
        print("  R: Force refresh")
        print("  Q: Quit")
        
        while self.running:
            try:
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch()
                        # Handle arrow keys and special characters
                        if key in (b'\x00', b'\xe0'):  # Arrow keys prefix
                            msvcrt.getch()  # Consume the second byte
                            continue
                        
                        key = key.decode('ascii', errors='ignore').lower()
                        
                        if key == 'd':
                            self.display_data = not self.display_data
                            print(f"\nDisplay data: {'On' if self.display_data else 'Off'}")
                            if self.display_data and self.current_state:
                                self.display_system_state(self.current_state)
                        elif key == 'r':
                            print("\nForcing refresh...")
                            self.check_and_report()
                        elif key == 'q':
                            print("\nExiting...")
                            self.running = False
                            os._exit(0)
                    except UnicodeDecodeError:
                        # Ignore non-ASCII characters
                        pass
            except Exception as e:
                logger.error(f"Error handling user input: {e}")
            time.sleep(0.1)

def main():
    monitor = SystemMonitor()
    
    # Start user input handler in a separate thread
    input_thread = threading.Thread(target=monitor.handle_user_input, daemon=True)
    input_thread.start()
    
    # Schedule regular checks
    schedule.every(monitor.check_interval).seconds.do(monitor.check_and_report)
    
    # Do initial check immediately
    monitor.check_and_report()
    
    # Keep running
    try:
        while monitor.running:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.running = False

if __name__ == '__main__':
    if platform.system() != 'Windows':
        setup_daemon()
    main()
