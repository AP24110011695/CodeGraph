import threading
import logging
import time
from typing import Dict, Any, Callable
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TimeoutManager:
    def __init__(self):
        self._timeouts: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        with self._lock:
            if not self._running:
                self._running = True
                self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False

    def register_timeout(self, job_id: str, timeout_seconds: float, on_timeout: Callable):
        with self._lock:
            self._timeouts[job_id] = {
                "expires_at": time.time() + timeout_seconds,
                "callback": on_timeout
            }

    def unregister_timeout(self, job_id: str):
        with self._lock:
            if job_id in self._timeouts:
                del self._timeouts[job_id]

    def _monitor_loop(self):
        while self._running:
            now = time.time()
            expired = []
            
            with self._lock:
                for job_id, data in list(self._timeouts.items()):
                    if now >= data["expires_at"]:
                        expired.append((job_id, data["callback"]))
                        del self._timeouts[job_id]
            
            for job_id, callback in expired:
                try:
                    logger.warning(f"Job {job_id} timed out.")
                    callback(job_id)
                except Exception as e:
                    logger.error(f"Error executing timeout callback for {job_id}: {e}")
                    
            time.sleep(1.0)

# Global instance
timeout_manager = TimeoutManager()
