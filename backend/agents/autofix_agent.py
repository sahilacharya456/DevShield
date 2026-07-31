import structlog

logger = structlog.get_logger("DevShield.AutoFixAgent")

class AutoFixAgent:
    def __init__(self):
        self.rag = None
        try:
            from backend.engine.ai.rag_engine import RAGEngine
            self.rag = RAGEngine()
        except Exception as e:
            logger.warning(f"RAG context unavailable for AutoFixAgent: {e}")

    async def fix(self, code: str, vulnerabilities: list) -> dict:
        if not vulnerabilities:
            return {
                "fixed_code": code,
                "fixes_applied": ["No vulnerabilities detected"],
                "remaining_concerns": [],
                "confidence": 100
            }

        # 1. RAG context enrichment
        vuln_titles = [v.get("title", "") for v in vulnerabilities]
        context = self.rag.get_context_for_fix(" ".join(vuln_titles)) if self.rag else ""
        
        # 2. Strict JSON Auto-Fix via Instructor
        try:
            from backend.engine.ai.auto_fix import run_auto_fix
            result = run_auto_fix(code, vulnerabilities, context=context)
        except Exception as e:
            logger.error(f"Auto-fix engine unavailable: {e}")
            result = None
        
        if not result:
            return {
                "fixed_code": code,
                "fixes_applied": [],
                "remaining_concerns": ["Auto-fix engine failed or API key not configured."],
                "confidence": 0
            }
            
        return result
