import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Intents for which broad memory context (repo overview, architecture) is useful
_BROAD_MEMORY_INTENTS = {
    "architecture_explanation",
    "tech_stack_query",
    "general_explanation",
    "mechanism_explanation",
    "architecture",
}

# Intents that benefit from workflow memory
_WORKFLOW_INTENTS = {
    "workflow",
    "workflow_tracing",
    "general_query",
}

# Intents that benefit from symbol table lookup
_SYMBOL_INTENTS = {
    "file_lookup",
    "code_explanation",
    "bug_analysis",
    "general_query",
    "general_explanation",
}

# Intents that benefit from API memory
_API_INTENTS = {
    "workflow",
    "workflow_tracing",
    "architecture",
    "code_explanation",
    "general_query",
}


class ContextSelector:
    """Selects contextual facts from memory, semantic engine, knowledge graph, and timeline.

    Memory and RAG retrieval are kept as separate pipelines.
    Both feed into the Context Builder which assembles the final prompt payload.
    """

    def select_memory_context(self, repository_id: str, intent: str = "general_explanation") -> List[Dict]:
        """Fetch high-level structural facts from the Repository Memory Engine.

        Only returns generic repository/architecture overview for intents where it is
        broadly useful. Targeted intents use dedicated methods instead.
        """
        if intent not in _BROAD_MEMORY_INTENTS:
            return []

        items = []
        try:
            from app.repository_memory.memory_engine import memory_engine
            memory = memory_engine.get_memory_summary(repository_id)
            if memory:
                if memory.repository_summary:
                    items.append({
                        "source_type": "memory",
                        "reference": "Repository Overview",
                        "content": memory.repository_summary,
                    })
                if memory.architecture_summary:
                    items.append({
                        "source_type": "memory",
                        "reference": "Architecture Overview",
                        "content": memory.architecture_summary,
                    })
        except Exception as exc:  # noqa: BLE001
            logger.debug("Memory context unavailable: %s", exc)
        return items

    def select_workflow_context(self, repository_id: str, intent: str, query: str) -> List[Dict]:
        """Fetch workflow memory for workflow/tracing queries.

        Returns structured workflow traces as attributed context blocks.
        Memory is kept separate from RAG — both feed into Context Builder.
        """
        if intent not in _WORKFLOW_INTENTS:
            return []

        items = []
        try:
            from app.repository_memory.memory_engine import memory_engine
            memory = memory_engine.get_memory(repository_id)
            if memory and memory.workflow_summaries:
                query_lower = query.lower()
                for wf_name, wf in memory.workflow_summaries.items():
                    # Simple keyword relevance: match workflow name against query
                    if any(kw in query_lower for kw in wf.workflow_name.lower().split()) \
                            or any(kw in query_lower for kw in ["workflow", "flow", "upload", "process", "index"]):
                        steps_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(wf.steps))
                        files_text = ", ".join(wf.involved_files) if wf.involved_files else "Unknown"
                        content = (
                            f"Workflow: {wf.workflow_name}\n"
                            f"Start: {wf.starting_point}\n"
                            f"Steps:\n{steps_text}\n"
                            f"Files involved: {files_text}\n"
                            f"End result: {wf.end_result}"
                        )
                        items.append({
                            "source_type": "memory",
                            "reference": f"Workflow: {wf.workflow_name}",
                            "content": content,
                            "symbol": wf.workflow_name,
                        })
        except Exception as exc:
            logger.debug("Workflow memory context unavailable: %s", exc)
        return items

    def select_symbol_context(self, repository_id: str, intent: str, query: str) -> List[Dict]:
        """Fetch structured symbol table entries relevant to the query.

        Returns class/function records as attributed context blocks.
        Memory is kept separate from RAG — both feed into Context Builder.
        """
        if intent not in _SYMBOL_INTENTS:
            return []

        items = []
        try:
            from app.repository_memory.memory_engine import memory_engine
            memory = memory_engine.get_memory(repository_id)
            if memory and memory.symbol_summaries:
                query_lower = query.lower()
                query_terms = set(query_lower.split())
                matched = []
                for sym_id, sym in memory.symbol_summaries.items():
                    name_lower = sym.symbol_name.lower()
                    # Score by number of query terms that appear in symbol name or file path
                    score = sum(1 for t in query_terms if t in name_lower or t in sym.file_path.lower())
                    if score > 0:
                        matched.append((score, sym))

                # Return top-5 most relevant symbols
                matched.sort(key=lambda x: x[0], reverse=True)
                for _, sym in matched[:5]:
                    parts = [
                        f"Symbol: {sym.symbol_name}",
                        f"Type: {sym.symbol_type}",
                        f"File: {sym.file_path}",
                    ]
                    if sym.parent_class:
                        parts.append(f"Class: {sym.parent_class}")
                    if sym.methods:
                        parts.append(f"Methods: {', '.join(sym.methods[:10])}")
                    content = "\n".join(parts)
                    items.append({
                        "source_type": "memory",
                        "reference": sym.file_path,
                        "content": content,
                        "symbol": sym.symbol_name,
                    })
        except Exception as exc:
            logger.debug("Symbol memory context unavailable: %s", exc)
        return items

    def select_api_context(self, repository_id: str, intent: str, query: str) -> List[Dict]:
        """Fetch API endpoint memory relevant to the query.

        Returns endpoint records as attributed context blocks.
        Memory is kept separate from RAG — both feed into Context Builder.
        """
        if intent not in _API_INTENTS:
            return []

        items = []
        try:
            from app.repository_memory.memory_engine import memory_engine
            memory = memory_engine.get_memory(repository_id)
            if memory and memory.api_endpoints:
                query_lower = query.lower()
                for endpoint in memory.api_endpoints:
                    path_lower = endpoint.endpoint_path.lower()
                    handler_lower = endpoint.handler.lower()
                    # Match if query mentions the path segment or handler name
                    if any(t in path_lower or t in handler_lower for t in query_lower.split()):
                        files_text = ", ".join(endpoint.related_files) if endpoint.related_files else "Unknown"
                        content = (
                            f"API Endpoint: {endpoint.http_method} {endpoint.endpoint_path}\n"
                            f"Handler: {endpoint.handler}\n"
                            f"Files: {files_text}\n"
                            f"Purpose: {endpoint.purpose}"
                        )
                        items.append({
                            "source_type": "memory",
                            "reference": f"{endpoint.http_method} {endpoint.endpoint_path}",
                            "content": content,
                            "symbol": endpoint.handler,
                        })
        except Exception as exc:
            logger.debug("API memory context unavailable: %s", exc)
        return items

    def select_semantic_context(self, repository_id: str, query: str) -> List[Dict]:
        """Fetch chunks from the Semantic Engine / Vector Store using the current query."""
        items = []
        try:
            from app.api.search import search_service, _project_path
            path = _project_path(repository_id)
            if path and path.exists():
                # Use search_service directly (simpler, already verified working)
                res = search_service.search(
                    upload_id=repository_id,
                    query=query,
                    mode="semantic",
                    project_path=path,
                    limit=5
                )
                for rank_item in res.get("results", []):
                    snippet = rank_item.get("snippet", "").strip()
                    if not snippet:
                        continue
                    items.append({
                        "source_type": "semantic",
                        "reference": rank_item.get("path", "unknown"),
                        "content": snippet,
                        "score": rank_item.get("score", 0.0),
                    })
        except Exception as exc:
            logger.debug("Semantic context unavailable: %s", exc)
        return items

    def select_graph_context(self, repository_id: str, entities: List[str]) -> List[Dict]:
        """Fetch dependencies from Knowledge Graph for specific entities."""
        return []

    def select_timeline_context(self, repository_id: str, query: str = "") -> List[Dict]:
        """Fetch evolution / hotspot facts from Timeline Intelligence."""
        items: List[Dict] = []
        try:
            from app.timeline.timeline_engine import timeline_engine

            if query:
                answer = timeline_engine.answer(repository_id, query)
                items.append({
                    "source_type": "timeline",
                    "reference": "Timeline Answer",
                    "content": answer,
                })
            else:
                summary = timeline_engine.get_timeline(repository_id).historical_summary
                items.append({
                    "source_type": "timeline",
                    "reference": "Historical Summary",
                    "content": summary.narrative,
                })
        except Exception as exc:  # noqa: BLE001
            logger.debug("Timeline context unavailable: %s", exc)
        return items