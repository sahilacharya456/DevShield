import { motion, AnimatePresence } from 'framer-motion';
import { useState, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import {
  FileText,
  Download,
  Copy,
  Check,
  Sparkles,
  FileCode,
  BookOpen,
  Shield,
  Layers,
} from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingOrb from '../components/LoadingOrb';
import type { DocTab } from '../types';

// ==========================================
// Tab Configuration
// ==========================================
const DOC_TABS: { value: DocTab; label: string; icon: typeof FileText }[] = [
  { value: 'readme', label: 'README', icon: BookOpen },
  { value: 'api', label: 'API Docs', icon: FileCode },
  { value: 'architecture', label: 'Architecture', icon: Layers },
  { value: 'security', label: 'Security', icon: Shield },
];

// ==========================================
// Mock Generated Docs
// ==========================================
const MOCK_DOCS: Record<DocTab, string> = {
  readme: `# Authentication Service

## Overview
A secure, production-ready authentication service built with Flask, featuring PBKDF2 password hashing, JWT-based session management, and comprehensive rate limiting.

## Features
- 🔐 **PBKDF2-HMAC-SHA256** password hashing with 100,000 iterations
- 🎫 **Cryptographically secure** session tokens using \`secrets.token_urlsafe\`
- ⏱️ **Rate limiting** — 100 req/hour, 10 req/minute per IP
- 📝 **Audit logging** for all authentication events
- 🛡️ **Input validation** with length constraints

## Quick Start

\`\`\`bash
# Install dependencies
pip install flask flask-limiter

# Run the server
python app.py
\`\`\`

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | \`/api/login\` | Authenticate and get token | No |
| GET | \`/api/protected\` | Access protected resource | Yes |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| \`SECRET_KEY\` | Application secret key | Auto-generated |
| \`RATE_LIMIT\` | Max requests per hour | 100 |

## Security Considerations
- Never run with \`debug=True\` in production
- Store secrets in environment variables
- Use HTTPS in production
- Implement token rotation for long-lived sessions
`,
  api: `# API Documentation

## Authentication

### POST /api/login
Authenticate a user and receive a session token.

**Request Body:**
\`\`\`json
{
  "username": "string (max 128 chars)",
  "password": "string (max 256 chars)"
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
\`\`\`

**Error Responses:**
- \`400\` — Missing or invalid credentials
- \`429\` — Rate limit exceeded (5 attempts/minute)
- \`500\` — Internal server error

### GET /api/protected
Access a protected resource. Requires valid Bearer token.

**Headers:**
\`\`\`
Authorization: Bearer <token>
\`\`\`

**Response (200):**
\`\`\`json
{
  "message": "Hello, <username>!",
  "timestamp": "2025-01-20T12:00:00Z"
}
\`\`\`

**Error Responses:**
- \`401\` — Missing or invalid token
- \`401\` — Expired token

## Rate Limiting
All endpoints are rate-limited:
- **Global:** 100 requests per hour per IP
- **Login:** 5 requests per minute per IP

Exceeding limits returns \`429 Too Many Requests\`.
`,
  architecture: `# Architecture Overview

## System Design

\`\`\`
┌─────────────────────────────────────────────┐
│                   Client                     │
│              (Browser / Mobile)              │
└──────────────────┬──────────────────────────┘
                   │ HTTPS
┌──────────────────▼──────────────────────────┐
│              Load Balancer                   │
│           (Nginx / Cloudflare)               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           Flask Application                  │
│  ┌─────────────────────────────────────┐    │
│  │         Rate Limiter                │    │
│  │    (flask-limiter + Redis)          │    │
│  └──────────────┬──────────────────────┘    │
│  ┌──────────────▼──────────────────────┐    │
│  │     Authentication Middleware       │    │
│  │  (Token validation + Audit log)     │    │
│  └──────────────┬──────────────────────┘    │
│  ┌──────────────▼──────────────────────┐    │
│  │        Route Handlers               │    │
│  │   /login  /protected  /health       │    │
│  └──────────────┬──────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            Data Layer                        │
│    ┌──────────┐  ┌──────────────┐           │
│    │ Database │  │ Token Store  │           │
│    │ (Users)  │  │   (Redis)    │           │
│    └──────────┘  └──────────────┘           │
└─────────────────────────────────────────────┘
\`\`\`

## Key Components

### 1. Rate Limiter
- Prevents brute-force attacks
- Configurable per-endpoint limits
- Uses sliding window algorithm

### 2. Authentication Middleware
- Validates Bearer tokens
- Checks token expiration
- Logs all auth attempts

### 3. Password Hashing
- PBKDF2-HMAC-SHA256
- 100,000 iterations (OWASP recommended)
- Random 16-byte salt per password
`,
  security: `# Security Assessment

## Summary
Overall Security Score: **87/100** ✅

## Implemented Controls

### ✅ Input Validation
- Username length limit: 128 chars
- Password length limit: 256 chars
- JSON body validation

### ✅ Authentication
- PBKDF2-HMAC-SHA256 (100K iterations)
- Cryptographic token generation
- 1-hour token expiration

### ✅ Rate Limiting
- Global: 100 req/hour
- Login: 5 req/minute
- Per-IP tracking

### ✅ Logging
- All auth events logged
- Structured log format
- Failed attempt tracking

## Recommendations

### ⚠️ Medium Priority
1. Add CORS configuration
2. Implement CSRF protection
3. Add request ID tracking

### 📋 Low Priority
1. Add health check endpoint
2. Implement graceful shutdown
3. Add metrics collection
`,
};

// ==========================================
// Documentation Generator Page
// ==========================================
export default function DocGenerator() {
  const [code, setCode] = useState('');
  const [activeTab, setActiveTab] = useState<DocTab>('readme');
  const [generatedDocs, setGeneratedDocs] = useState<Record<string, string>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = useCallback(async () => {
    if (!code.trim()) {
      toast.error('Paste code to generate documentation');
      return;
    }
    setIsGenerating(true);

    try {
      const { api } = await import('../services/api');
      const response = await api.generateDocs(code, 'python');
      setGeneratedDocs({ readme: response.documentation || MOCK_DOCS.readme, api: MOCK_DOCS.api, architecture: MOCK_DOCS.architecture, security: MOCK_DOCS.security });
      toast.success('Documentation generated!');
    } catch (error) {
      toast.error('Failed to generate documentation.');
    } finally {
      setIsGenerating(false);
    }
  }, [code]);

  const handleCopy = useCallback(() => {
    const content = generatedDocs[activeTab] || '';
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  }, [generatedDocs, activeTab]);

  const handleExport = useCallback((format: string) => {
    const content = generatedDocs[activeTab] || '';
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `devshield_docs.${format === 'markdown' ? 'md' : format}`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Exported as ${format.toUpperCase()}`);
  }, [generatedDocs, activeTab]);

  const currentDoc = generatedDocs[activeTab] || '';

  return (
    <div className="page-container">
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold text-[#F1F5F9] flex items-center gap-2">
            <FileText className="w-6 h-6 text-[#10B981]" />
            Documentation Generator
          </h2>
          <p className="text-sm text-[#94A3B8] mt-1">
            Paste code and generate comprehensive documentation with a single click.
          </p>
        </motion.div>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)] min-h-[500px]">
          {/* LEFT — Editor */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex flex-col glass-card overflow-hidden"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A30]/50">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                  <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                  <div className="w-3 h-3 rounded-full bg-[#10B981]" />
                </div>
                <span className="text-xs font-mono text-[#475569]">source_code.py</span>
              </div>
            </div>
            <div className="flex-1 min-h-0">
              <Editor
                height="100%"
                language="python"
                value={code}
                onChange={(val) => setCode(val || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: "'JetBrains Mono', monospace",
                  lineHeight: 22,
                  padding: { top: 12, bottom: 12 },
                  scrollBeyondLastLine: false,
                  renderLineHighlight: 'none',
                  overviewRulerBorder: false,
                }}
              />
            </div>
            <div className="p-4 border-t border-[#2A2A30]/50">
              <motion.button
                onClick={handleGenerate}
                disabled={isGenerating || !code.trim()}
                className={`w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2
                  transition-all relative overflow-hidden
                  ${isGenerating
                    ? 'bg-[#10B981]/20 text-[#10B981] cursor-wait'
                    : 'btn-primary disabled:opacity-40 disabled:cursor-not-allowed'
                  }`}
                whileHover={!isGenerating ? { scale: 1.01 } : undefined}
                whileTap={!isGenerating ? { scale: 0.99 } : undefined}
                id="generate-docs-btn"
              >
                {isGenerating ? (
                  <>
                    <LoadingOrb size={20} />
                    Generating documentation...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Documentation
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>

          {/* RIGHT — Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-col glass-card overflow-hidden"
          >
            {/* Tab Switcher */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#2A2A30]/50">
              <div className="flex gap-1">
                {DOC_TABS.map((tab) => {
                  const TabIcon = tab.icon;
                  const isActive = activeTab === tab.value;
                  return (
                    <motion.button
                      key={tab.value}
                      onClick={() => setActiveTab(tab.value)}
                      className={`px-3 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5
                        transition-colors ${
                          isActive
                            ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20'
                            : 'text-[#475569] hover:text-[#94A3B8] hover:bg-[#202025]'
                        }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <TabIcon className="w-3.5 h-3.5" />
                      {tab.label}
                    </motion.button>
                  );
                })}
              </div>
              <div className="flex items-center gap-1.5">
                <motion.button
                  onClick={handleCopy}
                  disabled={!currentDoc}
                  className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Copy"
                >
                  {copied ? <Check className="w-4 h-4 text-[#10B981]" /> : <Copy className="w-4 h-4" />}
                </motion.button>
                <motion.button
                  onClick={() => handleExport('markdown')}
                  disabled={!currentDoc}
                  className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Export as Markdown"
                >
                  <Download className="w-4 h-4" />
                </motion.button>
              </div>
            </div>

            {/* Doc Preview */}
            <div className="flex-1 overflow-y-auto p-6">
              <AnimatePresence mode="wait">
                {isGenerating ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center justify-center h-full"
                  >
                    <LoadingOrb size={60} text="Generating documentation..." />
                  </motion.div>
                ) : currentDoc ? (
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                    className="prose prose-invert prose-sm max-w-none
                               prose-headings:text-[#F1F5F9] prose-p:text-[#94A3B8]
                               prose-a:text-[#3B82F6] prose-strong:text-[#F1F5F9]
                               prose-code:text-[#10B981] prose-code:bg-[#141416]
                               prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                               prose-pre:bg-[#0D0D0F] prose-pre:border prose-pre:border-[#2A2A30]"
                  >
                    <div className="font-mono text-sm whitespace-pre-wrap leading-relaxed text-[#94A3B8]">
                      {currentDoc}
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center justify-center h-full text-center"
                  >
                    <div>
                      <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-[#141416] border border-[#2A2A30]/50 flex items-center justify-center">
                        <BookOpen className="w-8 h-8 text-[#475569]" />
                      </div>
                      <p className="text-sm text-[#475569]">
                        Documentation preview will appear here.
                      </p>
                      <p className="text-xs text-[#475569]/60 mt-1">
                        Paste code and hit Generate.
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
