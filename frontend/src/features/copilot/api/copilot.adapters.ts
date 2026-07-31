import type {
  CopilotChatResponse,
  CopilotContextSnapshot,
  CopilotMessageView,
} from './copilot.types';

export function adaptChatResponseToMessage(
  response: CopilotChatResponse,
  messageId: string
): CopilotMessageView {
  return {
    id: messageId,
    role: 'assistant',
    content: response.answer || 'No answer returned.',
    createdAt: new Date().toISOString(),
    status: 'complete',
    confidence: response.confidence,
    citations: response.citations,
    relatedFiles: response.related_files,
    relatedComponents: response.related_components,
    modulesUsed: response.modules_used,
    toolsUsed: response.tools_used,
    recommendations: response.recommendations,
    followUpQuestions: response.follow_up_questions,
    reasoningSummary: response.reasoning_summary,
  };
}

export function adaptChatResponseToContext(
  response: CopilotChatResponse
): CopilotContextSnapshot {
  return {
    relatedFiles: response.related_files ?? [],
    relatedComponents: response.related_components ?? [],
    modulesUsed: response.modules_used ?? [],
    toolsUsed: response.tools_used ?? [],
    citations: response.citations ?? [],
    reasoningSummary: response.reasoning_summary ?? '',
    recommendations: response.recommendations ?? [],
  };
}
