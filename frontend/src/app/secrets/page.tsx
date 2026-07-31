"use client";

import { useState } from "react";
import { SeverityBadge } from "@/components/ui/Badge";
import Image from "next/image";

export default function SecretsCenter() {
  const [scanning, setScanning] = useState(false);
  const [secrets, setSecrets] = useState([
    { id: 1, type: "AWS Access Key", file: "payment-gateway/config.py", line: 14, severity: "critical", resolved: false },
    { id: 2, type: "Stripe Secret", file: "auth-service/billing.ts", line: 42, severity: "high", resolved: false },
    { id: 3, type: "Database Password", file: "legacy-api/.env.backup", line: 3, severity: "medium", resolved: false },
  ]);

  const handleScan = () => {
    setScanning(true);
    setTimeout(() => {
        setScanning(false);
        setSecrets([
            { id: Date.now(), type: "GitHub Personal Access Token", file: ".github/workflows/deploy.yml", line: 12, severity: "critical", resolved: false },
            ...secrets
        ]);
    }, 2000);
  };

  const resolveSecret = (id: number) => {
    setSecrets(secrets.map(s => s.id === id ? { ...s, resolved: true } : s));
  };

  const activeSecrets = secrets.filter(s => !s.resolved);
  const resolvedSecrets = secrets.filter(s => s.resolved);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 relative z-10 max-w-7xl mx-auto">
      
      {/* Attractive Cyber Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0B0F19] via-[#0A101C] to-black border border-ds-border mb-8 animate-in slide-in-from-bottom-2 duration-500 group">
        <div className="absolute inset-0 opacity-30 mix-blend-screen transition-transform duration-1000 group-hover:scale-105 pointer-events-none">
          <img src="/hero-secrets.png" alt="Secrets Center" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B0F19] via-[#0B0F19]/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated/50 border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
            Active Monitoring
          </div>
          <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight drop-shadow-lg">Secrets Leak Center</h1>
          <p className="text-text-secondary text-base max-w-2xl mb-6 drop-shadow-md">
            Detect, review, and remediate hardcoded credentials, API keys, and certificates across all connected repositories in real-time.
          </p>
          <div className="flex gap-4">
            <button 
                onClick={handleScan}
                disabled={scanning}
                className="bg-rose-600 hover:bg-rose-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(225,29,72,0.5)] hover:shadow-[0_0_25px_rgba(225,29,72,0.8)] hover:-translate-y-0.5 border border-rose-400/30 flex items-center gap-2 relative z-20 disabled:opacity-50 disabled:hover:bg-rose-600 disabled:hover:-translate-y-0"
            >
                {scanning ? <span className="animate-spin text-white">◌</span> : 
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>}
                {scanning ? "Scanning repositories..." : "Run Real-time Scan"}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 animate-in slide-in-from-bottom-2 duration-500 delay-100">
        <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5">
          <div className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-2">Active Leaks</div>
          <div className="text-3xl font-medium text-white">{activeSecrets.length}</div>
        </div>
        <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5">
          <div className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-2">Resolved</div>
          <div className="text-3xl font-medium text-text-secondary">{resolvedSecrets.length}</div>
        </div>
        <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5">
          <div className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-2">Coverage Scan</div>
          <div className="text-3xl font-medium text-white">98%</div>
        </div>
      </div>

      <div className="animate-in slide-in-from-bottom-2 duration-500 delay-150">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-white tracking-tight">Identified Findings</h2>
          <button className="text-sm font-medium text-text-muted hover:text-white transition-colors">Export CSV</button>
        </div>
        
        {activeSecrets.length === 0 ? (
          <div className="text-center py-16 bg-ds-elevated/20 rounded-xl border border-dashed border-ds-border">
            <svg className="w-12 h-12 text-text-muted mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <h3 className="text-lg font-medium text-white mb-1 tracking-tight">Zero Active Leaks</h3>
            <p className="text-sm text-text-secondary">All hardcoded credentials have been remediated.</p>
          </div>
        ) : (
          <div className="border border-ds-border rounded-xl overflow-hidden bg-ds-elevated/30">
            {activeSecrets.map((secret, i) => (
              <div key={secret.id} className={`flex flex-col md:flex-row items-start md:items-center justify-between p-4 bg-ds-navy hover:bg-ds-elevated transition-colors ${i !== activeSecrets.length - 1 ? 'border-b border-ds-border' : ''}`}>
                <div className="mb-4 md:mb-0">
                  <div className="flex items-center gap-3 mb-1.5">
                    <SeverityBadge severity={secret.severity.toUpperCase()} />
                    <h3 className="font-medium text-white text-sm">{secret.type}</h3>
                  </div>
                  <div className="text-xs text-text-muted font-mono flex items-center gap-2">
                    <svg className="w-3.5 h-3.5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                    {secret.file} <span className="text-ds-border mx-0.5">•</span> L{secret.line}
                  </div>
                </div>
                
                <div className="flex gap-2 w-full md:w-auto">
                  <button className="px-3 py-1.5 text-xs font-medium text-text-secondary hover:text-white bg-ds-elevated border border-ds-border rounded-md transition-colors flex-1 md:flex-none">
                    View Context
                  </button>
                  <button 
                    onClick={() => resolveSecret(secret.id)} 
                    className="px-3 py-1.5 text-xs font-medium text-ds-navy bg-white hover:bg-gray-200 rounded-md transition-colors flex-1 md:flex-none"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
