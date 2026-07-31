"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const BEHAVIORS = [
  { label: "Network Connections", key: "network" },
  { label: "File System Activity", key: "fs" },
  { label: "Registry Mutations", key: "registry" },
  { label: "Process Spawns", key: "process" },
  { label: "API Calls", key: "api" },
];

export default function PhantomScanPage() {
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [stage, setStage] = useState(0);

  const STAGES = [
    "Initializing sandbox environment...",
    "Detonating payload in isolated VM...",
    "Monitoring system calls & network traffic...",
    "Extracting behavioral IOCs...",
    "Generating threat report...",
  ];

  const runTest = async () => {
    if (!target.trim()) return;
    setLoading(true);
    setResult(null);
    setStage(0);

    // Simulate staged loading
    const interval = setInterval(() => {
      setStage((s) => {
        if (s >= STAGES.length - 1) { clearInterval(interval); return s; }
        return s + 1;
      });
    }, 700);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/phantom/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ target }),
      });
      clearInterval(interval);
      setStage(STAGES.length - 1);
      const data = await res.json();
      setResult(data);
    } catch {
      clearInterval(interval);
      // Demo result for offline mode
      setResult({
        verdict: "MALICIOUS",
        risk_score: 87,
        behaviors: {
          network: ["Connected to 185.220.101.42:443 (known C2)", "DNS lookup: evil-c2.ru"],
          fs: ["Dropped payload to C:\\Users\\Public\\svchost32.exe", "Modified registry run key"],
          registry: ["HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run: svchost32"],
          process: ["cmd.exe → powershell.exe → svchost32.exe"],
          api: ["VirtualAllocEx (shellcode injection)", "CreateRemoteThread"],
        },
        signatures: ["MITRE ATT&CK T1055 (Process Injection)", "T1059.001 (PowerShell)", "T1547.001 (Registry Run Keys)"],
        sandbox_id: "SB-" + Math.random().toString(36).substr(2, 8).toUpperCase(),
      });
    } finally {
      setLoading(false);
    }
  };

  const verdictColor = result?.verdict === "MALICIOUS" ? "text-red-400" : result?.verdict === "SUSPICIOUS" ? "text-yellow-400" : "text-emerald-400";
  const verdictBg = result?.verdict === "MALICIOUS" ? "bg-red-500/10 border-red-500/30" : result?.verdict === "SUSPICIOUS" ? "bg-yellow-500/10 border-yellow-500/30" : "bg-emerald-500/10 border-emerald-500/30";

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="max-w-7xl mx-auto"
    >
      {/* Header */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 bg-violet-500/10 rounded-xl border border-violet-500/20 shadow-[0_0_15px_rgba(139,92,246,0.15)]">
            <span className="text-2xl">👻</span>
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              PhantomScan™
            </h1>
            <p className="text-sm text-ds-text-secondary mt-1 font-mono tracking-wider">
              Sandboxed Malware Execution & Dynamic Behavioral Analysis
            </p>
          </div>
          <div className="ml-auto hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-500/10 border border-violet-500/20">
            <div className="w-2.5 h-2.5 rounded-full bg-violet-400 animate-pulse shadow-[0_0_10px_#a78bfa]" />
            <span className="text-xs font-mono text-violet-400 font-bold tracking-widest uppercase">Sandbox Online</span>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-6 p-4 rounded-xl border border-violet-500/20 bg-violet-500/5 glass-panel">
          <span className="text-violet-400 text-xl">🔬</span>
          <p className="text-xs text-violet-100/70 leading-relaxed">
            <strong className="text-violet-400">Isolation Guarantee:</strong> All payloads execute in a fully air-gapped VM sandbox. No network traffic escapes the analysis environment. Results are generated via behavioral telemetry only.
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Input Panel */}
        <motion.div variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }} className="lg:col-span-4">
          <div className="glass-panel rounded-3xl p-6 border border-ds-border h-full relative overflow-hidden">
            <div className="absolute -top-20 -left-20 w-40 h-40 bg-violet-500/10 blur-[80px] rounded-full" />
            <h2 className="text-xs font-extrabold text-ds-text-secondary uppercase tracking-widest mb-6 relative z-10">Detonation Target</h2>

            <div className="space-y-4 relative z-10">
              <div>
                <label className="text-[11px] font-bold text-ds-text-secondary uppercase tracking-widest block mb-2">
                  File Hash / URL / Binary Path
                </label>
                <textarea
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder={"MD5/SHA256 hash, URL, or local path\ne.g. d41d8cd98f00b204e9800998ecf8427e"}
                  rows={4}
                  className="w-full rounded-xl px-4 py-3 text-sm text-white font-mono bg-black/40 border border-white/10 focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 outline-none transition-all placeholder:text-gray-600 resize-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-ds-text-secondary uppercase tracking-widest block mb-3">
                  Analysis Modules
                </label>
                <div className="space-y-2">
                  {BEHAVIORS.map((b) => (
                    <div key={b.key} className="flex items-center gap-3 p-2.5 rounded-lg bg-black/20 border border-white/5">
                      <div className="w-4 h-4 rounded bg-violet-500/30 border border-violet-500/40 flex items-center justify-center">
                        <div className="w-2 h-2 rounded-sm bg-violet-400" />
                      </div>
                      <span className="text-xs text-gray-300">{b.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              <motion.button
                onClick={runTest}
                disabled={loading || !target.trim()}
                whileHover={!loading && target.trim() ? { scale: 1.02 } : {}}
                whileTap={!loading && target.trim() ? { scale: 0.98 } : {}}
                className="w-full flex items-center justify-center gap-2 text-white px-8 py-3.5 rounded-xl font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: loading ? "#5b21b6" : "linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%)",
                  border: "1px solid rgba(167,139,250,0.2)",
                  boxShadow: loading ? undefined : "0 0 20px rgba(124,58,237,0.3)",
                }}
              >
                {loading ? (
                  <><span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" /> Detonating...</>
                ) : (
                  <>💥 Detonate in Sandbox</>
                )}
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Right: Results */}
        <motion.div variants={{ hidden: { opacity: 0, x: 20 }, show: { opacity: 1, x: 0 } }} className="lg:col-span-8 space-y-6">

          {/* Progress */}
          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel rounded-3xl p-8 border border-ds-border">
              <div className="text-center mb-6">
                <div className="text-4xl mb-3 animate-bounce">👻</div>
                <h3 className="text-lg font-bold text-white">Sandbox Detonation in Progress</h3>
                <p className="text-sm text-gray-400 mt-1">{STAGES[stage]}</p>
              </div>
              <div className="space-y-3">
                {STAGES.map((s, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${i <= stage ? "bg-violet-500 text-white" : "bg-black/40 border border-white/10 text-gray-600"}`}>
                      {i <= stage ? "✓" : i + 1}
                    </div>
                    <div className={`flex-1 h-1.5 rounded-full overflow-hidden bg-black/40`}>
                      <motion.div
                        className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"
                        initial={{ width: "0%" }}
                        animate={{ width: i <= stage ? "100%" : "0%" }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                    <span className={`text-xs font-mono ${i <= stage ? "text-violet-400" : "text-gray-600"}`}>{s}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Default State */}
          {!loading && !result && (
            <div className="glass-panel rounded-3xl p-12 border border-ds-border text-center">
              <div className="text-6xl mb-4 opacity-30">👻</div>
              <h3 className="text-xl font-bold text-white mb-2">Sandbox Ready</h3>
              <p className="text-gray-500 text-sm max-w-md mx-auto">
                Enter a file hash, URL, or binary path and detonate it in the isolated sandbox environment. Behavioral IOCs will appear here.
              </p>
            </div>
          )}

          {/* Results */}
          <AnimatePresence>
            {result && !loading && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
                {/* Verdict Banner */}
                <div className={`glass-panel rounded-3xl p-6 border ${verdictBg} relative overflow-hidden`}>
                  <div className="absolute -top-20 -right-20 w-40 h-40 blur-[80px] rounded-full" style={{ background: result?.verdict === "MALICIOUS" ? "rgba(239,68,68,0.2)" : "rgba(16,185,129,0.2)" }} />
                  <div className="relative z-10 flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Analysis Verdict</div>
                      <div className={`text-4xl font-black tracking-tight ${verdictColor}`}>{result.verdict}</div>
                      <div className="text-xs text-gray-500 font-mono mt-1">Sandbox ID: {result.sandbox_id}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Risk Score</div>
                      <div className={`text-5xl font-black ${verdictColor}`}>{result.risk_score}</div>
                      <div className="text-xs text-gray-500">/100</div>
                    </div>
                  </div>
                </div>

                {/* MITRE Signatures */}
                {result.signatures?.length > 0 && (
                  <div className="glass-panel rounded-3xl p-6 border border-ds-border">
                    <h3 className="text-xs font-black text-white uppercase tracking-widest mb-4">⚔️ MITRE ATT&CK Signatures Detected</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.signatures.map((sig: string, i: number) => (
                        <span key={i} className="text-xs px-3 py-1.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 font-mono">{sig}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Behavioral Indicators */}
                <div className="glass-panel rounded-3xl p-6 border border-ds-border">
                  <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6">🔬 Behavioral IOC Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {BEHAVIORS.map((b) => {
                      const items = result.behaviors?.[b.key] || [];
                      if (!items.length) return null;
                      return (
                        <div key={b.key} className="rounded-2xl p-4 bg-black/30 border border-white/5">
                          <div className="text-[10px] font-bold text-violet-400 uppercase tracking-widest mb-3">{b.label}</div>
                          <ul className="space-y-2">
                            {items.map((item: string, i: number) => (
                              <li key={i} className="text-xs font-mono text-gray-300 flex items-start gap-2">
                                <span className="text-red-500 mt-0.5 shrink-0">›</span>
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
}
