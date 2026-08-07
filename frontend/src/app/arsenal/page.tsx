"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TOOLS = [
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
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const getLineColor = (type: string) => {
  if (type === "critical") return "#f87171";
  if (type === "warning") return "#fbbf24";
  if (type === "success") return "#4ade80";
  if (type === "error") return "#ef4444";
  if (type === "complete") return "#c084fc";
  return "#60a5fa";
};

export default function Arsenal() {
  const [selectedTool, setSelectedTool] = useState(TOOLS[0]);
  const [target, setTarget] = useState("");
  const [scanType, setScanType] = useState("quick");
  const [isScanning, setIsScanning] = useState(false);
  const [terminalLines, setTerminalLines] = useState<{ text: string; type: string }[]>([
    { text: "DevShield Arsenal v2.0.0 — Kali Linux Integration Hub", type: "info" },
    { text: "15 professional security tools integrated and ready.", type: "info" },
    { text: "LEGAL NOTICE: Only scan systems you own or have explicit written permission to test.", type: "warning" },
  ]);
  const [results, setResults] = useState<any>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [terminalLines]);

  const addLine = (text: string, type: string = "info") =>
    setTerminalLines(prev => [...prev, { text, type }]);

  const categories = [...new Set(TOOLS.map(t => t.category))];

  const runScan = async () => {
    if (!target.trim()) { addLine("[ERROR] No target specified.", "error"); return; }
    setIsScanning(true);
    setResults(null);
    addLine(`══════════════════════════════════════════════════════`, "info");
    addLine(`[INIT] ${selectedTool.name} scan → ${target}`, "info");
    addLine(`[TIME] ${new Date().toISOString()}`, "info");
    addLine(`══════════════════════════════════════════════════════`, "info");
    const token = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    try {
      if (selectedTool.id === "ports") {
        const res = await fetch(`${API_URL}/api/v1/arsenal/ports/scan`, { method: "POST", headers, body: JSON.stringify({ host: target }) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        for (const p of (data.open_ports || [])) {
          const t2 = p.risk === "CRITICAL" ? "critical" : p.risk === "HIGH" ? "warning" : "success";
          addLine(`[${p.risk}] Port ${p.port}/tcp OPEN | ${p.service} | ${p.banner || "No banner"} | ${p.note}`, t2);
        }
        addLine(`[SUMMARY] ${data.open_count} open ports | Overall Risk: ${data.overall_risk}`, data.overall_risk === "CRITICAL" ? "critical" : "success");
        setResults(data);
      } else if (selectedTool.id === "ssl") {
        const hostname = target.replace(/^https?:\/\//, "").split("/")[0];
        const res = await fetch(`${API_URL}/api/v1/arsenal/ssl/audit`, { method: "POST", headers, body: JSON.stringify({ hostname }) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        for (const f of (data.findings || [])) {
          const t2 = f.severity === "CRITICAL" ? "critical" : f.severity === "HIGH" ? "warning" : "info";
          addLine(`[${f.severity}] ${f.title}: ${f.description}`, t2);
        }
        addLine(`[RESULT] SSL Grade: ${data.overall_grade}`, data.overall_grade === "F" ? "critical" : data.overall_grade === "A" ? "success" : "warning");
        setResults(data);
      } else if (selectedTool.id === "waf") {
        const url = target.startsWith("http") ? target : `https://${target}`;
        const res = await fetch(`${API_URL}/api/v1/arsenal/waf/detect`, { method: "POST", headers, body: JSON.stringify({ target_url: url }) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        addLine(`[SCAN] WAF: ${data.waf_detected ? `✓ ${data.waf_type} (${data.waf_confidence}% confidence)` : "✗ No WAF detected"}`, data.waf_detected ? "success" : "critical");
        for (const f of (data.findings || [])) {
          addLine(`[${f.severity}] ${f.title}`, f.severity === "CRITICAL" ? "critical" : f.severity === "HIGH" ? "warning" : "info");
        }
        setResults(data);
      } else if (selectedTool.id === "sqlmap") {
        const res = await fetch(`${API_URL}/api/v1/arsenal/sqlmap/test`, { method: "POST", headers, body: JSON.stringify({ target_url: target }) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        addLine(`[RESULT] SQL Injectable: ${data.injectable ? "YES — CRITICAL" : "No injection found"}`, data.injectable ? "critical" : "success");
        if (data.dbms) addLine(`[INFO] DBMS: ${data.dbms}`, "warning");
        setResults(data);
      } else {
        addLine(`[INFO] Opening WebSocket stream for ${selectedTool.name}...`, "info");
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        const wsHost = new URL(API_URL).host;
        const wsUrl = `${wsProto}://${wsHost}/api/v1/arsenal/${selectedTool.id}/stream`;
        const ws = new WebSocket(wsUrl);
        ws.onopen = () => ws.send(JSON.stringify({ target, scan_type: scanType }));
        ws.onmessage = (evt) => {
          const msg = JSON.parse(evt.data);
          addLine(msg.line, msg.type || "info");
          if (msg.type === "complete") { setIsScanning(false); ws.close(); }
        };
        ws.onerror = () => { addLine("[ERROR] WebSocket failed. Check backend connection.", "error"); setIsScanning(false); };
        ws.onclose = () => setIsScanning(false);
        return;
      }
    } catch (err: any) {
      addLine(`[ERROR] ${err.message || "Connection failed."}`, "error");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <motion.div 
      initial="hidden" 
      animate="show" 
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="p-8 pb-20 max-w-7xl mx-auto"
    >
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
            <span className="text-2xl">🗡️</span>
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              Arsenal <span className="text-red-500 mx-1">//</span> Kali Tool Hub
            </h1>
            <p className="text-sm text-ds-text-secondary mt-1 font-mono tracking-wider">Professional Offensive Security Tools — Integrated & Production Ready</p>
          </div>
          <div className="ml-auto hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 shadow-inner">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_#ef4444]" />
            <span className="text-xs font-mono text-red-400 font-bold tracking-widest uppercase">OFFENSIVE MODE</span>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-6 p-4 rounded-xl border border-yellow-500/20 bg-yellow-500/5 glass-panel">
          <span className="text-yellow-400 text-xl">⚠️</span>
          <p className="text-xs text-yellow-100/70 leading-relaxed">
            <strong className="text-yellow-400">Legal Disclaimer:</strong> Only scan systems you own or have explicit written authorization to test. Unauthorized scanning is illegal and may result in criminal charges.
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Tool Selector */}
        <motion.div variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }} className="lg:col-span-4 xl:col-span-3">
          <div className="glass-panel border border-ds-border rounded-3xl p-6 relative overflow-hidden h-full">
            <div className="absolute -top-20 -left-20 w-40 h-40 bg-ds-accent-blue/10 blur-[80px] rounded-full" />
            <h2 className="text-xs font-extrabold text-ds-text-secondary uppercase tracking-widest mb-6 relative z-10">Tool Selection</h2>
            <div className="space-y-6 relative z-10 overflow-y-auto pr-2 max-h-[800px] scrollbar-thin">
              {categories.map(cat => (
                <div key={cat}>
                  <div className="text-[10px] font-bold uppercase tracking-widest mb-3 text-gray-500/80">{cat}</div>
                  <div className="space-y-2">
                    {TOOLS.filter(t => t.category === cat).map(tool => (
                      <motion.button key={tool.id} onClick={() => { setSelectedTool(tool); setTarget(""); setResults(null); }}
                        whileHover={{ x: 4, scale: 1.01 }}
                        whileTap={{ scale: 0.98 }}
                        className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all border ${selectedTool.id === tool.id ? 'bg-ds-accent-blue/15 border-ds-accent-blue/30 shadow-[0_0_20px_rgba(59,130,246,0.1)]' : 'bg-black/30 border-white/5 hover:border-white/10 hover:bg-white/5'}`}
                      >
                        <span className="text-xl">{tool.icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className={`text-xs font-bold truncate ${selectedTool.id === tool.id ? 'text-white' : 'text-gray-400'}`}>{tool.name}</div>
                        </div>
                        {tool.risk === "OFFENSIVE" && (
                          <span className="text-[9px] font-black px-1.5 py-0.5 rounded border bg-red-500/10 text-red-400 border-red-500/20">OFF</span>
                        )}
                      </motion.button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Main Area */}
        <motion.div variants={{ hidden: { opacity: 0, x: 20 }, show: { opacity: 1, x: 0 } }} className="lg:col-span-8 xl:col-span-9 space-y-6">
          {/* Tool Info */}
          <motion.div key={selectedTool.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="glass-panel rounded-3xl p-6 border border-ds-border flex flex-col md:flex-row md:items-center justify-between gap-4 relative overflow-hidden">
            <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 blur-[80px] rounded-full pointer-events-none" />
            <div className="flex items-center gap-5 relative z-10">
              <div className="w-16 h-16 rounded-2xl bg-black/40 border border-white/10 flex items-center justify-center text-3xl shadow-inner">
                {selectedTool.icon}
              </div>
              <div>
                <h2 className="text-2xl font-black text-white tracking-tight">{selectedTool.name}</h2>
                <p className="text-sm text-ds-text-secondary mt-1">{selectedTool.description}</p>
              </div>
            </div>
            <div className="relative z-10 self-start md:self-center">
              <span className={`text-xs font-black px-3 py-1.5 rounded-full border tracking-widest uppercase ${ selectedTool.risk === "OFFENSIVE" ? "bg-red-500/10 text-red-400 border-red-500/20" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" }`}>
                {selectedTool.risk}
              </span>
            </div>
          </motion.div>

          {/* Target Input */}
          <div className="glass-panel rounded-3xl p-6 border border-ds-border relative overflow-hidden">
            <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-ds-accent-purple/10 blur-[80px] rounded-full pointer-events-none" />
            <div className="flex flex-col md:flex-row gap-4 relative z-10">
              <div className="flex-1">
                <label className="text-xs font-bold text-ds-text-secondary uppercase tracking-widest block mb-2">Target Payload</label>
                <input type="text" value={target} onChange={e => setTarget(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !isScanning && runScan()}
                  placeholder={selectedTool.placeholder}
                  className="w-full rounded-xl px-4 py-3.5 text-sm text-white font-mono bg-black/40 border border-white/10 focus:border-ds-accent-blue/50 focus:ring-1 focus:ring-ds-accent-blue/50 outline-none transition-all placeholder:text-gray-600" />
              </div>
              {selectedTool.scanTypes && (
                <div className="md:w-48">
                  <label className="text-xs font-bold text-ds-text-secondary uppercase tracking-widest block mb-2">Scan Type</label>
                  <select value={scanType} onChange={e => setScanType(e.target.value)}
                    className="w-full rounded-xl px-4 py-3.5 text-sm text-white bg-black/40 border border-white/10 outline-none focus:border-ds-accent-blue/50">
                    {selectedTool.scanTypes.map((st: string) => <option key={st} value={st} className="bg-[#0b0f1a]">{st.toUpperCase()}</option>)}
                  </select>
                </div>
              )}
              <div className="flex items-end">
                <motion.button onClick={runScan} disabled={isScanning} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.95 }}
                  className="w-full md:w-auto flex items-center justify-center gap-2 text-white px-8 py-3.5 rounded-xl font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(220,38,38,0.2)] hover:shadow-[0_0_30px_rgba(220,38,38,0.4)]"
                  style={{ background: isScanning ? '#991b1b' : 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', border: '1px solid rgba(255,100,100,0.2)' }}>
                  {isScanning ? <><span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" /> EXECUTING...</> : <>▶ FIRE PAYLOAD</>}
                </motion.button>
              </div>
            </div>
          </div>

          {/* Terminal */}
          <div className="glass-panel rounded-3xl overflow-hidden border border-ds-success/20 shadow-[0_0_40px_rgba(16,185,129,0.03)] flex flex-col">
            <div className="px-6 py-4 flex items-center justify-between border-b border-white/5 bg-black/40">
              <div className="flex items-center gap-3">
                <span className="text-ds-success text-sm animate-pulse">■</span>
                <span className="text-[10px] font-mono font-bold text-ds-success tracking-widest">DEVSHIELD ARSENAL // LIVE OUTPUT</span>
              </div>
              <div className="flex gap-2">
                <div className="w-3.5 h-3.5 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center"><div className="w-1.5 h-1.5 rounded-full bg-red-500" /></div>
                <div className="w-3.5 h-3.5 rounded-full bg-yellow-500/20 border border-yellow-500/50 flex items-center justify-center"><div className="w-1.5 h-1.5 rounded-full bg-yellow-500" /></div>
                <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center animate-pulse"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /></div>
              </div>
            </div>
            <div className="p-6 h-[340px] overflow-y-auto font-mono text-[11px] md:text-xs space-y-1.5 bg-[#03060a]">
              {terminalLines.map((line, i) => (
                <div key={i} className="flex gap-3 leading-relaxed">
                  <span className="text-gray-600 select-none">&gt;</span>
                  <span style={{ color: getLineColor(line.type) }} className="break-all">{line.text}</span>
                </div>
              ))}
              {isScanning && (
                <div className="flex gap-3 mt-2">
                  <span className="text-gray-600">&gt;</span>
                  <span className="inline-block w-2.5 h-4 bg-ds-success/70 animate-pulse" />
                </div>
              )}
              <div ref={terminalEndRef} className="h-4" />
            </div>
          </div>

          {/* Results */}
          <AnimatePresence>
            {results && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
                className="glass-panel rounded-3xl p-6 border border-ds-border">
                <h3 className="text-sm font-black text-white mb-6 uppercase tracking-widest flex items-center gap-2">
                  <span className="text-ds-success">✓</span> Operation Complete
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {results.open_count !== undefined && (
                    <div className="rounded-2xl p-4 bg-black/40 border border-white/5 flex flex-col items-center justify-center">
                      <div className="text-3xl font-black text-white">{results.open_count}</div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">Open Ports</div>
                    </div>
                  )}
                  {results.overall_risk && (
                    <div className={`rounded-2xl p-4 border flex flex-col items-center justify-center ${results.overall_risk === 'CRITICAL' ? 'bg-red-500/5 border-red-500/20' : 'bg-yellow-500/5 border-yellow-500/20'}`}>
                      <div className={`text-xl font-black ${results.overall_risk === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`}>{results.overall_risk}</div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">Risk Level</div>
                    </div>
                  )}
                  {results.overall_grade && (
                    <div className={`rounded-2xl p-4 border flex flex-col items-center justify-center ${results.overall_grade === 'F' ? 'bg-red-500/5 border-red-500/20' : results.overall_grade === 'A' ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-yellow-500/5 border-yellow-500/20'}`}>
                      <div className={`text-4xl font-black ${results.overall_grade === 'F' ? 'text-red-400' : results.overall_grade === 'A' ? 'text-emerald-400' : 'text-yellow-400'}`}>{results.overall_grade}</div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">SSL Grade</div>
                    </div>
                  )}
                  {results.waf_type && (
                    <div className="rounded-2xl p-4 bg-purple-500/5 border border-purple-500/20 flex flex-col items-center justify-center text-center">
                      <div className="text-sm font-black text-purple-400 leading-tight">{results.waf_type}</div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-2">WAF Type</div>
                    </div>
                  )}
                  {results.injectable !== undefined && (
                    <div className={`rounded-2xl p-4 border flex flex-col items-center justify-center ${results.injectable ? 'bg-red-500/5 border-red-500/30' : 'bg-emerald-500/5 border-emerald-500/20'}`}>
                      <div className={`text-sm font-black ${results.injectable ? 'text-red-400' : 'text-emerald-400'}`}>{results.injectable ? 'VULNERABLE' : 'CLEAN'}</div>
                      <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">SQL Injection</div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
}
