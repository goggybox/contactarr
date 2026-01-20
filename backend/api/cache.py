
# # -----------------------------contactarr------------------------------
# This file is part of contactarr
# Copyright (C) 2025 goggybox https://github.com/goggybox

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# that this program is licensed under. See LICENSE file. If not
# available, see <https://www.gnu.org/licenses/>.

# Please keep this header comment in all copies of the program.
# --------------------------------------------------------------------

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

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading cache for {cache_key}: {e}")
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None

    def _save_cache(self, cache_key: str, data: Any, metadata: Optional[Dict] = None):
        cache_path = self._get_cache_path(cache_key)
        tmp_path = cache_path + ".tmp"

        cache_data = {
            'data': data,
            'metadata': metadata or {}
        }

        try:
            with open(tmp_path, 'w') as f:
                json.dump(cache_data, f)
            os.replace(tmp_path, cache_path)
        except IOError as e:
            logger.error(f"Error saving cache for {cache_key}: {e}")

    def _revalidate_async(self, url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None, cache_key: str = None):
        """revalidate cache in background thread"""
        def revalidate():
            try:
                # use per-URL lock to prevent concurrent revalidation of the same URL
                lock = self.revalidate_locks.setdefault(url, Lock())

                with lock:
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    response.raise_for_status()
                    new_data = response.json()

                    self._save_cache(cache_key, new_data)

                    if callback:
                        try:
                            callback(new_data)
                        except Exception as e:
                            logger.error(f"Error in callback for {url}: {e}")

            except Exception as e:
                logger.error(f"Error revalidating cache for {url}: {e}")

        thread = Thread(target=revalidate, daemon=True)
        thread.start()

    def get(self, url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None, forceFresh: Optional[bool] = False) -> Optional[Any]:
        cache_key = self._get_cache_key(url, params)

        cache_data = self._load_cache(cache_key)
        if cache_data and not forceFresh:
            self._revalidate_async(url, callback, headers, params, cache_key)
            return cache_data['data']

        # no valid cache, fetch fresh data
        try:
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


cache_manager = APICacheManager()

def apiGet(url: str, callback: Optional[Callable[[Any], None]] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None, forceFresh: Optional[bool] = False) -> Optional[Any]:
    return cache_manager.get(url, callback, headers, params, forceFresh)

def clearCache(url: str = None):
    cache_manager.clear_cache(url)