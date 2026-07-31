export interface ChangeTarget {
  target: string;
  target_type: string;
  change_type: string;
  related_files: string[];
}

export interface AffectedNode {
  id: string;
  name: string;
  node_type: string;
  distance: number;
  impact_weight: number;
  reason: string;
}

export interface PropagationHop {
  from_id: string;
  to_id: string;
  edge_type: string;
  depth: number;
}

export interface PropagationPath {
  path: string[];
  hops: PropagationHop[];
  length: number;
  severity: string;
}

export interface DependencyImpactResult {
  direct_dependents: AffectedNode[];
  transitive_dependents: AffectedNode[];
  dependent_services: string[];
  dependency_blast_radius: number;
  summary: string;
}

export interface ArchitectureImpactResult {
  affected_modules: string[];
  affected_layers: string[];
  boundary_crossings: string[];
  coupling_pressure: number;
  summary: string;
}

export interface APIImpactResult {
  affected_apis: string[];
  dependent_consumers: string[];
  breaking_change_likely: boolean;
  contract_risk: string;
  summary: string;
}

export interface MemoryImpactResult {
  affected_module_memories: string[];
  affected_file_memories: string[];
  affected_symbol_memories: string[];
  affected_api_memories: string[];
  memory_refresh_recommended: boolean;
  summary: string;
}

export interface ChangeRiskResult {
  risk_score: number;
  risk_level: string;
  factors: string[];
  hotspot_overlap: string[];
  recommendation: string;
}

export interface ImpactStatistics {
  nodes_analyzed: number;
  affected_nodes: number;
  propagation_paths: number;
  max_propagation_depth: number;
  dependency_impact_count: number;
  architecture_modules_affected: number;
  api_contracts_affected: number;
  confidence_score: number;
}

export interface ImpactAnalyzeRequest {
  target: string;
  target_type?: string;
  change_type?: string;
  related_files?: string[];
  max_depth?: number;
  query?: string | null;
}

export interface ImpactAnalyzeResponse {
  repository_id: string;
  target: ChangeTarget;
  dependency_impact: DependencyImpactResult;
  architecture_impact: ArchitectureImpactResult;
  api_impact: APIImpactResult;
  memory_impact: MemoryImpactResult;
  propagation_paths: PropagationPath[];
  risk: ChangeRiskResult;
  statistics: ImpactStatistics;
  what_breaks: string[];
  affected_modules: string[];
  affected_services: string[];
  affected_apis: string[];
  affected_symbols: string[];
  affected_repository_memory: string[];
  impact_summary: string;
  narrative: string;
  confidence_score: number;
  generated_at: string;
}

export interface ImpactSummaryResponse {
  repository_id: string;
  high_risk_targets: string[];
  critical_modules: string[];
  critical_apis: string[];
  critical_services: string[];
  average_blast_radius: number;
  confidence_score: number;
  summary: string;
  last_analyzed_targets: string[];
}
