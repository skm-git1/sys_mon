import platform
import subprocess
import logging
from typing import Dict
import winreg

logger = logging.getLogger(__name__)

def check_os_updates() -> Dict[str, any]:
    """Check OS update status"""
    system = platform.system()
    result = {
        'current_version': platform.version(),
        'updates_available': False,
        'status': 'unknown'
    }
    
    try:
        if system == 'Windows':
            # Use PowerShell to check for Windows updates
            ps_command = """
            $Updates = Get-WindowsUpdate
            @{
                updates_available = ($Updates.Count -gt 0)
                pending_updates = $Updates.Count
            } | ConvertTo-Json
            """
            proc = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True
            )
            if proc.returncode == 0:
                result['status'] = 'checked'
                result['updates_available'] = 'updates_available' in proc.stdout.lower()
                
        elif system == 'Darwin':  # macOS
            # Check software update
            proc = subprocess.run(['softwareupdate', '-l'], capture_output=True, text=True)
            result['updates_available'] = 'Software Update found' in proc.stdout
            result['status'] = 'checked'
            
        elif system == 'Linux':
            # This will work for apt-based systems
            proc = subprocess.run(['apt-get', 'update', '-q'], capture_output=True)
            if proc.returncode == 0:
                proc = subprocess.run(['apt-get', '-s', 'upgrade'], capture_output=True, text=True)
                result['updates_available'] = '0 upgraded, 0 newly installed' not in proc.stdout
                result['status'] = 'checked'
                
    except Exception as e:
        logger.error(f"Error checking OS updates: {e}")
        result['status'] = f"error: {str(e)}"
        
    return result
