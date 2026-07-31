from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from backend.security.auth import get_pro_user
from backend.engine.antivirus.aegis_engine import AegisEngine
import os
import shutil
import uuid

router = APIRouter()
engine = AegisEngine()

UPLOAD_DIR = os.path.join("backend", "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/scan")
async def scan_file(file: UploadFile = File(...), user=Depends(get_pro_user)):
    try:
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = await engine.scan_file(temp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
