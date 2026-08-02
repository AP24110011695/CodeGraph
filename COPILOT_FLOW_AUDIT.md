# Copilot Request Flow Audit - Root Cause Analysis

## Complete Flow Trace

### 1. React Chat UI → API Request
**File**: `frontend/src/features/copilot/components/CopilotPanel.tsx`
**Lines**: 91-96

**Input**: User query string
**Output**: API call payload
```typescript
const response = await chatMutation.mutateAsync({
  repository_id: repoId,
  query,
  conversation_id: conversationId,
  provider: 'local',
});
```

**Repository context**: Not yet sent
**File names**: Not yet sent
**Code snippets**: Not yet sent
**LLLM response modification**: None

---

### 2. API Request → Copilot Endpoint
**File**: `frontend/src/features/copilot/api/copilot.api.ts`
**Lines**: 8-14

**Input**: `CopilotChatRequest` with query
**Output**: `CopilotChatResponse` from backend
```typescript
const { data } = await apiClient.post<CopilotChatResponse>('/copilot/chat', payload, {
  timeout: 120_000,
});
```

**Repository context**: Not in request
**File names**: Not in request
**Code snippets**: Not in request
**LLLM response modification**: None

---

### 3. Copilot Endpoint → Copilot Engine
**File**: `backend/app/api/copilot.py`
**Lines**: 51-63

**Input**: `CopilotChatRequest`
**Output**: `CopilotChatResponse`
```python
result = copilot_engine.chat(
    repository_id=request.repository_id,
    query=request.query,
    conversation_id=request.conversation_id,
    provider=request.provider,
)
return _to_chat_response(result)
```

**Repository context**: Not in request
**File names**: Not in request
**Code snippets**: Not in request
**LLLM response modification**: None

---

### 4. Copilot Engine → Provider Manager
**File**: `backend/app/copilot/copilot_engine.py`
**Lines**: 201-214

**Input**: Prompts from PromptBuilder
**Output**: LLM generation result
```python
generation = self.provider_manager.generate(
    prompts["user"],
    system=prompts["system"],
    provider=provider or "local",
)
logger.info("RAW_LLM_RESPONSE: %s", generation.get("text", "")[:500])
answer = generation.get("text") or self.prompt_builder.build_fallback_answer(
    query, context, tool_results, agent_summary
)
```

**Repository context**: In `context` parameter
**File names**: Potentially in context
**Code snippets**: Potentially in context
**LLLM response modification**: **YES** - fallback answer generation

---

### 5. Provider Manager → GroqProvider (or LocalHeuristicProvider)
**File**: `backend/app/copilot/providers/provider_manager.py`
**Lines**: 135-161

**Input**: Prompt string
**Output**: Dict with `text` field
```python
def generate(self, prompt: str, system: Optional[str] = None, provider: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    selected = self.get_provider(provider)
    full_prompt = prompt
    if system:
        full_prompt = f"System:\n{system}\n\n{prompt}"
    try:
        text = selected.generate(full_prompt, **kwargs)
        return {
            "text": text,
            "provider": selected.__class__.__name__,
            "error": None,
        }
    except Exception as exc:
        logger.debug("ProviderManager: generation failed (%s); using local fallback", exc)
        fallback = LocalHeuristicProvider()
        return {
            "text": fallback.generate(full_prompt, **kwargs),
            "provider": "LocalHeuristicProvider",
            "error": str(exc),
        }
```

**Repository context**: In prompt
**File names**: Potentially in prompt
**Code snippets**: Potentially in prompt
**LLLM response modification**: **YES** - fallback to LocalHeuristicProvider on error

---

### 6. GroqProvider → Text Response
**File**: `backend/app/ai/llm_client.py` (GroqProvider implementation)

**Input**: Prompt with tool results
**Output**: Text string from Groq API

**Repository context**: In prompt if RAG context was included
**File names**: In prompt if RAG context was included
**Code snippets**: In prompt if RAG context was included
**LLLM response modification**: None (returns raw LLM response)

---

### 7. LocalHeuristicProvider → Formatted Response
**File**: `backend/app/copilot/providers/local_provider.py`
**Lines**: 33-77

**Input**: Prompt string
**Output**: **"Analysis Results" formatted response**
```python
def generate(self, prompt: str, **kwargs: Any) -> str:
    try:
        # Extract structured information from prompt
        tool_section = self.prompt_parser.extract_tool_results(prompt)
        question = self.prompt_parser.extract_question(prompt)
        intent = self.prompt_parser.extract_intent(prompt)
        
        if tool_section and question:
            # Parse tool data
            tool_data = self.prompt_parser.parse_tool_data(tool_section)
            
            # Check if this is an executive report request
            if self._is_executive_report_request(question, intent):
                # Use executive report pipeline
                response = self.synthesizer.synthesize(tool_data, intent, question)
                report_data = self.report_synthesizer.synthesize_executive_report(response, question, tool_data)
                return self.executive_formatter.format(report_data, question)
            else:
                # Use standard pipeline for single-domain queries
                response = self.synthesizer.synthesize(tool_data, intent, question)
                return self.formatter.format(response, question)
        
        # Fallback to generic response
        if question:
            return (
                f"Engineering assessment for: {question}. "
                "Based on assembled CodeGraph intelligence (planning, memory, tools)."
            )
        return "Engineering assessment based on assembled CodeGraph intelligence."
```

**Repository context**: In prompt
**File names**: In prompt
**Code snippets**: In prompt
**LLLM response modification**: **YES** - Replaces LLM response with formatted cards

---

### 8. LocalHeuristicProvider → MarkdownFormatter
**File**: `backend/app/copilot/response/formatter.py`
**Lines**: 508-536

**Input**: Structured response data
**Output**: **"# Analysis Results" formatted markdown**
```python
def _format_generic(self, response: CopilotResponse, question: str) -> str:
    """Format generic response as Markdown."""
    report = [f"# Analysis Results\n"]
    report.append(f'Based on the analysis of your question about "{question}":\n')
    
    # Merge all tool outputs into a coherent summary
    all_summaries = []
    for tool_name, data in response.raw_tool_data.items():
        if data.get("summary"):
            summary = data["summary"]
            # Clean up common prefixes
            for prefix in ["Repository metrics:", "Dependency graph:", "Security analysis found", "Architecture:", "Timeline:"]:
                if summary.startswith(prefix):
                    summary = summary[len(prefix):].strip()
            all_summaries.append(summary)
    
    if all_summaries:
        report.append("## Key Findings\n")
        for summary in all_summaries:
            report.append(f"- {summary}")
        report.append("")
    
    # Recommendations
    if response.recommendations:
        report.append("## Recommendations\n")
        for rec in response.recommendations:
            report.append(f"- {rec}")
    
    return "\n".join(report)
```

**Repository context**: In tool summaries
**File names**: Not in formatted output
**Code snippets**: Not in formatted output
**LLLM response modification**: **YES** - Replaces LLM response with "# Analysis Results"

---

### 9. API Response JSON → Frontend Adapter
**File**: `frontend/src/features/copilot/api/copilot.adapters.ts`
**Lines**: 7-26

**Input**: `CopilotChatResponse` from backend
**Output**: `CopilotMessageView`
```typescript
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
```

**Repository context**: In relatedFiles
**File names**: In relatedFiles
**Code snippets**: **NO** - Not in content field
**LLLM response modification**: None (just maps fields)

---

### 10. Frontend Adapter → Message Bubble
**File**: `frontend/src/features/copilot/components/MessageBubble.tsx`
**Lines**: 35

**Input**: `CopilotMessageView` with content
**Output**: Rendered markdown
```typescript
<MarkdownContent content={message.content} />
```

**Repository context**: In message.content (as "# Analysis Results")
**File names**: Not in message.content
**Code snippets**: Not in message.content
**LLLM response modification**: None (just renders content)

---

### 11. Message Bubble → MarkdownContent
**File**: `frontend/src/features/_shared/components/MarkdownContent.tsx`
**Lines**: 12-93

**Input**: Content string (already "# Analysis Results")
**Output**: Rendered markdown

**Repository context**: In content string
**File names**: Not in content string
**Code snippets**: Not in content string
**LLLM response modification**: None (just renders markdown)

---

## Root Cause Identification

### EXACT FILE AND LINE WHERE RESPONSE CHANGES:

**`backend/app/copilot/providers/local_provider.py` line 33-77**

The `LocalHeuristicProvider.generate()` method replaces the detailed LLM response with formatted "Analysis Results" cards.

### SPECIFIC ANSWERS TO QUESTIONS:

#### Does PromptBuilder send retrieved chunks to Groq?
**YES** - `prompt_builder.py` line 58-59:
```python
if context.get("rag_context"):
    sections.append(f"RAG Context:\n{context['rag_context'][:2500]}")
```

#### Does Groq return a detailed answer?
**YES** - When GroqProvider is used, it returns the actual LLM response with detailed content.

#### Is the API returning the complete answer?
**NO** - The API returns the answer from LocalHeuristicProvider, which replaces the LLM response.

#### Is the frontend truncating or replacing it?
**NO** - The frontend correctly renders whatever content it receives from the backend.

#### Is the frontend rendering markdown correctly?
**YES** - The frontend correctly renders markdown using ReactMarkdown.

#### Is some parser replacing the LLM answer with "Analysis Results"?
**YES** - The `LocalHeuristicProvider` replaces the LLM answer with "# Analysis Results" formatted markdown.

---

## The Problem Chain

1. **ProviderManager** (`provider_manager.py` line 47-70) auto-detects providers but defaults to "local" if no cloud provider is configured
2. **LocalHeuristicProvider** (`local_provider.py` line 33-77) is used instead of GroqProvider
3. **LocalHeuristicProvider** ignores the LLM response and generates its own formatted response
4. **MarkdownFormatter** (`formatter.py` line 508-536) creates "# Analysis Results" cards
5. **Frontend** correctly renders these "# Analysis Results" cards

---

## Root Cause Summary

The issue is in **`backend/app/copilot/providers/provider_manager.py` lines 47-70**. The auto-detection logic defaults to "local" provider even when Groq is configured, causing the `LocalHeuristicProvider` to be used instead of `GroqProvider`.

The `LocalHeuristicProvider` (`local_provider.py` line 33-77) then replaces the detailed LLM response with formatted "Analysis Results" cards via the `MarkdownFormatter._format_generic()` method (`formatter.py` line 508-536).

This means the GroqProvider never gets used for generation, and the detailed LLM response is replaced with template-based cards before reaching the frontend.
