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

export interface QualityRecommendations {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface QualityMetadata {
  total_files: number;
  total_folders: number;
  languages: Record<string, number>;
  containerized: boolean;
  package_managers: string[];
  backend_frameworks: string[];
  frontend_frameworks: string[];
}

export interface QualityResponse {
  project_name: string;
  scores: QualityScores;
  recommendations: QualityRecommendations;
  metadata: QualityMetadata;
}

export interface CodeSmell {
  type: string;
  severity: string;
  file: string;
  line: number | null;
  description: string;
}

export interface SmellSummary {
  total_smells: number;
  critical: number;
  major: number;
  minor: number;
}

export interface SmellsResponse {
  technical_debt: string;
  estimated_effort: string;
  summary: SmellSummary;
  smells: CodeSmell[];
}
