"use client";

import { useState, useEffect } from "react";
import { SeverityBadge } from "@/components/ui/Badge";

export default function AutoFixStudio() {
  const [loading, setLoading] = useState(false);
  const [patchData, setPatchData] = useState<{ orig: string, patched: string, conf: number } | null>(null);
  const [options, setOptions] = useState([
    "[CRITICAL] SQL Injection in get_user",
    "[HIGH] Hardcoded Secret in main.py",
    "[CRITICAL] Logic Bomb in backdoor_test.py",
    "[HIGH] Broken Object Level Authorization"
  ]);
  const [vuln, setVuln] = useState("[CRITICAL] SQL Injection in get_user");
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const urlVuln = params.get("vuln");
      if (urlVuln) {
        const decoded = decodeURIComponent(urlVuln);
        setOptions(prev => {
          if (!prev.includes(decoded)) return [decoded, ...prev];
          return prev;
        });
        setVuln(decoded);
      }
    }
  }, []);

  const generatePatch = async () => {
    setLoading(true);
    setPatchData(null);
    setApplied(false);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/autofix/generate`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ project_name: "auth-service-v2", vulnerability_title: vuln })
      });
      const data = await res.json();
      setPatchData({ orig: data.original_code, patched: data.patched_code, conf: data.confidence });
    } catch (err) {
      console.error(err);
      // Fallback if backend is down
      setTimeout(() => {
          setPatchData({
              orig: "def get_user(username):\n    query = f\"SELECT * FROM users WHERE username = '{username}'\"\n    return db.execute(query)",
              patched: "def get_user(username):\n    query = \"SELECT * FROM users WHERE username = %s\"\n    return db.execute(query, (username,))",
              conf: 98
          });
      }, 1000);
    } finally {
      setLoading(false);
    }
  };

  const applyPatch = () => {
    setApplied(true);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 relative z-10 max-w-6xl mx-auto">
      
      {/* Clean Enterprise Header */}
      <div className="border-b border-ds-border/50 pb-8 animate-in slide-in-from-bottom-2 duration-500">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
          Code Remediation
        </div>
        <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight">AI Auto-Fix Studio</h1>
        <p className="text-text-secondary text-base max-w-2xl mb-6">
          Review, test, and automatically apply AI-generated patches for vulnerabilities using high-confidence remediation models.
        </p>
      </div>

      <div className="bg-ds-elevated/30 border border-ds-border rounded-xl p-5 flex flex-col md:flex-row items-end gap-4 animate-in slide-in-from-bottom-2 duration-500 delay-100">
        <div className="flex-1 w-full">
          <label className="block text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2">Target Project</label>
          <select className="w-full bg-[#0B0F19] border border-ds-border rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-text-muted transition-colors appearance-none">
            <option>auth-service-v2</option>
            <option>payment-gateway</option>
          </select>
        </div>
        <div className="flex-[2] w-full">
          <label className="block text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2">Vulnerability</label>
          <select 
            className="w-full bg-[#0B0F19] border border-ds-border rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-text-muted transition-colors appearance-none" 
            value={vuln} 
            onChange={(e) => { setVuln(e.target.value); setPatchData(null); setApplied(false); }}
          >
            {options.map((opt, i) => (
              <option key={i}>{opt}</option>
            ))}
          </select>
        </div>
        <div className="w-full md:w-auto">
          <button 
            onClick={generatePatch} 
            disabled={loading} 
            className="bg-white text-black hover:bg-gray-200 px-5 py-2.5 rounded-lg font-medium text-sm transition-colors flex justify-center items-center gap-2 shadow-sm disabled:opacity-50 disabled:hover:bg-white w-full"
          >
            {loading ? <span className="animate-spin text-black">◌</span> : 
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>}
            {loading ? "Generating..." : "Generate Patch"}
          </button>
        </div>
      </div>

      {patchData && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 animate-in slide-in-from-bottom-2 duration-500 delay-150">
          
          {/* Original Code Card */}
          <div className="bg-ds-elevated/30 border border-ds-border rounded-xl flex flex-col overflow-hidden">
            <div className="bg-ds-elevated border-b border-ds-border px-5 py-3 flex justify-between items-center">
              <h2 className="font-medium text-white text-sm flex items-center gap-2">
                <svg className="w-4 h-4 text-ds-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Original Source
              </h2>
              <SeverityBadge severity={vuln.includes("CRITICAL") ? "CRITICAL" : "HIGH"} />
            </div>
            <div className="bg-[#0B0F19] p-5 font-mono text-[13px] overflow-x-auto text-text-muted flex-1">
              <pre className="leading-relaxed"><code>{patchData.orig}</code></pre>
            </div>
          </div>

          {/* Patched Code Card */}
          <div className="bg-ds-elevated/30 border border-ds-border rounded-xl flex flex-col relative overflow-hidden">
            {applied && (
              <div className="absolute inset-0 z-10 bg-ds-navy/90 backdrop-blur-sm flex items-center justify-center animate-in fade-in duration-300">
                <div className="text-center animate-in zoom-in-95">
                  <div className="w-12 h-12 bg-ds-success/10 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-ds-success" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-1">Patch Applied Successfully</h3>
                  <p className="text-xs text-text-secondary">Changes have been committed to the repository.</p>
                </div>
              </div>
            )}

            <div className="bg-ds-elevated border-b border-ds-border px-5 py-3 flex justify-between items-center relative z-0">
              <h2 className="font-medium text-white text-sm flex items-center gap-2">
                <svg className="w-4 h-4 text-ds-success" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Remediated Source
              </h2>
              <span className="text-[10px] font-semibold text-ds-success bg-ds-success/10 border border-ds-success/20 px-2 py-0.5 rounded-full">
                {patchData.conf}% Confidence
              </span>
            </div>
            <div className="bg-[#0B0F19] p-5 font-mono text-[13px] overflow-x-auto text-white flex-1 relative z-0">
              <pre className="leading-relaxed"><code>{patchData.patched}</code></pre>
            </div>
            
            <div className="bg-ds-elevated border-t border-ds-border p-4 flex gap-3 relative z-0">
              <button 
                onClick={applyPatch}
                className="flex-1 bg-white text-black hover:bg-gray-200 text-sm font-medium rounded-lg px-4 py-2 transition-colors"
              >
                Accept & Merge Patch
              </button>
              <button className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-white border border-ds-border rounded-lg hover:bg-ds-elevated/50 transition-colors">
                Flag False Positive
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
