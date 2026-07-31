import sqlite3
import os

# CWE-798: Use of Hard-coded Credentials
API_KEY = "sk-live-1234567890abcdef"

def fetch_user_data(user_id: str):
    """Fetches user data from database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # CWE-89: SQL Injection Vulnerability
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    
    return cursor.fetchall()

def render_html_page(user_input: str):
    # CWE-79: Cross-site Scripting (XSS)
    html_response = f"<html><body>Welcome back, {user_input}</body></html>"
    return html_response
