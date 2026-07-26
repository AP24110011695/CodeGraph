"""Endpoint detector for API documentation generation.

Detects API endpoints from parsed source code based on the detected framework.
Supports FastAPI, Flask, Express, NestJS, Spring Boot, Django, Laravel, and Next.js API Routes.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import Field

from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.framework_detector import DetectionResult

logger = logging.getLogger(__name__)


@dataclass
class Endpoint:
    """Detected API endpoint metadata."""

    method: str
    path: str
    handler: str
    controller: str | None = None
    authentication: str | None = None
    middleware: list[str] = field(default_factory=list)
    request_model: str | None = None
    response_model: str | None = None
    tags: list[str] = field(default_factory=list)
    parameters: list[dict[str, Any]] = field(default_factory=list)
    query_params: list[str] = field(default_factory=list)
    path_params: list[str] = field(default_factory=list)
    file_path: str = ""


@dataclass
class EndpointDetectionResult:
    """Complete result from endpoint detection."""

    framework: str
    endpoints: list[Endpoint] = field(default_factory=list)


class EndpointDetector:
    """Detects API endpoints from parsed source code.

    Uses framework-specific patterns to extract endpoint information
    from the AST parsing results.
    """

    def detect(
        self,
        project_path: Path,
        scan_result: Any,
        detection_result: DetectionResult,
        parsing_result: ProjectParsingResult,
    ) -> EndpointDetectionResult:
        """Detect API endpoints based on the detected framework.

        Args:
            project_path: Absolute path to the extracted project.
            scan_result: Output from RepositoryScanner.scan().
            detection_result: Output from FrameworkDetector.detect().
            parsing_result: Output from ParserEngine.parse_project().

        Returns:
            EndpointDetectionResult with detected framework and endpoints.
        """
        # Determine the primary backend framework
        backend_frameworks = [f.name for f in detection_result.backend if f.confidence >= 85]
        
        if not backend_frameworks:
            return EndpointDetectionResult(
                framework="Unknown",
                endpoints=[],
            )

        # Use the highest confidence backend framework
        primary_framework = backend_frameworks[0]
        
        logger.info(f"Detecting endpoints for framework: {primary_framework}")

        # Dispatch to framework-specific detector
        if primary_framework == "FastAPI":
            endpoints = self._detect_fastapi(parsing_result, project_path)
        elif primary_framework == "Flask":
            endpoints = self._detect_flask(parsing_result, project_path)
        elif primary_framework == "Express":
            endpoints = self._detect_express(parsing_result, project_path)
        elif primary_framework == "NestJS":
            endpoints = self._detect_nestjs(parsing_result, project_path)
        elif primary_framework == "Django":
            endpoints = self._detect_django(parsing_result, project_path)
        elif primary_framework == "Laravel":
            endpoints = self._detect_laravel(parsing_result, project_path)
        elif primary_framework == "Spring Boot":
            endpoints = self._detect_spring_boot(parsing_result, project_path)
        elif primary_framework == "Next.js":
            endpoints = self._detect_nextjs(parsing_result, project_path)
        else:
            logger.warning(f"Unsupported framework for endpoint detection: {primary_framework}")
            endpoints = []

        return EndpointDetectionResult(
            framework=primary_framework,
            endpoints=endpoints,
        )

    def _detect_fastapi(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect FastAPI endpoints from parsed Python files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            if file_result.language != "Python":
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # FastAPI route decorators: @app.get, @router.post, @api_route, etc.
            route_pattern = re.compile(
                r'@(?:(?:app|router)\.)?(?:get|post|put|delete|patch|api_route)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                re.MULTILINE
            )

            # Find all route decorators
            for match in route_pattern.finditer(source_code):
                path = match.group(1)
                method = self._extract_method_from_decorator(match.group(0))
                
                # Find the function definition after the decorator
                func_pattern = re.compile(
                    r'def\s+(\w+)\s*\([^)]*\)',
                    re.MULTILINE
                )
                func_match = func_pattern.search(source_code[match.end():])
                
                if func_match:
                    handler = func_match.group(1)
                    
                    # Extract additional info
                    auth = self._extract_fastapi_auth(source_code, match.start())
                    request_model = self._extract_fastapi_request_model(source_code, match.start(), match.end())
                    response_model = self._extract_fastapi_response_model(source_code, match.start(), match.end())
                    tags = self._extract_fastapi_tags(source_code, match.start())
                    
                    # Extract path parameters
                    path_params = self._extract_path_params(path)
                    
                    # Extract query parameters from function signature
                    query_params = self._extract_fastapi_query_params(source_code, match.end())

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        handler=handler,
                        authentication=auth,
                        request_model=request_model,
                        response_model=response_model,
                        tags=tags,
                        path_params=path_params,
                        query_params=query_params,
                        file_path=file_result.path,
                    )
                    endpoints.append(endpoint)

        return endpoints

    def _detect_flask(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Flask endpoints from parsed Python files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            if file_result.language != "Python":
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Flask route decorators: @app.route, @bp.route
            route_pattern = re.compile(
                r'@(?:(?:app|bp)\.)?route\s*\(\s*[\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?',
                re.MULTILINE
            )

            for match in route_pattern.finditer(source_code):
                path = match.group(1)
                methods_str = match.group(2)
                
                # Default to GET if no methods specified
                if methods_str:
                    methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
                    method = methods[0] if methods else "GET"
                else:
                    method = "GET"

                # Find the function definition
                func_pattern = re.compile(r'def\s+(\w+)\s*\([^)]*\)', re.MULTILINE)
                func_match = func_pattern.search(source_code[match.end():])
                
                if func_match:
                    handler = func_match.group(1)
                    path_params = self._extract_path_params(path)

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        handler=handler,
                        path_params=path_params,
                        file_path=file_result.path,
                    )
                    endpoints.append(endpoint)

        return endpoints

    def _detect_express(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Express endpoints from parsed JavaScript/TypeScript files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            if file_result.language not in ("JavaScript", "TypeScript"):
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Express route patterns: app.get, router.post, etc.
            # More flexible pattern to handle arrow functions and named functions
            route_pattern = re.compile(
                r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*(?:\w+|\([^)]*\))',
                re.MULTILINE
            )

            for match in route_pattern.finditer(source_code):
                method = match.group(1).upper()
                path = match.group(2)
                # Generate a handler name based on method and path
                handler = f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"
                path_params = self._extract_path_params(path)

                endpoint = Endpoint(
                    method=method,
                    path=path,
                    handler=handler,
                    path_params=path_params,
                    file_path=file_result.path,
                )
                endpoints.append(endpoint)

        return endpoints

    def _detect_nestjs(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect NestJS endpoints from parsed TypeScript files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            if file_result.language != "TypeScript":
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # NestJS decorators: @Get, @Post, @Put, @Delete, @Patch
            route_pattern = re.compile(
                r'@(Get|Post|Put|Delete|Patch)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                re.MULTILINE
            )

            # Extract controller name
            controller_pattern = re.compile(r'@Controller\s*\(\s*[\'"]?([^\'")\s]+)[\'"]?\s*\)', re.MULTILINE)
            controller_match = controller_pattern.search(source_code)
            controller = controller_match.group(1) if controller_match else None

            for match in route_pattern.finditer(source_code):
                method = match.group(1).upper()
                path = match.group(2)
                
                # Find the method definition
                method_pattern = re.compile(r'async\s+(\w+)\s*\(', re.MULTILINE)
                method_match = method_pattern.search(source_code[match.end():])
                
                if method_match:
                    handler = method_match.group(1)
                    path_params = self._extract_path_params(path)

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        handler=handler,
                        controller=controller,
                        path_params=path_params,
                        file_path=file_result.path,
                    )
                    endpoints.append(endpoint)

        return endpoints

    def _detect_django(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Django endpoints from URL configuration files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            # Django uses urls.py files
            if "urls.py" not in file_result.path.lower():
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Django URL patterns
            path_pattern = re.compile(
                r'path\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*(\w+)\.',
                re.MULTILINE
            )

            for match in path_pattern.finditer(source_code):
                path = match.group(1)
                handler = match.group(2)
                
                # Django typically uses GET by default
                method = "GET"
                path_params = self._extract_path_params(path)

                endpoint = Endpoint(
                    method=method,
                    path=path,
                    handler=handler,
                    path_params=path_params,
                    file_path=file_result.path,
                )
                endpoints.append(endpoint)

        return endpoints

    def _detect_laravel(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Laravel endpoints from route files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            # Laravel uses routes/ directory
            if "routes" not in file_result.path.lower():
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Laravel route patterns: Route::get, Route::post, etc.
            route_pattern = re.compile(
                r'Route::(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*\[?[\'"]?([^\'")\s]+)[\'"]?\]?',
                re.MULTILINE
            )

            for match in route_pattern.finditer(source_code):
                method = match.group(1).upper()
                path = match.group(2)
                handler = match.group(3)
                path_params = self._extract_path_params(path)

                endpoint = Endpoint(
                    method=method,
                    path=path,
                    handler=handler,
                    path_params=path_params,
                    file_path=file_result.path,
                )
                endpoints.append(endpoint)

        return endpoints

    def _detect_spring_boot(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Spring Boot endpoints from Java files."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            if file_result.language != "Java":
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Spring Boot annotations: @GetMapping, @PostMapping, etc.
            mapping_pattern = re.compile(
                r'@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                re.MULTILINE
            )

            # Extract controller name
            controller_pattern = re.compile(r'@RestController\s+class\s+(\w+)', re.MULTILINE)
            controller_match = controller_pattern.search(source_code)
            controller = controller_match.group(1) if controller_match else None

            for match in mapping_pattern.finditer(source_code):
                method = match.group(1).upper()
                path = match.group(2)
                
                # Find the method definition
                method_pattern = re.compile(r'public\s+\w+\s+(\w+)\s*\(', re.MULTILINE)
                method_match = method_pattern.search(source_code[match.end():])
                
                if method_match:
                    handler = method_match.group(1)
                    path_params = self._extract_path_params(path)

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        handler=handler,
                        controller=controller,
                        path_params=path_params,
                        file_path=file_result.path,
                    )
                    endpoints.append(endpoint)

        return endpoints

    def _detect_nextjs(
        self, parsing_result: ProjectParsingResult, project_path: Path
    ) -> list[Endpoint]:
        """Detect Next.js API routes from file structure."""
        endpoints: list[Endpoint] = []

        for file_result in parsing_result.files:
            # Next.js API routes are in pages/api/ or app/api/
            if "api" not in file_result.path.lower():
                continue

            file_path = project_path / file_result.path
            source_code = self._read_file_safe(file_path)
            if not source_code:
                continue

            # Extract HTTP method from export
            method_pattern = re.compile(r'export\s+(?:async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)', re.MULTILINE)
            method_match = method_pattern.search(source_code)
            
            if method_match:
                method = method_match.group(1)
                
                # Derive path from file path
                # pages/api/users/[id].js -> /api/users/[id]
                path = "/" + file_result.path.replace("\\", "/")
                
                # Remove file extension
                path = re.sub(r'\.(js|ts|jsx|tsx)$', '', path)
                
                handler = f"{method_match.group(1)} handler"
                path_params = self._extract_path_params(path)

                endpoint = Endpoint(
                    method=method,
                    path=path,
                    handler=handler,
                    path_params=path_params,
                    file_path=file_result.path,
                )
                endpoints.append(endpoint)

        return endpoints

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _read_file_safe(self, file_path: Path) -> str | None:
        """Read a file safely, returning None on error."""
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, PermissionError, UnicodeDecodeError):
            return None

    def _extract_method_from_decorator(self, decorator: str) -> str:
        """Extract HTTP method from a FastAPI decorator string."""
        if "get" in decorator.lower():
            return "GET"
        elif "post" in decorator.lower():
            return "POST"
        elif "put" in decorator.lower():
            return "PUT"
        elif "delete" in decorator.lower():
            return "DELETE"
        elif "patch" in decorator.lower():
            return "PATCH"
        return "GET"

    def _extract_path_params(self, path: str) -> list[str]:
        """Extract path parameters from a route path."""
        # Match patterns like {id}, <id>, [id]
        patterns = [r'\{(\w+)\}', r'<(\w+)>', r'\[(\w+)\]']
        params: list[str] = []
        
        for pattern in patterns:
            matches = re.findall(pattern, path)
            params.extend(matches)
        
        return params

    def _extract_fastapi_auth(self, source_code: str, position: int) -> str | None:
        """Extract authentication information from FastAPI decorator."""
        # Look for Depends, OAuth2PasswordBearer, etc.
        before_decorator = source_code[:position]
        
        if "Depends" in before_decorator:
            if "get_current_user" in before_decorator:
                return "JWT"
            elif "get_current_active_user" in before_decorator:
                return "JWT"
        
        return None

    def _extract_fastapi_request_model(
        self, source_code: str, start: int, end: int
    ) -> str | None:
        """Extract request model from FastAPI route."""
        # Look for Pydantic model in function signature
        section = source_code[start:end + 500]
        
        # Match patterns like: item: Item, user: UserCreate
        model_pattern = re.compile(r'(\w+)\s*:\s*(\w+)\s*(?::|\))', re.MULTILINE)
        matches = model_pattern.findall(section)
        
        for param_name, model_name in matches:
            if model_name[0].isupper():  # Pydantic models typically start with uppercase
                return model_name
        
        return None

    def _extract_fastapi_response_model(
        self, source_code: str, start: int, end: int
    ) -> str | None:
        """Extract response model from FastAPI decorator."""
        section = source_code[start:end + 200]
        
        # Look for response_model parameter
        response_pattern = re.compile(r'response_model\s*=\s*(\w+)', re.MULTILINE)
        match = response_pattern.search(section)
        
        if match:
            return match.group(1)
        
        return None

    def _extract_fastapi_tags(self, source_code: str, position: int) -> list[str]:
        """Extract tags from FastAPI decorator."""
        section = source_code[position:position + 200]
        
        # Look for tags parameter
        tags_pattern = re.compile(r'tags\s*=\s*\[([^\]]+)\]', re.MULTILINE)
        match = tags_pattern.search(section)
        
        if match:
            tags_str = match.group(1)
            # Extract tag names from quotes
            tags = re.findall(r'["\']([^"\']+)["\']', tags_str)
            return tags
        
        return []

    def _extract_fastapi_query_params(self, source_code: str, position: int) -> list[str]:
        """Extract query parameters from FastAPI function signature."""
        section = source_code[position:position + 300]
        
        # Find function signature
        func_pattern = re.compile(r'def\s+\w+\s*\(([^)]+)\)', re.MULTILINE)
        match = func_pattern.search(section)
        
        if match:
            params_str = match.group(1)
            # Extract parameter names
            params = re.findall(r'(\w+)\s*:', params_str)
            return params
        
        return []


endpoint_detector = EndpointDetector()
