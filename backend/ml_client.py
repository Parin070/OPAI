import os
import httpx
from fastapi import UploadFile

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://localhost:8001")

async def analyze_image_with_ml(file_bytes: bytes, filename: str, content_type: str) -> dict:
    async with httpx.AsyncClient() as client:
        # We send the file using multipart/form-data
        files = {"file": (filename, file_bytes, content_type)}
        response = await client.post(f"{ML_SERVICE_URL}/analyze", files=files)
        response.raise_for_status()
        return response.json()
