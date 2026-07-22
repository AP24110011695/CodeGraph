from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    status: str
    project_path: Optional[str] = None
