"""Tests for the DependencyGraphBuilder."""

import json
from pathlib import Path

import pytest

from app.services.dependency_graph import DependencyGraphBuilder
from app.services.scanner_service import RepositoryScanner


@pytest.fixture
def builder() -> DependencyGraphBuilder:
    return DependencyGraphBuilder()


@pytest.fixture
def scanner() -> RepositoryScanner:
    return RepositoryScanner()


class TestDependencyGraphBuilder:
    def test_javascript_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "js-app"
        project.mkdir()
        
        src = project / "src"
        src.mkdir()
        
        (src / "main.js").write_text(
            "import { logger } from './utils/logger';\n"
            "const config = require('../config');\n"
            "export { setup } from '@/setup.js';\n",
            encoding="utf-8"
        )
        
        utils = src / "utils"
        utils.mkdir()
        (utils / "logger.js").write_text("export const logger = {};", encoding="utf-8")
        
        (project / "config.js").write_text("module.exports = {};", encoding="utf-8")
        (src / "setup.js").write_text("export const setup = {};", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        assert len(graph.nodes) == 4
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("src/main.js", "src/utils/logger.js") in edges
        assert ("src/main.js", "config.js") in edges
        assert ("src/main.js", "src/setup.js") in edges

    def test_python_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "py-app"
        project.mkdir()
        
        (project / "main.py").write_text(
            "import utils.logger\n"
            "from models.user import User\n"
            "from . import helpers\n",
            encoding="utf-8"
        )
        
        utils = project / "utils"
        utils.mkdir()
        (utils / "__init__.py").write_text("", encoding="utf-8")
        (utils / "logger.py").write_text("", encoding="utf-8")
        
        models = project / "models"
        models.mkdir()
        (models / "user.py").write_text("", encoding="utf-8")
        
        (project / "helpers.py").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("main.py", "utils/logger.py") in edges
        assert ("main.py", "models/user.py") in edges
        assert ("main.py", "helpers.py") in edges

    def test_java_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "java-app"
        project.mkdir()
        
        com = project / "com" / "example"
        com.mkdir(parents=True)
        
        (com / "Main.java").write_text(
            "package com.example;\n"
            "import com.example.utils.Logger;\n"
            "import static com.example.Constants.MAX;\n",
            encoding="utf-8"
        )
        
        utils = com / "utils"
        utils.mkdir()
        (utils / "Logger.java").write_text("", encoding="utf-8")
        
        (com / "Constants.java").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("com/example/Main.java", "com/example/utils/Logger.java") in edges
        assert ("com/example/Main.java", "com/example/Constants.java") in edges

    def test_go_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "go-app"
        project.mkdir()
        
        (project / "main.go").write_text(
            'package main\n'
            'import (\n'
            '    "fmt"\n'
            '    "go-app/pkg/utils"\n'
            ')\n'
            'import log "go-app/pkg/logger"\n',
            encoding="utf-8"
        )
        
        pkg = project / "pkg"
        pkg.mkdir()
        
        utils = pkg / "utils"
        utils.mkdir()
        (utils / "utils.go").write_text("", encoding="utf-8")
        
        logger = pkg / "logger"
        logger.mkdir()
        (logger / "logger.go").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("main.go", "pkg/utils/utils.go") in edges
        assert ("main.go", "pkg/logger/logger.go") in edges

    def test_rust_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "rs-app"
        project.mkdir()
        
        (project / "main.rs").write_text(
            "mod utils;\n"
            "use crate::models::User;\n",
            encoding="utf-8"
        )
        
        (project / "utils.rs").write_text("", encoding="utf-8")
        
        models = project / "models"
        models.mkdir()
        (models / "mod.rs").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("main.rs", "utils.rs") in edges
        assert ("main.rs", "models/mod.rs") in edges

    def test_php_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "php-app"
        project.mkdir()
        
        (project / "index.php").write_text(
            "<?php\n"
            "require 'vendor/autoload.php';\n"
            "include_once 'config.php';\n",
            encoding="utf-8"
        )
        
        vendor = project / "vendor"
        vendor.mkdir()
        (vendor / "autoload.php").write_text("", encoding="utf-8")
        
        (project / "config.php").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("index.php", "vendor/autoload.php") in edges
        assert ("index.php", "config.php") in edges

    def test_csharp_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "cs-app"
        project.mkdir()
        
        (project / "Program.cs").write_text(
            "using System;\n"
            "using App.Models;\n",
            encoding="utf-8"
        )
        
        app = project / "App"
        app.mkdir()
        (app / "Models.cs").write_text("", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("Program.cs", "App/Models.cs") in edges

    def test_circular_imports(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "circular"
        project.mkdir()
        
        (project / "a.ts").write_text("import { b } from './b';", encoding="utf-8")
        (project / "b.ts").write_text("import { a } from './a';", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        edges = {(e.from_node, e.to_node) for e in graph.edges}
        assert ("a.ts", "b.ts") in edges
        assert ("b.ts", "a.ts") in edges
        assert graph.isolated_files == 0

    def test_unreadable_and_malformed_files(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "bad-files"
        project.mkdir()
        
        # Valid file
        (project / "main.py").write_text("import bad\nimport malformed", encoding="utf-8")
        
        # Unreadable encoding (binary pretending to be text)
        bad_file = project / "bad.py"
        bad_file.write_bytes(b"\xff\xfe\x00\x00")
        
        # Malformed source code (syntax error, but regex shouldn't care)
        (project / "malformed.py").write_text("import {;;;; \n import nothing", encoding="utf-8")
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        # Regex handles malformed text without crashing
        assert len(graph.nodes) == 3
        # valid edges because bad.py and malformed.py exist
        assert len(graph.edges) == 2

    def test_isolated_files_count(self, builder: DependencyGraphBuilder, scanner: RepositoryScanner, tmp_path: Path) -> None:
        project = tmp_path / "isolated"
        project.mkdir()
        
        (project / "a.js").write_text("import './b.js';", encoding="utf-8")
        (project / "b.js").write_text("", encoding="utf-8")
        (project / "c.js").write_text("", encoding="utf-8") # Isolated
        (project / "d.js").write_text("", encoding="utf-8") # Isolated
        
        scan_result = scanner.scan(project)
        graph = builder.build(project, scan_result)
        
        assert graph.isolated_files == 2
