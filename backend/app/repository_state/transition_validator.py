from app.schemas.repository_state import RepositoryStateEnum

class TransitionValidator:
    VALID_TRANSITIONS = {
        RepositoryStateEnum.UPLOADED: {
            RepositoryStateEnum.QUEUED,
            RepositoryStateEnum.SCANNING,  # Allow direct transition to SCANNING for auto-indexer
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.QUEUED: {
            RepositoryStateEnum.SCANNING,
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.SCANNING: {
            RepositoryStateEnum.PARSING,
            RepositoryStateEnum.INDEXING,  # Allow direct transition to INDEXING
            RepositoryStateEnum.READY,  # Allow direct transition to READY for simple repositories
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.PARSING: {
            RepositoryStateEnum.INDEXING,
            RepositoryStateEnum.READY,  # Allow direct transition to READY
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.INDEXING: {
            RepositoryStateEnum.EMBEDDING,
            RepositoryStateEnum.READY,  # Allow direct transition to READY
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.EMBEDDING: {
            RepositoryStateEnum.ANALYZING,
            RepositoryStateEnum.READY,  # Sometimes embedding is the last step before ready
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.ANALYZING: {
            RepositoryStateEnum.READY,
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.READY: {
            RepositoryStateEnum.STALE,
            RepositoryStateEnum.REINDEXING,
            RepositoryStateEnum.QUEUED
        },
        RepositoryStateEnum.STALE: {
            RepositoryStateEnum.QUEUED,
            RepositoryStateEnum.REINDEXING
        },
        RepositoryStateEnum.REINDEXING: {
            RepositoryStateEnum.READY,
            RepositoryStateEnum.CANCELLED,
            RepositoryStateEnum.FAILED
        },
        RepositoryStateEnum.FAILED: {
            RepositoryStateEnum.QUEUED,
            RepositoryStateEnum.UPLOADED
        },
        RepositoryStateEnum.CANCELLED: {
            RepositoryStateEnum.QUEUED,
            RepositoryStateEnum.UPLOADED
        }
    }

    @classmethod
    def is_valid_transition(cls, from_state: RepositoryStateEnum, to_state: RepositoryStateEnum) -> bool:
        if from_state == to_state:
            return True
        allowed = cls.VALID_TRANSITIONS.get(from_state, set())
        return to_state in allowed
