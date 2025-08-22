import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class SearchCache:
    """Simple file-based cache for search results."""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_seconds: int = 3600):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.proofcheck/cache
            ttl_seconds: Time to live for cache entries in seconds (default 1 hour)
        """
        if cache_dir is None:
            self.cache_dir = Path.home() / ".proofcheck" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
    
    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key from the query."""
        # Use SHA256 to create a consistent filename from the query
        return hashlib.sha256(query.encode()).hexdigest()[:16]
    
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key."""
        return self.cache_dir / f"search_{key}.json"
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached results for a query.
        
        Args:
            query: The search query
            
        Returns:
            Cached results if available and not expired, None otherwise
        """
        key = self._get_cache_key(query)
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(seconds=self.ttl_seconds):
                # Cache expired, remove file
                cache_file.unlink(missing_ok=True)
                return None
            
            return cache_data['data']
            
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, query: str, data: Dict[str, Any]) -> None:
        """
        Cache search results.
        
        Args:
            query: The search query
            data: The data to cache
        """
        key = self._get_cache_key(query)
        cache_file = self._get_cache_file(key)
        
        cache_data = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            # Silently fail if we can't write cache
            pass
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of cache entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("search_*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        return count
    
    def clear_expired(self) -> int:
        """
        Clear only expired cache entries.
        
        Returns:
            Number of expired entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("search_*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > timedelta(seconds=self.ttl_seconds):
                    cache_file.unlink()
                    count += 1
                    
            except Exception:
                # If we can't read/parse the file, remove it
                try:
                    cache_file.unlink()
                    count += 1
                except Exception:
                    pass
        
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("search_*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        expired = 0
        valid = 0
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > timedelta(seconds=self.ttl_seconds):
                    expired += 1
                else:
                    valid += 1
            except Exception:
                expired += 1
        
        return {
            'total_entries': len(cache_files),
            'valid_entries': valid,
            'expired_entries': expired,
            'total_size_bytes': total_size,
            'cache_directory': str(self.cache_dir),
            'ttl_seconds': self.ttl_seconds
        }