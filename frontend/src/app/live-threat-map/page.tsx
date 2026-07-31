"use client";

import React from "react";
import { ThreatMapWidget } from "@/components/ui/ThreatMapWidget";
import { ThreatStatsCards } from "@/components/ui/ThreatStatsCards";
import { Shield, Globe, Info, AlertTriangle, ArrowRight } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function LiveThreatMap() {
  return (
    <motion.div 
      initial="hidden" 
      animate="show" 
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="p-8 pb-20 max-w-7xl mx-auto space-y-8 relative z-10"
    >
      {/* Dynamic Glow Orbs */}
      <div className="absolute top-[10%] left-[20%] w-[350px] h-[350px] rounded-full bg-blue-600/5 blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-[20%] right-[20%] w-[350px] h-[350px] rounded-full bg-purple-600/5 blur-[120px] pointer-events-none -z-10" />

      {/* Modern Cyber Header Panel */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="glass-panel border border-ds-border rounded-3xl p-8 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-r from-ds-accent-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-ds-accent-blue/10 blur-[80px] rounded-full pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold uppercase tracking-widest shadow-inner">
              Threat Intelligence Engine
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight drop-shadow-sm flex items-center gap-3">
              <Globe className="w-8 h-8 text-ds-accent-blue" />
              Live Threat Map & Cyber Attack Intelligence
            </h1>
            <p className="text-ds-text-secondary text-sm max-w-3xl leading-relaxed">
              This module visualizes live global cyber threat activity using trusted external cyber threat intelligence maps. It helps users understand how attacks move across countries, industries, and networks in real time.
            </p>
          </div>
          <Link href="/dashboard">
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="bg-black/40 hover:bg-white/10 text-white border border-white/10 hover:border-white/20 px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-sm flex items-center gap-2 whitespace-nowrap self-start md:self-center backdrop-blur-md">
              Back to Command Center <ArrowRight className="w-4 h-4 text-ds-text-secondary" />
            </motion.button>
          </Link>
        </div>
      </motion.div>

      {/* Grid of Threat Statistics Cards */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}>
        <ThreatStatsCards />
      </motion.div>

      {/* Interactive Global Map Widget */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}>
        <ThreatMapWidget />
      </motion.div>

      {/* Service layer documentation card for the developer/user */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }} className="glass-panel border border-ds-border rounded-3xl p-8 space-y-5 relative overflow-hidden">
        <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-ds-accent-purple/10 blur-[80px] rounded-full pointer-events-none" />
        <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2 relative z-10">
          <Info className="w-5 h-5 text-ds-accent-blue" /> Professional Service Integration Layer
        </h3>
        <p className="text-sm text-ds-text-secondary leading-relaxed relative z-10">
          The threat intelligence service layer in DevShield is ready for programmatic expansion. Connecting your premium API keys activates real-time, sandbox-safe audits against:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-2 relative z-10">
          <div className="bg-black/40 border border-white/5 hover:border-white/10 rounded-2xl p-5 space-y-2 transition-colors">
            <span className="text-[10px] font-bold text-ds-accent-blue font-mono tracking-widest uppercase">1. AbuseIPDB API</span>
            <p className="text-xs text-ds-text-secondary leading-relaxed">IP reputation lookup and active scan fuzzer audit checks.</p>
          </div>
          <div className="bg-black/40 border border-white/5 hover:border-white/10 rounded-2xl p-5 space-y-2 transition-colors">
            <span className="text-[10px] font-bold text-cyan-400 font-mono tracking-widest uppercase">2. VirusTotal API</span>
            <p className="text-xs text-ds-text-secondary leading-relaxed">Cryptographic hash reputation verification and domain health index scans.</p>
          </div>
          <div className="bg-black/40 border border-white/5 hover:border-white/10 rounded-2xl p-5 space-y-2 transition-colors">
            <span className="text-[10px] font-bold text-pink-400 font-mono tracking-widest uppercase">3. AlienVault OTX</span>
            <p className="text-xs text-ds-text-secondary leading-relaxed">Security Pulse correlation mappings and active IOC intelligence hashes.</p>
          </div>
          <div className="bg-black/40 border border-white/5 hover:border-white/10 rounded-2xl p-5 space-y-2 transition-colors">
            <span className="text-[10px] font-bold text-orange-400 font-mono tracking-widest uppercase">4. GreyNoise API</span>
            <p className="text-xs text-ds-text-secondary leading-relaxed">Mass-scanner telemetry categorization to filter background noise.</p>
          </div>
        </div>
      </motion.div>

    </motion.div>
  );
}
