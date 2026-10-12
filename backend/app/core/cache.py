import time
from typing import Any, Optional, Dict
import hashlib
import json

class InMemoryCache:
    def __init__(self, default_ttl: int = 86400):  # 24 hours default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def _generate_key(self, prefix: str, data: Any) -> str:
        serialized = json.dumps(data, sort_keys=True, default=str)
        hash_digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"{prefix}:{hash_digest}"

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }

    def clear(self) -> None:
        self._cache.clear()

# Global singleton cache instance for scholarly queries
scholarly_cache = InMemoryCache()
