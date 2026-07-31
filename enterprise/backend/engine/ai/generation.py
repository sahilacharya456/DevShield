import ast
import json
import logging
from engine.ai.router import AIRouter
from engine.ai.prompts import PromptEngine

logger = logging.getLogger("DevShield.CodeGeneration")

class CodeGenerationPipeline:
    
    @staticmethod
    def _validate_syntax(code: str, language: str) -> bool:
        """Validate syntax before returning to user. Supports Python AST."""
        if language.lower() not in ["python", "py"]:
            return True # Cannot AST validate other languages locally easily
            
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.warning(f"Generated Python syntax is invalid: {e}")
            return False

    @classmethod
    async def generate(cls, task: str, language: str, context: str = "", preferences: str = "") -> dict:
        """Generates secure code, automatically retrying if syntax is invalid."""
        
        prompt = PromptEngine.generate_system_prompt(
            task=f"Write {language} code for: {task}",
            preferences=preferences,
            context=context,
            constraints="Return ONLY valid JSON: {'code': '...', 'security_features': ['...']}"
        )
        
        max_attempts = 2
        for attempt in range(max_attempts):
            response_text = await AIRouter.generate(prompt=prompt, json_mode=True)
            
            try:
                data = json.loads(response_text)
                generated_code = data.get("code", "")
                
                # Post-Processing: Syntax Validation
                is_valid = cls._validate_syntax(generated_code, language)
                if is_valid:
                    return {
                        "success": True,
                        "code": generated_code,
                        "security_features": data.get("security_features", []),
                        "attempts": attempt + 1
                    }
                else:
                    logger.info("Syntax invalid. Asking LLM to fix its own code...")
                    prompt += f"\n\nYOUR PREVIOUS CODE HAD A SYNTAX ERROR. Fix it:\n{generated_code}"
            except Exception as e:
                logger.error(f"Failed to parse generation response: {e}")
                
        return {"success": False, "code": "// Generation failed or syntax invalid"}
