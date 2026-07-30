"""Resolve repository symbols from existing knowledge-graph nodes."""

from typing import Any


class SymbolResolver:
    def resolve(self, query: str, graph: Any) -> list[dict]:
        terms = {term.lower() for term in query.replace("?", "").split() if len(term) > 2}
        matches = []
        for node in graph.nodes:
            name = node.name.lower()
            if terms and any(term in name for term in terms):
                matches.append({"id": node.id, "name": node.name, "type": node.type, "properties": node.properties})
        return matches
