from typing import Dict, List
from app.schemas.repository_memory import WorkflowMemory, APIEndpointMemory, MemoryMetadata
from app.parsers.ast_models import ProjectParsingResult

class WorkflowMemoryExtractor:
    @staticmethod
    def extract(
        repository_id: str, 
        api_endpoints: Dict[str, APIEndpointMemory], 
        parsing_result: ProjectParsingResult
    ) -> Dict[str, WorkflowMemory]:
        workflows: Dict[str, WorkflowMemory] = {}

        if not api_endpoints or not parsing_result:
            return workflows

        # Map file paths to their parsing results for easy lookup
        file_map = {f.path: f for f in parsing_result.files}

        for endpoint_id, endpoint in api_endpoints.items():
            workflow_name = f"{endpoint.http_method} {endpoint.endpoint_path} Workflow"
            starting_point = f"{endpoint.http_method} {endpoint.endpoint_path}"
            
            steps = []
            involved_files = list(endpoint.related_files)
            
            # Step 1: API Endpoint hit
            steps.append(f"Receive request at {starting_point}")
            
            # Step 2: Handler invocation
            if endpoint.handler and endpoint.handler != "Unknown":
                steps.append(f"Invoke handler {endpoint.handler}")

            # Try to infer downstream steps based on imports in the API file
            for file_path in endpoint.related_files:
                file_info = file_map.get(file_path)
                if file_info and hasattr(file_info, "imports"):
                    # Look for internal service imports as subsequent steps
                    internal_imports = [imp for imp in file_info.imports if "app." in imp or "src." in imp]
                    for imp in internal_imports:
                        steps.append(f"Call downstream dependency {imp}")
                        # We could optionally map these imports to their actual files if needed,
                        # but keeping it simple for structural extraction.

            steps.append("Return response")

            workflows[workflow_name] = WorkflowMemory(
                metadata=MemoryMetadata(
                    repository_id=repository_id,
                    evidence_sources=involved_files
                ),
                workflow_name=workflow_name,
                starting_point=starting_point,
                steps=steps,
                involved_files=involved_files,
                end_result="Request processed successfully"
            )

        return workflows

workflow_memory_extractor = WorkflowMemoryExtractor()
