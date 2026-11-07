import os
import uuid
from pathlib import Path
from typing import Tuple
from werkzeug.utils import secure_filename
from flask import current_app
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 Megabytes

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is an allowed resume format."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_file_extension(filename: str) -> str:
    """Extract lowercase file extension."""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""

def save_uploaded_resume(file: FileStorage, user_id: int) -> Tuple[Path, str, int, str]:
    """Validate, secure, and save an uploaded resume file for a user.
    Returns: (saved_path, original_filename, file_size, file_type)
    """
    if not file or not file.filename:
        raise ValueError("No file uploaded or filename is empty")

    original_filename = secure_filename(file.filename)
    if not is_allowed_file(original_filename):
        raise ValueError("Only PDF (.pdf) and Microsoft Word (.docx) files are supported")

    file_ext = get_file_extension(original_filename)

    # Determine storage directory for this user
    base_storage_dir = Path(current_app.config.get("RESUME_STORAGE_DIR", "./storage/resumes"))
    user_storage_dir = base_storage_dir / str(user_id)
    user_storage_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to prevent overwriting or collisions
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    target_path = user_storage_dir / unique_filename

    # Read bytes and check file size limit
    file_bytes = file.read()
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File exceeds maximum allowed size of 10 MB ({file_size / (1024*1024):.2f} MB)")

    if file_size == 0:
        raise ValueError("Uploaded file is empty (0 bytes)")

    # Save to disk
    with open(target_path, "wb") as f:
        f.write(file_bytes)

    return target_path, original_filename, file_size, file_ext

def delete_stored_resume(file_path_str: str) -> bool:
    """Safely delete resume file from disk if it exists."""
    try:
        path = Path(file_path_str)
        if path.exists() and path.is_file():
            path.unlink()
            return True
    except Exception:
        pass
    return False
