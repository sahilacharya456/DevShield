from fastapi import APIRouter, Request
from backend.models.schemas import DocumentRequest
from backend.ai.ai_router import AIRouter
from backend.docs.doc_generator import DocGenerator

router = APIRouter()

@router.post("/")
async def generate_docs(request: Request, body: DocumentRequest):
    ai = AIRouter()
    prompt = f"Generate {body.doc_type} documentation for this code:\n```\n{body.code}\n```"
    text, tokens, ai_used = await ai.route_request(prompt)
    
    # Generate real .docx and .pdf files
    doc_gen = DocGenerator()
    project_name = "DevShield_App"
    docx_path = doc_gen.generate_word_doc(body.code, text, project_name)
    pdf_path = doc_gen.generate_pdf(body.code, text, project_name)
    
    return {
        "documentation": text, 
        "format": "markdown", 
        "ai_used": ai_used,
        "docx_path": docx_path,
        "pdf_path": pdf_path
    }
