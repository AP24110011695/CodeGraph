from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from app.schemas.upload import UploadResponse
from app.services.upload_service import upload_service
from app.services.extraction_service import extraction_service
from app.repository_state.state_machine import RepositoryStateMachine
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from storage.repository_store import repository_store

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    upload_id, filename = await upload_service.save_upload(file)
    project_path = extraction_service.extract(upload_id, filename)

    display_name = Path(file.filename or "repository").stem or upload_id
    
    # Register repository with proper metadata
    repository_store.register_upload(
        upload_id,
        project_path,
        repository_id=upload_id,
        name=display_name,
    )
    
    # Log repository registration
    import logging
    logger = logging.getLogger(__name__)
    logger.info("UPLOAD: Registered repository %s (%s) at %s", display_name, upload_id, project_path)

    # Initialize state machine
    RepositoryStateMachine(upload_id)

    # Publish event
    event_bus.publish(
        event_type=EventType.REPOSITORY_UPLOADED,
        repository_id=upload_id,
        payload={"filename": filename, "project_path": str(project_path), "name": display_name}
    )

    return UploadResponse(
        upload_id=upload_id,
        filename=filename,
        status="extracted",
        project_path=project_path
    )
