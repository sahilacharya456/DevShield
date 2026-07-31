from fastapi import APIRouter, Request
from backend.models.schemas import FeedbackRequest, FeedbackResponse
from backend.learning.feedback_store import FeedbackStore

router = APIRouter()
store = FeedbackStore()

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(request: Request, body: FeedbackRequest):
    await store.log_feedback(body.model_dump())
    return FeedbackResponse(status="success", message="Feedback recorded for fine-tuning")
