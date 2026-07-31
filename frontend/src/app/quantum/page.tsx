"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type QuantumFinding = {
  title: string;
  severity: string;
  line: number;
  quantum_threat: string;
  nist_replacement: string;
  migration_code: string;
};

type QuantumResult = {
  quantum_score: number;
  quantum_readiness: string;
  total_findings: number;
  findings: QuantumFinding[];
};

const DEMO_CODE = `import hashlib
import rsa
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import ec

private_key, public_key = rsa.newkeys(2048)
md5_hash = hashlib.md5(data).hexdigest()
sha1_hash = hashlib.sha1(data).hexdigest()
cipher = AES.new(key[:16], AES.MODE_CBC)
private_key = ec.generate_private_key(ec.SECP256R1())
`;

export default function QuantumPage() {
  const [code, setCode] = useState(DEMO_CODE);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QuantumResult | null>(null);
  const [error, setError] = useState("");
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
  const [copied, setCopied] = useState<number | null>(null);

  const runAudit = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setResults(null);
    setError("");
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/quantum/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ code, filename: "code.py", use_ast: true }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResults(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Quantum audit failed");
    } finally {
      setLoading(false);
    }
  };

  const copyCode = (value: string, idx: number) => {
    navigator.clipboard.writeText(value);
    setCopied(idx);
    setTimeout(() => setCopied(null), 2000);
  };

  const score = results?.quantum_score ?? 0;
  const scoreColor = score >= 80 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  const circumference = 2 * Math.PI * 52;

  return (
    <div className="min-h-screen p-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-lg border" style={{ background: "rgba(139,92,246,0.1)", borderColor: "rgba(139,92,246,0.2)" }}>
            <span className="text-2xl">Q</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">QuantumVault <span style={{ color: "#a78bfa" }}>Post-Quantum Auditor</span></h1>
            <p className="text-sm text-gray-500">Detect quantum-vulnerable cryptography and generate NIST PQC migrations</p>
          </div>
          <div className="ml-auto px-3 py-1.5 rounded-full border text-xs font-mono font-bold" style={{ background: "rgba(139,92,246,0.1)", borderColor: "rgba(139,92,246,0.2)", color: "#a78bfa" }}>NIST PQC</div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white mb-3">Code to Audit</h2>
          <textarea value={code} onChange={e => setCode(e.target.value)} className="w-full h-64 bg-[#050912] border border-white/10 rounded-lg p-4 text-xs font-mono text-gray-300 focus:outline-none resize-none" placeholder="Paste Python code here..." />
          <motion.button onClick={runAudit} disabled={loading} whileTap={{ scale: 0.97 }}
            className="mt-3 w-full text-white py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            style={{ background: loading ? "#6d28d9" : "#7c3aed" }}>
            {loading ? "Auditing quantum vectors..." : "Run QuantumVault Audit"}
          </motion.button>
        </div>

        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5 flex flex-col items-center justify-center gap-6">
          <div className="relative w-36 h-36">
            <svg className="w-full h-full" style={{ transform: "rotate(-90deg)" }}>
              <circle cx="72" cy="72" r="52" stroke="rgba(255,255,255,0.05)" strokeWidth="10" fill="transparent" />
              <circle cx="72" cy="72" r="52" stroke={scoreColor} strokeWidth="10" fill="transparent"
                strokeDasharray={circumference}
                strokeDashoffset={results ? circumference * (1 - score / 100) : circumference}
                strokeLinecap="round"
                style={{ transition: "stroke-dashoffset 1.5s ease", filter: `drop-shadow(0 0 8px ${scoreColor})` }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-extrabold text-white">{score}</span>
              <span className="text-xs text-gray-400">/ 100</span>
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold mb-1" style={{ color: results?.quantum_readiness === "READY" ? "#22c55e" : results?.quantum_readiness === "AT_RISK" ? "#f59e0b" : "#ef4444" }}>
              {results?.quantum_readiness || "AWAITING SCAN"}
            </div>
            <p className="text-xs text-gray-500">Quantum Readiness Status</p>
          </div>
          {results && (
            <div className="grid grid-cols-2 gap-3 w-full">
              <div className="bg-[#050912] rounded-lg p-3 text-center border border-white/5">
                <div className="text-xl font-bold text-red-400">{results.total_findings}</div>
                <div className="text-xs text-gray-400">Findings</div>
              </div>
              <div className="bg-[#050912] rounded-lg p-3 text-center border border-white/5">
                <div className="text-xl font-bold" style={{ color: "#a78bfa" }}>AST</div>
                <div className="text-xs text-gray-400">Analysis</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-sm text-red-300">
          {error}
        </div>
      )}

      <AnimatePresence>
        {results && results.findings.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
            <h2 className="text-lg font-bold text-white">Quantum Vulnerabilities ({results.findings.length})</h2>
            {results.findings.map((f: QuantumFinding, i: number) => (
              <div key={i} className="bg-[#0b0f1a] border border-white/5 rounded-xl overflow-hidden">
                <button onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
                  className="w-full flex items-center justify-between p-4 hover:bg-white/3 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${ f.severity === "CRITICAL" ? "bg-red-500/10 text-red-400 border-red-500/20" : "bg-orange-500/10 text-orange-400 border-orange-500/20" }`}>{f.severity}</span>
                    <span className="font-semibold text-white text-sm">{f.title}</span>
                    <span className="text-xs text-gray-500 font-mono">Line {f.line}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-red-400 font-mono">{f.quantum_threat}</span>
                    <span className="text-gray-400">{expandedIdx === i ? "Up" : "Down"}</span>
                  </div>
                </button>
                {expandedIdx === i && (
                  <div className="px-4 pb-4 border-t border-white/5 pt-4 space-y-3">
                    <div>
                      <div className="text-xs text-gray-400 mb-1">NIST PQC Replacement</div>
                      <span className="text-xs px-2 py-1 rounded-md font-mono" style={{ background: "rgba(139,92,246,0.1)", color: "#c4b5fd", border: "1px solid rgba(139,92,246,0.2)" }}>{f.nist_replacement}</span>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-xs text-gray-400">Migration Code</div>
                        <button onClick={() => copyCode(f.migration_code, i)} className="text-xs text-gray-400 hover:text-white transition-colors">
                          {copied === i ? "Copied" : "Copy"}
                        </button>
                      </div>
                      <pre className="bg-[#050912] border border-white/5 rounded-lg p-3 text-xs font-mono text-green-300 overflow-x-auto">{f.migration_code}</pre>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
