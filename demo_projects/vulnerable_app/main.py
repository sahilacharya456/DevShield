# Vulnerable Demo Project
# This is a sample script to test DevShield AI X's SAST and Secrets engines.

import os
import sqlite3
import yaml
import pickle

# 1. Hardcoded Secrets (Should be caught by Secret Scanner)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
GITHUB_TOKEN = "ghp_1a2b3c4d5e6f7g8h9i0jklmnopqrstuvw"

def connect_db():
    # 2. Hardcoded Database Credentials
    db_password = "super_secret_db_password_123!"
    conn = sqlite3.connect("users.db")
    return conn

def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    # 3. SQL Injection Vulnerability (Should be caught by SAST engine)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()

def load_config(payload):
    # 4. Insecure Deserialization (Should be caught by SAST engine)
    return pickle.loads(payload)

def parse_yaml(yaml_string):
    # 5. Insecure YAML parsing
    return yaml.load(yaml_string)

def run_system_command(user_input):
    # 6. Command Injection
    os.system(f"ping -c 1 {user_input}")

if __name__ == "__main__":
    print("Running vulnerable demo. Do NOT deploy this code.")
