/** Backend-aligned types for GET /dependency-graph/{upload_id}. */

export interface DependencyGraphNodeDto {
  id: string;
  path: string;
  language: string;
}

export interface DependencyGraphEdgeDto {
  from: string;
  to: string;
  type: string;
}

export interface DependencyGraphResponseDto {
  project: { name: string; root_path: string };
  summary: { files: number; folders: number };
  nodes: DependencyGraphNodeDto[];
  edges: DependencyGraphEdgeDto[];
  statistics: {
    nodes: number;
    edges: number;
    isolated_files: number;
  };
}

export interface GraphNodeModel {
  id: string;
  path: string;
  name: string;
  language: string;
  folder: string;
  dependencyCount: number;
  dependentCount: number;
  dependencies: string[];
  dependents: string[];
  isolated: boolean;
}

export interface GraphEdgeModel {
  id: string;
  source: string;
  target: string;
  type: string;
}

export interface DependencyGraphModel {
  projectName: string;
  nodes: GraphNodeModel[];
  edges: GraphEdgeModel[];
  languages: string[];
  statistics: {
    nodes: number;
    edges: number;
    isolatedFiles: number;
  };
}

export interface GraphUiFilters {
  languages: string[];
  hideIsolated: boolean;
  searchQuery: string;
}
