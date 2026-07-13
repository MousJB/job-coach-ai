import time
from collections import OrderedDict
from threading import Lock
from typing import Any


class TTLCache:
    """Cache mémoire simple avec expiration et taille bornée (pas de dépendance externe)."""

    def __init__(self, ttl_seconds: int = 900, max_size: int = 100):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + self._ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self._max_size:
                self._store.popitem(last=False)


pipeline_cache = TTLCache()
