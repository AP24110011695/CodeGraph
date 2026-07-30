"""Copilot API — Unified Intelligence Orchestrator (CG-070)."""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.copilot.copilot_engine import copilot_engine
from app.schemas.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotClearHistoryResponse,
    CopilotExecuteRequest,
    CopilotHistoryResponse,
    CopilotPlanSummary,
    CopilotRequest,
    CopilotResponse,
)

router = APIRouter(prefix="/copilot", tags=["copilot"])


def _to_chat_response(result: dict) -> CopilotChatResponse:
    plan = result.get("plan") or {}
    return CopilotChatResponse(
        conversation_id=result.get("conversation_id", ""),
        repository_id=result.get("repository_id", ""),
        query=result.get("query", ""),
        answer=result.get("answer", ""),
        confidence=float(result.get("confidence") or 0.0),
        repository_context=result.get("repository_context") or {},
        modules_used=result.get("modules_used") or [],
        tools_used=result.get("tools_used") or [],
        reasoning_summary=result.get("reasoning_summary") or "",
        related_components=result.get("related_components") or [],
        related_files=result.get("related_files") or [],
        recommendations=result.get("recommendations") or [],
        follow_up_questions=result.get("follow_up_questions") or [],
        citations=result.get("citations") or [],
        execution_time_ms=int(result.get("execution_time_ms") or 0),
        provider=result.get("provider"),
        intent=result.get("intent"),
        plan_confidence=float(result.get("plan_confidence") or 0.0),
        mode=result.get("mode") or "chat",
        plan=CopilotPlanSummary(**plan) if plan else None,
    )


@router.post("/chat", response_model=CopilotChatResponse)
async def copilot_chat(request: CopilotChatRequest) -> CopilotChatResponse:
    """Answer an engineering question by orchestrating existing intelligence."""
    try:
        result = copilot_engine.chat(
            repository_id=request.repository_id,
            query=request.query,
            conversation_id=request.conversation_id,
            provider=request.provider,
        )
        return _to_chat_response(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/execute", response_model=CopilotChatResponse)
async def copilot_execute(request: CopilotExecuteRequest) -> CopilotChatResponse:
    """Execute orchestration with optional explicit tools."""
    try:
        options = {}
        if request.impact_target:
            options["impact_target"] = request.impact_target
        result = copilot_engine.execute(
            repository_id=request.repository_id,
            query=request.query,
            conversation_id=request.conversation_id,
            provider=request.provider,
            tools=request.tools,
            options=options,
        )
        return _to_chat_response(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history", response_model=CopilotHistoryResponse)
async def copilot_history(
    conversation_id: Optional[str] = Query(None),
    repository_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> CopilotHistoryResponse:
    """Return conversation history (independent of Repository Memory)."""
    result = copilot_engine.get_history(conversation_id, repository_id, limit)
    return CopilotHistoryResponse(**result)


@router.delete("/history", response_model=CopilotClearHistoryResponse)
async def copilot_clear_history(
    conversation_id: Optional[str] = Query(None),
    repository_id: Optional[str] = Query(None),
) -> CopilotClearHistoryResponse:
    """Clear conversation history for a conversation, repository, or all."""
    result = copilot_engine.clear_history(conversation_id, repository_id)
    return CopilotClearHistoryResponse(**result)


@router.post("/{upload_id}", response_model=CopilotResponse)
async def process_copilot_query(
    upload_id: str,
    request: CopilotRequest,
    download: bool = Query(False, description="If true, return copilot_response.json file"),
) -> CopilotResponse | FileResponse:
    """Legacy capability-routing endpoint (pre-CG-070). Prefer /copilot/chat."""
    result = copilot_engine.process_query(upload_id, request.query)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = CopilotResponse(
        upload_id=result.get("upload_id"),
        query=result.get("query"),
        intent=result.get("intent"),
        module=result.get("module"),
        confidence=result.get("confidence", 0),
        answer=result.get("answer"),
        sources=result.get("sources", []),
        evidence=result.get("evidence", []),
        related_modules=result.get("related_modules", []),
        error=result.get("error"),
    )

    if download:
        report_file = Path("copilot_response.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)
        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_copilot_response.json",
        )

    return response
