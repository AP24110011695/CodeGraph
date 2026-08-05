import asyncio
import time
import uuid
import sys
from pathlib import Path

# Add the app to path if necessary
sys.path.insert(0, str(Path(__file__).parent))

from app.services.scanner_service import scanner_service
from app.services.framework_detector import detector_service
from app.services.dependency_graph import graph_builder
from app.parsers.parser_engine import ParserEngine
from app.analyzers.architecture_builder import architecture_builder
from app.quality.quality_analyzer import quality_analyzer
from app.risk.risk_engine import RiskEngine
from app.indexing.index_manager import get_shared_index_manager

async def main():
    project_path = Path(r"c:\Projects\CodeGraph\backend\app")
    upload_id = str(uuid.uuid4())
    print(f"Measuring on project path: {project_path}")

    # Stage: Scan
    t0 = time.time()
    scan_result = scanner_service.scan(project_path)
    t_scan = time.time() - t0
    print(f"Repository scan: {t_scan:.4f}s")

    # Stage: Detect
    t0 = time.time()
    detection_result = detector_service.detect(project_path, scan_result)
    t_detect = time.time() - t0
    print(f"Framework detection: {t_detect:.4f}s")

    # Stage: Graph
    t0 = time.time()
    graph_result = graph_builder.build(project_path, scan_result)
    t_graph = time.time() - t0
    print(f"Dependency graph generation: {t_graph:.4f}s")

    # Stage: Parse
    t0 = time.time()
    parsing_result = ParserEngine.parse_project(project_path, scan_result)
    t_parse = time.time() - t0
    print(f"Tree-sitter parsing: {t_parse:.4f}s")

    # Stage: Architecture
    t0 = time.time()
    arch_result = architecture_builder.build(scan_result, detection_result, graph_result, parsing_result)
    t_arch = time.time() - t0
    print(f"Architecture analysis: {t_arch:.4f}s")

    # Stage: Quality
    t0 = time.time()
    qual_result = quality_analyzer.analyze(project_path)
    t_qual = time.time() - t0
    print(f"Quality analysis: {t_qual:.4f}s")

    # Stage: Risk
    t0 = time.time()
    index_manager = get_shared_index_manager()
    risk_engine = RiskEngine(index_manager=index_manager)
    risk_result = risk_engine.analyze(project_path, upload_id)
    t_risk = time.time() - t0
    print(f"Risk analysis (Security/Risk): {t_risk:.4f}s")

    # Stage: Dashboard APIs (Simulate overlapping identical work)
    t0 = time.time()
    # Quality re-scans, arch re-scans...
    # We will simulate the duplicated work that happens on the backend right now
    # when dashboard loads
    t0_api = time.time()
    scanner_service.scan(project_path)
    detector_service.detect(project_path, scan_result)
    graph_builder.build(project_path, scan_result)
    ParserEngine.parse_project(project_path, scan_result)
    architecture_builder.build(scan_result, detection_result, graph_result, parsing_result)
    quality_analyzer.analyze(project_path)
    t_api = time.time() - t0_api
    print(f"Dashboard API responses (sync block time): {t_api:.4f}s")

if __name__ == "__main__":
    asyncio.run(main())
