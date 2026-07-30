"""Build cross-file context without parsing or embedding files again."""

from typing import Any


class ContextBuilder:
    def build(self, results: list[dict], symbols: list[dict], relationships: list[dict]) -> dict[str, Any]:
        related_paths = {
            str(symbol.get("properties", {}).get("path", ""))
            for symbol in symbols
            if symbol.get("properties", {}).get("path")
        }
        return {
            "results": results,
            "symbols": symbols,
            "relationships": relationships,
            "related_paths": related_paths,
        }
