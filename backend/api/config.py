import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

_env_path = None

def get_env_path():
    """get the path to the .env file"""
    global _env_path
    if _env_path is None:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        _env_path = project_root / '.env'
    return _env_path

def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """get a fresh configuration value from the environment"""
    env_path = get_env_path()
    load_dotenv(dotenv_path=env_path, override=True)
    
    value = os.getenv(key, default)
    
    if key.endswith('_API_URL') and value and not value.startswith(('http://', 'https://')):
        value = f'http://{value}'
    
    return value

def set_config_value(key: str, value: str) -> bool:
    try:
        env_path = get_env_path()

        env_data = {}
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        env_data[k.strip()] = v.strip()

        env_data[key] = value

        with open(env_path, 'w', encoding='utf-8') as f:
            for k, v in env_data.items():
                f.write(f'{k}={v}\n')

        load_dotenv(dotenv_path=env_path, override=True)

        return True
    except Exception as e:
        return False

def get_tautulli_config():
    """get fresh Tautulli configuration"""
    return {
        'api_key': get_config_value('TAUTULLI_API_KEY'),
        'api_url': get_config_value('TAUTULLI_API_URL'),
    }

def get_tvdb_config():
    """get fresh TVdb configuration"""
    return {
        'api_key': get_config_value('TVDB_API_KEY'),
        'api_url': get_config_value('TVDB_API_URL', 'https://api.thetvdb.com'),
    }