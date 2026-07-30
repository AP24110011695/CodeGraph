import logging
from .planning_pipeline import PlanningPipeline
from app.schemas.planning import AIPlanResponse

logger = logging.getLogger(__name__)

class PlanningEngine:
    """Facade for the AI Planning subsystem."""
    def __init__(self):
        self.pipeline = PlanningPipeline()
        
    def plan(self, repository_id: str, query: str) -> AIPlanResponse:
        logger.info(f"PlanningEngine: Planning query for {repository_id}")
        return self.pipeline.generate_plan(query)

planning_engine = PlanningEngine()
