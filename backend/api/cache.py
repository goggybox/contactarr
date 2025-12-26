import os
import json
import time
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Dict
from threading import Thread, Lock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APICacheManager:
    def __init__(self, cache_dir: str = ".api_cache"):
        """
        initialise the cache manager
        """
        self.cache_dir = cache_dir
        self.cache_lock = Lock()
        self.revalidate_locks = {}

        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """ generate a cache key for the URL and parameters"""
        content = url
        if params:
            content += json.dumps(params, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def _load_cache(self, cache_key: str) -> Optional[Dict]:
        cache_path = self._get_cache_path(cache_key)

        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading cache for {cache_key}: {e}")

        return None

    def _save_cache(self, cache_key: str, data: Any, metadata: Optional[Dict] = None):
        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'data': data,
            'metadata': metadata or {}
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except IOError as e:
            logger.error(f"Error saving cache for {cache_key}: {e}")

    def _revalidate_async(self, url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None, cache_key: str = None):
        """revalidate cache in background thread"""
        def revalidate():
            try:
                # use per-URL lock to prevent concurrent revalidation of the same URL
                lock = self.revalidate_locks.setdefault(url, Lock())

                with lock:
                    logger.info(f"Revalidating cache for: {url}")
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    response.raise_for_status()
                    new_data = response.json()

                    self._save_cache(cache_key, new_data)

                    if callback:
                        try:
                            callback(new_data)
                        except Exception as e:
                            logger.error(f"Error in callback for {url}: {e}")
                    
                    logger.info(f"Cache revalidated successfully for: {url}")

            except Exception as e:
                logger.error(f"Error revalidating cache for {url}: {e}")

        thread = Thread(target=revalidate, daemon=True)
        thread.start()

    def get(self, url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Any]:
        cache_key = self._get_cache_key(url, params)

        cache_data = self._load_cache(cache_key)
        if cache_data:
            logger.info(f"Cache hit for: {url}")
            self._revalidate_async(url, callback, headers, params, cache_key)
            return cache_data['data']

        # no valid cache, fetch fresh data
        try:
            logger.info(f"Fetching fresh data for: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            self._save_cache(cache_key, data)

            if callback:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in callback for {url}: {e}")
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return None

    def clear_cache(self, url: str = None, params: Optional[Dict] = None):
        """clear cache for specific URL or all cache"""
        if url:
            cache_key = self._get_cache_key(url, params)
            cache_path = self._get_cache_path(cache_key)
            try:
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    logger.info(f"Cleared cache for: {url}")
            except OSError as e:
                logger.error(f"Error clearing cache for {url}: {e}")

        else:
            # clear all cache!
            import glob
            cache_files = glob.glob(os.path.join(self.cache_dir, "*.json"))
            for file in cache_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            logger.info("Cleared all cache")


cache_manager = APICacheManager()

def apiGet(url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Any]:
    return cache_manager.get(url, callback, headers, params)

def clearCache(url: str = None):
    cache_manager.clear_cache(url)