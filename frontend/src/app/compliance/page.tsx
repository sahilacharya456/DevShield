"use client";

import { useState } from "react";
import Image from "next/image";

export default function ComplianceCenter() {
  const [running, setRunning] = useState(false);
  const [resultsReady, setResultsReady] = useState(false);

  const handleRun = () => {
    setRunning(true);
    setResultsReady(false);
    setTimeout(() => {
        setRunning(false);
        setResultsReady(true);
    }, 1800);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 relative z-10 max-w-6xl mx-auto">
      
      {/* Attractive Cyber Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0B0F19] via-[#0A101C] to-black border border-ds-border mb-8 animate-in slide-in-from-bottom-2 duration-500 group">
        <div className="absolute inset-0 opacity-30 mix-blend-screen transition-transform duration-1000 group-hover:scale-105 pointer-events-none">
          <img src="/hero-reports.png" alt="Compliance Center" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B0F19] via-[#0B0F19]/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated/50 border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
            Regulatory Framework
          </div>
          <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight drop-shadow-lg">Compliance Center</h1>
          <p className="text-text-secondary text-base max-w-2xl mb-6 drop-shadow-md">
            Automatically map your DevSecOps findings against OWASP Top 10, SOC 2, HIPAA, and PCI-DSS compliance frameworks.
          </p>
          <div className="flex gap-4">
            <button 
              onClick={handleRun}
              disabled={running}
              className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(37,99,235,0.5)] hover:shadow-[0_0_25px_rgba(37,99,235,0.8)] hover:-translate-y-0.5 border border-blue-400/30 flex items-center gap-2 relative z-20 disabled:opacity-50 disabled:hover:bg-blue-600 disabled:hover:-translate-y-0"
            >
              {running ? <span className="animate-spin text-white">◌</span> : 
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>}
              {running ? "Analyzing Frameworks..." : "Run Compliance Check"}
            </button>
          </div>
        </div>
      </div>
      
      {resultsReady && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 animate-in slide-in-from-bottom-2 duration-500 delay-100">
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors text-center">
                <div className="text-3xl font-medium text-white mb-2">92%</div>
                <div className="text-xs font-semibold text-text-muted uppercase tracking-wider">OWASP Top 10</div>
            </div>
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors text-center">
                <div className="text-3xl font-medium text-white mb-2">78%</div>
                <div className="text-xs font-semibold text-text-muted uppercase tracking-wider">SOC 2 Type II</div>
            </div>
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors text-center">
                <div className="text-3xl font-medium text-white mb-2">45%</div>
                <div className="text-xs font-semibold text-text-muted uppercase tracking-wider">PCI-DSS</div>
            </div>
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors text-center">
                <div className="text-3xl font-medium text-white mb-2">100%</div>
                <div className="text-xs font-semibold text-text-muted uppercase tracking-wider">GDPR Privacy</div>
            </div>
          </div>
      )}
    </div>
  );
}
