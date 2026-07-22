"""Tests for the FrameworkDetector service."""

import json
from pathlib import Path

import pytest

from app.services.framework_detector import FrameworkDetector
from app.services.scanner_service import RepositoryScanner


@pytest.fixture
def detector() -> FrameworkDetector:
    return FrameworkDetector()


@pytest.fixture
def scanner() -> RepositoryScanner:
    return RepositoryScanner()


class TestFrameworkDetector:
    def test_react_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "react-app"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^18.2.0"}}), encoding="utf-8"
        )
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(f.name == "React" and f.confidence == 95 for f in result.frameworks)
        assert "npm" not in result.package_managers # no lock file

    def test_nextjs_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "next-app"
        project.mkdir()
        (project / "next.config.js").write_text("module.exports = {};", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(f.name == "Next.js" and f.confidence == 100 for f in result.frameworks)

    def test_vue_angular_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "multi-app"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps({"dependencies": {"vue": "^3.0.0", "@angular/core": "^15.0.0"}}), encoding="utf-8"
        )
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(f.name == "Vue" and f.confidence == 95 for f in result.frameworks)
        assert any(f.name == "Angular" and f.confidence == 95 for f in result.frameworks)

    def test_fastapi_flask_django_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "py-app"
        project.mkdir()
        (project / "requirements.txt").write_text("fastapi\nflask\nDjango==4.0.0", encoding="utf-8")
        (project / "manage.py").write_text("# django manage.py", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(b.name == "FastAPI" and b.confidence == 95 for b in result.backend)
        assert any(b.name == "Flask" and b.confidence == 95 for b in result.backend)
        assert any(b.name == "Django" and b.confidence == 95 for b in result.backend) # Dep confidence wins over text match
        assert "pip" in result.package_managers

    def test_express_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "express-app"
        project.mkdir()
        (project / "package.json").write_text(
            json.dumps({"dependencies": {"express": "^4.18.2"}}), encoding="utf-8"
        )
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(b.name == "Express" and b.confidence == 95 for b in result.backend)

    def test_spring_boot_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "spring-app"
        project.mkdir()
        (project / "pom.xml").write_text("<dependency><artifactId>spring-boot-starter-web</artifactId></dependency>", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(b.name == "Spring Boot" and b.confidence == 80 for b in result.backend)
        assert "maven" in result.package_managers

    def test_cargo_rust(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "rust-app"
        project.mkdir()
        (project / "Cargo.toml").write_text("[package]\nname = \"rust-app\"", encoding="utf-8")
        (project / "main.rs").write_text("fn main() {}", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert "cargo" in result.package_managers
        assert "rust" in result.parser_targets

    def test_composer_laravel(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "php-app"
        project.mkdir()
        (project / "composer.json").write_text(
            json.dumps({"require": {"laravel/framework": "^10.0"}}), encoding="utf-8"
        )
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(b.name == "Laravel" and b.confidence == 95 for b in result.backend)
        assert "composer" in result.package_managers

    def test_docker_detection(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "docker-app"
        project.mkdir()
        (project / "Dockerfile").write_text("FROM node:18", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert result.containerized is True

    def test_malformed_configs(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "malformed"
        project.mkdir()
        (project / "package.json").write_text("{malformed-json", encoding="utf-8")
        (project / "pyproject.toml").write_text("[malformed-toml", encoding="utf-8")
        (project / "pom.xml").write_text("<malformed-xml", encoding="utf-8") # Read as text, won't break
        (project / "pnpm-lock.yaml").write_text("malformed-yaml: [", encoding="utf-8") # Checks presence, not content
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        # Should handle gracefully without crashing
        assert len(result.frameworks) == 0
        assert "pnpm" in result.package_managers

    def test_unknown_repository(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "empty"
        project.mkdir()
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert len(result.frameworks) == 0
        assert len(result.backend) == 0
        assert len(result.package_managers) == 0
        assert result.containerized is False

    def test_monorepo(self, detector: FrameworkDetector, scanner: RepositoryScanner, tmp_path: Path) -> None:
        # Note: detector is currently root-level only by design.
        # This test ensures it doesn't crash on a monorepo structure.
        project = tmp_path / "monorepo"
        project.mkdir()
        apps = project / "apps"
        apps.mkdir()
        (apps / "package.json").write_text("{}", encoding="utf-8")
        
        (project / "package.json").write_text(
            json.dumps({"dependencies": {"next": "13.0"}}), encoding="utf-8"
        )
        
        scan_result = scanner.scan(project)
        result = detector.detect(project, scan_result)

        assert any(f.name == "Next.js" for f in result.frameworks)
