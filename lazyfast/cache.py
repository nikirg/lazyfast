import functools
import hashlib
from lazyfast.state import StateField
from lazyfast import context, tags


class Cache:
    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> str | None:
        return self._cache.get(key)
    
    def set(self, key: str, value: str):
        self._cache[key] = value


# cache decorator
def cache(invalidate_on: list[StateField] | None = None, max_age: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            #context.enable_caching()

            cache_key = hashlib.md5(
                f"{func.__module__}.{func.__qualname__}:{args}:{kwargs}".encode(),
            ).hexdigest()

            if session := context.get_session():
                if content := session.cache.get(cache_key):
                    tags.raw(content)
                    return 

                func(*args, **kwargs)
            
        return wrapper

    return decorator
