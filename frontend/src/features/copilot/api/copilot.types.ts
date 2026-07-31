/** Types for POST /copilot/chat and related endpoints. */

export interface CopilotChatRequest {
  repository_id: string;
  query: string;
  conversation_id?: string | null;
  provider?: string | null;
}

export interface CopilotPlanSummary {
  intent?: string | null;
  required_modules: string[];
  execution_order: string[];
  confidence_score?: number | null;
  estimated_cost?: string | null;
}

export interface CopilotChatResponse {
  conversation_id: string;
  repository_id: string;
  query: string;
  answer: string;
  confidence: number;
  repository_context: Record<string, unknown>;
  modules_used: string[];
  tools_used: string[];
  reasoning_summary: string;
  related_components: string[];
  related_files: string[];
  recommendations: string[];
  follow_up_questions: string[];
  citations: string[];
  execution_time_ms: number;
  provider?: string | null;
  intent?: string | null;
  plan_confidence: number;
  mode: string;
  plan?: CopilotPlanSummary | null;
}

export interface CopilotHistoryResponse {
  conversation_id?: string | null;
  repository_id?: string | null;
  count: number;
  history: Array<Record<string, unknown>>;
}

export interface CopilotMessageView {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
  status?: 'pending' | 'complete' | 'error';
  confidence?: number;
  citations?: string[];
  relatedFiles?: string[];
  relatedComponents?: string[];
  modulesUsed?: string[];
  toolsUsed?: string[];
  recommendations?: string[];
  followUpQuestions?: string[];
  reasoningSummary?: string;
  error?: string;
}

export interface CopilotContextSnapshot {
  relatedFiles: string[];
  relatedComponents: string[];
  modulesUsed: string[];
  toolsUsed: string[];
  citations: string[];
  reasoningSummary: string;
  recommendations: string[];
}
