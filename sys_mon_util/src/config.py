import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'api_endpoint': 'http://localhost:8000/api/status',
    'check_interval': 900,  # 15 minutes in seconds
    'log_level': 'INFO',
    'log_file': 'system_monitor.log'
}

def load_config(config_path: str = None) -> dict:
    """Load configuration from file or return defaults"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.yaml'
        )
    
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    config.update(user_config)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
    
    return config
