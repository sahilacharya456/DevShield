from pydantic import BaseModel, Field
from typing import List, Optional

class ScanRequest(BaseModel):
    code: str = Field(..., description="The source code to scan.")
    language: str = Field(..., description="Language of the source code (e.g., python, typescript).")

class VulnerabilityIssue(BaseModel):
    name: str
    severity: str
    line: Optional[int]
    description: str
    source: str

class ScanResponse(BaseModel):
    total_issues: int
    vulnerabilities: List[VulnerabilityIssue]

class FeedbackRequest(BaseModel):
    issue_id: str
    is_false_positive: bool
    user_comment: Optional[str]

class DocRequest(BaseModel):
    code: str

class DocResponse(BaseModel):
    markdown: str

class CodeGenRequest(BaseModel):
    prompt: str
    language: Optional[str] = "python"

class CodeGenResponse(BaseModel):
    code: str
