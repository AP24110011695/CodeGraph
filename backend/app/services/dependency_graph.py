"""Dependency graph builder for CodeGraph.

Parses source files using regex to identify internal dependencies.
Does not use ASTs, Tree-sitter, or external package resolution.
"""

import logging
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.services.scanner_service import ScanResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# JS/TS
JS_IMPORT_REQ_RE = re.compile(r"""(?:import|require)\s*\(\s*['"]([^'"]+)['"]\s*\)""")
JS_BARE_IMPORT_RE = re.compile(r"""import\s+['"]([^'"]+)['"]""")
JS_FROM_RE = re.compile(r"""(?:import|export)\s+[^'"]+\s+from\s+['"]([^'"]+)['"]""")

# Python
PY_IMPORT_RE = re.compile(r"""^\s*import\s+([a-zA-Z0-9_., ]+)""", re.MULTILINE)
PY_FROM_RE = re.compile(r"""^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_., ]+)""", re.MULTILINE)

# Java / C#
JAVA_CS_IMPORT_RE = re.compile(r"""^\s*(?:import|using)\s+(?:static\s+)?([a-zA-Z0-9_.]+);""", re.MULTILINE)

# PHP
PHP_IMPORT_RE = re.compile(r"""(?:require|require_once|include|include_once)\s*\(?\s*['"]([^'"]+)['"]""")

# Go
GO_LINE_IMPORT_RE = re.compile(r"""(?:^|\n)\s*import\s*(?:[a-zA-Z0-9_.]+\s+)?["']([^"']+)["']""")
GO_BLOCK_IMPORT_RE = re.compile(r"""import\s*\((.*?)\)""", re.DOTALL)
GO_QUOTES_RE = re.compile(r"""["']([^"']+)["']""")

# Rust
RUST_USE_RE = re.compile(r"""^\s*use\s+([a-zA-Z0-9_:]+)""", re.MULTILINE)
RUST_MOD_RE = re.compile(r"""^\s*mod\s+([a-zA-Z0-9_]+)""", re.MULTILINE)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class Edge:
    from_node: str
    to_node: str
    edge_type: str = "import"


@dataclass
class GraphResult:
    nodes: list[dict] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    isolated_files: int = 0


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class DependencyGraphBuilder:
    """Builds an internal dependency graph using deterministic rule-based analysis."""

    def build(self, root_path: Path, scan_result: ScanResult) -> GraphResult:
        """Parse source files to extract relationships and return a GraphResult."""
        root = root_path.resolve()

        if not root.exists() or not root.is_dir():
            logger.error("Root path is not a valid directory: %s", root)
            return GraphResult()

        valid_files = {f.path: f for f in scan_result.files}
        
        # Build search indexes for fast resolution
        # path -> actual file path
        path_index: set[str] = set(valid_files.keys())
        
        # suffix -> actual file path (e.g. 'utils/logger.py' -> 'src/utils/logger.py')
        suffix_index: dict[str, str] = {}
        for path in path_index:
            parts = path.split("/")
            for i in range(len(parts)):
                suffix = "/".join(parts[i:])
                if suffix not in suffix_index:
                    suffix_index[suffix] = path

        edges: set[tuple[str, str]] = set()

        for file_info in scan_result.files:
            file_path = root / file_info.path
            
            # Skip unreadable or overly large files
            if not file_path.is_file() or file_info.size > 1_000_000:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            raw_imports = self._extract_raw_imports(content, file_info.language)
            
            for raw_import in raw_imports:
                target_path = self._resolve_import(
                    raw_import=raw_import,
                    source_path=file_info.path,
                    language=file_info.language,
                    path_index=path_index,
                    suffix_index=suffix_index,
                )
                if target_path and target_path != file_info.path:
                    edges.add((file_info.path, target_path))

        # Compile final results
        nodes = []
        for file_info in scan_result.files:
            nodes.append({
                "id": file_info.path,
                "path": file_info.path,
                "language": file_info.language,
            })

        final_edges = [Edge(from_node=src, to_node=dst) for src, dst in sorted(edges)]

        # Calculate isolated files
        connected_nodes = set()
        for e in final_edges:
            connected_nodes.add(e.from_node)
            connected_nodes.add(e.to_node)
        
        isolated = len(nodes) - len(connected_nodes)

        return GraphResult(nodes=nodes, edges=final_edges, isolated_files=max(0, isolated))

    def _extract_raw_imports(self, content: str, language: str) -> list[str]:
        """Extract import strings from source code using regex."""
        imports: list[str] = []

        if language in ("JavaScript", "TypeScript"):
            imports.extend(JS_IMPORT_REQ_RE.findall(content))
            imports.extend(JS_BARE_IMPORT_RE.findall(content))
            imports.extend(JS_FROM_RE.findall(content))

        elif language == "Python":
            for match in PY_IMPORT_RE.findall(content):
                for part in match.split(","):
                    imports.append(part.strip())
            for mod, names in PY_FROM_RE.findall(content):
                imports.append(mod.strip())
                if mod.strip() == ".":
                    for name in names.split(","):
                        imports.append(name.strip())

        elif language in ("Java", "C#"):
            imports.extend(JAVA_CS_IMPORT_RE.findall(content))

        elif language == "PHP":
            imports.extend(PHP_IMPORT_RE.findall(content))

        elif language == "Go":
            imports.extend(GO_LINE_IMPORT_RE.findall(content))
            for block in GO_BLOCK_IMPORT_RE.findall(content):
                imports.extend(GO_QUOTES_RE.findall(block))

        elif language == "Rust":
            # use std::collections::HashMap -> std::collections::HashMap
            for match in RUST_USE_RE.findall(content):
                imports.append(match.split("{")[0].strip().rstrip(":"))
            imports.extend(RUST_MOD_RE.findall(content))

        return [i for i in imports if i]

    def _resolve_import(
        self,
        raw_import: str,
        source_path: str,
        language: str,
        path_index: set[str],
        suffix_index: dict[str, str],
    ) -> str | None:
        """Resolve a raw import string to a valid internal file path."""
        candidates = self._generate_candidates(raw_import, source_path, language)

        for candidate in candidates:
            # 1. Exact path match
            if candidate in path_index:
                return candidate
            
            # 2. Suffix match (e.g., matching 'utils/logger.py' to 'src/utils/logger.py')
            if candidate in suffix_index:
                return suffix_index[candidate]

        return None

    def _generate_candidates(self, raw_import: str, source_path: str, language: str) -> list[str]:
        """Generate possible file paths for a raw import string."""
        candidates = []
        source_dir = posixpath.dirname(source_path)

        # JS / TS / PHP (Path based)
        if language in ("JavaScript", "TypeScript", "PHP"):
            if raw_import.startswith("."):
                base = posixpath.normpath(posixpath.join(source_dir, raw_import))
            else:
                # Alias or bare import (e.g. '@/components/Button' or 'components/Button')
                base = raw_import.replace("@/", "").lstrip("/")
            
            candidates.append(base)
            if language == "PHP":
                candidates.append(f"{base}.php")
            else:
                for ext in (".js", ".ts", ".jsx", ".tsx", "/index.js", "/index.ts"):
                    candidates.append(f"{base}{ext}")

        # Python (Module based)
        elif language == "Python":
            # a.b.c -> a/b/c
            base = raw_import.replace(".", "/")
            candidates.extend([
                f"{base}.py",
                f"{base}/__init__.py"
            ])
            # Handle relative imports like `.utils` or `..utils` (stripped to `utils` in raw_import)
            # Actually, `from .utils import` -> PY_FROM_RE grabs `utils`
            rel_base = posixpath.normpath(posixpath.join(source_dir, base))
            candidates.extend([
                f"{rel_base}.py",
                f"{rel_base}/__init__.py"
            ])

        # Java / C#
        elif language in ("Java", "C#"):
            base = raw_import.replace(".", "/")
            ext = ".java" if language == "Java" else ".cs"
            candidates.append(f"{base}{ext}")
            
            # If importing a static member or specific class, the file might be the parent namespace
            parent = posixpath.dirname(base)
            if parent:
                candidates.append(f"{parent}{ext}")
            
            # Sometimes imports are wildcards: `import com.example.*;` -> ignore
            if base.endswith("/*"):
                candidates.clear()

        # Go
        elif language == "Go":
            candidates.append(f"{raw_import}/main.go")
            pkg_name = raw_import.split("/")[-1]
            candidates.append(f"{raw_import}/{pkg_name}.go")
            candidates.append(f"{raw_import}") 
            
            # Handle full module paths (e.g. "go-app/pkg/utils" -> "pkg/utils")
            if "/" in raw_import:
                stripped = raw_import.split("/", 1)[1]
                candidates.append(f"{stripped}/main.go")
                candidates.append(f"{stripped}/{pkg_name}.go")
                candidates.append(f"{stripped}")

        # Rust
        elif language == "Rust":
            base = raw_import.replace("::", "/")
            if base.startswith("crate/"):
                base = base[6:]
            
            # Standard item mapping
            candidates.extend([
                f"{base}.rs",
                f"{base}/mod.rs"
            ])
            
            # If importing a specific struct/fn, the file is the parent module
            parent = posixpath.dirname(base)
            if parent:
                candidates.extend([
                    f"{parent}.rs",
                    f"{parent}/mod.rs"
                ])
                
            rel_base = posixpath.normpath(posixpath.join(source_dir, base))
            candidates.extend([
                f"{rel_base}.rs",
                f"{rel_base}/mod.rs"
            ])
            if parent:
                rel_parent = posixpath.normpath(posixpath.join(source_dir, parent))
                candidates.extend([
                    f"{rel_parent}.rs",
                    f"{rel_parent}/mod.rs"
                ])

        return candidates


graph_builder = DependencyGraphBuilder()
