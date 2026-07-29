"""Endpoint detector for API dependency flow engine.

Detects API endpoints from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Endpoint:
    """An API endpoint."""

    method: str
    path: str
    controller: str
    middleware: list[str]
    dependencies: list[str]
    database_access: list[str]
    evidence: str


class EndpointDetector:
    """Detects API endpoints from repository analysis.

    Reuses outputs from:
    - Parser Engine
    - Repository Scanner
    - Framework Detector
    """

    def __init__(self):
        """Initialize the endpoint detector."""
        pass

    def detect_endpoints(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
        framework_result: Any | None = None,
    ) -> list[Endpoint]:
        """Detect API endpoints in the repository.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.
            framework_result: The framework detection result.

        Returns:
            List of detected endpoints.
        """
        endpoints: list[Endpoint] = []

        # Detect FastAPI endpoints
        endpoints.extend(self._detect_fastapi_endpoints(project_path))

        # Detect Flask endpoints
        endpoints.extend(self._detect_flask_endpoints(project_path))

        # Detect Express endpoints
        endpoints.extend(self._detect_express_endpoints(project_path))

        # Detect Spring Boot endpoints
        endpoints.extend(self._detect_spring_endpoints(project_path))

        # Detect Django endpoints
        endpoints.extend(self._detect_django_endpoints(project_path))

        return endpoints

    def _detect_fastapi_endpoints(self, project_path: Path) -> list[Endpoint]:
        """Detect FastAPI endpoints.

        Args:
            project_path: The project path.

        Returns:
            List of FastAPI endpoints.
        """
        endpoints: list[Endpoint] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "@router" in content or "@app" in content:
                        import re
                        # Detect @app.get, @app.post, @router.get, @router.post
                        endpoint_pattern = r'@(?:router|app)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)'
                        matches = re.findall(endpoint_pattern, content)
                        for method, path in matches:
                            controller = self._extract_controller_name(file.name)
                            middleware = self._extract_fastapi_middleware(content)
                            dependencies = self._extract_dependencies(content)
                            database_access = self._extract_database_access(content)
                            endpoints.append(
                                Endpoint(
                                    method=method.upper(),
                                    path=path,
                                    controller=controller,
                                    middleware=middleware,
                                    dependencies=dependencies,
                                    database_access=database_access,
                                    evidence=f"FastAPI endpoint detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return endpoints

    def _detect_flask_endpoints(self, project_path: Path) -> list[Endpoint]:
        """Detect Flask endpoints.

        Args:
            project_path: The project path.

        Returns:
            List of Flask endpoints.
        """
        endpoints: list[Endpoint] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "@app.route" in content:
                        import re
                        endpoint_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"]\s*,\s*methods=\[([^\]]+)\]'
                        matches = re.findall(endpoint_pattern, content)
                        for path, methods in matches:
                            methods_list = [m.strip().strip('\'"') for m in methods.split(',')]
                            for method in methods_list:
                                controller = self._extract_controller_name(file.name)
                                middleware = self._extract_flask_middleware(content)
                                dependencies = self._extract_dependencies(content)
                                database_access = self._extract_database_access(content)
                                endpoints.append(
                                    Endpoint(
                                        method=method.upper(),
                                        path=path,
                                        controller=controller,
                                        middleware=middleware,
                                        dependencies=dependencies,
                                        database_access=database_access,
                                        evidence=f"Flask endpoint detected in {file.name}",
                                    )
                                )
                except Exception:
                    continue

        return endpoints

    def _detect_express_endpoints(self, project_path: Path) -> list[Endpoint]:
        """Detect Express endpoints.

        Args:
            project_path: The project path.

        Returns:
            List of Express endpoints.
        """
        endpoints: list[Endpoint] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".js", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "router." in content or "app." in content:
                        import re
                        endpoint_pattern = r'(?:router|app)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
                        matches = re.findall(endpoint_pattern, content)
                        for method, path in matches:
                            controller = self._extract_controller_name(file.name)
                            middleware = self._extract_express_middleware(content)
                            dependencies = self._extract_dependencies(content)
                            database_access = self._extract_database_access(content)
                            endpoints.append(
                                Endpoint(
                                    method=method.upper(),
                                    path=path,
                                    controller=controller,
                                    middleware=middleware,
                                    dependencies=dependencies,
                                    database_access=database_access,
                                    evidence=f"Express endpoint detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return endpoints

    def _detect_spring_endpoints(self, project_path: Path) -> list[Endpoint]:
        """Detect Spring Boot endpoints.

        Args:
            project_path: The project path.

        Returns:
            List of Spring Boot endpoints.
        """
        endpoints: list[Endpoint] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".java":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "@RequestMapping" in content or "@GetMapping" in content or "@PostMapping" in content:
                        import re
                        # Detect @GetMapping, @PostMapping, etc.
                        endpoint_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping\([\'"]([^\'"]+)[\'"]\)'
                        matches = re.findall(endpoint_pattern, content)
                        for method, path in matches:
                            controller = self._extract_controller_name(file.name)
                            middleware = self._extract_spring_middleware(content)
                            dependencies = self._extract_dependencies(content)
                            database_access = self._extract_database_access(content)
                            endpoints.append(
                                Endpoint(
                                    method=method.upper(),
                                    path=path,
                                    controller=controller,
                                    middleware=middleware,
                                    dependencies=dependencies,
                                    database_access=database_access,
                                    evidence=f"Spring Boot endpoint detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return endpoints

    def _detect_django_endpoints(self, project_path: Path) -> list[Endpoint]:
        """Detect Django endpoints.

        Args:
            project_path: The project path.

        Returns:
            List of Django endpoints.
        """
        endpoints: list[Endpoint] = []

        urls_file = project_path / "urls.py"
        if urls_file.exists():
            try:
                content = urls_file.read_text(encoding="utf-8", errors="ignore")
                import re
                # Detect path() patterns
                endpoint_pattern = r'path\([\'"]([^\'"]+)[\'"]'
                matches = re.findall(endpoint_pattern, content)
                for path in matches:
                    controller = "Django Views"
                    middleware = self._extract_django_middleware(content)
                    dependencies = self._extract_dependencies(content)
                    database_access = self._extract_database_access(content)
                    endpoints.append(
                        Endpoint(
                            method="GET",
                            path=path,
                            controller=controller,
                            middleware=middleware,
                            dependencies=dependencies,
                            database_access=database_access,
                            evidence="Django URL pattern detected in urls.py",
                        )
                    )
            except Exception:
                pass

        return endpoints

    def _extract_controller_name(self, filename: str) -> str:
        """Extract controller name from filename."""
        return filename.replace(".py", "").replace(".java", "").replace(".js", "").replace(".ts", "")

    def _extract_fastapi_middleware(self, content: str) -> list[str]:
        """Extract FastAPI middleware."""
        middleware = []
        if "Depends" in content:
            import re
            dep_pattern = r'Depends\([\'"]?(\w+)'
            matches = re.findall(dep_pattern, content)
            middleware.extend(matches)
        return middleware

    def _extract_flask_middleware(self, content: str) -> list[str]:
        """Extract Flask middleware."""
        middleware = []
        if "before_request" in content:
            middleware.append("before_request")
        if "after_request" in content:
            middleware.append("after_request")
        return middleware

    def _extract_express_middleware(self, content: str) -> list[str]:
        """Extract Express middleware."""
        middleware = []
        if ".use(" in content:
            import re
            use_pattern = r'\.use\([\'"]?(\w+)'
            matches = re.findall(use_pattern, content)
            middleware.extend(matches)
        return middleware

    def _extract_spring_middleware(self, content: str) -> list[str]:
        """Extract Spring middleware."""
        middleware = []
        if "@PreAuthorize" in content:
            middleware.append("PreAuthorize")
        if "@PostAuthorize" in content:
            middleware.append("PostAuthorize")
        return middleware

    def _extract_django_middleware(self, content: str) -> list[str]:
        """Extract Django middleware."""
        middleware = []
        if "MIDDLEWARE" in content:
            import re
            mw_pattern = r'MIDDLEWARE\s*=\s*\[([^\]]+)\]'
            match = re.search(mw_pattern, content)
            if match:
                middleware_str = match.group(1)
                middleware = [m.strip().strip('\'"') for m in middleware_str.split(',')]
        return middleware

    def _extract_dependencies(self, content: str) -> list[str]:
        """Extract dependencies."""
        dependencies = []
        import re
        # Detect service calls
        service_pattern = r'(\w+Service)\('
        matches = re.findall(service_pattern, content)
        dependencies.extend(matches)
        return list(set(dependencies))[:5]  # Limit to 5

    def _extract_database_access(self, content: str) -> list[str]:
        """Extract database access."""
        db_access = []
        if "session" in content.lower() or "query" in content.lower() or "repository" in content.lower():
            db_access.append("Database")
        return db_access


endpoint_detector = EndpointDetector()
