import os
import sys
import logging
import platform

logger = logging.getLogger(__name__)

def setup_daemon():
    """Setup daemon process for non-Windows systems"""
    if platform.system() == 'Windows':
        return
        
    try:
        import daemon
        from daemon import pidfile
        
        pid_file = '/var/run/system_monitor.pid'
        log_file = '/var/log/system_monitor.log'
        
        # Ensure we have permission to write to these locations
        if not os.access(os.path.dirname(pid_file), os.W_OK):
            pid_file = os.path.expanduser('~/.system_monitor.pid')
        if not os.access(os.path.dirname(log_file), os.W_OK):
            log_file = os.path.expanduser('~/.system_monitor.log')
            
        context = daemon.DaemonContext(
            working_directory='/',
            umask=0o002,
            pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        )
        
        # Open the log file
        context.stdout = open(log_file, 'a+')
        context.stderr = context.stdout
        
        with context:
            # Reconfigure logging for daemon context
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(context.stdout)
                ]
            )
            
    except ImportError:
        logger.warning("python-daemon package not available, running in foreground")
    except Exception as e:
        logger.error(f"Failed to setup daemon: {e}")
        sys.exit(1)
