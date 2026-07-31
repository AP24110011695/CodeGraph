export interface CommitRecordDto {
  sha: string;
  message: string;
  author: string;
  email: string;
  timestamp: string;
  files_changed: string[];
  insertions: number;
  deletions: number;
  modules_touched: string[];
}

export interface HotspotDto {
  path: string;
  hotspot_type: string;
  change_frequency: number;
  churn_score: number;
  authors: string[];
  risk_level: string;
  reason: string;
}

export interface ArchitectureDriftEventDto {
  event_id: string;
  timestamp: string;
  description: string;
  severity: string;
  modules_affected: string[];
  coupling_delta: number;
  category: string;
}

export interface HistoricalSummaryDto {
  repository_id: string;
  period_start?: string | null;
  period_end?: string | null;
  what_changed_most: string[];
  unstable_files: string[];
  modules_evolving_together: string[];
  architecture_evolution: string;
  tightly_coupled_components: string[];
  narrative: string;
}

export interface TimelineStatisticsDto {
  total_commits: number;
  total_authors: number;
  total_files_touched: number;
  total_modules_touched: number;
  hotspot_count: number;
  drift_event_count: number;
  average_files_per_commit: number;
  most_active_author?: string | null;
  most_changed_module?: string | null;
  most_changed_file?: string | null;
  change_frequency_by_module: Record<string, number>;
}

export interface RepositoryTimelineDto {
  repository_id: string;
  provider: string;
  commits: CommitRecordDto[];
  statistics: TimelineStatisticsDto;
  historical_summary: HistoricalSummaryDto;
  hotspots: HotspotDto[];
  ownership: Array<{
    path: string;
    primary_owner: string;
    ownership_pct: number;
    contributors: Record<string, number>;
    bus_factor: number;
  }>;
  architecture_drift_events: ArchitectureDriftEventDto[];
  generated_at: string;
}

export interface ModuleEvolutionDto {
  module_name: string;
  change_count: number;
  file_count: number;
  authors: string[];
  related_modules: string[];
  stability: string;
  summary: string;
}

export interface EvolutionDto {
  repository_id: string;
  modules: ModuleEvolutionDto[];
  files: Array<{
    file_path: string;
    change_count: number;
    authors: string[];
    stability: string;
    summary: string;
  }>;
  co_evolution: Array<{
    module_a: string;
    module_b: string;
    co_change_count: number;
    coupling_score: number;
  }>;
  what_changed_most: string[];
  modules_evolving_together: string[];
  summary: string;
}

export interface HotspotsResponseDto {
  repository_id: string;
  hotspots: HotspotDto[];
  unstable_files: string[];
  frequently_changing_parts: string[];
  summary: string;
}

export interface TimelineSnapshot {
  id: string;
  sha: string;
  label: string;
  timestamp: string;
  author: string;
  message: string;
  filesChanged: number;
  insertions: number;
  deletions: number;
  modules: string[];
}

export interface SnapshotComparison {
  left: TimelineSnapshot;
  right: TimelineSnapshot;
  addedFiles: string[];
  removedFiles: string[];
  sharedFiles: string[];
  moduleDelta: string[];
  changeSummary: string;
}
