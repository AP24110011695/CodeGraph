import os
import shutil
import zipfile
from pathlib import Path
from fastapi import HTTPException

class ExtractionService:
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB max individual file size
    MAX_TOTAL_SIZE = 1000 * 1024 * 1024  # 1GB total extracted size
    MAX_FILES = 10000

    def __init__(self) -> None:
        self.STORAGE_DIR = Path("storage/extracted")
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR = Path("uploads")

    def extract(self, upload_id: str, filename: str) -> str:
        zip_path = self.UPLOAD_DIR / filename
        extract_path = self.STORAGE_DIR / upload_id

        if not zip_path.exists():
            raise HTTPException(status_code=404, detail="Upload not found")

        # Clean extraction if exists (prevent overwriting)
        if extract_path.exists():
            shutil.rmtree(extract_path)
        
        extract_path.mkdir(parents=True, exist_ok=True)

        try:
            total_size = 0
            file_count = 0

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Reject path traversal
                    if ".." in file_info.filename or file_info.filename.startswith("/") or file_info.filename.startswith("\\"):
                        raise ValueError(f"Path traversal attempt detected: {file_info.filename}")

                    # Reject symlinks
                    # High 4 bits of external_attr: 0xA is symlink
                    is_symlink = (file_info.external_attr >> 16) & 0xA000 == 0xA000
                    if is_symlink:
                        raise ValueError(f"Symbolic links are not allowed: {file_info.filename}")

                    # Check for zip bomb
                    total_size += file_info.file_size
                    file_count += 1
                    
                    if file_info.file_size > self.MAX_FILE_SIZE:
                        raise ValueError(f"File {file_info.filename} exceeds maximum allowed size")
                    if total_size > self.MAX_TOTAL_SIZE:
                        raise ValueError("Total extracted size exceeds maximum allowed (zip bomb protection)")
                    if file_count > self.MAX_FILES:
                        raise ValueError("Too many files in archive (zip bomb protection)")

                    # Extract file (zipfile.extract resolves paths safely when checked properly)
                    zip_ref.extract(file_info, extract_path)

            return str(extract_path.as_posix())

        except Exception as e:
            # Clean extraction on failure
            if extract_path.exists():
                shutil.rmtree(extract_path)
            raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")

extraction_service = ExtractionService()
