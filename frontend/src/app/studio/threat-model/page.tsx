"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ShieldAlert, GitBranch, Database, Globe, Network, Server, ArrowRight, X, Shield, Lock, Eye } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface ThreatNode {
  id: string;
  label: string;
  icon: React.ReactNode;
  risk: string;
  desc: string;
  details: string;
  impact: string;
  stride: string;
}

export default function ThreatModelStudio() {
  const router = useRouter();
  const [nodes, setNodes] = useState<ThreatNode[]>([]);
  const [isGenerating, setIsGenerating] = useState(true);
  const [selectedNode, setSelectedNode] = useState<ThreatNode | null>(null);

  // Mocking an AI generating the threat model structure
  useEffect(() => {
    const timer = setTimeout(() => {
      setNodes([
        { 
          id: "auth", 
          label: "Auth Service", 
          icon: <ShieldAlert className="w-5 h-5 text-red-400" />, 
          risk: "Critical", 
          desc: "JWT signing key is weak. SQL Injection risk detected in User Repository.",
          stride: "Spoofing / Elevation of Privilege",
          impact: "Complete bypass of authentication checks and backend DB compromise.",
          details: "Tree-Sitter parsed the user login query and confirmed unparameterized f-string values flowing straight into a raw cursor.execute. Attackers can inject SQL queries to retrieve all user hashes."
        },
        { 
          id: "api", 
          label: "API Gateway", 
          icon: <Globe className="w-5 h-5 text-orange-400" />, 
          risk: "High", 
          desc: "Exposed public internet gateway. Rate limiting is missing on authentication paths.",
          stride: "Denial of Service / Info Disclosure",
          impact: "Brute-force credential stuffing and endpoint exhaustion.",
          details: "Rate limiting is completely absent in the gateway routing file. Public routes are subject to high velocity automated fuzzing attacks."
        },
        { 
          id: "db", 
          label: "User Database", 
          icon: <Database className="w-5 h-5 text-yellow-400" />, 
          risk: "Medium", 
          desc: "Data connections do not require mutual TLS (mTLS) verification.",
          stride: "Tampering / Information Disclosure",
          impact: "Man-in-the-Middle (MitM) database sniffing.",
          details: "PostgreSQL connections rely on plaintext verification without enforceSSL variables, leaving internal traffic susceptible to side-channel packet inspection."
        },
        { 
          id: "worker", 
          label: "Task Queue", 
          icon: <Server className="w-5 h-5 text-green-400" />, 
          risk: "Low", 
          desc: "Internal service queue. Protected behind secure AWS VPC subnets.",
          stride: "Repudiation",
          impact: "Audit logging missing on message receipt.",
          details: "Task queues execute asynchronous background tasks but fail to log standard actor parameters, making non-repudiation difficult during post-incident analysis."
        }
      ]);
      setIsGenerating(false);
    }, 1800);
    return () => clearTimeout(timer);
  }, []);

  const handleSendToAutoFix = (node: ThreatNode) => {
    let vulnTitle = "";
    if (node.id === "auth") {
      vulnTitle = "[CRITICAL] SQL Injection in get_user";
    } else if (node.id === "api") {
      vulnTitle = "[HIGH] Hardcoded Secret in main.py";
    } else {
      vulnTitle = `[HIGH] Vulnerability in ${node.label}`;
    }
    router.push(`/studio/autofix?vuln=${encodeURIComponent(vulnTitle)}`);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] p-6 lg:p-10 text-gray-100 relative overflow-hidden">
      {/* Grid background for the node graph feel */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/3 w-[350px] h-[350px] rounded-full bg-red-600/5 blur-[120px] pointer-events-none" />

      <nav className="relative z-10 flex justify-between items-center mb-10">
        <Link href="/dashboard">
          <div className="flex items-center gap-3 cursor-pointer text-gray-400 hover:text-white transition-colors">
            <ArrowRight className="w-5 h-5 rotate-180" />
            <span className="font-semibold text-sm">Back to Command Center</span>
          </div>
        </Link>
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-purple-500 flex items-center gap-2">
          <Network className="text-red-400 w-5 h-5" /> Threat Model Studio
        </h1>
      </nav>

      <div className="relative z-10 max-w-6xl mx-auto">
        
        {/* Architecture Header */}
        <div className="bg-[#0F1420]/80 border border-ds-border rounded-2xl p-8 mb-8 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          <h2 className="text-3xl font-extrabold text-white mb-3 tracking-tight">Active STRIDE Threat Matrix</h2>
          <p className="text-text-secondary text-sm max-w-3xl leading-relaxed">
            Our multi-engine semantic security analyzer parses repository architectures dynamically, maps microservice boundary crossings, and generates real-time threat landscapes conforming to the Microsoft STRIDE framework.
          </p>
        </div>

        {isGenerating ? (
          <div className="flex flex-col items-center justify-center h-72 bg-[#0F1420]/45 border border-ds-border rounded-2xl">
            <div className="w-12 h-12 border-4 border-red-500/20 border-t-red-500 rounded-full animate-spin mb-4" />
            <p className="text-sm font-semibold text-red-400 animate-pulse tracking-widest font-mono">MAP-PROCESSING REPOSITORY GRAPH...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
            
            {nodes.map((node, i) => (
              <motion.div
                key={node.id}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="bg-[#0F1420]/80 border border-ds-border hover:border-white/10 rounded-2xl p-6 transition-all duration-300 relative group"
                style={{
                  borderLeft: `4px solid ${
                    node.risk === "Critical" ? "#ef4444" : 
                    node.risk === "High" ? "#f97316" : 
                    node.risk === "Medium" ? "#eab308" : "#22c55e"
                  }`
                }}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-[#070B13] rounded-xl border border-ds-border">
                      {node.icon}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white tracking-tight">{node.label}</h3>
                      <span className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full ${
                          node.risk === "Critical" ? "bg-red-500/10 text-red-400 border border-red-500/20" : 
                          node.risk === "High" ? "bg-orange-500/10 text-orange-400 border border-orange-500/20" : 
                          node.risk === "Medium" ? "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20" : 
                          "bg-green-500/10 text-green-400 border border-green-500/20"
                        }`}>
                        {node.risk} Risk Level
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-text-secondary text-sm leading-relaxed mb-6">{node.desc}</p>
                
                <div className="pt-4 border-t border-ds-border/60 flex gap-3">
                  <button 
                    onClick={() => setSelectedNode(node)}
                    className="flex-1 text-xs bg-ds-elevated hover:bg-[#1a2335] text-white border border-ds-border px-3.5 py-2.5 rounded-xl font-bold transition-all flex items-center justify-center gap-1.5"
                  >
                    <Eye className="w-3.5 h-3.5" /> View Details
                  </button>
                  <button 
                    onClick={() => handleSendToAutoFix(node)}
                    className="flex-1 text-xs bg-white text-black hover:bg-gray-200 px-3.5 py-2.5 rounded-xl font-extrabold transition-all flex items-center justify-center gap-1.5"
                  >
                    <Lock className="w-3.5 h-3.5" /> Auto-Fix Remediation
                  </button>
                </div>
              </motion.div>
            ))}

            {/* SVG lines mimicking connections between cards (visual flair) */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none -z-10 opacity-20 hidden lg:block">
              <path d="M 200 120 Q 400 240 600 120" fill="transparent" stroke="#ef4444" strokeWidth="1.5" strokeDasharray="6,6" />
              <path d="M 200 340 Q 400 240 600 340" fill="transparent" stroke="#eab308" strokeWidth="1.5" strokeDasharray="6,6" />
            </svg>

          </div>
        )}
      </div>

      {/* STRIDE Detailed Inspection Modal */}
      <AnimatePresence>
        {selectedNode && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-in fade-in duration-200">
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0b0f19] border border-ds-border w-full max-w-xl rounded-2xl shadow-2xl overflow-hidden relative"
            >
              {/* Colored top bar based on risk */}
              <div className={`h-1.5 w-full ${
                selectedNode.risk === "Critical" ? "bg-red-500" : 
                selectedNode.risk === "High" ? "bg-orange-500" : 
                selectedNode.risk === "Medium" ? "bg-yellow-500" : "bg-green-500"
              }`} />

              <button 
                onClick={() => setSelectedNode(null)} 
                className="absolute top-4 right-4 text-text-muted hover:text-white transition-colors p-1.5 bg-[#0F1420] border border-ds-border rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="p-6 md:p-8 space-y-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-[#0F1420] rounded-xl border border-ds-border">
                    {selectedNode.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white tracking-tight">{selectedNode.label} Detailed Audit</h3>
                    <span className="text-xs font-mono font-bold text-red-400">{selectedNode.stride}</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-[#070B13] border border-ds-border rounded-xl p-4">
                    <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1.5">Abstract Syntax Tree Findings</h4>
                    <p className="text-sm text-text-primary leading-relaxed font-light">{selectedNode.details}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-[#070B13] border border-ds-border rounded-xl p-4">
                      <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Impact Vector</h4>
                      <p className="text-xs text-white leading-relaxed">{selectedNode.impact}</p>
                    </div>
                    <div className="bg-[#070B13] border border-ds-border rounded-xl p-4">
                      <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">Risk Classification</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${
                          selectedNode.risk === "Critical" ? "bg-red-500/10 text-red-400" : "bg-orange-500/10 text-orange-400"
                        }`}>
                          {selectedNode.risk.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-6 border-t border-ds-border/60 flex gap-3">
                  <button 
                    onClick={() => setSelectedNode(null)}
                    className="flex-1 text-sm bg-ds-elevated hover:bg-[#1a2335] text-white border border-ds-border px-4 py-2.5 rounded-xl font-semibold transition-colors"
                  >
                    Close Inspection
                  </button>
                  <button 
                    onClick={() => {
                      setSelectedNode(null);
                      handleSendToAutoFix(selectedNode);
                    }}
                    className="flex-1 text-sm bg-white text-black hover:bg-gray-200 px-4 py-2.5 rounded-xl font-extrabold transition-all"
                  >
                    Generate Secure Patch
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
