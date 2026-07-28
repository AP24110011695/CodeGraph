"""License detector for license compliance analyzer.

Detects licenses from repository files and dependency manifests.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class LicenseInfo:
    """Information about a detected license."""

    license_name: str
    source: str
    file_path: str = ""
    confidence: float = 1.0


class LicenseDetector:
    """Detects licenses from repository files and dependency manifests.

    Reuses existing scanner and framework detector results.
    """

    # Common license file names
    LICENSE_FILES = [
        "LICENSE",
        "LICENSE.md",
        "LICENSE.txt",
        "LICENSE.rst",
        "COPYING",
        "COPYING.md",
        "COPYING.txt",
        "NOTICE",
        "NOTICE.md",
        "NOTICE.txt",
        "LICENSE-MIT",
        "LICENSE-APACHE",
        "LICENSE-BSD",
    ]

    # Common license patterns
    LICENSE_PATTERNS = {
        "MIT": [
            "MIT License",
            "MIT",
            "Permission is hereby granted",
            "The MIT License (MIT)",
        ],
        "Apache-2.0": [
            "Apache License",
            "Apache-2.0",
            "Apache License 2.0",
            "http://www.apache.org/licenses/LICENSE-2.0",
        ],
        "GPL-3.0": [
            "GNU General Public License",
            "GPL-3.0",
            "GNU GPL",
            "Lesser General Public License",
        ],
        "BSD-3-Clause": [
            "BSD License",
            "BSD 3-Clause",
            "Redistribution and use in source and binary forms",
        ],
        "BSD-2-Clause": [
            "BSD 2-Clause",
            "Redistribution and use in source and compiled form",
        ],
        "ISC": [
            "ISC License",
            "ISC",
            "Permission to use, copy, modify, and/or distribute",
        ],
        "MPL-2.0": [
            "Mozilla Public License",
            "MPL-2.0",
            "Mozilla Public License 2.0",
        ],
        "LGPL-3.0": [
            "Lesser General Public License",
            "LGPL-3.0",
            "GNU Lesser General Public License",
        ],
        "AGPL-3.0": [
            "GNU Affero General Public License",
            "AGPL-3.0",
            "Affero General Public License",
        ],
        "Unlicense": [
            "The Unlicense",
            "Unlicense",
            "This is free and unencumbered software",
        ],
    }

    def __init__(self):
        """Initialize the license detector."""
        pass

    def detect_repository_license(self, project_path: Path) -> LicenseInfo | None:
        """Detect the repository license from LICENSE files.

        Args:
            project_path: Path to the project directory.

        Returns:
            LicenseInfo if detected, None otherwise.
        """
        project_path = project_path.resolve()

        # Check for common license files
        for license_file in self.LICENSE_FILES:
            file_path = project_path / license_file
            if file_path.exists():
                license_name = self._detect_license_from_file(file_path)
                if license_name:
                    return LicenseInfo(
                        license_name=license_name,
                        source="repository",
                        file_path=str(file_path.relative_to(project_path)),
                        confidence=0.9,
                    )

        # Check for license in package.json (JavaScript/TypeScript)
        package_json = project_path / "package.json"
        if package_json.exists():
            license_name = self._detect_license_from_package_json(package_json)
            if license_name:
                return LicenseInfo(
                    license_name=license_name,
                    source="package.json",
                    file_path="package.json",
                    confidence=0.8,
                )

        # Check for license in setup.py or pyproject.toml (Python)
        for config_file in ["setup.py", "pyproject.toml", "setup.cfg"]:
            config_path = project_path / config_file
            if config_path.exists():
                license_name = self._detect_license_from_python_config(config_path)
                if license_name:
                    return LicenseInfo(
                        license_name=license_name,
                        source=config_file,
                        file_path=config_file,
                        confidence=0.8,
                    )

        # Check for license in pom.xml (Java)
        pom_xml = project_path / "pom.xml"
        if pom_xml.exists():
            license_name = self._detect_license_from_pom_xml(pom_xml)
            if license_name:
                return LicenseInfo(
                    license_name=license_name,
                    source="pom.xml",
                    file_path="pom.xml",
                    confidence=0.8,
                )

        # Check for license in Cargo.toml (Rust)
        cargo_toml = project_path / "Cargo.toml"
        if cargo_toml.exists():
            license_name = self._detect_license_from_cargo_toml(cargo_toml)
            if license_name:
                return LicenseInfo(
                    license_name=license_name,
                    source="Cargo.toml",
                    file_path="Cargo.toml",
                    confidence=0.8,
                )

        # Check for license in go.mod (Go)
        go_mod = project_path / "go.mod"
        if go_mod.exists():
            return LicenseInfo(
                license_name="Unknown",
                source="go.mod",
                file_path="go.mod",
                confidence=0.5,
            )

        return None

    def detect_dependency_licenses(self, project_path: Path) -> dict[str, str]:
        """Detect licenses from dependency manifests.

        Args:
            project_path: Path to the project directory.

        Returns:
            Dictionary mapping dependency names to license names.
        """
        project_path = project_path.resolve()
        dependency_licenses: dict[str, str] = {}

        # Python: requirements.txt, pyproject.toml
        for file_name in ["requirements.txt", "pyproject.toml", "setup.py"]:
            file_path = project_path / file_name
            if file_path.exists():
                licenses = self._extract_python_dependency_licenses(file_path)
                dependency_licenses.update(licenses)

        # JavaScript/TypeScript: package.json, yarn.lock, package-lock.json
        for file_name in ["package.json", "yarn.lock", "package-lock.json"]:
            file_path = project_path / file_name
            if file_path.exists():
                licenses = self._extract_js_dependency_licenses(file_path)
                dependency_licenses.update(licenses)

        # Java: pom.xml
        pom_xml = project_path / "pom.xml"
        if pom_xml.exists():
            licenses = self._extract_java_dependency_licenses(pom_xml)
            dependency_licenses.update(licenses)

        # Rust: Cargo.toml
        cargo_toml = project_path / "Cargo.toml"
        if cargo_toml.exists():
            licenses = self._extract_rust_dependency_licenses(cargo_toml)
            dependency_licenses.update(licenses)

        return dependency_licenses

    def _detect_license_from_file(self, file_path: Path) -> str | None:
        """Detect license from file content."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

            # Check for more specific patterns first
            # Apache
            if "apache license" in content or "apache-2.0" in content or "http://www.apache.org/licenses/" in content:
                return "Apache-2.0"

            # GPL
            if "gnu general public license" in content or "gpl-3.0" in content:
                return "GPL-3.0"

            # BSD
            if "bsd 3-clause" in content or "redistribution and use in source and binary forms" in content:
                return "BSD-3-Clause"

            if "bsd 2-clause" in content or "redistribution and use in source and compiled form" in content:
                return "BSD-2-Clause"

            # MIT
            if "mit license" in content or "permission is hereby granted" in content:
                return "MIT"

            # ISC
            if "isc license" in content or "permission to use, copy, modify, and/or distribute" in content:
                return "ISC"

            # MPL
            if "mozilla public license" in content or "mpl-2.0" in content:
                return "MPL-2.0"

            # LGPL
            if "lesser general public license" in content or "lgpl-3.0" in content:
                return "LGPL-3.0"

            # AGPL
            if "gnu affero general public license" in content or "agpl-3.0" in content:
                return "AGPL-3.0"

            # Unlicense
            if "the unlicense" in content or "this is free and unencumbered software" in content:
                return "Unlicense"

            return None
        except Exception as e:
            logger.warning(f"Failed to read license file {file_path}: {e}")
            return None

    def _detect_license_from_package_json(self, file_path: Path) -> str | None:
        """Detect license from package.json."""
        try:
            import json

            content = file_path.read_text(encoding="utf-8")
            data = json.loads(content)

            license_field = data.get("license")
            if license_field:
                if isinstance(license_field, str):
                    return self._normalize_license_name(license_field)
                elif isinstance(license_field, dict):
                    return self._normalize_license_name(license_field.get("type", "Unknown"))

            return None
        except Exception as e:
            logger.warning(f"Failed to parse package.json: {e}")
            return None

    def _detect_license_from_python_config(self, file_path: Path) -> str | None:
        """Detect license from Python config files."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

            # Look for license field
            if "license" in content:
                for license_name in self.LICENSE_PATTERNS.keys():
                    if license_name.lower() in content:
                        return license_name

            return None
        except Exception as e:
            logger.warning(f"Failed to read Python config {file_path}: {e}")
            return None

    def _detect_license_from_pom_xml(self, file_path: Path) -> str | None:
        """Detect license from pom.xml."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

            for license_name in self.LICENSE_PATTERNS.keys():
                if license_name.lower() in content:
                    return license_name

            return None
        except Exception as e:
            logger.warning(f"Failed to read pom.xml: {e}")
            return None

    def _detect_license_from_cargo_toml(self, file_path: Path) -> str | None:
        """Detect license from Cargo.toml."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

            for license_name in self.LICENSE_PATTERNS.keys():
                if license_name.lower() in content:
                    return license_name

            return None
        except Exception as e:
            logger.warning(f"Failed to read Cargo.toml: {e}")
            return None

    def _extract_python_dependency_licenses(self, file_path: Path) -> dict[str, str]:
        """Extract licenses from Python dependency files."""
        licenses: dict[str, str] = {}

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # For requirements.txt, we can't easily determine licenses without external data
            # Return empty dict to indicate unknown licenses
            if file_path.name == "requirements.txt":
                lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
                for line in lines:
                    # Extract package name
                    pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0].strip()
                    if pkg_name:
                        licenses[pkg_name] = "Unknown"

        except Exception as e:
            logger.warning(f"Failed to extract Python dependency licenses: {e}")

        return licenses

    def _extract_js_dependency_licenses(self, file_path: Path) -> dict[str, str]:
        """Extract licenses from JavaScript dependency files."""
        licenses: dict[str, str] = {}

        try:
            import json

            content = file_path.read_text(encoding="utf-8")

            if file_path.name == "package.json":
                data = json.loads(content)
                dependencies = data.get("dependencies", {})
                dev_dependencies = data.get("devDependencies", {})

                for dep_name in list(dependencies.keys()) + list(dev_dependencies.keys()):
                    licenses[dep_name] = "Unknown"  # License info not in package.json

        except Exception as e:
            logger.warning(f"Failed to extract JS dependency licenses: {e}")

        return licenses

    def _extract_java_dependency_licenses(self, file_path: Path) -> dict[str, str]:
        """Extract licenses from Java pom.xml."""
        licenses: dict[str, str] = {}

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Extract artifact IDs as dependency names
            # License info typically not in pom.xml
            if "<artifactId>" in content:
                import re

                artifact_ids = re.findall(r"<artifactId>([^<]+)</artifactId>", content)
                for artifact_id in artifact_ids:
                    licenses[artifact_id] = "Unknown"

        except Exception as e:
            logger.warning(f"Failed to extract Java dependency licenses: {e}")

        return licenses

    def _extract_rust_dependency_licenses(self, file_path: Path) -> dict[str, str]:
        """Extract licenses from Rust Cargo.toml."""
        licenses: dict[str, str] = {}

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Extract dependency names from [dependencies] section
            in_deps = False
            for line in content.split("\n"):
                line = line.strip()
                if line == "[dependencies]":
                    in_deps = True
                elif line.startswith("["):
                    in_deps = False
                elif in_deps and "=" in line:
                    dep_name = line.split("=")[0].strip()
                    if dep_name:
                        licenses[dep_name] = "Unknown"

        except Exception as e:
            logger.warning(f"Failed to extract Rust dependency licenses: {e}")

        return licenses

    def _normalize_license_name(self, license_name: str) -> str:
        """Normalize license name to standard format."""
        license_name = license_name.strip()

        # Map common variations to standard names
        mappings = {
            "mit": "MIT",
            "apache": "Apache-2.0",
            "apache-2.0": "Apache-2.0",
            "apache 2.0": "Apache-2.0",
            "gpl": "GPL-3.0",
            "gpl-3.0": "GPL-3.0",
            "gpl3": "GPL-3.0",
            "bsd": "BSD-3-Clause",
            "bsd-3": "BSD-3-Clause",
            "bsd-2": "BSD-2-Clause",
            "isc": "ISC",
            "mpl": "MPL-2.0",
            "mpl-2.0": "MPL-2.0",
            "lgpl": "LGPL-3.0",
            "lgpl-3.0": "LGPL-3.0",
            "agpl": "AGPL-3.0",
            "agpl-3.0": "AGPL-3.0",
            "unlicense": "Unlicense",
        }

        normalized = mappings.get(license_name.lower(), license_name)

        # If not in mappings, return as-is but capitalize
        if normalized == license_name:
            return license_name

        return normalized


license_detector = LicenseDetector()
