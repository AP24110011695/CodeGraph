"""Thread-safe cache for expensive analysis results with TTL and invalidation."""

import functools
import threading
import time
from pathlib import Path
from typing import Callable, Any

_global_cache: dict[str, tuple[float, Any]] = {}
_key_locks: dict[str, threading.Lock] = {}
_global_lock = threading.Lock()

def memoize_by_path(ttl_seconds: int = 300) -> Callable:
    """
    Memoize function results based on the Path argument, with a TTL.
    Thread-safe to prevent the thundering herd problem.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Find the Path argument
            project_path = next((arg for arg in args if isinstance(arg, Path)), None)
            if not project_path:
                return func(*args, **kwargs)
                
            key = f"{func.__module__}.{func.__name__}:{project_path.resolve()}"
            
            with _global_lock:
                if key not in _key_locks:
                    _key_locks[key] = threading.Lock()
                lock = _key_locks[key]
                
            with lock:
                now = time.time()
                # Check if it's cached and within TTL
                if key in _global_cache:
                    timestamp, result = _global_cache[key]
                    if now - timestamp < ttl_seconds:
                        return result
                
                # Execute and cache
                result = func(*args, **kwargs)
                _global_cache[key] = (now, result)
                return result
                
        return wrapper
    return decorator

def clear_analysis_cache(project_path: Path) -> None:
    """Clear all cached results for a specific project path."""
    path_str = str(project_path.resolve())
    with _global_lock:
        keys_to_delete = [k for k in _global_cache.keys() if k.endswith(f":{path_str}")]
        for k in keys_to_delete:
            _global_cache.pop(k, None)
            _key_locks.pop(k, None)
