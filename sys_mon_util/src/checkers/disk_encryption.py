import platform
import subprocess
import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)

def check_disk_encryption() -> Dict[str, any]:
    """Check disk encryption status for system drives"""
    system = platform.system()
    result = {
        'enabled': False,
        'status': 'unknown',
        'details': None
    }
    
    try:
        if system == 'Windows':
            # Check BitLocker status using manage-bde
            proc = subprocess.run(
                ['manage-bde', '-status', 'C:'],
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0:
                output = proc.stdout.lower()
                if 'protection on' in output:
                    result['enabled'] = True
                    result['status'] = 'enabled'
                    result['details'] = 'BitLocker'
                    
                    # Extract encryption method if available
                    method_match = re.search(r'encryption method:\s+(.+)', output)
                    if method_match:
                        result['details'] = f"BitLocker ({method_match.group(1).strip()})"
                else:
                    result['enabled'] = False
                    result['status'] = 'disabled'
                    
                    # Check if BitLocker is in progress
                    if 'conversion status' in output and 'percentage completed' in output:
                        result['status'] = 'encryption_in_progress'
                        result['details'] = 'BitLocker (encrypting)'
            
        elif system == 'Darwin':  # macOS
            # Check FileVault status
            proc = subprocess.run(['fdesetup', 'status'], capture_output=True, text=True)
            if proc.returncode == 0:
                result['enabled'] = 'FileVault is On' in proc.stdout
                result['status'] = 'enabled' if result['enabled'] else 'disabled'
                if result['enabled']:
                    result['details'] = 'FileVault'
                    
                    # Get additional FileVault details
                    detail_proc = subprocess.run(['fdesetup', 'show'], capture_output=True, text=True)
                    if detail_proc.returncode == 0 and detail_proc.stdout.strip():
                        result['details'] = f"FileVault ({detail_proc.stdout.splitlines()[0].strip()})"
            
        elif system == 'Linux':
            # Check LUKS encryption status
            proc = subprocess.run(['lsblk', '-f'], capture_output=True, text=True)
            if proc.returncode == 0:
                result['enabled'] = 'crypto_LUKS' in proc.stdout
                result['status'] = 'enabled' if result['enabled'] else 'disabled'
                if result['enabled']:
                    result['details'] = 'LUKS'
                    
                    # Try to get LUKS version and cipher info
                    try:
                        detail_proc = subprocess.run(
                            ['cryptsetup', 'status', 'root'],
                            capture_output=True,
                            text=True
                        )
                        if detail_proc.returncode == 0:
                            for line in detail_proc.stdout.splitlines():
                                if 'cipher:' in line.lower():
                                    result['details'] = f"LUKS ({line.split(':')[1].strip()})"
                                    break
                    except Exception:
                        pass  # Ignore if cryptsetup not available
            
    except Exception as e:
        logger.error(f"Error checking disk encryption: {e}")
        result['status'] = f"error: {str(e)}"
        
    return result
