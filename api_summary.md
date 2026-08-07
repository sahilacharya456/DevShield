# DevShield API Modules & Inputs Summary

## Pydantic Input Schemas

### APITokenCreate
- **name** (string)

### AutoFixRequest
- **code** (string)
- **vulnerability_report** (any)

### Body_login_access_token_api_v1_auth_login_post
- **grant_type** (any)
- **username** (string)
- **password** (string)
- **scope** (string)
- **client_id** (any)
- **client_secret** (any)

### Body_scan_file_api_v1_antivirus_scan_post
- **file** (string)

### BulkPredictRequest
- **cve_ids** (array of string)

### ChainbreakerRequest
- **target** (string)
- **manifest_name** (any)
- **manifest_content** (any)
- **options** (object)

### ChangePasswordRequest
- **old_password** (string)
- **new_password** (string)

### ChatMessage
- **message** (string)
- **project_context** (any)

### CheckoutRequest
- **plan** (string)

### CodeGenRequest
- **task** (string)
- **language** (string)
- **security_level** (string)

### CreateProjectRequest
- **name** (string)
- **language** (string)
- **repo_url** (string)

### DocumentRequest
- **code** (string)
- **doc_type** (string)

### ExploitPredictRequest
- **cve_id** (string)

### FeedbackRequest
- **session_id** (string)
- **rating** (integer)
- **comments** (any)

### FixRequest
- **project_name** (string)
- **vulnerability_title** (string)

### HTTPValidationError
- **detail** (array of any)

### MalwareforgeRequest
- **target** (string)
- **options** (object)

### NmapRequest
- **target** (string)
- **scan_type** (string)

### OsintradarRequest
- **target** (string)
- **options** (object)

### PhantomscanRequest
- **target** (string)
- **options** (object)

### PortScanRequest
- **host** (string)
- **ports** (any)

### PromptAnalyzeRequest
- **prompt** (string)

### QuantumAuditRequest
- **code** (string)
- **filename** (string)
- **use_ast** (boolean)

### RedagentRequest
- **target** (string)
- **options** (object)

### ResetPasswordRequest
- **email** (string)
- **new_password** (string)

### SQLMapRequest
- **target_url** (string)
- **level** (integer)
- **risk** (integer)

### SSLRequest
- **hostname** (string)
- **port** (integer)

### SastSynthesizeRequest
- **code** (string)
- **project_name** (string)
- **attacker_profile** (string)

### SecurityScanRequest
- **code** (string)
- **filename** (string)

### SupplyChainScanJobRequest
- **manifest_name** (string)
- **manifest_content** (string)

### SynthesizeRequest
- **vulnerabilities** (array of object)
- **project_name** (string)
- **attacker_profile** (string)

### SystemPromptAuditRequest
- **system_prompt** (string)

### TestSuiteRequest
- **category** (string)

### Token
- **access_token** (string)
- **token_type** (string)
- **user_id** (integer)
- **role** (string)

### TrainRequest
- **developer_id** (string)
- **code_samples** (array of string)

### UserCreate
- **username** (string)
- **email** (string)
- **password** (string)

### ValidationError
- **loc** (array of any)
- **msg** (string)
- **type** (string)
- **input** (any)
- **ctx** (object)

### VerifyRequest
- **developer_id** (string)
- **code** (string)

### Vulnerability
- **title** (string)
- **severity** (string)
- **description** (string)
- **line** (any)
- **confidence** (any)
- **cwe** (any)
- **owasp** (any)
- **remediation** (any)

### WAFRequest
- **target_url** (string)

## Endpoints

### [POST] /api/v1/auth/change-password
- **Tags**: ['🔐 Authentication']
- **Summary**: Change Password

### [POST] /api/v1/auth/reset-password
- **Tags**: ['🔐 Authentication']
- **Summary**: Reset Password

### [POST] /api/v1/auth/login
- **Tags**: ['🔐 Authentication']
- **Summary**: Login Access Token

### [POST] /api/v1/auth/register
- **Tags**: ['🔐 Authentication']
- **Summary**: Register User

### [GET] /api/v1/auth/me
- **Tags**: ['🔐 Authentication']
- **Summary**: Read Users Me

### [GET] /api/v1/dashboard/metrics
- **Tags**: ['📊 Dashboard']
- **Summary**: Get Dashboard Metrics

### [POST] /api/v1/soc/chat
- **Tags**: ['🤖 SOC Copilot']
- **Summary**: Chat With Soc

### [POST] /api/v1/autofix/generate
- **Tags**: ['🔧 Auto-Fix']
- **Summary**: Generate Patch

### [GET] /api/v1/reports/download
- **Tags**: ['📑 Reports']
- **Summary**: Download Report
- **Query/Path Parameters**:
  - project_name (string, query, optional)
  - risk_level (string, query, optional)
  - critical_count (integer, query, optional)
  - high_count (integer, query, optional)
  - medium_count (integer, query, optional)

### [POST] /api/v1/code/
- **Tags**: ['💻 Code Generation']
- **Summary**: Generate Code

### [POST] /api/v1/security/scan
- **Tags**: ['🛡️ Security Scanning']
- **Summary**: Scan Code

### [POST] /api/v1/security/autofix
- **Tags**: ['🛡️ Security Scanning']
- **Summary**: Autofix Code

### [POST] /api/v1/docs/
- **Tags**: ['📄 Documentation']
- **Summary**: Generate Docs

### [POST] /api/v1/feedback/
- **Tags**: ['💬 Feedback']
- **Summary**: Submit Feedback

### [GET] /api/v1/history/
- **Tags**: ['📜 History']
- **Summary**: Get History
- **Query/Path Parameters**:
  - limit (integer, query, optional)

### [POST] /api/v1/apikeys/generate
- **Tags**: ['🔑 API Keys']
- **Summary**: Generate Token

### [GET] /api/v1/apikeys/list
- **Tags**: ['🔑 API Keys']
- **Summary**: List Tokens

### [DELETE] /api/v1/apikeys/revoke/{token_id}
- **Tags**: ['🔑 API Keys']
- **Summary**: Revoke Token
- **Query/Path Parameters**:
  - token_id (integer, path, required)

### [POST] /api/v1/billing/checkout
- **Tags**: ['💳 Billing']
- **Summary**: Create Checkout Session

### [POST] /api/v1/billing/webhook
- **Tags**: ['💳 Billing']
- **Summary**: Stripe Webhook

### [POST] /api/v1/jobs/scans/supply-chain
- **Tags**: ['Background Jobs']
- **Summary**: Enqueue Supply Chain Scan

### [GET] /api/v1/jobs/{job_id}
- **Tags**: ['Background Jobs']
- **Summary**: Get Job Status
- **Query/Path Parameters**:
  - job_id (string, path, required)

### [GET] /api/v1/projects/
- **Tags**: ['📦 Projects']
- **Summary**: Get Projects

### [POST] /api/v1/projects/
- **Tags**: ['📦 Projects']
- **Summary**: Create Project

### [POST] /api/v1/projects/{project_id}/scan
- **Tags**: ['📦 Projects']
- **Summary**: Start Scan
- **Query/Path Parameters**:
  - project_id (integer, path, required)

### [POST] /api/v1/quantum/audit
- **Tags**: ['QuantumVault™']
- **Summary**: QuantumVault™: PQC Code Audit

### [GET] /api/v1/quantum/algorithms
- **Tags**: ['QuantumVault™']
- **Summary**: List quantum-vulnerable algorithms

### [POST] /api/v1/cognitive/train
- **Tags**: ['CognitiveDNA™']
- **Summary**: CognitiveDNA™: Register Developer Profile

### [POST] /api/v1/cognitive/verify
- **Tags**: ['CognitiveDNA™']
- **Summary**: CognitiveDNA™: Verify Code Authorship

### [GET] /api/v1/cognitive/profiles
- **Tags**: ['CognitiveDNA™']
- **Summary**: List all registered developer profiles

### [GET] /api/v1/cognitive/profiles/{developer_id}
- **Tags**: ['CognitiveDNA™']
- **Summary**: Get developer profile summary
- **Query/Path Parameters**:
  - developer_id (string, path, required)

### [DELETE] /api/v1/cognitive/profiles/{developer_id}
- **Tags**: ['CognitiveDNA™']
- **Summary**: Remove a developer profile
- **Query/Path Parameters**:
  - developer_id (string, path, required)

### [POST] /api/v1/promptshield/analyze
- **Tags**: ['PromptShield™']
- **Summary**: PromptShield™: Scan a Prompt for Injection

### [POST] /api/v1/promptshield/audit-system-prompt
- **Tags**: ['PromptShield™']
- **Summary**: PromptShield™: Audit LLM System Prompt

### [POST] /api/v1/promptshield/test-suite
- **Tags**: ['PromptShield™']
- **Summary**: PromptShield™: Get Injection Test Payloads

### [GET] /api/v1/promptshield/categories
- **Tags**: ['PromptShield™']
- **Summary**: List available injection attack categories

### [POST] /api/v1/exploit-intel/predict
- **Tags**: ['ExploitPredict™']
- **Summary**: ExploitPredict™: Score CVE Exploit Likelihood

### [POST] /api/v1/exploit-intel/bulk-predict
- **Tags**: ['ExploitPredict™']
- **Summary**: ExploitPredict™: Batch CVE Risk Scoring

### [GET] /api/v1/exploit-intel/kev/{cve_id}
- **Tags**: ['ExploitPredict™']
- **Summary**: ExploitPredict™: CISA KEV Lookup
- **Query/Path Parameters**:
  - cve_id (string, path, required)

### [GET] /api/v1/exploit-intel/kev-catalog
- **Tags**: ['ExploitPredict™']
- **Summary**: ExploitPredict™: View Full KEV Catalog Subset

### [POST] /api/v1/killchain/synthesize
- **Tags**: ['AttackPath™']
- **Summary**: AttackPath™: Synthesize Kill-Chain from Vulnerabilities

### [POST] /api/v1/killchain/synthesize-from-code
- **Tags**: ['AttackPath™']
- **Summary**: AttackPath™: SAST Scan + Kill-Chain in One Step

### [GET] /api/v1/killchain/mitre-mappings
- **Tags**: ['AttackPath™']
- **Summary**: AttackPath™: View MITRE ATT&CK Mappings

### [GET] /api/v1/killchain/attacker-profiles
- **Tags**: ['AttackPath™']
- **Summary**: AttackPath™: View Attacker Profiles

### [POST] /api/v1/phantom/run
- **Tags**: ['PhantomScan™']
- **Summary**: Run Module

### [POST] /api/v1/supplychain/run
- **Tags**: ['ChainBreaker™']
- **Summary**: Run Module

### [POST] /api/v1/osint/run
- **Tags**: ['OsintRadar™']
- **Summary**: Run Module

### [POST] /api/v1/deobfuscator/run
- **Tags**: ['MalwareForge™']
- **Summary**: Run Module

### [POST] /api/v1/redteam/run
- **Tags**: ['RedAgent™']
- **Summary**: Run Module

### [GET] /api/v1/redteam/job/{job_id}
- **Tags**: ['RedAgent™']
- **Summary**: Get Job Status
- **Query/Path Parameters**:
  - job_id (string, path, required)

### [POST] /api/v1/antivirus/scan
- **Tags**: ['Aegis Antivirus™']
- **Summary**: Scan File

### [POST] /api/v1/arsenal/nmap/scan
- **Tags**: ['🗡️ Arsenal (Kali Tools)', 'Arsenal']
- **Summary**: Run Nmap structured scan

### [POST] /api/v1/arsenal/ssl/audit
- **Tags**: ['🗡️ Arsenal (Kali Tools)', 'Arsenal']
- **Summary**: Audit SSL/TLS configuration

### [POST] /api/v1/arsenal/waf/detect
- **Tags**: ['🗡️ Arsenal (Kali Tools)', 'Arsenal']
- **Summary**: Detect WAF presence and type

### [POST] /api/v1/arsenal/ports/scan
- **Tags**: ['🗡️ Arsenal (Kali Tools)', 'Arsenal']
- **Summary**: Scan open ports (Python-native)

### [POST] /api/v1/arsenal/sqlmap/test
- **Tags**: ['🗡️ Arsenal (Kali Tools)', 'Arsenal']
- **Summary**: Quick SQLMap injection test

### [GET] /health
- **Tags**: ['System']
- **Summary**: Health Check

### [GET] /
- **Tags**: ['System']
- **Summary**: Root

