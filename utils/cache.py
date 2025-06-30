import json
import os
import hashlib
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCache:
    def __init__(self, cache_dir="cache", default_expiry_hours=1):
        self.cache_dir = cache_dir
        self.default_expiry_hours = default_expiry_hours
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, key_data):
        """Generate a hash-based cache key"""
        if isinstance(key_data, dict):
            key_string = json.dumps(key_data, sort_keys=True)
        else:
            key_string = str(key_data)
        
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key):
        """Get the full path for a cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def set(self, key_data, value, expiry_hours=None):
        """Store a value in cache with expiration"""
        try:
            cache_key = self._get_cache_key(key_data)
            cache_file = self._get_cache_file_path(cache_key)
            
            expiry_hours = expiry_hours or self.default_expiry_hours
            expiry_time = datetime.now() + timedelta(hours=expiry_hours)
            
            cache_data = {
                'value': value,
                'expiry': expiry_time.isoformat(),
                'created': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached data with key {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def get(self, key_data):
        """Retrieve a value from cache if not expired"""
        try:
            cache_key = self._get_cache_key(key_data)
            cache_file = self._get_cache_file_path(cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            expiry_time = datetime.fromisoformat(cache_data['expiry'])
            if datetime.now() > expiry_time:
                # Clean up expired cache
                os.remove(cache_file)
                logger.debug(f"Cache expired for key {cache_key}")
                return None
            
            logger.debug(f"Cache hit for key {cache_key}")
            return cache_data['value']
            
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None
    
    def invalidate(self, key_data):
        """Remove a specific cache entry"""
        try:
            cache_key = self._get_cache_key(key_data)
            cache_file = self._get_cache_file_path(cache_key)
            
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.debug(f"Invalidated cache for key {cache_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return False
    
    def clear_expired(self):
        """Clear all expired cache entries"""
        try:
            cleared_count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                        
                        expiry_time = datetime.fromisoformat(cache_data['expiry'])
                        if datetime.now() > expiry_time:
                            os.remove(cache_file)
                            cleared_count += 1
                    
                    except Exception:
                        # If we can't read the cache file, remove it
                        os.remove(cache_file)
                        cleared_count += 1
            
            logger.info(f"Cleared {cleared_count} expired cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
            return 0
    
    def get_cache_stats(self):
        """Get statistics about the cache"""
        try:
            total_files = 0
            expired_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(cache_file)
                    
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                        
                        expiry_time = datetime.fromisoformat(cache_data['expiry'])
                        if datetime.now() > expiry_time:
                            expired_files += 1
                    
                    except Exception:
                        expired_files += 1
            
            return {
                'total_files': total_files,
                'expired_files': expired_files,
                'active_files': total_files - expired_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)} 