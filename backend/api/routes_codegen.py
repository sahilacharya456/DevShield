from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.models.schemas import CodeGenRequest, CodeGenResponse, StandardErrorResponse
from backend.agents.codegen_agent import CodeGenAgent
from backend.agents.security_agent import SecurityAgent
from backend.learning.preference_manager import PreferenceManager
from backend.learning.session_manager import SessionManager

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

from backend.security.auth import get_current_user

@router.post("/", response_model=CodeGenResponse)
@limiter.limit("10/minute")
async def generate_code(request: Request, body: CodeGenRequest, user=Depends(get_current_user)):
    try:
        pref_manager = PreferenceManager()
        prefs = await pref_manager.get_preferences()
        
        agent = CodeGenAgent()
        result = await agent.generate(body.task, body.language, body.security_level, prefs)
        
        # Perform quick security scan to associate score with session
        sec_agent = SecurityAgent()
        sec_report = await sec_agent.analyze(result["code"])
        
        sess_manager = SessionManager()
        session_id = await sess_manager.create_session(
            user_id=user.id,
            task=body.task,
            language=body.language,
            code=result["code"],
            ai_used=result["ai_used"],
            score=sec_report["overall_score"]
        )
        
        return CodeGenResponse(
            code=result["code"],
            confidence_score=result["confidence_score"],
            alternative_approaches=result["alternative_approaches"],
            token_cost=result["token_cost"],
            ai_used=result["ai_used"]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return generic server error handled by fastAPI natively or customize
        raise e
