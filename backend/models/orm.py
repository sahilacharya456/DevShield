from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stripe_customer_id = Column(String(100), nullable=True, unique=True, index=True)
    subscription_tier = Column(String(50), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    api_tokens = relationship("APIToken", back_populates="organization", cascade="all, delete-orphan")

class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_revoked = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="api_tokens")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="Developer") # Admin or Developer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    organization = relationship("Organization", back_populates="users")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    language = Column(String(50), nullable=False)
    repo_url = Column(String(255), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="projects")
    scans = relationship("Scan", back_populates="project", cascade="all, delete-orphan")
    threat_models = relationship("ThreatModel", back_populates="project")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, default=100)
    status = Column(String(20), default="COMPLETED") # PENDING, RUNNING, COMPLETED, FAILED
    scan_type = Column(String(50), default="SAST") # SAST, DAST, SCA
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    file_path = Column(String(255), nullable=False)
    line_number = Column(Integer, nullable=True)
    remediation = Column(Text, nullable=True)
    status = Column(String(20), default="OPEN") # OPEN, RESOLVED, FALSE_POSITIVE

    scan = relationship("Scan", back_populates="findings")

class ThreatModel(Base):
    __tablename__ = "threat_models"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    architecture_json = Column(JSON, nullable=False)
    stride_matrix_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="threat_models")

class SessionHistory(Base):
    """Stores AI generation and analysis sessions (from the original Streamlit tool)"""
    __tablename__ = "session_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_description = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    generated_code = Column(Text, nullable=True)
    ai_used = Column(String(50), nullable=True)
    vulnerability_score = Column(Integer, nullable=True)
    analyzed = Column(Boolean, default=False)
    doc_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
