# Common Interview Q&A

**Q: Is this just LangChain over a repo?**  
A: No. Core value is structured engines (graphs, memory, planning, impact). LLMs synthesize; they don’t replace analyzers.

**Q: How do you avoid spaghetti as modules grow?**  
A: Package-per-capability, facade singletons, thin APIs, Planning for orchestration, AI_RULES forbidding duplication.

**Q: How is Copilot different from `/chat`?**  
A: `/chat` is RAG-oriented conversation with indexing prerequisites. Copilot orchestrates Planning + many engines and returns structured engineering payloads.

**Q: What happens when the Knowledge Graph isn’t built?**  
A: Impact can use a lightweight memory/timeline-seeded graph and reflect that in confidence—rather than failing hard.

**Q: How would you scale this?**  
A: Implement Redis CacheInterface, external vector DB, durable stores for conversation/reports, auth at the edge, workerized heavy analyses (hooks already exist).

**Q: Biggest technical risk today?**  
A: Open API without AuthN/AuthZ and process-local stores—documented as RC-1 production blockers.

**Q: Why tree-sitter?**  
A: Consistent multi-language AST extraction feeding parsers/analyzers without ad-hoc regex sprawl.

**Q: How do tests prove quality?**  
A: Broad pytest suite across engines and APIs; RC-1 closed registration debt instead of skipping failures.
