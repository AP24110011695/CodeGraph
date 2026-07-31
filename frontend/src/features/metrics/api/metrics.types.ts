export interface MetricsSummary {
  total_files: number;
  total_directories: number;
  total_size: number;
  average_file_size: number | null;
  supported_languages: string[];
  detected_frameworks: string[];
  containerized: boolean;
  package_managers: string[];
}

export interface MetricsStatistics {
  total_files: number;
  total_directories: number;
  total_lines: number | null;
  code_lines: number | null;
  comment_lines: number | null;
  blank_lines: number | null;
  average_file_size: number | null;
  total_size: number;
  supported_languages: Record<string, number>;
  language_breakdown: Record<string, { count: number; percentage: number } | number>;
  detected_frameworks: string[];
  framework_breakdown: Record<string, unknown>;
  file_distribution: Record<string, number>;
  dependency_count: number;
  isolated_modules: number;
  dependency_density: number | null;
  architecture_layers: string[];
  architecture_modules: number;
  architecture_components: number;
  average_function_size: number | null;
  average_class_size: number | null;
  total_functions: number;
  total_classes: number;
  total_interfaces: number;
  quality_score: number | null;
  quality_breakdown: Record<string, number>;
  security_score: number | null;
  security_summary: Record<string, number>;
  smell_count: number;
  smell_summary: Record<string, number>;
  refactoring_count: number;
  refactoring_summary: Record<string, number>;
}

export interface MetricsQuality {
  quality_score: number | null;
  breakdown: Record<string, number>;
  recommendations_count: number;
}

export interface MetricsSecurity {
  security_score: number | null;
  summary: Record<string, number>;
  total_issues: number;
}

export interface MetricsArchitecture {
  layers: string[];
  modules: number;
  components: number;
  relationships: number;
}

export interface MetricsSmells {
  smell_count: number;
  summary: Record<string, number>;
  debt_estimate: number | null;
}

export interface MetricsRefactoring {
  refactoring_count: number;
  summary: Record<string, number>;
}

export interface MetricsResponse {
  project_name: string;
  summary: MetricsSummary;
  statistics: MetricsStatistics;
  quality: MetricsQuality;
  security: MetricsSecurity;
  architecture: MetricsArchitecture;
  smells: MetricsSmells;
  refactoring: MetricsRefactoring;
}
