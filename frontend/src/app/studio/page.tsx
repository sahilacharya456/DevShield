"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Wrench, CheckCircle2, Code, Terminal, Zap, GitBranch } from "lucide-react";

export default function AutoFixStudio() {
  const [isApplying, setIsApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  const applyFix = () => {
    setIsApplying(true);
    setTimeout(() => {
      setIsApplying(false);
      setApplied(true);
    }, 1500);
  };

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="max-w-7xl mx-auto"
    >
      {/* Header */}
      <motion.div
        variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 bg-cyan-500/10 rounded-xl border border-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              Auto-Fix Studio
            </h1>
            <p className="text-sm text-ds-text-secondary mt-1 font-mono tracking-wider">
              RAG-Powered AI Patching — FAISS + SentenceTransformers
            </p>
          </div>
          <div className="ml-auto hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_#22d3ee]" />
            <span className="text-xs font-mono text-cyan-400 font-bold tracking-widest uppercase">RAG Active</span>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col: Context & Vulnerability */}
        <motion.div
          variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }}
          className="lg:col-span-1 space-y-6"
        >
          {/* Vulnerability Card */}
          <div className="glass-panel rounded-3xl p-6 border-l-4 border-l-red-500 border border-ds-border relative overflow-hidden">
            <div className="absolute -top-10 -right-10 w-32 h-32 bg-red-500/10 blur-[40px] rounded-full" />
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] font-bold uppercase tracking-widest mb-4">
                🔴 Critical Risk
              </div>
              <h2 className="text-xl font-bold text-red-400 mb-2">SQL Injection Risk</h2>
              <p className="text-sm text-gray-300 mb-4 leading-relaxed">
                Detected dynamic string concatenation in <code className="text-red-300 font-mono">cursor.execute()</code>. This is highly vulnerable to injection attacks.
              </p>
              <div className="bg-red-500/10 p-4 rounded-xl text-sm text-red-200 border border-red-500/20 font-mono leading-relaxed">
                <div className="text-gray-500 text-xs mb-2">payment-gateway/api.py:14</div>
                cursor.execute("SELECT * FROM users WHERE id=" + req_id)
              </div>
            </div>
          </div>

          {/* RAG Context Card */}
          <div className="glass-panel rounded-3xl p-6 border border-ds-border relative overflow-hidden">
            <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-purple-500/10 blur-[40px] rounded-full" />
            <div className="relative z-10">
              <h3 className="font-bold mb-4 flex items-center gap-2 text-white">
                <Code className="w-5 h-5 text-purple-400" /> RAG Context Used
              </h3>
              <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                FAISS retrieved the following similar historical fixes to guide this patch:
              </p>
              <ul className="text-sm text-gray-300 space-y-3">
                <li className="flex items-start gap-3 p-3 rounded-xl bg-purple-500/5 border border-purple-500/10">
                  <GitBranch className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="font-mono text-purple-300 text-xs">a1b2c3d</div>
                    <div className="text-xs text-gray-400 mt-1">Migrated to parameterized queries in auth.py</div>
                  </div>
                </li>
                <li className="flex items-start gap-3 p-3 rounded-xl bg-purple-500/5 border border-purple-500/10">
                  <GitBranch className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="font-mono text-purple-300 text-xs">f9e8d7c</div>
                    <div className="text-xs text-gray-400 mt-1">Fixed SQLi in dashboard query module</div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-panel rounded-2xl p-4 border border-ds-border text-center">
              <div className="text-2xl font-black text-white">98%</div>
              <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">Confidence</div>
            </div>
            <div className="glass-panel rounded-2xl p-4 border border-emerald-500/20 text-center">
              <div className="text-2xl font-black text-emerald-400">1</div>
              <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">Line Changed</div>
            </div>
          </div>
        </motion.div>

        {/* Right Col: Diff Viewer */}
        <motion.div
          variants={{ hidden: { opacity: 0, x: 20 }, show: { opacity: 1, x: 0 } }}
          className="lg:col-span-2 glass-panel rounded-3xl flex flex-col overflow-hidden border border-ds-border"
        >
          {/* Terminal Header */}
          <div className="bg-black/40 border-b border-white/5 p-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <h3 className="font-bold text-gray-200 text-sm">Proposed Patch — Unified Diff</h3>
            </div>
            <div className="flex items-center gap-3">
              {applied ? (
                <span className="text-emerald-400 flex items-center gap-2 text-sm font-bold">
                  <CheckCircle2 className="w-4 h-4" /> Patch Applied Successfully
                </span>
              ) : (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={applyFix}
                  disabled={isApplying}
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white px-5 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(37,99,235,0.4)] disabled:opacity-50"
                >
                  {isApplying ? (
                    <><span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" /> Applying...</>
                  ) : (
                    <><Zap className="w-4 h-4" /> Apply Fix to Repo</>
                  )}
                </motion.button>
              )}
            </div>
          </div>

          {/* Mac-style traffic lights */}
          <div className="px-4 py-2 flex items-center gap-2 bg-black/20 border-b border-white/5">
            <div className="w-3 h-3 rounded-full bg-red-500/60 border border-red-500/40" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/60 border border-yellow-500/40" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/60 border border-emerald-500/40 animate-pulse" />
            <span className="text-[10px] font-mono text-gray-500 ml-2">payment-gateway/api.py</span>
          </div>

          {/* Diff Content */}
          <div className="flex-1 bg-[#0d1117] p-6 font-mono text-sm overflow-x-auto">
            <div className="text-gray-500 select-none mb-3 text-xs">@@ -12,4 +12,4 @@</div>
            <div className="text-gray-300 py-1 flex">
              <span className="w-8 text-gray-600 select-none text-right pr-3">12</span>
              <span>&nbsp;&nbsp;def get_user_data(req_id):</span>
            </div>
            <div className="text-gray-300 py-1 flex">
              <span className="w-8 text-gray-600 select-none text-right pr-3">13</span>
              <span>&nbsp;&nbsp;&nbsp;&nbsp;conn = sqlite3.connect(&apos;db.sqlite&apos;)</span>
            </div>
            <div className="text-gray-300 py-1 flex">
              <span className="w-8 text-gray-600 select-none text-right pr-3">14</span>
              <span>&nbsp;&nbsp;&nbsp;&nbsp;cursor = conn.cursor()</span>
            </div>

            <AnimatePresence>
              {!applied && (
                <motion.div
                  initial={{ backgroundColor: "transparent" }}
                  animate={{ backgroundColor: "rgba(248, 113, 113, 0.08)" }}
                  className="text-red-400 py-1 flex rounded"
                >
                  <span className="w-8 text-red-500/50 select-none text-right pr-3 text-xs">−</span>
                  <span>&nbsp;&nbsp;&nbsp;&nbsp;cursor.execute(&quot;SELECT * FROM users WHERE id=&quot; + req_id)</span>
                </motion.div>
              )}
            </AnimatePresence>

            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="text-emerald-400 py-1 flex bg-emerald-500/8 rounded"
            >
              <span className="w-8 text-emerald-500/50 select-none text-right pr-3 text-xs">+</span>
              <span>&nbsp;&nbsp;&nbsp;&nbsp;cursor.execute(&quot;SELECT * FROM users WHERE id=?&quot;, (req_id,))</span>
            </motion.div>

            <div className="text-gray-300 py-1 flex">
              <span className="w-8 text-gray-600 select-none text-right pr-3">17</span>
              <span>&nbsp;&nbsp;&nbsp;&nbsp;return cursor.fetchone()</span>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/5 bg-black/20 flex items-center justify-between text-xs">
            <div className="flex items-center gap-4">
              <span className="text-red-400 font-mono">- 1 deletion</span>
              <span className="text-emerald-400 font-mono">+ 1 insertion</span>
            </div>
            <span className="text-gray-600 font-mono">CVSS 9.8 → Mitigated</span>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
