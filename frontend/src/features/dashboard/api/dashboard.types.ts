export interface FrameworkMatch {
  name: string;
  confidence: number;
}

export interface FrameworksResponse {
  project: { name: string; root_path: string };
  summary: { files: number; folders: number };
  languages: Record<string, number>;
  frameworks: FrameworkMatch[];
  backend: FrameworkMatch[];
  package_managers: string[];
  containerized: boolean;
  parser_targets: string[];
}

export interface ArchitectureResponse {
  project: { name: string; root_path: string };
  layers: string[];
  modules: Array<{
    name: string;
    type: string;
    files: string[];
    components: unknown[];
    layer: string;
  }>;
  relationships: unknown[];
  statistics: {
    modules: number;
    components: number;
    relationships: number;
  };
}

export interface ArchitectureSummaryResponse {
  repository_id: string;
  overall_architecture: string;
}

export interface QualityScores {
  architecture: number;
  security: number;
  documentation: number;
  maintainability: number;
  testing: number;
  complexity: number;
  readability: number;
  scalability: number;
}

export interface QualityResponse {
  project_name: string;
  scores: QualityScores;
  recommendations: {
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  };
  metadata: {
    total_files: number;
    total_folders: number;
    languages: Record<string, number>;
    containerized: boolean;
    package_managers: string[];
    backend_frameworks: string[];
    frontend_frameworks: string[];
  };
}

export interface RiskItem {
  title: string;
  category: string;
  risk_level: string;
  score: number;
  reason: string;
  evidence: string;
  affected_files: string[];
  recommendation: string;
  potential_impact: string;
  source: string;
}

export interface RiskResponse {
  project_name: string;
  overall_risk_score: number;
  overall_level: string;
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  risks: RiskItem[];
  top_risks: RiskItem[];
  priority_recommendations: string[];
}

export interface IndexStatsResponse {
  upload_id: string;
  status: string;
  statistics: {
    files: number;
    chunks: number;
    embeddings: number;
    added: number;
    modified: number;
    deleted: number;
    unchanged: number;
  };
  indexed_at: string | null;
}

export interface DashboardOverviewModel {
  projectName: string;
  files: number;
  folders: number;
  languages: Array<{ name: string; count: number }>;
  languageCount: number;
  dependencyChunks: number;
  embeddings: number;
  frameworks: FrameworkMatch[];
  backendFrameworks: FrameworkMatch[];
  packageManagers: string[];
  containerized: boolean;
  healthScore: number | null;
  qualityScores: QualityScores | null;
  architectureSummary: string;
  architectureLayers: string[];
  architectureStats: { modules: number; components: number; relationships: number } | null;
  topRisks: RiskItem[];
  overallRiskScore: number | null;
  overallRiskLevel: string | null;
}
