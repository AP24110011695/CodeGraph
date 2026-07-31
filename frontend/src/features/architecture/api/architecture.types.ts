/** Backend-aligned types for architecture analysis APIs. */

export interface ArchitectureComponentDto {
  name: string;
  type: string;
  file_path: string;
  language: string;
}

export interface ArchitectureModuleDto {
  name: string;
  type: string;
  files: string[];
  components: ArchitectureComponentDto[];
  layer: string;
}

export interface ArchitectureRelationshipDto {
  source: string;
  target: string;
  type: string;
}

export interface ArchitectureStatisticsDto {
  modules: number;
  components: number;
  relationships: number;
}

export interface ArchitectureResponse {
  project: { name: string; root_path: string };
  layers: string[];
  modules: ArchitectureModuleDto[];
  relationships: ArchitectureRelationshipDto[];
  statistics: ArchitectureStatisticsDto;
}

export interface ArchitectureSummaryResponse {
  repository_id: string;
  overall_architecture: string;
}

export interface ArchitectureExplanationResponse {
  summary: string;
  evidence: string[];
  referenced_modules: string[];
  confidence_score: number;
  reasoning_trace: { step: string; description: string }[];
}

export interface ArchitectureModuleModel {
  id: string;
  name: string;
  type: string;
  layer: string;
  files: string[];
  components: ArchitectureComponentDto[];
  componentCount: number;
  incomingCount: number;
  outgoingCount: number;
  incoming: string[];
  outgoing: string[];
}

export interface ArchitectureEdgeModel {
  id: string;
  source: string;
  target: string;
  type: string;
}

export interface ArchitectureModel {
  projectName: string;
  layers: string[];
  modules: ArchitectureModuleModel[];
  edges: ArchitectureEdgeModel[];
  statistics: {
    modules: number;
    components: number;
    relationships: number;
  };
}
