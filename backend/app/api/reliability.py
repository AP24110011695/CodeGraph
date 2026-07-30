from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.schemas.reliability import DeadLetterJob, CircuitBreakerStatus
from app.reliability.dead_letter_queue import dead_letter_queue
from app.reliability.circuit_breaker import circuit_breaker_manager
from app.reliability.reliability_manager import reliability_manager

router = APIRouter(prefix="/reliability", tags=["reliability"])

@router.get("/jobs", response_model=Dict[str, Any])
def get_reliability_stats():
    # Return some basic stats
    return {
        "status": "healthy",
        "dlq_size": len(dead_letter_queue.get_jobs(limit=1000)),
        "circuit_breakers": len(circuit_breaker_manager.get_all_statuses())
    }

@router.get("/dead-letter", response_model=List[DeadLetterJob])
def get_dead_letter_queue(limit: int = 100, offset: int = 0):
    return dead_letter_queue.get_jobs(limit=limit, offset=offset)

@router.post("/replay/{job_id}")
def replay_dlq_job(job_id: str):
    success = reliability_manager.replay_dlq_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found in DLQ")
    return {"message": f"Job {job_id} replayed successfully"}

@router.get("/circuit-breakers", response_model=List[CircuitBreakerStatus])
def get_circuit_breakers():
    return circuit_breaker_manager.get_all_statuses()
