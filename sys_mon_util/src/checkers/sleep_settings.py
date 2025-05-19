import platform
import subprocess
import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)

def parse_windows_timeout(output: str) -> int:
    """Parse Windows power config output to find sleep timeout"""
    ac_timeout = None
    dc_timeout = None
    
    # Look for sleep timeout settings
    ac_pattern = r"Current AC Power Setting Index: (0x[0-9a-f]+)"
    dc_pattern = r"Current DC Power Setting Index: (0x[0-9a-f]+)"
      # Only parse the sleep section
    sleep_section = None
    sections = output.split("Power Setting GUID:")
    for section in sections:
        if "Sleep after" in section:
            sleep_section = section
            break
    
    if sleep_section:
        # Find AC and DC timeouts
        ac_match = re.search(ac_pattern, sleep_section, re.IGNORECASE)
        if ac_match:
            try:
                ac_timeout = int(ac_match.group(1), 16) // 60  # Convert seconds to minutes
            except ValueError:
                pass
                
        dc_match = re.search(dc_pattern, sleep_section, re.IGNORECASE)
        if dc_match:
            try:
                dc_timeout = int(dc_match.group(1), 16) // 60  # Convert seconds to minutes
            except ValueError:
                pass
    
    # Return the shorter timeout (more restrictive)
    if ac_timeout is not None and dc_timeout is not None:
        return min(ac_timeout, dc_timeout)
    return ac_timeout or dc_timeout

def check_sleep_settings() -> Dict[str, any]:
    """Check system sleep/inactivity settings"""
    system = platform.system()
    result = {
        'sleep_timeout': None,
        'compliant': False,
        'status': 'unknown'
    }
    
    try:
        if system == 'Windows':
            # Get current power scheme settings
            proc = subprocess.run(
                ['powercfg', '/q', 'scheme_current'],
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0:
                timeout = parse_windows_timeout(proc.stdout)
                if timeout is not None:
                    result['sleep_timeout'] = timeout
                    result['compliant'] = timeout <= 10
                    result['status'] = 'checked'
            
        elif system == 'Darwin':  # macOS
            # Check sleep settings using pmset
            proc = subprocess.run(['pmset', '-g'], capture_output=True, text=True)
            if proc.returncode == 0:
                # Look for both display and system sleep
                display_sleep = None
                system_sleep = None
                
                for line in proc.stdout.splitlines():
                    if 'displaysleep' in line:
                        try:
                            display_sleep = int(line.split()[-1])
                        except ValueError:
                            pass
                    elif 'sleep' in line and 'displaysleep' not in line:
                        try:
                            system_sleep = int(line.split()[-1])
                        except ValueError:
                            pass
                
                # Use the shorter timeout
                timeout = None
                if display_sleep is not None and system_sleep is not None:
                    timeout = min(display_sleep, system_sleep)
                else:
                    timeout = display_sleep or system_sleep
                
                if timeout is not None:
                    result['sleep_timeout'] = timeout
                    result['compliant'] = timeout <= 10
                    result['status'] = 'checked'
            
        elif system == 'Linux':
            # Try multiple methods to check sleep settings
            timeout = None
            
            # First try dconf for GNOME
            try:
                dconf_proc = subprocess.run(
                    ['dconf', 'read', '/org/gnome/settings-daemon/plugins/power/sleep-inactive-ac-timeout'],
                    capture_output=True,
                    text=True
                )
                if dconf_proc.returncode == 0 and dconf_proc.stdout.strip():
                    timeout = int(dconf_proc.stdout.strip()) / 60  # Convert seconds to minutes
            except (ValueError, subprocess.SubprocessError):
                pass
            
            # If dconf failed, try systemd
            if timeout is None:
                try:
                    systemd_proc = subprocess.run(
                        ['systemctl', 'show', '-p', 'IdleAction,IdleActionSec', 'system-suspend.target'],
                        capture_output=True,
                        text=True
                    )
                    if systemd_proc.returncode == 0:
                        for line in systemd_proc.stdout.splitlines():
                            if 'IdleActionSec=' in line:
                                try:
                                    timeout = int(line.split('=')[1]) / 60  # Convert seconds to minutes
                                    break
                                except ValueError:
                                    pass
                except subprocess.SubprocessError:
                    pass
            
            if timeout is not None:
                result['sleep_timeout'] = timeout
                result['compliant'] = timeout <= 10
                result['status'] = 'checked'
                    
    except Exception as e:
        logger.error(f"Error checking sleep settings: {e}")
        result['status'] = f"error: {str(e)}"
        
    return result
