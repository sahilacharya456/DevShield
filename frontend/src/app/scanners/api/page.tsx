"use client";

import { useState } from "react";
import { SeverityBadge } from "@/components/ui/Badge";
import Image from "next/image";

export default function APISecurity() {
  const [scanning, setScanning] = useState(false);
  const [resultsReady, setResultsReady] = useState(false);

  const handleScan = () => {
    setScanning(true);
    setResultsReady(false);
    setTimeout(() => {
        setScanning(false);
        setResultsReady(true);
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 relative z-10 max-w-6xl mx-auto">
      
      {/* Attractive Cyber Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0B0F19] via-[#0A101C] to-black border border-ds-border mb-8 animate-in slide-in-from-bottom-2 duration-500 group">
        <div className="absolute inset-0 opacity-30 mix-blend-screen transition-transform duration-1000 group-hover:scale-105 pointer-events-none">
          <img src="/hero-shield.png" alt="API Security Lab" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B0F19] via-[#0B0F19]/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated/50 border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
            Endpoint Protection
          </div>
          <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight drop-shadow-lg">API Security Lab</h1>
          <p className="text-text-secondary text-base max-w-2xl mb-6 drop-shadow-md">
            Scan your OpenAPI specs, GraphQL schemas, and REST endpoints for SSRF, missing authentication, and rate limiting bypasses.
          </p>
          <div className="flex gap-4">
            <button 
              onClick={handleScan}
              disabled={scanning}
              className="bg-amber-500 hover:bg-amber-400 text-black px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(245,158,11,0.5)] hover:shadow-[0_0_25px_rgba(245,158,11,0.8)] hover:-translate-y-0.5 border border-amber-300/30 flex items-center gap-2 relative z-20 disabled:opacity-50 disabled:hover:bg-amber-500 disabled:hover:-translate-y-0"
            >
              {scanning ? <span className="animate-spin text-black">◌</span> : 
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>}
              {scanning ? "Fuzzing endpoints..." : "Start API Scan"}
            </button>
          </div>
        </div>
      </div>
      
      {resultsReady && (
          <div className="animate-in slide-in-from-bottom-2 duration-500 delay-100">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-white tracking-tight">Recent API DAST Findings</h2>
            </div>
            <div className="border border-ds-border rounded-xl overflow-hidden bg-ds-elevated/30">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between p-4 bg-ds-navy hover:bg-ds-elevated transition-colors border-b border-ds-border">
                <div className="mb-4 md:mb-0">
                    <div className="flex items-center gap-3 mb-1.5">
                    <SeverityBadge severity="CRITICAL" />
                    <h3 className="font-medium text-white text-sm">Server-Side Request Forgery (SSRF)</h3>
                    </div>
                    <div className="text-xs text-text-muted font-mono flex items-center gap-2">
                        <span className="text-ds-blue font-semibold uppercase text-[10px]">POST</span>
                        /api/v1/fetch-url
                    </div>
                </div>
                <button className="px-3 py-1.5 text-xs font-medium text-text-secondary hover:text-white bg-ds-elevated border border-ds-border rounded-md transition-colors">View Payload</button>
              </div>
              
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between p-4 bg-ds-navy hover:bg-ds-elevated transition-colors">
                <div className="mb-4 md:mb-0">
                    <div className="flex items-center gap-3 mb-1.5">
                    <SeverityBadge severity="HIGH" />
                    <h3 className="font-medium text-white text-sm">Broken Object Level Authorization (BOLA)</h3>
                    </div>
                    <div className="text-xs text-text-muted font-mono flex items-center gap-2">
                        <span className="text-ds-success font-semibold uppercase text-[10px]">GET</span>
                        /api/v1/users/{"{id}"}
                    </div>
                </div>
                <button className="px-3 py-1.5 text-xs font-medium text-text-secondary hover:text-white bg-ds-elevated border border-ds-border rounded-md transition-colors">View Payload</button>
              </div>
            </div>
          </div>
      )}
    </div>
  );
}
