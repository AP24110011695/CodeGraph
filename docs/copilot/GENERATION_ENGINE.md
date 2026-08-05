# GENERATION_ENGINE.md

### CodeGraph — Generation Engine

---

## 1. Overview
The Generation Engine handles interactions with the LLM (Groq), applying the final prompt templates, receiving raw model output, and triggering post-processing.

## 2. Details
- **LLM Call**: Executes generation against the fully-specified prompt.
- **Post Processing**: Parses structured output from the LLM and attaches/links citations to the chunks that back them.
- **Answer Verification**: Validates the output against structural, citation, and factual requirements.

TODO: Expand on specific LLM parameters (temperature, max tokens), streaming mechanisms, and fail-safes.

## 3. References
- [Prompt Pipeline](../architecture/PROMPT_PIPELINE.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
