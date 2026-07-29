"""Pattern detector for design pattern detection engine.

Detects common software design patterns from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PatternDetection:
    """A detected design pattern."""

    name: str
    category: str
    confidence: int
    evidence: str
    affected_files: list[str]
    reason: str


class PatternDetector:
    """Detects design patterns from repository analysis.

    Reuses outputs from:
    - Parser Engine
    - Dependency Graph
    - Architecture Builder
    - Repository Scanner
    """

    def __init__(self):
        """Initialize the pattern detector."""
        pass

    def detect_patterns(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
        dependency_graph: dict | None = None,
        architecture_result: dict | None = None,
    ) -> list[PatternDetection]:
        """Detect design patterns in the repository.

        Args:
            project_path: Absolute path to the project directory.
            parsing_result: Result from parser engine.
            dependency_graph: Dependency graph from dependency builder.
            architecture_result: Result from architecture builder.

        Returns:
            List of detected patterns.
        """
        patterns: list[PatternDetection] = []

        # Detect Repository Pattern
        patterns.extend(self._detect_repository_pattern(project_path, architecture_result))

        # Detect Singleton Pattern
        patterns.extend(self._detect_singleton_pattern(project_path, parsing_result))

        # Detect Factory Pattern
        patterns.extend(self._detect_factory_pattern(project_path, parsing_result))

        # Detect Dependency Injection
        patterns.extend(self._detect_dependency_injection(project_path, parsing_result))

        # Detect MVC Pattern
        patterns.extend(self._detect_mvc_pattern(project_path, architecture_result))

        # Detect Layered Architecture
        patterns.extend(self._detect_layered_architecture(project_path, architecture_result))

        # Detect Strategy Pattern
        patterns.extend(self._detect_strategy_pattern(project_path, parsing_result))

        # Detect Observer Pattern
        patterns.extend(self._detect_observer_pattern(project_path, parsing_result))

        # Detect Decorator Pattern
        patterns.extend(self._detect_decorator_pattern(project_path, parsing_result))

        # Detect Facade Pattern
        patterns.extend(self._detect_facade_pattern(project_path, parsing_result))

        # Detect Adapter Pattern
        patterns.extend(self._detect_adapter_pattern(project_path, parsing_result))

        return patterns

    def _detect_repository_pattern(self, project_path: Path, architecture_result: dict | None) -> list[PatternDetection]:
        """Detect Repository pattern.

        Args:
            project_path: The project path.
            architecture_result: The architecture result.

        Returns:
            List of detected Repository patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for repository folders
        repository_folders = ["repository", "repositories", "dao", "data-access"]
        affected_files = []

        for folder in repository_folders:
            repo_path = project_path / folder
            if repo_path.exists() and repo_path.is_dir():
                for file in repo_path.rglob("*"):
                    if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                        affected_files.append(str(file.relative_to(project_path)))

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Repository Pattern",
                    category="Architectural",
                    confidence=90,
                    evidence=f"Found {len(affected_files)} files in repository folders.",
                    affected_files=affected_files[:10],  # Limit to 10 files
                    reason="Repository classes isolate persistence operations from business logic.",
                )
            )

        return patterns

    def _detect_singleton_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Singleton pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Singleton patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for singleton keywords in files
        singleton_keywords = ["_instance", "getInstance", "instance()", "__new__", "Singleton"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for keyword in singleton_keywords:
                        if keyword in content:
                            affected_files.append(str(file.relative_to(project_path)))
                            break
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Singleton Pattern",
                    category="Creational",
                    confidence=75,
                    evidence=f"Found singleton-related keywords in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Singleton pattern ensures a class has only one instance.",
                )
            )

        return patterns

    def _detect_factory_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Factory pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Factory patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for factory keywords in files
        factory_keywords = ["Factory", "create", "build", "make"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for keyword in factory_keywords:
                        if keyword in content and "factory" in content.lower():
                            affected_files.append(str(file.relative_to(project_path)))
                            break
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Factory Pattern",
                    category="Creational",
                    confidence=70,
                    evidence=f"Found factory-related keywords in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Factory pattern creates objects without specifying exact class.",
                )
            )

        return patterns

    def _detect_dependency_injection(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Dependency Injection pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Dependency Injection patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for DI keywords in files
        di_keywords = ["@Inject", "@Autowired", "inject", "dependency", "container"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for keyword in di_keywords:
                        if keyword in content:
                            affected_files.append(str(file.relative_to(project_path)))
                            break
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Dependency Injection",
                    category="Architectural",
                    confidence=80,
                    evidence=f"Found dependency injection keywords in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Dependency injection promotes loose coupling and testability.",
                )
            )

        return patterns

    def _detect_mvc_pattern(self, project_path: Path, architecture_result: dict | None) -> list[PatternDetection]:
        """Detect MVC pattern.

        Args:
            project_path: The project path.
            architecture_result: The architecture result.

        Returns:
            List of detected MVC patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for MVC folders
        mvc_folders = ["controller", "model", "view", "views"]
        found_folders = []

        for folder in mvc_folders:
            folder_path = project_path / folder
            if folder_path.exists() and folder_path.is_dir():
                found_folders.append(folder)

        if len(found_folders) >= 2:
            patterns.append(
                PatternDetection(
                    name="MVC Pattern",
                    category="Architectural",
                    confidence=85,
                    evidence=f"Found MVC folders: {', '.join(found_folders)}",
                    affected_files=[],
                    reason="MVC pattern separates concerns into Model, View, and Controller.",
                )
            )

        return patterns

    def _detect_layered_architecture(self, project_path: Path, architecture_result: dict | None) -> list[PatternDetection]:
        """Detect Layered Architecture pattern.

        Args:
            project_path: The project path.
            architecture_result: The architecture result.

        Returns:
            List of detected Layered Architecture patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for layer folders
        layer_folders = ["api", "service", "repository", "data", "domain"]
        found_layers = []

        for folder in layer_folders:
            folder_path = project_path / folder
            if folder_path.exists() and folder_path.is_dir():
                found_layers.append(folder)

        if len(found_layers) >= 3:
            patterns.append(
                PatternDetection(
                    name="Layered Architecture",
                    category="Architectural",
                    confidence=90,
                    evidence=f"Found layer folders: {', '.join(found_layers)}",
                    affected_files=[],
                    reason="Layered architecture organizes code into distinct layers.",
                )
            )

        return patterns

    def _detect_strategy_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Strategy pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Strategy patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for strategy keywords
        strategy_keywords = ["Strategy", "strategy", "interface", "abstract"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "strategy" in content.lower() and any(kw in content for kw in strategy_keywords):
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Strategy Pattern",
                    category="Behavioral",
                    confidence=65,
                    evidence=f"Found strategy-related code in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Strategy pattern defines a family of algorithms.",
                )
            )

        return patterns

    def _detect_observer_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Observer pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Observer patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for observer keywords
        observer_keywords = ["Observer", "observer", "subscribe", "notify", "listener"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if any(kw in content for kw in observer_keywords):
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Observer Pattern",
                    category="Behavioral",
                    confidence=70,
                    evidence=f"Found observer-related code in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Observer pattern defines one-to-many dependency.",
                )
            )

        return patterns

    def _detect_decorator_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Decorator pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Decorator patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for decorator keywords
        decorator_keywords = ["@decorator", "Decorator", "wrapper", "wrap"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if any(kw in content for kw in decorator_keywords):
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Decorator Pattern",
                    category="Structural",
                    confidence=75,
                    evidence=f"Found decorator-related code in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Decorator pattern adds behavior to objects dynamically.",
                )
            )

        return patterns

    def _detect_facade_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Facade pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Facade patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for facade keywords
        facade_keywords = ["Facade", "facade", "client", "simplify"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "facade" in content.lower():
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Facade Pattern",
                    category="Structural",
                    confidence=70,
                    evidence=f"Found facade-related code in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Facade pattern provides simplified interface to complex subsystem.",
                )
            )

        return patterns

    def _detect_adapter_pattern(self, project_path: Path, parsing_result: Any | None) -> list[PatternDetection]:
        """Detect Adapter pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Adapter patterns.
        """
        patterns: list[PatternDetection] = []

        # Look for adapter keywords
        adapter_keywords = ["Adapter", "adapter", "convert", "transform"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "adapter" in content.lower():
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            patterns.append(
                PatternDetection(
                    name="Adapter Pattern",
                    category="Structural",
                    confidence=70,
                    evidence=f"Found adapter-related code in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    reason="Adapter pattern allows incompatible interfaces to work together.",
                )
            )

        return patterns


pattern_detector = PatternDetector()
