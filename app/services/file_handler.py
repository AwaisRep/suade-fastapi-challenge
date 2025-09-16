import os
from fastapi import UploadFile
from ..config import UPLOADS_DIR

class FileTooLargeError(Exception):
    """Raised when an uploaded file exceeds the allowed size."""
    pass

MAX_FILE_SIZE = 95 * 1024 * 1024 # 95mb limit, this would have been 100mb but Github applies 100mb limit so it is difficult to test
CHUNK_SIZE = 8192 # 8kb chunk size to allow for reading into memory

async def load_from_disk() -> bytes:
    """
    Attempts to load the transactions file by using the path in config.py

    Returns:
        Some bytes-like object to be processed by the upload endpoint
    """
    file_path = UPLOADS_DIR / "latest.csv"

    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise

async def load_file(file: UploadFile) -> bytes:
    """
    Only loads the file into memory, on user upload, if it passes file constraints

    Args: 
        file: The CSV file of transaction data a user wishes to upload
    
    Returns:
        bytes: Some bytes-like object ready for data validation
    """

    try:
        # Load the file using chunking to verify file size
        file_size = 0
        while chunk := await file.read(CHUNK_SIZE):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise FileTooLargeError("File is too large") # No need to read more than necessary, limit is 100mb

        file.file.seek(0) # Reset seek pointer to 0 so that it reads all contents
        return await file.read()
    except:
        raise

async def save_file(file: UploadFile) -> str:
    """
    Attempts to save the transactions CSV file to the uploads folder

    Args:
        file: The validated file to be uploaded
    
    Returns:
        str: The raw path of the file object
    """

    file_path = UPLOADS_DIR / "latest.csv"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True) # Only write to disk if the uplaod directory exists

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return str(file_path)