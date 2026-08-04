import logging
from pathlib import Path
from app.schemas.repository_memory import RepositoryMemory, MemoryMetadata
from app.indexing.repository_access import resolve_indexed_project_path

# Services & extractors
from app.services.scanner_service import scanner_service
from app.parsers.parser_engine import ParserEngine
from app.services.framework_detector import detector_service
from app.services.dependency_graph import graph_builder
from app.analyzers.architecture_builder import architecture_builder

from .symbol_table_extractor import symbol_table_extractor
from .module_memory_extractor import module_memory_extractor
from .api_memory_extractor import api_memory_extractor
from .workflow_memory_extractor import workflow_memory_extractor

logger = logging.getLogger(__name__)

class MemoryBuilder:
    def __init__(self):
        pass

    def build(self, repository_id: str) -> RepositoryMemory:
        logger.info(f"Building repository memory for {repository_id}")
        
        try:
            project_path = resolve_indexed_project_path(repository_id)
        except Exception as e:
            logger.error(f"Failed to resolve project path for {repository_id}: {e}")
            return RepositoryMemory(
                metadata=MemoryMetadata(repository_id=repository_id),
                repository_summary="Error resolving project path"
            )

        # 1. Gather foundational data
        scan_result = scanner_service.scan(project_path)
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
        detection_result = detector_service.detect(project_path, scan_result)
        graph_result = graph_builder.build(project_path, scan_result)
        architecture_result = architecture_builder.build(scan_result, detection_result, graph_result, parsing_result)

        # 2. Extract structured memories
        symbol_summaries = symbol_table_extractor.extract(repository_id, parsing_result)
        module_summaries = module_memory_extractor.extract(repository_id, architecture_result)
        api_endpoints = api_memory_extractor.extract(repository_id, project_path, scan_result)
        workflow_summaries = workflow_memory_extractor.extract(repository_id, api_endpoints, parsing_result)

        # Build framework summary string
        frameworks = []
        if detection_result:
            frameworks.extend([f.name for f in detection_result.frameworks])
            frameworks.extend([f.name for f in detection_result.backend])
        
        # Build layer summary string
        architecture_layers = []
        if architecture_result and architecture_result.layers:
            architecture_layers = architecture_result.layers

        metadata = MemoryMetadata(
            repository_id=repository_id,
            evidence_sources=["Scanner", "Parser", "ArchitectureBuilder"]
        )

        memory = RepositoryMemory(
            metadata=metadata,
            repository_summary=f"Repository {scan_result.project_name} with {scan_result.total_files} files in {len(scan_result.languages)} languages.",
            architecture_summary=f"Architecture layers: {', '.join(architecture_layers) if architecture_layers else 'Unknown'}",
            framework_summary=f"Detected frameworks: {', '.join(frameworks) if frameworks else 'None'}",
            service_relationships="Dependencies and relationships extracted via dependency graph.",
            module_summaries=module_summaries,
            symbol_summaries=symbol_summaries,
            api_endpoints=list(api_endpoints.values()),
            workflow_summaries=workflow_summaries
        )
        
        return memory

