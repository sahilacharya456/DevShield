"use client";

import { useState } from "react";
import Image from "next/image";

export default function ReportsCenter() {
  const [downloading, setDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setDownloadSuccess(false);
    try {
        const response = await fetch("http://localhost:8000/api/v1/reports/download");
        if (!response.ok) throw new Error("Failed to download");
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "devshield-audit-report.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setDownloadSuccess(true);
        setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (error) {
        console.error(error);
    } finally {
        setDownloading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 relative z-10 max-w-6xl mx-auto">
      
      {/* Attractive Cyber Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0B0F19] via-[#0A101C] to-black border border-ds-border mb-8 animate-in slide-in-from-bottom-2 duration-500 group">
        <div className="absolute inset-0 opacity-30 mix-blend-screen transition-transform duration-1000 group-hover:scale-105 pointer-events-none">
          <img src="/hero-reports.png" alt="Reports Center" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B0F19] via-[#0B0F19]/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated/50 border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
            Executive Summaries
          </div>
          <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight drop-shadow-lg">Reports Center</h1>
          <p className="text-text-secondary text-base max-w-2xl mb-6 drop-shadow-md">
            Export comprehensive DevSecOps audit reports, compliance matrices, and SBOMs for engineering leaders and auditors.
          </p>
          <div className="flex gap-4 items-center">
            <button 
              onClick={handleDownload}
              disabled={downloading}
              className="bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(124,58,237,0.5)] hover:shadow-[0_0_25px_rgba(124,58,237,0.8)] hover:-translate-y-0.5 border border-violet-400/30 flex items-center gap-2 relative z-20 disabled:opacity-50 disabled:hover:bg-violet-600 disabled:hover:-translate-y-0"
            >
              {downloading ? <span className="animate-spin text-white">◌</span> : 
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>}
              {downloading ? "Generating PDF..." : "Download Latest PDF"}
            </button>
            <button className="bg-pink-600 hover:bg-pink-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all shadow-[0_0_15px_rgba(219,39,119,0.5)] hover:shadow-[0_0_25px_rgba(219,39,119,0.8)] hover:-translate-y-0.5 border border-pink-400/30 relative z-20">
              Export SBOM (CycloneDX)
            </button>
          </div>
          
          {downloadSuccess && (
              <p className="text-sm font-medium text-ds-success mt-4 animate-in slide-in-from-bottom-2 duration-300 relative z-20">
                  devshield-audit-report.pdf downloaded successfully!
              </p>
          )}
        </div>
      </div>
      
      <div className="animate-in slide-in-from-bottom-2 duration-500 delay-100">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-white tracking-tight">Audit History</h2>
          <button className="text-sm font-medium text-text-muted hover:text-white transition-colors">Generate Custom →</button>
        </div>
        
        <div className="border border-ds-border rounded-xl overflow-hidden bg-ds-elevated/30">
          {[1,2,3].map((i) => (
            <div key={i} className={`flex items-center justify-between p-4 bg-ds-navy hover:bg-ds-elevated transition-colors group cursor-pointer ${i !== 3 ? 'border-b border-ds-border' : ''}`}>
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-[#0B0F19] border border-ds-border flex items-center justify-center text-text-secondary">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                </div>
                <div>
                  <h3 className="font-medium text-white text-sm">Q1 Security Audit - Auth Service</h3>
                  <p className="text-xs text-text-muted mt-0.5 font-mono">PDF • Generated Today</p>
                </div>
              </div>
              <button 
                onClick={handleDownload}
                className="px-3 py-1.5 text-xs font-medium text-text-secondary hover:text-white bg-ds-elevated border border-ds-border rounded-md transition-colors opacity-0 group-hover:opacity-100"
              >
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
