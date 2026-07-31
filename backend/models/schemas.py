from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CodeGenRequest(BaseModel):
    task: str = Field(..., description="Task description for code generation")
    language: str = Field(..., description="Programming language")
    security_level: str = Field(default="high", description="Security rigor level")
    
class CodeGenResponse(BaseModel):
    code: str
    confidence_score: int
    alternative_approaches: List[str]
    token_cost: int
    ai_used: str

class Vulnerability(BaseModel):
    title: str
    severity: str
    description: str
    line: Optional[int] = None
    confidence: Optional[int] = None
    cwe: Optional[str] = None
    owasp: Optional[str] = None
    remediation: Optional[str] = None

class SecurityScanRequest(BaseModel):
    code: str
    filename: str = "app.py"

class SecurityScanResponse(BaseModel):
    overall_score: int
    vulnerabilities: List[Vulnerability]
    remediation_priorities: List[str]

class AutoFixRequest(BaseModel):
    code: str
    vulnerability_report: SecurityScanResponse

class AutoFixResponse(BaseModel):
    fixed_code: str
    diff: str
    fix_explanations: Dict[str, str]
    rescan_confirmation: bool

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int = Field(ge=1, le=5)
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    message: str
    
class DocumentRequest(BaseModel):
    code: str
    doc_type: str = Field(default="readme")

class StandardErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
