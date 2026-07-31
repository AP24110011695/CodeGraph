export interface SecurityIssue {
  severity: string;
  rule: string;
  file: string;
  line: number;
  description: string;
  language: string;
}

export interface SecuritySummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface SecurityResponse {
  summary: SecuritySummary;
  issues: SecurityIssue[];
  total_issues: number;
}
