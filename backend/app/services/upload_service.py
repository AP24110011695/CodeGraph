import os
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException


class UploadService:
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB
    UPLOAD_DIR = Path("uploads")
    ALLOWED_MIME_TYPES = [
        "application/zip",
        "application/x-zip-compressed",
        "application/x-zip",
    ]
    EXECUTABLE_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".ps1", ".msi", ".dll", ".so", ".dylib"}

    def __init__(self) -> None:
        self.UPLOAD_DIR.mkdir(exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        if file.size is None or file.size == 0:
            raise HTTPException(status_code=400, detail="Empty file upload")

        if file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024 * 1024)} MB",
            )

        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=415, detail="Invalid file type. Only ZIP files are allowed")

    def validate_zip_content(self, file_path: Path) -> None:
        try:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    file_ext = Path(file_info.filename).suffix.lower()
                    if file_ext in self.EXECUTABLE_EXTENSIONS:
                        raise ValueError(f"ZIP contains executable file: {file_info.filename}")
                    if ".." in file_info.filename or file_info.filename.startswith("/") or file_info.filename.startswith("\\"):
                        raise ValueError(f"ZIP contains path traversal risk: {file_info.filename}")

                if not zip_ref.namelist():
                    raise ValueError("ZIP archive is empty")

        except zipfile.BadZipFile:
            raise ValueError("Corrupted or invalid ZIP file")

    async def save_upload(self, file: UploadFile) -> tuple[str, str]:
        self.validate_file(file)

        upload_id = str(uuid.uuid4())
        filename = f"{upload_id}.zip"
        file_path = self.UPLOAD_DIR / filename

        try:
            import aiofiles
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)

            try:
                self.validate_zip_content(file_path)
            except ValueError as ve:
                if file_path.exists():
                    os.remove(file_path)
                raise HTTPException(status_code=400, detail=str(ve))

            return upload_id, filename

        except HTTPException:
            raise
        except Exception as e:
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


upload_service = UploadService()
