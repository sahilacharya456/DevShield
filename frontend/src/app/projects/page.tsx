"use client";

import { useState, useEffect } from "react";
import { SeverityBadge } from "@/components/ui/Badge";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";

export default function ProjectsPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          // Transform if needed or just set
          setProjects(data.map((p: any) => ({
            id: p.id,
            name: p.name,
            lang: p.language,
            score: p.score || 100, // mock score if not returned
            lastScan: new Date(p.created_at).toLocaleDateString(),
            vulns: p.vulns || 0 // mock vulns
          })));
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchProjects();
  }, []);

  const handleStartScan = async () => {
    if (!repoUrl.trim()) return;
    setModalOpen(false);
    setScanning(true);
    setProgress(10);
    
    try {
      const token = localStorage.getItem("access_token");
      
      // Create project
      const repoName = repoUrl.split('/').pop()?.replace('.git', '') || "new-repository";
      const createRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: repoName, language: "Unknown", repo_url: repoUrl })
      });
      
      if (!createRes.ok) throw new Error("Failed to create project");
      const projectData = await createRes.json();
      setProgress(40);
      
      // Start scan
      const scanRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects/${projectData.id}/scan`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!scanRes.ok) throw new Error("Failed to start scan");
      setProgress(80);
      
      // Since the backend uses LocalCelery or eager execution, the scan completes during the request.
      // We can just fetch the updated projects to see the real score.
      const listRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (listRes.ok) {
        const data = await listRes.json();
        setProjects(data.map((p: any) => ({
          id: p.id,
          name: p.name,
          lang: p.language,
          score: p.score || 100,
          lastScan: new Date(p.created_at).toLocaleDateString(),
          vulns: p.vulns || 0
        })));
      }
      
      setProgress(100);
      setTimeout(() => {
        setScanning(false);
        setRepoUrl("");
      }, 500);
      
    } catch (e) {
      console.error(e);
      setScanning(false);
    }
  };

  return (
    <motion.div 
      initial="hidden" 
      animate="show" 
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="space-y-8 pb-12 relative z-10 max-w-7xl mx-auto p-8"
    >
      
      {/* Attractive Cyber Header */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="relative overflow-hidden rounded-3xl glass-panel border border-ds-border mb-8 group">
        <div className="absolute inset-0 opacity-30 mix-blend-screen transition-transform duration-1000 group-hover:scale-105 pointer-events-none">
          <img src="/hero-projects.png" alt="Repository Scanners" className="absolute inset-0 w-full h-full object-cover animate-in fade-in duration-700" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-ds-navy/95 via-ds-navy/80 to-transparent pointer-events-none"></div>
        <div className="relative z-10 p-8 md:p-12 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-fuchsia-500/10 border border-fuchsia-500/20 text-fuchsia-400 text-[10px] font-bold uppercase tracking-widest mb-4 shadow-inner">
            Orchestration Engine
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tight drop-shadow-lg">Repository Scanners</h1>
          <p className="text-ds-text-secondary text-base max-w-2xl mb-8 drop-shadow-md">
            Connect your codebase to trigger multi-engine SAST orchestration, secret detection, and SBOM pipeline analysis.
          </p>
          <div className="flex gap-4">
            {!scanning ? (
              <motion.button 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setModalOpen(true)} 
                className="bg-gradient-to-r from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500 text-white px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-[0_0_20px_rgba(192,38,211,0.4)] hover:shadow-[0_0_30px_rgba(192,38,211,0.6)] border border-fuchsia-400/30 flex items-center gap-2 relative z-20"
              >
                <span className="text-xl leading-none font-black">+</span> Connect Repository
              </motion.button>
            ) : (
              <div className="flex-1 max-w-md bg-black/60 backdrop-blur-md border border-ds-border rounded-xl p-5 relative z-20 shadow-2xl">
                <div className="flex justify-between text-xs text-ds-text-secondary mb-3 font-bold uppercase tracking-widest">
                  <span className="flex items-center gap-2 animate-pulse">Scanning source code...</span>
                  <span className="text-white font-black">{progress}%</span>
                </div>
                <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden border border-white/10">
                  <div className="bg-gradient-to-r from-fuchsia-500 to-purple-500 h-full transition-all duration-300 relative shadow-[0_0_15px_rgba(192,38,211,0.6)]" style={{ width: `${progress}%` }}></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      <motion.div variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }} className="flex justify-between items-center mt-4">
          <h2 className="text-xl font-black text-white tracking-tight uppercase">Active Projects</h2>
      </motion.div>

      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project, idx) => (
          <motion.div key={idx} whileHover={{ y: -5 }} className="glass-panel border border-ds-border hover:border-white/20 transition-all rounded-3xl p-6 cursor-pointer group">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-black/40 border border-white/5 shadow-inner flex items-center justify-center text-xl text-ds-text-secondary group-hover:text-white group-hover:bg-white/5 transition-all">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg tracking-tight group-hover:text-ds-accent-blue transition-colors">{project.name}</h3>
                  <span className="text-[10px] text-ds-text-secondary font-mono font-bold uppercase tracking-widest">{project.lang}</span>
                </div>
              </div>
            </div>
            
            <div className="flex justify-between items-end border-t border-white/5 pt-5">
              <div>
                <p className="text-[10px] font-bold text-ds-text-secondary mb-1 uppercase tracking-widest">Risk Score</p>
                <p className={`text-3xl font-black tracking-tight ${project.score >= 90 ? 'text-ds-success drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]' : project.score >= 70 ? 'text-white' : 'text-ds-critical drop-shadow-[0_0_10px_rgba(239,68,68,0.3)]'}`}>
                  {project.score}
                </p>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-bold text-ds-text-secondary mb-1.5 uppercase tracking-widest">Vulnerabilities</p>
                <div className="flex items-center gap-3 justify-end">
                  <span className="text-xl font-black text-white">{project.vulns}</span>
                  {project.vulns > 0 ? <SeverityBadge severity={project.score < 75 ? "HIGH" : "LOW"} /> : <SeverityBadge severity="INFO" />}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Connect Repo Modal */}
      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/60 backdrop-blur-md" onClick={() => setModalOpen(false)}></motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }} className="relative glass-panel border border-ds-border shadow-2xl rounded-3xl w-full max-w-md p-8 m-4">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-xl font-black text-white tracking-tight">Connect Repository</h2>
                <button onClick={() => setModalOpen(false)} className="w-8 h-8 rounded-full bg-black/40 border border-white/10 flex items-center justify-center text-ds-text-secondary hover:text-white hover:bg-white/10 transition-all">✕</button>
              </div>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-[11px] font-bold text-ds-text-secondary uppercase tracking-widest mb-3">Repository URL</label>
                  <input 
                    type="text" 
                    autoFocus
                    placeholder="https://github.com/org/repo.git" 
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-white font-mono focus:outline-none focus:border-ds-accent-blue/50 focus:ring-1 focus:ring-ds-accent-blue/50 transition-all placeholder:text-gray-600"
                  />
                </div>
                <div className="flex items-center justify-center w-full mt-4">
                    <label className="flex flex-col items-center justify-center w-full h-36 bg-black/20 border-2 border-white/5 border-dashed rounded-xl cursor-pointer hover:bg-white/5 hover:border-white/20 transition-all group">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg className="w-8 h-8 text-ds-text-muted mb-3 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                            <p className="mb-1 text-sm text-ds-text-secondary font-bold">Click to upload a ZIP archive</p>
                            <p className="text-[10px] font-mono text-ds-text-muted uppercase tracking-widest">.zip, .tar.gz (MAX. 500MB)</p>
                        </div>
                    </label>
                </div>
              </div>

              <div className="mt-8 flex justify-end gap-3 border-t border-white/5 pt-6">
                <button onClick={() => setModalOpen(false)} className="px-6 py-3 rounded-xl text-sm font-bold text-ds-text-secondary hover:text-white hover:bg-white/5 transition-colors">Cancel</button>
                <motion.button 
                  whileHover={repoUrl.trim() ? { scale: 1.02 } : {}}
                  whileTap={repoUrl.trim() ? { scale: 0.98 } : {}}
                  onClick={handleStartScan}
                  disabled={!repoUrl.trim()} 
                  className="bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-xl font-black text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                >
                  Start Scan
                </motion.button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
