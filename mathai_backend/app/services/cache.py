"""In-memory caching service for improved performance."""
from typing import Optional, Any
from datetime import datetime, timedelta
from threading import Lock
import hashlib
import json


class CacheEntry:
    """Cache entry with expiration."""
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > self.expires_at


class CacheService:
    """Thread-safe in-memory cache service."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and kwargs."""
        # Sort kwargs for consistent key generation
        key_data = json.dumps({k: v for k, v in sorted(kwargs.items())}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL."""
        with self._lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self._max_size:
                # Remove 10% of oldest entries
                to_remove = max(1, self._max_size // 10)
                for old_key in list(self._cache.keys())[:to_remove]:
                    del self._cache[old_key]
            
            self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests
            }
    
    # Convenience methods for common cache patterns
    
    def cache_question(self, question_id: str, data: dict, ttl_seconds: int = 3600):
        """Cache question data."""
        key = f"question:{question_id}"
        self.set(key, data, ttl_seconds)
    
    def get_question(self, question_id: str) -> Optional[dict]:
        """Get cached question data."""
        key = f"question:{question_id}"
        return self.get(key)
    
    def cache_hint(self, question_id: str, hint_level: int, hint: str, ttl_seconds: int = 1800):
        """Cache hint for question."""
        key = f"hint:{question_id}:{hint_level}"
        self.set(key, hint, ttl_seconds)
    
    def get_hint(self, question_id: str, hint_level: int) -> Optional[str]:
        """Get cached hint."""
        key = f"hint:{question_id}:{hint_level}"
        return self.get(key)
    
    def cache_solution(self, question_id: str, solution: dict, ttl_seconds: int = 3600):
        """Cache solution for question (dict with answer and solution_steps)."""
        key = f"solution:{question_id}"
        self.set(key, solution, ttl_seconds)
    
    def get_solution(self, question_id: str) -> Optional[dict]:
        """Get cached solution (dict with answer and solution_steps)."""
        key = f"solution:{question_id}"
        return self.get(key)


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create global cache service."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(max_size=1000)
    return _cache_service
