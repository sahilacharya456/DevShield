from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from backend.security.auth import get_pro_user
from backend.engine.antivirus.aegis_engine import AegisEngine
import os
import uuid
import aiofiles
import re

def secure_filename(filename: str) -> str:
    if not filename:
        return ""
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename.strip('._')

router = APIRouter()
engine = AegisEngine()

UPLOAD_DIR = os.path.join("backend", "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/scan")
async def scan_file(file: UploadFile = File(...), user=Depends(get_pro_user)):
    try:
        # 1. Limit file size (25MB max)
        MAX_FILE_SIZE = 25 * 1024 * 1024
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 25MB.")
            
        # 2. Prevent path traversal using secure_filename
        safe_filename = secure_filename(file.filename)
        if not safe_filename:
            safe_filename = "unnamed_file"
            
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{safe_filename}")
        
        # 3. Prevent Event Loop Blocking by using aiofiles
        async with aiofiles.open(temp_path, "wb") as buffer:
            while content := await file.read(1024 * 1024):  # Read in 1MB chunks
                await buffer.write(content)
            
        result = await engine.scan_file(temp_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
