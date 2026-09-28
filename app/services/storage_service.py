"""Storage service supporting local filesystem and cloud S3."""

from pathlib import Path
import shutil
from typing import BinaryIO, Optional
from fastapi import UploadFile
from app.config import settings
from app.utils.logger import logger


class StorageService:
    """Manages file storage for uploaded datasets."""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_file(self, upload_file: UploadFile, destination_name: Optional[str] = None) -> Path:
        """Save an uploaded file to the local storage directory."""
        filename = destination_name or upload_file.filename or "uploaded_data.csv"
        dest_path = self.upload_dir / filename

        try:
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            logger.info("File saved successfully", path=str(dest_path), size=dest_path.stat().st_size)
            return dest_path
        except Exception as exc:
            logger.log_upload_failed(filename, str(exc))
            raise


storage_service = StorageService()
