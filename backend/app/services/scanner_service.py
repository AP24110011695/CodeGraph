"""Repository scanner service for collecting project file metadata."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

IGNORED_DIRECTORIES: frozenset[str] = frozenset({
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    ".cache",
    ".idea",
    ".vscode",
})

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".md": "Markdown",
    ".sql": "SQL",
}

FILENAME_LANGUAGE_MAP: dict[str, str] = {
    "Dockerfile": "Docker",
}


@dataclass
class FileInfo:
    """Metadata for a single scanned file."""

    name: str
    path: str
    extension: str
    language: str
    size: int
    folder: str


@dataclass
class ScanResult:
    """Complete scan output for a project directory."""

    project_name: str
    root_path: str
    total_files: int = 0
    total_folders: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    files: list[FileInfo] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize the scan result to a plain dictionary."""
        return {
            "project_name": self.project_name,
            "root_path": self.root_path,
            "summary": {
                "files": self.total_files,
                "folders": self.total_folders,
            },
            "languages": dict(
                sorted(self.languages.items(), key=lambda item: item[1], reverse=True)
            ),
            "files": [
                {
                    "name": f.name,
                    "path": f.path,
                    "extension": f.extension,
                    "language": f.language,
                    "size": f.size,
                    "folder": f.folder,
                }
                for f in self.files
            ],
        }


def _detect_language(file_path: Path) -> str:
    """Detect language from file extension or special filenames."""
    language = FILENAME_LANGUAGE_MAP.get(file_path.name)
    if language:
        return language

    extension = file_path.suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(extension, "Unknown")


class RepositoryScanner:
    """Recursively scans a project directory and collects file metadata.

    Skips directories listed in IGNORED_DIRECTORIES.
    Detects language based on file extension or filename.
    Returns a structured ScanResult with project-level summary and per-file details.
    """

    def __init__(self, ignored_dirs: frozenset[str] | None = None) -> None:
        self._ignored_dirs = ignored_dirs if ignored_dirs is not None else IGNORED_DIRECTORIES

    def scan(self, root_path: Path) -> ScanResult:
        """Scan the directory tree rooted at root_path.

        Args:
            root_path: Absolute path to the extracted project directory.

        Returns:
            A ScanResult containing all collected metadata.

        Raises:
            FileNotFoundError: If root_path does not exist.
            NotADirectoryError: If root_path is not a directory.
            PermissionError: If root_path is not readable.
        """
        root_path = root_path.resolve()

        if not root_path.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")

        if not root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root_path}")

        result = ScanResult(
            project_name=root_path.name,
            root_path=str(root_path),
        )

        self._walk(root_path, root_path, result)

        result.total_files = len(result.files)

        return result

    def _walk(self, current: Path, root: Path, result: ScanResult) -> None:
        """Recursively walk the directory tree, populating result.

        Args:
            current: The directory currently being traversed.
            root: The top-level project root (used for relative paths).
            result: The accumulator for scan data.
        """
        try:
            entries = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            logger.warning("Permission denied: %s", current)
            return

        for entry in entries:
            if entry.is_dir():
                if entry.name in self._ignored_dirs:
                    continue

                result.total_folders += 1
                self._walk(entry, root, result)

            elif entry.is_file():
                self._collect_file(entry, root, result)

    def _collect_file(self, file_path: Path, root: Path, result: ScanResult) -> None:
        """Collect metadata for a single file.

        Args:
            file_path: Absolute path to the file.
            root: The project root directory.
            result: The accumulator for scan data.
        """
        try:
            size = file_path.stat().st_size
        except (PermissionError, OSError):
            logger.warning("Cannot stat file: %s", file_path)
            return

        relative = file_path.relative_to(root)
        language = _detect_language(file_path)
        extension = file_path.suffix.lower()

        file_info = FileInfo(
            name=file_path.name,
            path=relative.as_posix(),
            extension=extension,
            language=language,
            size=size,
            folder=relative.parent.as_posix(),
        )

        result.files.append(file_info)

        if language != "Unknown":
            result.languages[language] = result.languages.get(language, 0) + 1


scanner_service = RepositoryScanner()
