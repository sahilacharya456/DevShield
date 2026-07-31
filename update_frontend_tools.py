import os

frontend_file = r'c:\Users\sahil\Desktop\DevShield\frontend\src\app\arsenal\page.tsx'

with open(frontend_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_tools = '''const TOOLS = [
  { id: "ports", name: "PortGrabber", category: "Network", icon: "🔌", description: "Fast async port scanner with banner grabbing", risk: "SAFE", placeholder: "192.168.1.1 or hostname", color: "cyan" },
  { id: "ssl", name: "SSL Auditor", category: "Cryptography", icon: "🔐", description: "TLS/SSL certificate & cipher suite auditor with A-F grading", risk: "SAFE", placeholder: "example.com", color: "green" },
  { id: "waf", name: "WAF Detector", category: "Web", icon: "🛡️", description: "Web Application Firewall fingerprinting (10+ WAF signatures)", risk: "SAFE", placeholder: "https://example.com", color: "purple" },
  { id: "sqlmap", name: "SQLMap", category: "Web", icon: "💉", description: "Automated SQL injection detection and exploitation", risk: "OFFENSIVE", placeholder: "https://example.com/page?id=1", color: "red" },
  { id: "nmap", name: "Nmap", category: "Network", icon: "🖥️", description: "Network discovery & port/service/vulnerability scanner", risk: "OFFENSIVE", placeholder: "192.168.1.0/24 or example.com", scanTypes: ["quick", "full", "vuln", "stealth"], color: "blue" },
  { id: "dnsrecon", name: "DNSRecon", category: "Network", icon: "🌐", description: "DNS Enumeration and Zone Transfer checks", risk: "SAFE", placeholder: "example.com", color: "blue" },
  { id: "gobuster", name: "Gobuster", category: "Web", icon: "👻", description: "Directory/File brute-forcing and enumeration", risk: "OFFENSIVE", placeholder: "https://example.com", color: "orange" },
  { id: "harvester", name: "theHarvester", category: "OSINT", icon: "🌾", description: "Email, subdomain and employee OSINT gathering", risk: "SAFE", placeholder: "example.com", color: "yellow" },
  { id: "hydra", name: "Hydra", category: "Exploitation", icon: "🐉", description: "Parallelized network logon cracking", risk: "OFFENSIVE", placeholder: "192.168.1.100", color: "red" },
  { id: "nikto", name: "Nikto", category: "Web", icon: "🕸️", description: "Web server scanner for thousands of vulnerabilities", risk: "OFFENSIVE", placeholder: "http://example.com", color: "red" },
  { id: "shodan", name: "Shodan", category: "OSINT", icon: "👁️", description: "Query Internet-connected device intelligence", risk: "SAFE", placeholder: "1.1.1.1 or example.com", color: "blue" },
  { id: "sublister", name: "Sublist3r", category: "OSINT", icon: "🔍", description: "Fast subdomains enumeration tool using search engines", risk: "SAFE", placeholder: "example.com", color: "cyan" },
  { id: "whatweb", name: "WhatWeb", category: "Web", icon: "🕵️", description: "Next generation web scanner & technology fingerprinting", risk: "SAFE", placeholder: "https://example.com", color: "purple" },
  { id: "zap", name: "OWASP ZAP", category: "Web", icon: "⚡", description: "Automated web application security scanner", risk: "OFFENSIVE", placeholder: "https://example.com", color: "blue" },
  { id: "hash", name: "Hash Analyzer", category: "Cryptography", icon: "#️⃣", description: "Hash type identification and database cracking", risk: "SAFE", placeholder: "e99a18c428cb38d5f260853678922e03", color: "green" },
];'''

# Replace old TOOLS definition
import re
content = re.sub(r'const TOOLS = \[[\s\S]*?\];', new_tools, content)

with open(frontend_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated tools in frontend.")
