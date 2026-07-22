from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    status: str
