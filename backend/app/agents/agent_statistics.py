class AgentStatistics:
    def __init__(self):
        self.total_executions = 0
        self.total_time_ms = 0
        
    def record_execution(self, agent_count: int, time_ms: int):
        self.total_executions += 1
        self.total_time_ms += time_ms

agent_statistics = AgentStatistics()
