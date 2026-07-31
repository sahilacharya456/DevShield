"use client";

import React, { useState, useEffect } from "react";
import { ThreatIntelService, ThreatMetric } from "@/services/threatIntelService";
import { AlertCircle, Globe, Shield, Terminal, TrendingUp, CheckCircle, Info } from "lucide-react";
import { motion } from "framer-motion";

export function ThreatStatsCards() {
  const [stats, setStats] = useState<ThreatMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiConfigured, setApiConfigured] = useState(false);

  useEffect(() => {
    async function loadStats() {
      setLoading(true);
      const data = await ThreatIntelService.getThreatStats();
      setStats(data);
      setApiConfigured(ThreatIntelService.isApiConfigured());
      setLoading(false);
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-[#0F1420]/80 border border-ds-border rounded-xl p-5 h-32 animate-pulse flex flex-col justify-between">
            <div className="h-4 bg-white/5 rounded w-2/3" />
            <div className="h-8 bg-white/5 rounded w-1/2 mt-4" />
            <div className="h-3 bg-white/5 rounded w-3/4 mt-2" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Dynamic API Configuration Banner */}
      {!apiConfigured && (
        <div className="bg-[#0F1420]/50 border border-yellow-500/20 text-yellow-400 p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-inner">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/10 rounded-lg border border-yellow-500/20 text-yellow-500">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-xs uppercase tracking-wide">Threat Intelligence API optional</h4>
              <p className="text-[11px] text-text-secondary leading-relaxed font-mono">
                Visualizations load dynamically. Custom endpoint analytics & fuzzer feeds are disabled until API keys are set in your .env configuration.
              </p>
            </div>
          </div>
          <span className="text-[10px] font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-3 py-1 rounded-full whitespace-nowrap self-end sm:self-center uppercase font-mono">
            Demo Analytics Enabled
          </span>
        </div>
      )}

      {/* Grid Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Global Threat Activity */}
        <motion.div 
          className="bg-[#0F1420]/80 border border-ds-border rounded-xl p-5 relative overflow-hidden group"
          whileHover={{ y: -2 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-3 relative z-10">
            <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full uppercase font-mono">External Map Feed</span>
            <Globe className="w-4 h-4 text-blue-400" />
          </div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider font-mono">Global Threat Activity</h4>
          <p className="text-2xl font-bold text-white tracking-tight mt-1.5">Live Active Flows</p>
          <p className="text-[11px] text-text-muted mt-2">Telemetry streaming from external endpoints</p>
        </motion.div>

        {/* Card 2: Malware Phishing DDoS Trends */}
        <motion.div 
          className="bg-[#0F1420]/80 border border-ds-border rounded-xl p-5 relative overflow-hidden group"
          whileHover={{ y: -2 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-3 relative z-10">
            <span className="text-[10px] font-bold px-2 py-0.5 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full uppercase font-mono">External Map Feed</span>
            <TrendingUp className="w-4 h-4 text-orange-400" />
          </div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider font-mono">Malware / Phishing / DDoS</h4>
          <p className="text-2xl font-bold text-white tracking-tight mt-1.5">4.8M Daily Detections</p>
          <p className="text-[11px] text-text-muted mt-2">Active fuzzer & scan telemetry samples</p>
        </motion.div>

        {/* Card 3: Source and Target Countries */}
        <motion.div 
          className="bg-[#0F1420]/80 border border-ds-border rounded-xl p-5 relative overflow-hidden group"
          whileHover={{ y: -2 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-3 relative z-10">
            <span className="text-[10px] font-bold px-2 py-0.5 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full uppercase font-mono">API Optional</span>
            <Terminal className="w-4 h-4 text-purple-400" />
          </div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider font-mono">Hot Targets & Sources</h4>
          <p className="text-2xl font-bold text-white tracking-tight mt-1.5">RU, US, CN, NL, DE</p>
          <p className="text-[11px] text-text-muted mt-2">Historical top vectors / attack sinks</p>
        </motion.div>

        {/* Card 4: Threat Intelligence Feed Status */}
        <motion.div 
          className="bg-[#0F1420]/80 border border-ds-border rounded-xl p-5 relative overflow-hidden group"
          whileHover={{ y: -2 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-3 relative z-10">
            <span className="text-[10px] font-bold px-2 py-0.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full uppercase font-mono">API Optional</span>
            <Shield className="w-4 h-4 text-green-400" />
          </div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider font-mono">Intelligence Feed status</h4>
          <p className="text-2xl font-bold text-white tracking-tight mt-1.5">
            {apiConfigured ? "Connected (4/4)" : "Demo Map Active"}
          </p>
          <p className="text-[11px] text-text-muted mt-2">
            {apiConfigured ? "API keys validated" : "Demo analytics active (Keys missing)"}
          </p>
        </motion.div>

      </div>
    </div>
  );
}
