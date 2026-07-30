import hashlib
import json
from typing import Dict, Any, Optional
import threading

class IdempotencyManager:
    def __init__(self):
        self._execution_fingerprints: Dict[str, str] = {}
        self._lock = threading.Lock()

    def generate_fingerprint(self, task_type: str, repository_id: str, payload: Dict[str, Any]) -> str:
        """Generate a unique execution fingerprint based on task type, repository, and payload."""
        data = {
            "task_type": task_type,
            "repository_id": repository_id,
            "payload": payload
        }
        # Serialize with sorted keys for consistency
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def mark_execution_started(self, job_id: str, fingerprint: str) -> bool:
        """
        Mark a fingerprint as being executed. 
        Returns True if successful, False if it's already executed/executing.
        """
        with self._lock:
            if fingerprint in self._execution_fingerprints:
                return False
            self._execution_fingerprints[fingerprint] = job_id
            return True

    def mark_execution_completed(self, fingerprint: str) -> None:
        """
        In a real system, you might record the result to replay later.
        For now, we just keep the fingerprint registered.
        """
        pass

    def remove_fingerprint(self, fingerprint: str) -> None:
        """Allow a fingerprint to be executed again (e.g. for replay)."""
        with self._lock:
            if fingerprint in self._execution_fingerprints:
                del self._execution_fingerprints[fingerprint]

# Global instance
idempotency_manager = IdempotencyManager()
