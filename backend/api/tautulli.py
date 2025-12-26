import os
import requests
from dotenv import load_dotenv
from backend.api.cache import apiGet, clearCache
from backend.api.config import get_tautulli_config

def get_tautulli_status():
    config = get_tautulli_config()
    api_key = config['api_key']
    api_url = config['api_url']

    if not api_key or not api_url:
        return {"error": "Tautulli API key or API URL not configured"}

    url = f"{api_url}"
    params = {
        'apikey': api_key,
        'cmd': 'get_libraries'
    }

    try:
        data = apiGet(url=url, params=params)

        if data:
            return {
                "status": "ok",
                "service": "tautulli",
                "data": data
            }
        else:
            return {
                "status": "error",
                "service": "tautulli",
                "message": "Failed to get data"
            }

    except Exception as e:
        return {
            "status": "error",
            "service": "tautulli",
            "message": str(e)
        }

