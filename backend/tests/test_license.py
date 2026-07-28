"""Tests for the License Compliance Analyzer."""

import json
from pathlib import Path

import pytest

from app.license.compliance_checker import ComplianceChecker, ComplianceFinding, ComplianceStatus
from app.license.license_detector import LicenseDetector, LicenseInfo
from app.license.license_engine import LicenseAnalysisResult, LicenseEngine


@pytest.fixture
def license_engine() -> LicenseEngine:
    """Provide a fresh LicenseEngine instance."""
    return LicenseEngine()


@pytest.fixture
def license_detector() -> LicenseDetector:
    """Provide a fresh LicenseDetector instance."""
    return LicenseDetector()


@pytest.fixture
def compliance_checker() -> ComplianceChecker:
    """Provide a fresh ComplianceChecker instance."""
    return ComplianceChecker()


@pytest.fixture
def sample_mit_project(tmp_path: Path) -> Path:
    """Create a sample MIT-licensed project for testing."""
    project = tmp_path / "mit_project"
    project.mkdir()

    # LICENSE file
    (project / "LICENSE").write_text("""
MIT License

Copyright (c) 2024 Test Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""", encoding="utf-8")

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("print('hello')", encoding="utf-8")

    # requirements.txt
    (project / "requirements.txt").write_text("fastapi\nuvicorn", encoding="utf-8")

    return project


@pytest.fixture
def sample_apache_project(tmp_path: Path) -> Path:
    """Create a sample Apache-2.0 licensed project for testing."""
    project = tmp_path / "apache_project"
    project.mkdir()

    # LICENSE file
    (project / "LICENSE").write_text("""
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""", encoding="utf-8")

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("print('hello')", encoding="utf-8")

    return project


@pytest.fixture
def sample_gpl_project(tmp_path: Path) -> Path:
    """Create a sample GPL-3.0 licensed project for testing."""
    project = tmp_path / "gpl_project"
    project.mkdir()

    # LICENSE file
    (project / "LICENSE").write_text("""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
""", encoding="utf-8")

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("print('hello')", encoding="utf-8")

    return project


@pytest.fixture
def sample_bsd_project(tmp_path: Path) -> Path:
    """Create a sample BSD licensed project for testing."""
    project = tmp_path / "bsd_project"
    project.mkdir()

    # LICENSE file
    (project / "LICENSE").write_text("""
BSD 3-Clause License

Copyright (c) 2024, Test Project
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
""", encoding="utf-8")

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("print('hello')", encoding="utf-8")

    return project


@pytest.fixture
def sample_no_license_project(tmp_path: Path) -> Path:
    """Create a sample project without LICENSE for testing."""
    project = tmp_path / "no_license_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("print('hello')", encoding="utf-8")

    return project


@pytest.fixture
def sample_js_project(tmp_path: Path) -> Path:
    """Create a sample JavaScript project with package.json for testing."""
    project = tmp_path / "js_project"
    project.mkdir()

    # package.json with MIT license
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "version": "1.0.0",
        "license": "MIT",
        "dependencies": {
            "react": "^18.0.0",
            "lodash": "^4.17.21"
        }
    }), encoding="utf-8")

    # src/
    src = project / "src"
    src.mkdir()
    (src / "index.js").write_text("console.log('hello');", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


@pytest.fixture
def sample_large_project(tmp_path: Path) -> Path:
    """Create a large project for testing."""
    project = tmp_path / "large_project"
    project.mkdir()

    # LICENSE
    (project / "LICENSE").write_text("MIT License\n\nPermission is hereby granted...", encoding="utf-8")

    # Create many files
    for i in range(100):
        file_path = project / f"file_{i}.py"
        file_path.write_text(f"def func_{i}(): pass\n", encoding="utf-8")

    # requirements.txt with many dependencies
    deps = "\n".join([f"package_{i}>=1.0.0" for i in range(50)])
    (project / "requirements.txt").write_text(deps, encoding="utf-8")

    return project


class TestLicenseDetector:
    """Tests for LicenseDetector."""

    def test_detect_mit_license(self, license_detector: LicenseDetector, sample_mit_project: Path) -> None:
        """Test MIT license detection."""
        license_info = license_detector.detect_repository_license(sample_mit_project)

        assert license_info is not None
        assert license_info.license_name == "MIT"
        assert license_info.source == "repository"

    def test_detect_apache_license(self, license_detector: LicenseDetector, sample_apache_project: Path) -> None:
        """Test Apache-2.0 license detection."""
        license_info = license_detector.detect_repository_license(sample_apache_project)

        assert license_info is not None
        assert license_info.license_name == "Apache-2.0"
        assert license_info.source == "repository"

    def test_detect_gpl_license(self, license_detector: LicenseDetector, sample_gpl_project: Path) -> None:
        """Test GPL-3.0 license detection."""
        license_info = license_detector.detect_repository_license(sample_gpl_project)

        assert license_info is not None
        assert license_info.license_name == "GPL-3.0"
        assert license_info.source == "repository"

    def test_detect_bsd_license(self, license_detector: LicenseDetector, sample_bsd_project: Path) -> None:
        """Test BSD license detection."""
        license_info = license_detector.detect_repository_license(sample_bsd_project)

        assert license_info is not None
        assert license_info.license_name == "BSD-3-Clause"
        assert license_info.source == "repository"

    def test_detect_no_license(self, license_detector: LicenseDetector, sample_no_license_project: Path) -> None:
        """Test project without license."""
        license_info = license_detector.detect_repository_license(sample_no_license_project)

        assert license_info is None

    def test_detect_from_package_json(self, license_detector: LicenseDetector, sample_js_project: Path) -> None:
        """Test license detection from package.json."""
        license_info = license_detector.detect_repository_license(sample_js_project)

        assert license_info is not None
        assert license_info.license_name == "MIT"
        assert license_info.source == "package.json"

    def test_detect_dependency_licenses(self, license_detector: LicenseDetector, sample_mit_project: Path) -> None:
        """Test dependency license detection."""
        dependency_licenses = license_detector.detect_dependency_licenses(sample_mit_project)

        assert isinstance(dependency_licenses, dict)
        # Should detect dependencies from requirements.txt
        assert len(dependency_licenses) > 0


class TestComplianceChecker:
    """Tests for ComplianceChecker."""

    def test_check_compliance_mit_with_unknown_deps(self, compliance_checker: ComplianceChecker) -> None:
        """Test compliance check with MIT license and unknown dependencies."""
        dependency_licenses = {
            "fastapi": "Unknown",
            "uvicorn": "Unknown",
        }

        findings, status = compliance_checker.check_compliance("MIT", dependency_licenses)

        assert status.status == "WARNING"
        assert status.unknown_licenses == 2
        assert len(findings) > 0

    def test_check_compliance_no_repository_license(self, compliance_checker: ComplianceChecker) -> None:
        """Test compliance check without repository license."""
        dependency_licenses = {
            "fastapi": "MIT",
            "uvicorn": "MIT",
        }

        findings, status = compliance_checker.check_compliance(None, dependency_licenses)

        assert status.status == "WARNING"
        assert len(findings) > 0

    def test_check_compliance_license_conflict(self, compliance_checker: ComplianceChecker) -> None:
        """Test compliance check with license conflict."""
        dependency_licenses = {
            "gpl_lib": "GPL-3.0",
        }

        findings, status = compliance_checker.check_compliance("MIT", dependency_licenses)

        assert status.status == "NON_COMPLIANT"
        assert status.conflicts == 1

    def test_check_compliance_copyleft_in_permissive(self, compliance_checker: ComplianceChecker) -> None:
        """Test compliance check with copyleft in permissive project."""
        dependency_licenses = {
            "lgpl_lib": "LGPL-3.0",
        }

        findings, status = compliance_checker.check_compliance("MIT", dependency_licenses)

        # LGPL-3.0 is incompatible with MIT, so it should be NON_COMPLIANT
        assert status.status == "NON_COMPLIANT"
        assert len(findings) > 0

    def test_check_compliance_fully_compliant(self, compliance_checker: ComplianceChecker) -> None:
        """Test fully compliant scenario."""
        dependency_licenses = {
            "fastapi": "MIT",
            "uvicorn": "MIT",
        }

        findings, status = compliance_checker.check_compliance("MIT", dependency_licenses)

        assert status.status == "COMPLIANT"
        assert status.conflicts == 0
        assert status.unknown_licenses == 0


class TestLicenseEngine:
    """Tests for LicenseEngine."""

    def test_analyze_mit_project(self, license_engine: LicenseEngine, sample_mit_project: Path) -> None:
        """Test license analysis for MIT project."""
        result = license_engine.analyze(sample_mit_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "mit_project"
        assert result.repository_license == "MIT"
        assert result.compliance_status in ["COMPLIANT", "WARNING", "NON_COMPLIANT", "UNKNOWN"]

    def test_analyze_apache_project(self, license_engine: LicenseEngine, sample_apache_project: Path) -> None:
        """Test license analysis for Apache project."""
        result = license_engine.analyze(sample_apache_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "apache_project"
        assert result.repository_license == "Apache-2.0"

    def test_analyze_gpl_project(self, license_engine: LicenseEngine, sample_gpl_project: Path) -> None:
        """Test license analysis for GPL project."""
        result = license_engine.analyze(sample_gpl_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "gpl_project"
        assert result.repository_license == "GPL-3.0"

    def test_analyze_bsd_project(self, license_engine: LicenseEngine, sample_bsd_project: Path) -> None:
        """Test license analysis for BSD project."""
        result = license_engine.analyze(sample_bsd_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "bsd_project"
        assert result.repository_license == "BSD-3-Clause"

    def test_analyze_no_license_project(self, license_engine: LicenseEngine, sample_no_license_project: Path) -> None:
        """Test license analysis for project without license."""
        result = license_engine.analyze(sample_no_license_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "no_license_project"
        assert result.repository_license == "Unknown"
        assert result.compliance_status == "WARNING"

    def test_analyze_js_project(self, license_engine: LicenseEngine, sample_js_project: Path) -> None:
        """Test license analysis for JavaScript project."""
        result = license_engine.analyze(sample_js_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "js_project"
        assert result.repository_license == "MIT"

    def test_analyze_empty_project(self, license_engine: LicenseEngine, sample_empty_project: Path) -> None:
        """Test license analysis for empty project."""
        result = license_engine.analyze(sample_empty_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "empty_project"
        assert result.repository_license == "Unknown"

    def test_analyze_large_project(self, license_engine: LicenseEngine, sample_large_project: Path) -> None:
        """Test license analysis for large project."""
        result = license_engine.analyze(sample_large_project)

        assert isinstance(result, LicenseAnalysisResult)
        assert result.project_name == "large_project"
        assert result.repository_license == "MIT"

    def test_analyze_nonexistent_path(self, license_engine: LicenseEngine) -> None:
        """Test license analysis for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            license_engine.analyze(Path("/nonexistent/path"))

    def test_analyze_file_instead_of_directory(self, license_engine: LicenseEngine, tmp_path: Path) -> None:
        """Test license analysis when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            license_engine.analyze(file_path)

    def test_analyze_with_index_manager(self, sample_mit_project: Path) -> None:
        """Test license analysis with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        license_engine = LicenseEngine(index_manager=index_manager)

        result = license_engine.analyze(sample_mit_project)

        assert isinstance(result, LicenseAnalysisResult)

    def test_recommendations_generation(self, license_engine: LicenseEngine, sample_no_license_project: Path) -> None:
        """Test that recommendations are generated."""
        result = license_engine.analyze(sample_no_license_project)

        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0


class TestLicenseAPI:
    """Tests for the license API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_license_not_indexed(self, client) -> None:
        """Test license API for non-indexed repository."""
        response = client.post("/license/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
