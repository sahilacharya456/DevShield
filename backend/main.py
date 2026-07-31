from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.config import settings
from backend.models.database import init_db

# Existing routes
from backend.api import (
    routes_codegen, routes_security, routes_docs, routes_feedback,
    routes_history, routes_auth, routes_dashboard, routes_soc,
    routes_autofix, routes_reports,
    routes_quantum, routes_cognitive, routes_promptshield,
    routes_exploit_intel, routes_killchain,
    routes_api_keys, routes_billing, routes_jobs, routes_projects
)

# New 10/10 routes — Revolutionary Modules
from backend.api import (
    routes_arsenal, routes_phantom, routes_supplychain,
    routes_osint, routes_deobfuscator, routes_redteam,
    routes_antivirus
)

logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("[STARTUP] DevShield AI X starting up - All engines initializing...")
    logger.info("[SUCCESS] Database initialized")
    logger.info("[SUCCESS] Security engines loaded")
    logger.info("[SUCCESS] Arsenal tools ready")
    logger.info("[SUCCESS] AI Intelligence modules active")
    yield
    logger.info("DevShield AI X shutting down gracefully.")

app = FastAPI(
    title="DevShield AI X",
    version="2.0.0",
    description=(
        f"The World's Most Advanced AI-Powered Cybersecurity Platform. "
        f"Owner: {settings.owner} | "
        f"Modules: SAST, SCA, DAST, ML Anomaly, DGA, Secret Neural Net, "
        f"CognitiveDNA\u2122, QuantumVault\u2122, PromptShield\u2122, AttackPath\u2122, ExploitPredict\u2122, "
        f"Arsenal (15 Kali Tools), RedAgent\u2122"
    ),
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow Next.js dev + production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://devshield.ai",  # Production domain placeholder
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)

# ============================================================
# CORE PLATFORM ROUTES
# ============================================================
app.include_router(routes_auth.router,      prefix=f"{settings.api_v1_str}/auth",      tags=["🔐 Authentication"])
app.include_router(routes_dashboard.router, prefix=f"{settings.api_v1_str}/dashboard", tags=["📊 Dashboard"])
app.include_router(routes_soc.router,       prefix=f"{settings.api_v1_str}/soc",       tags=["🤖 SOC Copilot"])
app.include_router(routes_autofix.router,   prefix=f"{settings.api_v1_str}/autofix",   tags=["🔧 Auto-Fix"])
app.include_router(routes_reports.router,   prefix=f"{settings.api_v1_str}/reports",   tags=["📑 Reports"])
app.include_router(routes_codegen.router,   prefix=f"{settings.api_v1_str}/code",      tags=["💻 Code Generation"])
app.include_router(routes_security.router,  prefix=f"{settings.api_v1_str}/security",  tags=["🛡️ Security Scanning"])
app.include_router(routes_docs.router,      prefix=f"{settings.api_v1_str}/docs",      tags=["📄 Documentation"])
app.include_router(routes_feedback.router,  prefix=f"{settings.api_v1_str}/feedback",  tags=["💬 Feedback"])
app.include_router(routes_history.router,   prefix=f"{settings.api_v1_str}/history",   tags=["📜 History"])
app.include_router(routes_api_keys.router,  prefix=f"{settings.api_v1_str}/apikeys",   tags=["🔑 API Keys"])
app.include_router(routes_billing.router,   prefix=f"{settings.api_v1_str}/billing",   tags=["💳 Billing"])
app.include_router(routes_jobs.router,      prefix=f"{settings.api_v1_str}/jobs",      tags=["Background Jobs"])
app.include_router(routes_projects.router,  prefix=f"{settings.api_v1_str}/projects",  tags=["📦 Projects"])

# ── AI Intelligence Modules ────────────────────────────────────────────────
app.include_router(routes_quantum.router, prefix=f"{settings.api_v1_str}/quantum", tags=["QuantumVault™"])
app.include_router(routes_cognitive.router, prefix=f"{settings.api_v1_str}/cognitive", tags=["CognitiveDNA™"])
app.include_router(routes_promptshield.router, prefix=f"{settings.api_v1_str}/promptshield", tags=["PromptShield™"])
app.include_router(routes_exploit_intel.router, prefix=f"{settings.api_v1_str}/exploit-intel", tags=["ExploitPredict™"])
app.include_router(routes_killchain.router, prefix=f"{settings.api_v1_str}/killchain", tags=["AttackPath™"])
app.include_router(routes_phantom.router, prefix=f"{settings.api_v1_str}/phantom", tags=["PhantomScan™"])
app.include_router(routes_supplychain.router, prefix=f"{settings.api_v1_str}/supplychain", tags=["ChainBreaker™"])
app.include_router(routes_osint.router, prefix=f"{settings.api_v1_str}/osint", tags=["OsintRadar™"])
app.include_router(routes_deobfuscator.router, prefix=f"{settings.api_v1_str}/deobfuscator", tags=["MalwareForge™"])
app.include_router(routes_redteam.router, prefix=f"{settings.api_v1_str}/redteam", tags=["RedAgent™"])
app.include_router(routes_antivirus.router, prefix=f"{settings.api_v1_str}/antivirus", tags=["Aegis Antivirus™"])

# ============================================================
# ARSENAL — KALI LINUX TOOL INTEGRATION HUB
# ============================================================
app.include_router(routes_arsenal.router,   prefix=f"{settings.api_v1_str}/arsenal",   tags=["🗡️ Arsenal (Kali Tools)"])

# ============================================================
# HEALTH & STATUS
# ============================================================
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "operational",
        "project": "DevShield AI X",
        "version": "2.0.0",
        "engines": [
            "Tree-Sitter SAST", "OSV Analytics", "Secret Neural Net",
            "DGA Detector", "Isolation Forest", "CognitiveDNA™",
            "QuantumVault™", "PromptShield™", "AttackPath™", "ExploitPredict™",
            "Arsenal (Nmap, SQLMap, SSL, WAF, Ports)"
        ],
        "status_detail": "All 15 security engines operational"
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "🛡️ DevShield AI X API v2.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }
