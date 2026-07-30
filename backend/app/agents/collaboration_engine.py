import time
from app.schemas.agents import AgentExecutionResponse
from app.planning.planning_engine import planning_engine
from .task_dispatcher import TaskDispatcher
from .agent_statistics import agent_statistics

class CollaborationEngine:
    """Coordinates multi-agent collaboration driven by the AI Planning Engine."""
    def __init__(self):
        self.dispatcher = TaskDispatcher()
        
    def _map_intent_to_agents(self, intent: str) -> list[str]:
        if intent == "architecture_explanation":
            return ["ArchitectureAgent", "DocumentationAgent"]
        elif intent == "timeline_analysis":
            return ["TimelineAgent", "ArchitectureAgent", "DocumentationAgent"]
        elif intent == "code_modification":
            return ["RefactoringAgent"]
        elif intent == "impact_analysis":
            return ["ImpactAgent", "DependencyAgent", "ArchitectureAgent"]
        elif intent == "concept_explanation":
            return ["DocumentationAgent"]
        elif intent == "code_location":
            return ["DocumentationAgent"] # fallback
        return ["DocumentationAgent"]

    def execute_collaboration(self, repository_id: str, query: str) -> AgentExecutionResponse:
        start_time = time.time()
        
        # 1. Ask Planning Engine for the orchestration plan
        plan = planning_engine.plan(repository_id, query)
        
        # 2. Determine required agents based on intent
        agents_to_run = self._map_intent_to_agents(plan.intent)
        
        # 3. Dispatch tasks sequentially sharing the planning context
        shared_context = {"plan": plan.model_dump()}
        agent_results = self.dispatcher.dispatch(repository_id, query, agents_to_run, shared_context)
        
        # 4. Synthesize final summary
        if not agent_results:
            summary = "No agents executed."
        else:
            summary = " | ".join([f"[{res.agent_name}]: {res.result}" for res in agent_results])
            
        exec_time = int((time.time() - start_time) * 1000)
        
        agent_statistics.record_execution(len(agents_to_run), exec_time)
        
        return AgentExecutionResponse(
            query=query,
            plan=plan,
            agent_results=agent_results,
            final_summary=summary,
            execution_time_ms=exec_time
        )
