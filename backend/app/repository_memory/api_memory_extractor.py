import re
from pathlib import Path
from typing import Dict, List
from app.schemas.repository_memory import APIEndpointMemory, MemoryMetadata
from app.services.scanner_service import ScanResult

class APIMemoryExtractor:
    @staticmethod
    def extract(repository_id: str, project_path: Path, scan_result: ScanResult) -> Dict[str, APIEndpointMemory]:
        endpoints: Dict[str, APIEndpointMemory] = {}

        if not scan_result or not scan_result.files:
            return endpoints

        # Common FastAPI/Flask decorator patterns
        # e.g. @router.post("/upload", response_model=UploadResponse)
        # e.g. @app.get("/health")
        route_pattern = re.compile(r'@(?:router|app)\.(get|post|put|delete|patch|options)\([\'"]([^\'"]+)[\'"]')
        
        # Regex to find function definition right after decorator
        func_pattern = re.compile(r'def\s+([a-zA-Z0-9_]+)\s*\(')

        for file_info in scan_result.files:
            # Heuristic to find API files
            is_api = any(part in file_info.path.lower() for part in ["api", "route", "controller", "endpoint"])
            if not is_api and file_info.language != "Python":
                continue

            full_path = project_path / file_info.path
            if not full_path.exists():
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            # Find all routes in the file
            lines = content.split('\n')
            for i, line in enumerate(lines):
                match = route_pattern.search(line)
                if match:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    handler = "Unknown"
                    # Look ahead a few lines for the handler function
                    for j in range(i+1, min(i+5, len(lines))):
                        func_match = func_pattern.search(lines[j])
                        if func_match:
                            handler = func_match.group(1)
                            break
                    
                    # Basic extraction for models if present in the decorator line
                    response_model = None
                    if "response_model=" in line:
                        resp_match = re.search(r'response_model=([a-zA-Z0-9_]+)', line)
                        if resp_match:
                            response_model = resp_match.group(1)

                    endpoint_id = f"{method} {path}"
                    
                    endpoints[endpoint_id] = APIEndpointMemory(
                        metadata=MemoryMetadata(
                            repository_id=repository_id,
                            evidence_sources=[file_info.path]
                        ),
                        endpoint_path=path,
                        http_method=method,
                        handler=handler,
                        response_model=response_model,
                        related_files=[file_info.path],
                        purpose=f"Handles {method} requests to {path}"
                    )

        return endpoints

api_memory_extractor = APIMemoryExtractor()
