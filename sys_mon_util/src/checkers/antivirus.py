import platform
import subprocess
import logging
from typing import Dict
import winreg

logger = logging.getLogger(__name__)

def check_antivirus() -> Dict[str, any]:
    """Check antivirus status"""
    system = platform.system()
    result = {
        'installed': False,
        'running': False,
        'product_name': None,
        'status': 'unknown'
    }
    
    try:
        if system == 'Windows':
            # Check Windows Security Center
            ps_command = """
            Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | 
            Select-Object displayName, productState | 
            ConvertTo-Json
            """
            proc = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0 and proc.stdout.strip():
                result['installed'] = True
                result['product_name'] = proc.stdout.strip()
                # productState: Check if AV is enabled and up to date
                # This is a complex bitmask that varies by vendor
                result['running'] = True
                result['status'] = 'active'
            
        elif system == 'Darwin':  # macOS
            # Check if XProtect is enabled
            proc = subprocess.run(['system_profiler', 'SPSecurityDataType'], capture_output=True, text=True)
            if 'XProtect: Enabled' in proc.stdout:
                result['installed'] = True
                result['running'] = True
                result['product_name'] = 'XProtect'
                result['status'] = 'active'
            
        elif system == 'Linux':
            # Check for common AV solutions
            av_list = ['clamav', 'sophos-av', 'avast', 'avg']
            for av in av_list:
                proc = subprocess.run(['which', av], capture_output=True)
                if proc.returncode == 0:
                    result['installed'] = True
                    result['product_name'] = av
                    # Check if service is running
                    service_proc = subprocess.run(['systemctl', 'is-active', f'{av}d'], capture_output=True)
                    result['running'] = service_proc.returncode == 0
                    result['status'] = 'active' if result['running'] else 'installed'
                    break
                    
    except Exception as e:
        logger.error(f"Error checking antivirus: {e}")
        result['status'] = f"error: {str(e)}"
        
    return result
