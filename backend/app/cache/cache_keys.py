"""Namespaced keys for cacheable CodeGraph data."""


class CacheKeys:
    REPOSITORY_SNAPSHOT = "repository_snapshot"
    WORKFLOW_STATE = "workflow_state"
    REPOSITORY_STATE = "repository_state"
    WORKER_STATUS = "worker_status"
    KNOWLEDGE_GRAPH_FRAGMENT = "knowledge_graph_fragment"
    EMBEDDINGS_METADATA = "embeddings_metadata"
    SEARCH_RESULTS = "search_results"
    DASHBOARD_AGGREGATES = "dashboard_aggregates"
    COPILOT_CONTEXT = "copilot_context"

    @staticmethod
    def namespace(namespace: str) -> str:
        return f"{namespace}:"

    @classmethod
    def build(cls, namespace: str, *parts: str) -> str:
        return cls.namespace(namespace) + ":".join(str(part) for part in parts)

    @classmethod
    def repository_snapshot(cls, repository_id: str) -> str:
        return cls.build(cls.REPOSITORY_SNAPSHOT, repository_id)

    @classmethod
    def workflow_state(cls, workflow_id: str) -> str:
        return cls.build(cls.WORKFLOW_STATE, workflow_id)

    @classmethod
    def repository_state(cls, repository_id: str) -> str:
        return cls.build(cls.REPOSITORY_STATE, repository_id)

    @classmethod
    def worker_status(cls, worker_id: str) -> str:
        return cls.build(cls.WORKER_STATUS, worker_id)

    @classmethod
    def knowledge_graph_fragment(cls, repository_id: str, fragment_id: str) -> str:
        return cls.build(cls.KNOWLEDGE_GRAPH_FRAGMENT, repository_id, fragment_id)

    @classmethod
    def embeddings_metadata(cls, repository_id: str) -> str:
        return cls.build(cls.EMBEDDINGS_METADATA, repository_id)

    @classmethod
    def search_results(cls, repository_id: str, query_hash: str) -> str:
        return cls.build(cls.SEARCH_RESULTS, repository_id, query_hash)

    @classmethod
    def dashboard_aggregates(cls, workspace_id: str) -> str:
        return cls.build(cls.DASHBOARD_AGGREGATES, workspace_id)

    @classmethod
    def copilot_context(cls, repository_id: str, context_id: str) -> str:
        return cls.build(cls.COPILOT_CONTEXT, repository_id, context_id)
