from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DevShield AI X API",
    description="Professional SaaS Backend for DevSecOps",
    version="2.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to DevShield AI X API"}

# Include routers here later
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
