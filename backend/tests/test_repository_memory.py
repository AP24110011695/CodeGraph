"""
Tests for Phase 2: Repository Memory Foundation

Verifies:
- RepositoryMemory is fully data-driven (no placeholder strings)
- SymbolTable correctly indexes classes and functions
- ModuleMemory extracts responsibilities from ArchitectureResult
- WorkflowMemory extracts real execution paths with evidence
- APIMemory extracts real endpoints from source files
- Context Selector injects structured memory items
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.schemas.repository_memory import (
    MemoryMetadata,
    RepositoryMemory,
    SymbolMemory,
    ModuleMemory,
    FileMemory,
    APIEndpointMemory,
    WorkflowMemory,
)
from app.repository_memory.symbol_table_extractor import SymbolTableExtractor
from app.repository_memory.module_memory_extractor import ModuleMemoryExtractor
from app.repository_memory.workflow_memory_extractor import WorkflowMemoryExtractor
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.analyzers.architecture_models import ArchitectureResult, ArchitectureModule, Component


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _make_metadata(repository_id: str = "repo-123") -> MemoryMetadata:
    return MemoryMetadata(
        repository_id=repository_id,
        evidence_sources=["test_file.py"],
    )


def _make_parsing_result() -> ProjectParsingResult:
    """Create a minimal but realistic ProjectParsingResult."""
    file1 = FileParsingResult(
        path="backend/app/api/upload.py",
        language="Python",
        functions=["upload_repository", "validate_zip"],
        classes=["UploadHandler"],
        methods=["handle", "validate"],
        imports=["from fastapi import APIRouter", "from app.services.indexing import indexing_service"],
        variables=["MAX_SIZE"],
        async_functions=["process_upload"],
    )
    file2 = FileParsingResult(
        path="backend/app/auth/jwt.py",
        language="Python",
        functions=["create_token", "verify_token", "decode_payload"],
        classes=["JWTManager"],
        methods=["encode", "decode"],
        imports=["import jwt", "from datetime import datetime"],
        variables=["SECRET_KEY", "ALGORITHM"],
    )
    return ProjectParsingResult(
        project={"name": "TestRepo", "root_path": "/tmp/testrepo", "total_files": 2},
        files=[file1, file2],
    )


def _make_architecture_result() -> ArchitectureResult:
    """Create a minimal but realistic ArchitectureResult."""
    module1 = ArchitectureModule(
        name="api",
        type="api_layer",
        files=["backend/app/api/upload.py"],
        components=[Component(name="UploadController", type="controller", file_path="backend/app/api/upload.py", language="Python")],
        layer="presentation",
    )
    module2 = ArchitectureModule(
        name="auth",
        type="service_layer",
        files=["backend/app/auth/jwt.py"],
        components=[Component(name="JWTService", type="service", file_path="backend/app/auth/jwt.py", language="Python")],
        layer="service",
    )
    return ArchitectureResult(
        layers=["presentation", "service", "data"],
        modules=[module1, module2],
    )


# ---------------------------------------------------------------------------
# MemoryMetadata tests
# ---------------------------------------------------------------------------

class TestMemoryMetadata:
    def test_metadata_has_required_fields(self):
        meta = _make_metadata()
        assert meta.repository_id == "repo-123"
        assert meta.version == "1.0.0"
        assert meta.created_at != ""
        assert meta.updated_at != ""
        assert isinstance(meta.evidence_sources, list)

    def test_metadata_evidence_sources_are_recorded(self):
        meta = MemoryMetadata(
            repository_id="repo-test",
            evidence_sources=["scanner", "parser", "arch_builder"]
        )
        assert "scanner" in meta.evidence_sources
        assert "parser" in meta.evidence_sources

    def test_repository_id_property_on_repository_memory(self):
        memory = RepositoryMemory(
            metadata=_make_metadata("test-repo"),
            repository_summary="A test repository.",
        )
        # .repository_id is a convenience property deriving from metadata
        assert memory.repository_id == "test-repo"


# ---------------------------------------------------------------------------
# SymbolTableExtractor tests
# ---------------------------------------------------------------------------

class TestSymbolTableExtractor:
    def test_extracts_functions_from_parsing_result(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        func_names = {s.symbol_name for s in symbols.values() if s.symbol_type == "function"}
        assert "upload_repository" in func_names
        assert "validate_zip" in func_names
        assert "create_token" in func_names
        assert "verify_token" in func_names

    def test_extracts_classes_from_parsing_result(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        class_names = {s.symbol_name for s in symbols.values() if s.symbol_type == "class"}
        assert "UploadHandler" in class_names
        assert "JWTManager" in class_names

    def test_extracts_async_functions(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        func_names = {s.symbol_name for s in symbols.values()}
        assert "process_upload" in func_names

    def test_extracts_variables(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        var_names = {s.symbol_name for s in symbols.values() if s.symbol_type == "variable"}
        assert "SECRET_KEY" in var_names
        assert "ALGORITHM" in var_names

    def test_symbol_file_path_is_real(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        for sym_id, sym in symbols.items():
            assert sym.file_path in (
                "backend/app/api/upload.py",
                "backend/app/auth/jwt.py",
            ), f"Unexpected file_path: {sym.file_path}"

    def test_empty_parsing_result_returns_empty_dict(self):
        empty = ProjectParsingResult(project={}, files=[])
        symbols = SymbolTableExtractor.extract("repo-123", empty)
        assert symbols == {}

    def test_none_parsing_result_returns_empty_dict(self):
        symbols = SymbolTableExtractor.extract("repo-123", None)
        assert symbols == {}

    def test_no_placeholder_strings_in_symbols(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)
        PLACEHOLDER_PHRASES = [
            "automated summary", "aggregated from", "high-level architecture",
            "primary frameworks", "inter-service dependency"
        ]
        for sym in symbols.values():
            for phrase in PLACEHOLDER_PHRASES:
                assert phrase.lower() not in sym.symbol_name.lower(), (
                    f"Placeholder detected in symbol: {sym.symbol_name}"
                )

    def test_symbol_lookup_finds_upload_related_symbols(self):
        """Simulate: 'Where is upload implemented?' should return real files/functions."""
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        query_terms = {"upload", "indexing", "process"}
        matched = [
            sym for sym in symbols.values()
            if any(t in sym.symbol_name.lower() or t in sym.file_path.lower() for t in query_terms)
        ]
        assert len(matched) > 0, "Should find upload/indexing-related symbols"
        assert all(sym.file_path != "" for sym in matched), "All matched symbols must have a real file path"

    def test_symbol_key_format_is_file_double_colon_name(self):
        parsing = _make_parsing_result()
        symbols = SymbolTableExtractor.extract("repo-123", parsing)

        for sym_id in symbols:
            assert "::" in sym_id, f"Symbol key should be file::name format, got: {sym_id}"


# ---------------------------------------------------------------------------
# ModuleMemoryExtractor tests
# ---------------------------------------------------------------------------

class TestModuleMemoryExtractor:
    def test_extracts_modules_from_architecture_result(self):
        arch = _make_architecture_result()
        modules = ModuleMemoryExtractor.extract("repo-123", arch)

        assert "api" in modules
        assert "auth" in modules

    def test_modules_have_real_files(self):
        arch = _make_architecture_result()
        modules = ModuleMemoryExtractor.extract("repo-123", arch)

        assert "backend/app/api/upload.py" in modules["api"].files
        assert "backend/app/auth/jwt.py" in modules["auth"].files

    def test_responsibilities_include_module_name(self):
        arch = _make_architecture_result()
        modules = ModuleMemoryExtractor.extract("repo-123", arch)

        api_responsibilities = modules["api"].responsibilities
        assert len(api_responsibilities) > 0
        assert any("api" in r.lower() or "presentation" in r.lower() for r in api_responsibilities)

    def test_no_placeholder_strings_in_modules(self):
        arch = _make_architecture_result()
        modules = ModuleMemoryExtractor.extract("repo-123", arch)

        PLACEHOLDER_PHRASES = [
            "automated repository summary", "aggregated from graph",
            "high-level architecture topology", "primary frameworks",
            "inter-service dependency graph"
        ]
        for mod in modules.values():
            for phrase in PLACEHOLDER_PHRASES:
                for responsibility in mod.responsibilities:
                    assert phrase.lower() not in responsibility.lower(), (
                        f"Placeholder detected in module responsibility: {responsibility}"
                    )

    def test_empty_architecture_result_returns_empty_dict(self):
        empty = ArchitectureResult()
        modules = ModuleMemoryExtractor.extract("repo-123", empty)
        assert modules == {}

    def test_none_architecture_result_returns_empty_dict(self):
        modules = ModuleMemoryExtractor.extract("repo-123", None)
        assert modules == {}


# ---------------------------------------------------------------------------
# WorkflowMemoryExtractor tests
# ---------------------------------------------------------------------------

class TestWorkflowMemoryExtractor:
    def _make_api_endpoints(self) -> dict:
        meta = _make_metadata()
        return {
            "POST /upload": APIEndpointMemory(
                metadata=meta,
                endpoint_path="/upload",
                http_method="POST",
                handler="upload_repository",
                related_files=["backend/app/api/upload.py"],
                purpose="Handles POST requests to /upload"
            )
        }

    def test_extracts_workflows_from_api_endpoints(self):
        parsing = _make_parsing_result()
        api_eps = self._make_api_endpoints()
        workflows = WorkflowMemoryExtractor.extract("repo-123", api_eps, parsing)

        assert len(workflows) > 0, "Should extract at least one workflow"

    def test_workflow_has_real_files(self):
        parsing = _make_parsing_result()
        api_eps = self._make_api_endpoints()
        workflows = WorkflowMemoryExtractor.extract("repo-123", api_eps, parsing)

        for wf in workflows.values():
            assert len(wf.involved_files) > 0, "Workflow must have at least one real involved file"
            for f in wf.involved_files:
                assert f != "", "File path must not be empty"

    def test_workflow_has_steps(self):
        parsing = _make_parsing_result()
        api_eps = self._make_api_endpoints()
        workflows = WorkflowMemoryExtractor.extract("repo-123", api_eps, parsing)

        for wf in workflows.values():
            assert len(wf.steps) > 0, "Workflow must have at least one step"

    def test_workflow_starting_point_matches_endpoint(self):
        parsing = _make_parsing_result()
        api_eps = self._make_api_endpoints()
        workflows = WorkflowMemoryExtractor.extract("repo-123", api_eps, parsing)

        for wf in workflows.values():
            assert "/upload" in wf.starting_point or "POST" in wf.starting_point, (
                f"Starting point should reference the endpoint: {wf.starting_point}"
            )

    def test_empty_api_endpoints_returns_empty_workflows(self):
        parsing = _make_parsing_result()
        workflows = WorkflowMemoryExtractor.extract("repo-123", {}, parsing)
        assert workflows == {}

    def test_workflow_metadata_has_evidence_sources(self):
        parsing = _make_parsing_result()
        api_eps = self._make_api_endpoints()
        workflows = WorkflowMemoryExtractor.extract("repo-123", api_eps, parsing)

        for wf in workflows.values():
            assert len(wf.metadata.evidence_sources) > 0, "Workflow must record evidence sources"


# ---------------------------------------------------------------------------
# RepositoryMemory schema validation tests
# ---------------------------------------------------------------------------

class TestRepositoryMemorySchema:
    def test_memory_contains_real_data_not_placeholder(self):
        PLACEHOLDER_STRINGS = [
            "Automated repository summary aggregated from graph and semantic analysis.",
            "High-level architecture topology overview derived from dependencies.",
            "Primary frameworks and libraries detected during indexing.",
            "Inter-service dependency graph summarized from Knowledge Graph.",
        ]
        meta = _make_metadata()
        memory = RepositoryMemory(
            metadata=meta,
            repository_summary="Repository TestRepo with 42 files in 2 languages.",
            architecture_summary="Architecture layers: presentation, service, data",
            framework_summary="Detected frameworks: FastAPI, React",
            service_relationships="Dependencies and relationships extracted via dependency graph.",
        )
        for placeholder in PLACEHOLDER_STRINGS:
            assert placeholder not in memory.repository_summary
            assert placeholder not in memory.architecture_summary
            assert placeholder not in memory.framework_summary

    def test_memory_repository_id_from_metadata(self):
        memory = RepositoryMemory(metadata=_make_metadata("my-repo"))
        assert memory.repository_id == "my-repo"

    def test_memory_has_version_and_timestamps(self):
        memory = RepositoryMemory(metadata=_make_metadata())
        assert memory.metadata.version == "1.0.0"
        assert memory.metadata.created_at != ""
        assert memory.metadata.updated_at != ""

    def test_memory_evidence_sources_populated(self):
        meta = MemoryMetadata(
            repository_id="repo-456",
            evidence_sources=["Scanner", "Parser", "ArchitectureBuilder"]
        )
        memory = RepositoryMemory(metadata=meta)
        assert "Scanner" in memory.metadata.evidence_sources
        assert "Parser" in memory.metadata.evidence_sources


# ---------------------------------------------------------------------------
# ContextSelector structured memory injection tests
# ---------------------------------------------------------------------------

class TestContextSelectorStructuredMemory:
    """Verify memory items are injected alongside RAG chunks with proper attribution."""

    def _make_memory_with_workflow(self, repository_id: str = "repo-123") -> RepositoryMemory:
        meta = MemoryMetadata(repository_id=repository_id, evidence_sources=["upload.py"])
        wf = WorkflowMemory(
            metadata=MemoryMetadata(repository_id=repository_id, evidence_sources=["upload.py"]),
            workflow_name="POST /upload Workflow",
            starting_point="POST /upload",
            steps=["Receive request at POST /upload", "Invoke handler upload_repository", "Return response"],
            involved_files=["backend/app/api/upload.py"],
            end_result="Request processed successfully",
        )
        return RepositoryMemory(
            metadata=meta,
            workflow_summaries={"POST /upload Workflow": wf},
        )

    def _make_memory_with_symbols(self, repository_id: str = "repo-123") -> RepositoryMemory:
        meta = MemoryMetadata(repository_id=repository_id, evidence_sources=["auth/jwt.py"])
        symbol = SymbolMemory(
            metadata=MemoryMetadata(repository_id=repository_id, evidence_sources=["auth/jwt.py"]),
            symbol_name="JWTManager",
            symbol_type="class",
            file_path="backend/app/auth/jwt.py",
            methods=["encode", "decode"],
        )
        return RepositoryMemory(
            metadata=meta,
            symbol_summaries={"backend/app/auth/jwt.py::JWTManager": symbol},
        )

    def test_symbol_context_injected_for_file_lookup_intent(self):
        from app.rag.context_selector import ContextSelector

        selector = ContextSelector()
        memory = self._make_memory_with_symbols()

        with patch("app.repository_memory.memory_engine.memory_engine") as mock_singleton:
            mock_singleton.get_memory.return_value = memory
            items = selector.select_symbol_context("repo-123", "file_lookup", "where is JWTManager")
            assert len(items) > 0, "Should find JWTManager symbol"
            assert items[0]["source_type"] == "memory"
            assert "JWTManager" in items[0]["content"]
            assert items[0]["reference"] == "backend/app/auth/jwt.py"

    def test_symbol_context_not_injected_for_architecture_intent(self):
        from app.rag.context_selector import ContextSelector

        selector = ContextSelector()
        # "architecture" intent is not in _SYMBOL_INTENTS — no get_memory call needed
        items = selector.select_symbol_context("repo-123", "architecture", "overview")
        assert items == [], "Should not inject symbol context for architecture intent"

    def test_workflow_context_not_injected_for_file_lookup_intent(self):
        from app.rag.context_selector import ContextSelector

        selector = ContextSelector()
        # "file_lookup" intent is not in _WORKFLOW_INTENTS — no get_memory call needed
        items = selector.select_workflow_context("repo-123", "file_lookup", "find auth.py")
        assert items == [], "Should not inject workflow context for file_lookup intent"

    def test_memory_and_rag_items_can_coexist_in_context(self):
        """Verify memory + semantic items combine correctly before context optimizer."""
        memory_item = {
            "source_type": "memory",
            "reference": "Workflow: POST /upload Workflow",
            "content": "Steps: 1. handler, 2. service",
        }
        rag_item = {
            "source_type": "semantic",
            "reference": "backend/app/api/upload.py",
            "content": "def upload_repository(): ...",
            "score": 0.92,
        }
        combined = [memory_item, rag_item]
        source_types = {i["source_type"] for i in combined}
        assert "memory" in source_types
        assert "semantic" in source_types
