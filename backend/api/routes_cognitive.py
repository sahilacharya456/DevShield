from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.security.auth import get_current_user
from backend.models.orm import User

router = APIRouter()


class TrainRequest(BaseModel):
    developer_id: str = Field(..., description="Unique developer identifier (e.g., GitHub username).")
    code_samples: List[str] = Field(..., description="List of code samples from this developer's history (min 3).")


class VerifyRequest(BaseModel):
    developer_id: str = Field(..., description="Developer to verify against.")
    code: str = Field(..., description="New code snippet to compare against the registered profile.")


class RemoveProfileRequest(BaseModel):
    developer_id: str = Field(..., description="Developer whose profile should be removed.")


@router.post("/train", summary="CognitiveDNA™: Register Developer Profile")
async def train_developer(
    payload: TrainRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **CognitiveDNA™ — Developer Behavioral Profiling**

    Builds a unique coding-style fingerprint from a developer's historical commits.
    Requires at least 3 code samples. Extracts 20 behavioral features including:
    - Naming conventions (snake_case vs camelCase)
    - Comment density and docstring usage
    - Function length and structure patterns
    - Import style, quote preference, indentation
    """
    from backend.engine.cognitive.developer_fingerprinter import developer_fingerprinter

    if len(payload.code_samples) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"At least 3 code samples required. Got {len(payload.code_samples)}."
        )

    success = developer_fingerprinter.train_developer(payload.developer_id, payload.code_samples)
    if not success:
        raise HTTPException(
            status_code=422,
            detail="Profile training failed. Ensure samples are valid Python code."
        )

    return {
        "status": "trained",
        "developer_id": payload.developer_id,
        "samples_processed": len(payload.code_samples),
        "message": f"CognitiveDNA™ profile registered for '{payload.developer_id}'."
    }


@router.post("/verify", summary="CognitiveDNA™: Verify Code Authorship")
async def verify_author(
    payload: VerifyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **CognitiveDNA™ — Authorship Verification**

    Compares a code snippet against a registered developer's style profile
    using cosine similarity + z-score deviation analysis across 20 features.

    Alerts if similarity drops below 65% — possible insider threat or account compromise.
    """
    from backend.engine.cognitive.developer_fingerprinter import developer_fingerprinter
    return developer_fingerprinter.verify_author(payload.developer_id, payload.code)


@router.get("/profiles", summary="List all registered developer profiles")
async def list_profiles(
    current_user: User = Depends(get_current_user)
):
    """List all developer IDs with registered CognitiveDNA™ profiles."""
    from backend.engine.cognitive.developer_fingerprinter import developer_fingerprinter
    profiles = developer_fingerprinter.list_profiles()
    return {
        "total_profiles": len(profiles),
        "profiles": profiles
    }


@router.get("/profiles/{developer_id}", summary="Get developer profile summary")
async def get_profile(
    developer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the style summary for a specific developer's registered profile."""
    from backend.engine.cognitive.developer_fingerprinter import developer_fingerprinter
    result = developer_fingerprinter.get_profile_summary(developer_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/profiles/{developer_id}", summary="Remove a developer profile")
async def remove_profile(
    developer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a developer's CognitiveDNA™ profile (e.g., off-boarding)."""
    from backend.engine.cognitive.developer_fingerprinter import developer_fingerprinter
    removed = developer_fingerprinter.remove_profile(developer_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"No profile found for '{developer_id}'.")
    return {"status": "removed", "developer_id": developer_id}
