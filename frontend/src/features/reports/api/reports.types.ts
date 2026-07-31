export type ReportType =
  | 'executive'
  | 'architecture'
  | 'technical_debt'
  | 'repository_health'
  | 'security_overview'
  | 'impact_analysis'
  | 'custom';

export interface ReportSectionDto {
  section_id: string;
  title: string;
  content: string;
  highlights: string[];
  metrics: Record<string, unknown>;
  source_modules: string[];
}

export interface HealthScoreBreakdownDto {
  overall: number;
  architecture: number;
  memory_coverage: number;
  timeline_stability: number;
  impact_risk_inverse: number;
  debt_pressure_inverse: number;
  grade: string;
}

export interface EngineeringReportDto {
  report_id: string;
  repository_id: string;
  report_type: ReportType;
  title: string;
  executive_summary: string;
  repository_overview: string;
  architecture_summary: string;
  repository_memory_summary: string;
  semantic_insights: string;
  timeline_evolution_summary: string;
  code_impact_summary: string;
  dependency_analysis: string;
  security_findings: string[];
  technical_debt_summary: string;
  hotspots_high_risk: string[];
  quality_metrics: Record<string, unknown>;
  repository_health_score: HealthScoreBreakdownDto;
  risk_assessment: string;
  improvement_recommendations: string[];
  suggested_refactoring: string[];
  ai_engineering_summary: string;
  sections: ReportSectionDto[];
  export_format: string;
  exported_content?: string | null;
  sources_used: string[];
  confidence_score: number;
  generated_at: string;
}

export interface EngineeringReportListDto {
  repository_id: string;
  reports: EngineeringReportDto[];
  count: number;
}

export interface EngineeringReportSummaryDto {
  repository_id: string;
  latest_report_id?: string | null;
  latest_report_type?: ReportType | null;
  health_score: number;
  health_grade: string;
  top_risks: string[];
  top_recommendations: string[];
  report_count: number;
  summary: string;
  last_generated_at?: string | null;
}

export interface ReportGenerateRequest {
  report_type?: ReportType;
  export_format?: 'json' | 'markdown' | 'html' | 'pdf';
  include_sections?: string[];
  impact_target?: string | null;
}
