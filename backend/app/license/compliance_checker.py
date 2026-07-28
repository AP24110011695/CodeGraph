"""Compliance checker for license compliance analyzer.

Checks license compatibility and identifies potential conflicts.
"""

import logging
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class ComplianceFinding:
    """A license compliance finding."""

    title: str
    category: str
    severity: str
    compliance_status: str
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ComplianceStatus:
    """Overall compliance status."""

    status: Literal["COMPLIANT", "WARNING", "NON_COMPLIANT", "UNKNOWN"]
    licensed_dependencies: int = 0
    unknown_licenses: int = 0
    conflicts: int = 0


class ComplianceChecker:
    """Checks license compatibility and identifies potential conflicts.

    Reuses existing dependency information from dependency graph and framework detector.
    """

    # License compatibility matrix (simplified)
    # True = compatible, False = potentially incompatible
    COMPATIBILITY_MATRIX = {
        "MIT": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "Apache-2.0": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "BSD-3-Clause": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "BSD-2-Clause": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "ISC": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "MPL-2.0": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "LGPL-3.0": {"MIT": False, "Apache-2.0": False, "BSD-3-Clause": False, "BSD-2-Clause": False, "ISC": False, "MPL-2.0": False, "LGPL-3.0": True, "GPL-3.0": True, "AGPL-3.0": False, "Unlicense": False, "Unknown": False},
        "GPL-3.0": {"MIT": False, "Apache-2.0": False, "BSD-3-Clause": False, "BSD-2-Clause": False, "ISC": False, "MPL-2.0": False, "LGPL-3.0": True, "GPL-3.0": True, "AGPL-3.0": True, "Unlicense": False, "Unknown": False},
        "AGPL-3.0": {"MIT": False, "Apache-2.0": False, "BSD-3-Clause": False, "BSD-2-Clause": False, "ISC": False, "MPL-2.0": False, "LGPL-3.0": False, "GPL-3.0": True, "AGPL-3.0": True, "Unlicense": False, "Unknown": False},
        "Unlicense": {"MIT": True, "Apache-2.0": True, "BSD-3-Clause": True, "BSD-2-Clause": True, "ISC": True, "MPL-2.0": True, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": True, "Unknown": False},
        "Unknown": {"MIT": False, "Apache-2.0": False, "BSD-3-Clause": False, "BSD-2-Clause": False, "ISC": False, "MPL-2.0": False, "LGPL-3.0": False, "GPL-3.0": False, "AGPL-3.0": False, "Unlicense": False, "Unknown": False},
    }

    def __init__(self):
        """Initialize the compliance checker."""
        pass

    def check_compliance(
        self,
        repository_license: str | None,
        dependency_licenses: dict[str, str],
    ) -> tuple[list[ComplianceFinding], ComplianceStatus]:
        """Check license compliance for the repository.

        Args:
            repository_license: The repository's license.
            dependency_licenses: Dictionary mapping dependency names to license names.

        Returns:
            Tuple of (findings, compliance_status).
        """
        findings: list[ComplianceFinding] = []

        # Check for missing repository license
        if not repository_license:
            findings.append(ComplianceFinding(
                title="Missing Repository License",
                category="Repository",
                severity="Medium",
                compliance_status="WARNING",
                evidence="No LICENSE file or license declaration found in the repository.",
                affected_files=[],
                recommendation="Add a LICENSE file to specify the repository's license.",
            ))

        # Check for unknown dependency licenses
        unknown_deps = {name: lic for name, lic in dependency_licenses.items() if lic == "Unknown"}
        if unknown_deps:
            findings.append(ComplianceFinding(
                title=f"Unknown Dependency Licenses ({len(unknown_deps)})",
                category="Dependency",
                severity="Medium",
                compliance_status="WARNING",
                evidence=f"{len(unknown_deps)} dependencies have unknown or undetected licenses.",
                affected_files=list(unknown_deps.keys())[:10],
                recommendation="Verify the licenses of these dependencies before distribution.",
            ))

        # Check for license conflicts
        if repository_license:
            conflicts = self._check_license_conflicts(repository_license, dependency_licenses)
            for dep_name, dep_license in conflicts:
                findings.append(ComplianceFinding(
                    title=f"Potential License Conflict: {dep_name}",
                    category="Compatibility",
                    severity="High",
                    compliance_status="NON_COMPLIANT",
                    evidence=f"Repository license ({repository_license}) may be incompatible with dependency license ({dep_license}).",
                    affected_files=[dep_name],
                    recommendation="Review the license compatibility or consider replacing the dependency.",
                ))

        # Check for copyleft licenses in permissive projects
        if repository_license in ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"]:
            copyleft_deps = {name: lic for name, lic in dependency_licenses.items() if lic in ["GPL-3.0", "AGPL-3.0", "LGPL-3.0"]}
            if copyleft_deps:
                findings.append(ComplianceFinding(
                    title=f"Copyleft Dependencies in Permissive Project ({len(copyleft_deps)})",
                    category="Compatibility",
                    severity="Medium",
                    compliance_status="WARNING",
                    evidence=f"Project uses permissive license ({repository_license}) but has {len(copyleft_deps)} copyleft dependencies.",
                    affected_files=list(copyleft_deps.keys())[:10],
                    recommendation="Review the implications of copyleft licenses on your project's licensing.",
                ))

        # Determine overall compliance status
        status = self._determine_compliance_status(findings, repository_license, dependency_licenses)

        return findings, status

    def _check_license_conflicts(self, repository_license: str, dependency_licenses: dict[str, str]) -> list[tuple[str, str]]:
        """Check for license conflicts between repository and dependencies.

        Args:
            repository_license: The repository's license.
            dependency_licenses: Dictionary mapping dependency names to license names.

        Returns:
            List of (dependency_name, dependency_license) tuples with potential conflicts.
        """
        conflicts = []

        for dep_name, dep_license in dependency_licenses.items():
            if dep_license == "Unknown":
                continue

            # Check compatibility matrix
            repo_compat = self.COMPATIBILITY_MATRIX.get(repository_license, {})
            is_compatible = repo_compat.get(dep_license, False)

            if not is_compatible:
                conflicts.append((dep_name, dep_license))

        return conflicts

    def _determine_compliance_status(
        self,
        findings: list[ComplianceFinding],
        repository_license: str | None,
        dependency_licenses: dict[str, str],
    ) -> ComplianceStatus:
        """Determine overall compliance status.

        Args:
            findings: List of compliance findings.
            repository_license: The repository's license.
            dependency_licenses: Dictionary mapping dependency names to license names.

        Returns:
            ComplianceStatus object.
        """
        licensed_count = len([lic for lic in dependency_licenses.values() if lic != "Unknown"])
        unknown_count = len([lic for lic in dependency_licenses.values() if lic == "Unknown"])
        conflict_count = len([f for f in findings if f.compliance_status == "NON_COMPLIANT"])

        if not repository_license:
            return ComplianceStatus(
                status="WARNING",
                licensed_dependencies=licensed_count,
                unknown_licenses=unknown_count,
                conflicts=conflict_count,
            )

        if conflict_count > 0:
            return ComplianceStatus(
                status="NON_COMPLIANT",
                licensed_dependencies=licensed_count,
                unknown_licenses=unknown_count,
                conflicts=conflict_count,
            )

        if unknown_count > 0:
            return ComplianceStatus(
                status="WARNING",
                licensed_dependencies=licensed_count,
                unknown_licenses=unknown_count,
                conflicts=conflict_count,
            )

        return ComplianceStatus(
            status="COMPLIANT",
            licensed_dependencies=licensed_count,
            unknown_licenses=unknown_count,
            conflicts=conflict_count,
        )


compliance_checker = ComplianceChecker()
