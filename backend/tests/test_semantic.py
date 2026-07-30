from pathlib import Path

from app.cache.memory_cache import MemoryCache
from app.knowledge_graph.graph_builder import GraphEdge, GraphNode, KnowledgeGraph
from app.semantic.hybrid_retriever import HybridRetriever
from app.semantic.relationship_traverser import RelationshipTraverser
from app.semantic.semantic_engine import SemanticEngine
from app.semantic.semantic_search import SemanticSearch
from app.semantic.symbol_resolver import SymbolResolver


class FakeSearchService:
    def __init__(self):
        self.calls = 0

    def search(self, **kwargs):
        self.calls += 1
        return {"results": [
            {"path": "services/auth.py", "score": 0.8, "snippet": "def jwt_auth(): pass", "language": "Python", "line_start": 1, "line_end": 1},
            {"path": "controllers/user.py", "score": 0.7, "snippet": "UserRepository()", "language": "Python", "line_start": 4, "line_end": 4},
        ]}


def _graph_provider(_, __):
    return KnowledgeGraph(
        nodes=[
            GraphNode(id="auth", type="function", name="jwt_auth", properties={"path": "services/auth.py"}),
            GraphNode(id="repo", type="class", name="UserRepository", properties={"path": "repositories/user.py"}),
            GraphNode(id="service", type="class", name="UserService", properties={"path": "services/user.py"}),
        ],
        edges=[GraphEdge(source="service", target="repo", type="depends_on"), GraphEdge(source="service", target="auth", type="uses")],
    )


def _engine(search_service):
    retriever = HybridRetriever(search_service)
    return SemanticEngine(SemanticSearch(retriever), _graph_provider, cache=MemoryCache())


def test_semantic_retrieval_ranking_and_cache_reuse():
    service = FakeSearchService()
    engine = _engine(service)

    response = engine.search("repo", "Where is JWT authentication implemented?", Path("."), "semantic")
    cached = engine.search("repo", "Where is JWT authentication implemented?", Path("."), "semantic")

    assert response["results"][0]["path"] == "services/auth.py"
    assert response["results"][0]["context_score"] == 0.9
    assert response == cached
    assert service.calls == 1


def test_hybrid_retrieval_symbol_resolution_and_relationship_traversal():
    response = _engine(FakeSearchService()).search("repo", "Which services depend on UserRepository?", Path("."), "hybrid")

    assert any(symbol["name"] == "UserRepository" for symbol in response["symbols"])
    assert any(edge["type"] == "depends_on" for edge in response["relationships"])


def test_symbol_and_relationship_components_are_bounded():
    graph = _graph_provider("repo", Path("."))
    symbols = SymbolResolver().resolve("UserRepository", graph)
    relationships = RelationshipTraverser().traverse(graph, [symbols[0]["id"]], max_depth=1)

    assert symbols[0]["id"] == "repo"
    assert relationships == [{"source": "service", "target": "repo", "type": "depends_on", "depth": 1}]
