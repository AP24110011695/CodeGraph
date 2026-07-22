"""Framework detection engine for CodeGraph.

Detects frontend frameworks, backend frameworks, package managers,
and containerization from project configuration files.

All detection is rule-based and deterministic.
No AI, no LLMs, no source code parsing.
Only project configuration files are read.
"""

import json
import logging
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from app.services.scanner_service import ScanResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Confidence tiers
# ---------------------------------------------------------------------------
CONFIDENCE_CONFIG_FILE: int = 100
CONFIDENCE_DEPENDENCY: int = 95
CONFIDENCE_DEV_DEPENDENCY: int = 85
CONFIDENCE_TEXT_MATCH: int = 80


# ---------------------------------------------------------------------------
# Language → tree-sitter parser name mapping
# ---------------------------------------------------------------------------
LANGUAGE_PARSER_MAP: dict[str, str] = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "java",
    "Go": "go",
    "Rust": "rust",
    "C#": "c_sharp",
    "C++": "cpp",
    "C": "c",
    "PHP": "php",
}


# ---------------------------------------------------------------------------
# Safe file readers — return None on any error
# ---------------------------------------------------------------------------
def _read_json_safe(path: Path) -> dict | None:
    """Read and parse a JSON file, returning None on any error."""
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except (OSError, PermissionError, json.JSONDecodeError, UnicodeDecodeError):
        if path.exists():
            logger.warning("Failed to parse JSON: %s", path)
        return None


def _read_toml_safe(path: Path) -> dict | None:
    """Read and parse a TOML file, returning None on any error."""
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except (OSError, PermissionError, tomllib.TOMLDecodeError):
        if path.exists():
            logger.warning("Failed to parse TOML: %s", path)
        return None


def _read_text_safe(path: Path) -> str | None:
    """Read a text file, returning None on any error."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, PermissionError, UnicodeDecodeError):
        if path.exists():
            logger.warning("Failed to read file: %s", path)
        return None


# ---------------------------------------------------------------------------
# Config file dependency extractors
# ---------------------------------------------------------------------------
_REQUIREMENT_NAME_RE = re.compile(r"^([a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?)")


def _get_js_dependencies(pkg_json: dict) -> tuple[set[str], set[str]]:
    """Extract JS dependency names from package.json.

    Returns:
        (runtime_deps, dev_only_deps) where runtime_deps includes
        dependencies and peerDependencies, and dev_only_deps contains
        devDependencies keys not already in runtime_deps.
    """
    runtime: set[str] = set()
    for key in ("dependencies", "peerDependencies"):
        section = pkg_json.get(key)
        if isinstance(section, dict):
            runtime.update(section.keys())

    dev_section = pkg_json.get("devDependencies")
    dev_all = set(dev_section.keys()) if isinstance(dev_section, dict) else set()
    dev_only = dev_all - runtime

    return runtime, dev_only


def _get_python_dependencies(
    requirements_txt: str | None,
    pyproject_data: dict | None,
) -> set[str]:
    """Extract Python dependency names from requirements.txt and/or pyproject.toml."""
    deps: set[str] = set()

    if requirements_txt:
        for line in requirements_txt.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            match = _REQUIREMENT_NAME_RE.match(line)
            if match:
                deps.add(match.group(1).lower())

    if pyproject_data:
        project_deps = pyproject_data.get("project", {}).get("dependencies", [])
        if isinstance(project_deps, list):
            for dep in project_deps:
                if isinstance(dep, str):
                    match = _REQUIREMENT_NAME_RE.match(dep.strip())
                    if match:
                        deps.add(match.group(1).lower())

        poetry_deps = (
            pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )
        if isinstance(poetry_deps, dict):
            for key in poetry_deps:
                if key.lower() != "python":
                    deps.add(key.lower())

    return deps


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _any_file_exists(root: Path, *names: str) -> bool:
    """Return True if any of the named files exist directly under root."""
    return any((root / name).is_file() for name in names)


def _update_confidence(matches: dict[str, int], name: str, confidence: int) -> None:
    """Set the confidence for a match, keeping the highest value."""
    matches[name] = max(matches.get(name, 0), confidence)


def _to_match_list(matches: dict[str, int]) -> list["FrameworkMatch"]:
    """Convert a {name: confidence} dict to a sorted list of FrameworkMatch."""
    return sorted(
        [FrameworkMatch(name=k, confidence=v) for k, v in matches.items()],
        key=lambda m: (-m.confidence, m.name),
    )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class FrameworkMatch:
    """A detected framework or technology with a confidence score."""

    name: str
    confidence: int


@dataclass
class DetectionResult:
    """Complete output from the framework detection engine."""

    frameworks: list[FrameworkMatch] = field(default_factory=list)
    backend: list[FrameworkMatch] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    containerized: bool = False
    parser_targets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "frameworks": [
                {"name": m.name, "confidence": m.confidence}
                for m in self.frameworks
            ],
            "backend": [
                {"name": m.name, "confidence": m.confidence}
                for m in self.backend
            ],
            "package_managers": list(self.package_managers),
            "containerized": self.containerized,
            "parser_targets": list(self.parser_targets),
        }


# ---------------------------------------------------------------------------
# Framework Detector
# ---------------------------------------------------------------------------
class FrameworkDetector:
    """Detects the technology stack of a scanned repository.

    All detection is rule-based and deterministic.
    Only project configuration files are inspected.
    Source code is never read or parsed.
    """

    def detect(self, root_path: Path, scan_result: ScanResult) -> DetectionResult:
        """Run all detection rules against a project.

        Args:
            root_path: Absolute path to the extracted project root.
            scan_result: Output from RepositoryScanner.scan().

        Returns:
            A DetectionResult with all detected technologies.

        Raises:
            FileNotFoundError: If root_path does not exist.
            NotADirectoryError: If root_path is not a directory.
        """
        root = root_path.resolve()

        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root}")

        pkg_json = _read_json_safe(root / "package.json")
        runtime_deps, dev_only_deps = (
            _get_js_dependencies(pkg_json) if pkg_json else (set(), set())
        )
        all_js_deps = runtime_deps | dev_only_deps

        pyproject = _read_toml_safe(root / "pyproject.toml")
        req_txt = _read_text_safe(root / "requirements.txt")
        py_deps = _get_python_dependencies(req_txt, pyproject)

        return DetectionResult(
            frameworks=self._detect_frontend(root, runtime_deps, dev_only_deps),
            backend=self._detect_backend(root, all_js_deps, py_deps, scan_result),
            package_managers=self._detect_package_managers(root, pyproject),
            containerized=self._detect_containerization(root),
            parser_targets=self._build_parser_targets(scan_result.languages),
        )

    # ------------------------------------------------------------------
    # Frontend framework detection
    # ------------------------------------------------------------------
    def _detect_frontend(
        self,
        root: Path,
        runtime_deps: set[str],
        dev_only_deps: set[str],
    ) -> list[FrameworkMatch]:
        """Detect frontend frameworks from config files and package.json."""
        matches: dict[str, int] = {}
        all_deps = runtime_deps | dev_only_deps

        # React
        if "react" in runtime_deps:
            _update_confidence(matches, "React", CONFIDENCE_DEPENDENCY)
        elif "react" in dev_only_deps:
            _update_confidence(matches, "React", CONFIDENCE_DEV_DEPENDENCY)

        # Next.js
        if _any_file_exists(root, "next.config.js", "next.config.mjs", "next.config.ts"):
            _update_confidence(matches, "Next.js", CONFIDENCE_CONFIG_FILE)
        if "next" in all_deps:
            _update_confidence(matches, "Next.js", CONFIDENCE_DEPENDENCY)

        # Vue
        if "vue" in runtime_deps:
            _update_confidence(matches, "Vue", CONFIDENCE_DEPENDENCY)
        elif "vue" in dev_only_deps:
            _update_confidence(matches, "Vue", CONFIDENCE_DEV_DEPENDENCY)

        # Nuxt
        if _any_file_exists(root, "nuxt.config.js", "nuxt.config.ts"):
            _update_confidence(matches, "Nuxt", CONFIDENCE_CONFIG_FILE)
        if "nuxt" in all_deps:
            _update_confidence(matches, "Nuxt", CONFIDENCE_DEPENDENCY)

        # Angular
        if _any_file_exists(root, "angular.json"):
            _update_confidence(matches, "Angular", CONFIDENCE_CONFIG_FILE)
        if "@angular/core" in all_deps:
            _update_confidence(matches, "Angular", CONFIDENCE_DEPENDENCY)

        # Svelte
        if _any_file_exists(root, "svelte.config.js", "svelte.config.ts"):
            _update_confidence(matches, "Svelte", CONFIDENCE_CONFIG_FILE)
        if "svelte" in all_deps:
            _update_confidence(matches, "Svelte", CONFIDENCE_DEPENDENCY)

        # SolidJS
        if "solid-js" in runtime_deps:
            _update_confidence(matches, "SolidJS", CONFIDENCE_DEPENDENCY)
        elif "solid-js" in dev_only_deps:
            _update_confidence(matches, "SolidJS", CONFIDENCE_DEV_DEPENDENCY)

        # Astro
        if _any_file_exists(root, "astro.config.mjs", "astro.config.js", "astro.config.ts"):
            _update_confidence(matches, "Astro", CONFIDENCE_CONFIG_FILE)
        if "astro" in all_deps:
            _update_confidence(matches, "Astro", CONFIDENCE_DEPENDENCY)

        return _to_match_list(matches)

    # ------------------------------------------------------------------
    # Backend framework detection
    # ------------------------------------------------------------------
    def _detect_backend(
        self,
        root: Path,
        all_js_deps: set[str],
        py_deps: set[str],
        scan_result: ScanResult,
    ) -> list[FrameworkMatch]:
        """Detect backend frameworks from config files and manifests."""
        matches: dict[str, int] = {}

        # Express
        if "express" in all_js_deps:
            _update_confidence(matches, "Express", CONFIDENCE_DEPENDENCY)

        # NestJS
        if "@nestjs/core" in all_js_deps:
            _update_confidence(matches, "NestJS", CONFIDENCE_DEPENDENCY)

        # FastAPI
        if "fastapi" in py_deps:
            _update_confidence(matches, "FastAPI", CONFIDENCE_DEPENDENCY)

        # Flask
        if "flask" in py_deps:
            _update_confidence(matches, "Flask", CONFIDENCE_DEPENDENCY)

        # Django
        if "django" in py_deps:
            _update_confidence(matches, "Django", CONFIDENCE_DEPENDENCY)
        if _any_file_exists(root, "manage.py"):
            _update_confidence(matches, "Django", CONFIDENCE_TEXT_MATCH)

        # Spring Boot
        self._detect_spring_boot(root, matches)

        # ASP.NET Core
        self._detect_aspnet(root, scan_result, matches)

        # Laravel
        self._detect_laravel(root, matches)

        # Ruby on Rails
        self._detect_rails(root, matches)

        # Go frameworks (Gin, Fiber)
        self._detect_go_frameworks(root, matches)

        return _to_match_list(matches)

    def _detect_spring_boot(self, root: Path, matches: dict[str, int]) -> None:
        """Detect Spring Boot from pom.xml or build.gradle."""
        pom_text = _read_text_safe(root / "pom.xml")
        if pom_text and "spring-boot" in pom_text.lower():
            _update_confidence(matches, "Spring Boot", CONFIDENCE_TEXT_MATCH)

        for gradle_name in ("build.gradle", "build.gradle.kts"):
            gradle_text = _read_text_safe(root / gradle_name)
            if gradle_text and "spring-boot" in gradle_text.lower():
                _update_confidence(matches, "Spring Boot", CONFIDENCE_TEXT_MATCH)

    def _detect_aspnet(
        self, root: Path, scan_result: ScanResult, matches: dict[str, int]
    ) -> None:
        """Detect ASP.NET Core from .csproj files found by the scanner."""
        csproj_files = [f for f in scan_result.files if f.extension == ".csproj"]
        for file_info in csproj_files:
            csproj_text = _read_text_safe(root / file_info.path)
            if csproj_text and "microsoft.aspnetcore" in csproj_text.lower():
                _update_confidence(matches, "ASP.NET Core", CONFIDENCE_TEXT_MATCH)
                break

    def _detect_laravel(self, root: Path, matches: dict[str, int]) -> None:
        """Detect Laravel from composer.json."""
        composer = _read_json_safe(root / "composer.json")
        if not composer:
            return
        require = composer.get("require", {})
        if isinstance(require, dict) and "laravel/framework" in require:
            _update_confidence(matches, "Laravel", CONFIDENCE_DEPENDENCY)

    def _detect_rails(self, root: Path, matches: dict[str, int]) -> None:
        """Detect Ruby on Rails from Gemfile."""
        gemfile = _read_text_safe(root / "Gemfile")
        if gemfile and re.search(r"""gem\s+['"]rails['"]""", gemfile):
            _update_confidence(matches, "Ruby on Rails", CONFIDENCE_TEXT_MATCH)

    def _detect_go_frameworks(self, root: Path, matches: dict[str, int]) -> None:
        """Detect Go frameworks (Gin, Fiber) from go.mod."""
        gomod = _read_text_safe(root / "go.mod")
        if not gomod:
            return
        if "github.com/gin-gonic/gin" in gomod:
            _update_confidence(matches, "Gin", CONFIDENCE_TEXT_MATCH)
        if "github.com/gofiber/fiber" in gomod:
            _update_confidence(matches, "Fiber", CONFIDENCE_TEXT_MATCH)

    # ------------------------------------------------------------------
    # Package manager detection
    # ------------------------------------------------------------------
    def _detect_package_managers(
        self, root: Path, pyproject: dict | None
    ) -> list[str]:
        """Detect package managers from lock files and config files."""
        managers: list[str] = []

        if (root / "package-lock.json").is_file():
            managers.append("npm")
        if (root / "pnpm-lock.yaml").is_file():
            managers.append("pnpm")
        if (root / "yarn.lock").is_file():
            managers.append("yarn")

        if (root / "requirements.txt").is_file():
            managers.append("pip")
        if pyproject:
            poetry_section = pyproject.get("tool", {}).get("poetry")
            if poetry_section is not None:
                managers.append("poetry")

        if (root / "Cargo.toml").is_file():
            managers.append("cargo")

        if (root / "pom.xml").is_file():
            managers.append("maven")
        for gradle_name in ("build.gradle", "build.gradle.kts"):
            if (root / gradle_name).is_file():
                managers.append("gradle")
                break

        if (root / "composer.json").is_file():
            managers.append("composer")

        return sorted(managers)

    # ------------------------------------------------------------------
    # Containerization detection
    # ------------------------------------------------------------------
    def _detect_containerization(self, root: Path) -> bool:
        """Detect Docker containerization."""
        return _any_file_exists(
            root,
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
        )

    # ------------------------------------------------------------------
    # Parser targets
    # ------------------------------------------------------------------
    def _build_parser_targets(self, languages: dict[str, int]) -> list[str]:
        """Map detected languages to tree-sitter parser names."""
        targets: list[str] = []
        for language in sorted(languages.keys()):
            parser = LANGUAGE_PARSER_MAP.get(language)
            if parser:
                targets.append(parser)
        return targets


detector_service = FrameworkDetector()
