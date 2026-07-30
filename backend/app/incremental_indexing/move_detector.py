"""Directory move classification for checksum-matched files."""

import posixpath
from typing import Dict


class MoveDetector:
    """Classifies path relocations that retain their filename as directory moves."""

    @staticmethod
    def detect(relocations: Dict[str, str]) -> Dict[str, str]:
        return {
            old_path: new_path
            for old_path, new_path in relocations.items()
            if posixpath.basename(old_path) == posixpath.basename(new_path)
            and posixpath.dirname(old_path) != posixpath.dirname(new_path)
        }
