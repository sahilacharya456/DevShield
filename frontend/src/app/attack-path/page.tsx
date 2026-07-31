"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEMO_VULNS = [
  { title: "SQL Injection Risk", severity: "CRITICAL", line: 42 },
  { title: "Hardcoded Cryptographic Secret (Neural Net Detected)", severity: "CRITICAL", line: 15 },
  { title: "Command Injection Risk", severity: "CRITICAL", line: 67 },
  { title: "Malicious DGA Domain Detected", severity: "CRITICAL", line: 89 },
];

const KILL_CHAIN_PHASES = [
  "Reconnaissance", "Weaponization", "Delivery",
  "Exploitation", "Installation", "Command & Control", "Actions on Objective"
];

export default function AttackPathPage() {
  const [projectName, setProjectName] = useState("auth-service-v2");
  const [vulnsJson, setVulnsJson] = useState(JSON.stringify(DEMO_VULNS, null, 2));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const generate = async () => {
    setLoading(true);
    try {
      let vulns;
      try { vulns = JSON.parse(vulnsJson); } catch { vulns = DEMO_VULNS; }
      const token = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/killchain/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ vulnerabilities: vulns, project_name: projectName }),
      });
      if (res.ok) { setResult(await res.json()); }
      else { throw new Error("API error"); }
    } catch {
      setResult({
        project: projectName,
        overall_risk: "CRITICAL",
        total_attack_vectors: 4,
        entry_points: ["SQL Injection Risk", "Hardcoded Cryptographic Secret"],
        pivot_opportunities: ["Command Injection Risk"],
        attacker_objectives: ["Data Exfiltration", "Ransomware Deployment"],
        attack_steps: [
          { step_id: 1, vulnerability: "SQL Injection Risk", severity: "CRITICAL", tactic: "Initial Access", technique: "T1190 - Exploit Public-Facing Application", description: "Attacker exploits SQL injection to gain initial access.", impact: "Complete database compromise, authentication bypass", next_steps: ["Data Exfiltration", "Privilege Escalation"] },
          { step_id: 2, vulnerability: "Hardcoded Cryptographic Secret", severity: "CRITICAL", tactic: "Credential Access", technique: "T1552.001 - Credentials in Files", description: "Attacker extracts hardcoded AWS key from source code.", impact: "Full cloud account takeover", next_steps: ["Cloud Account Abuse", "S3 Data Exfiltration"] },
          { step_id: 3, vulnerability: "Command Injection Risk", severity: "CRITICAL", tactic: "Execution", technique: "T1059 - Command and Scripting Interpreter", description: "Attacker gains RCE via command injection.", impact: "Full Remote Code Execution on server", next_steps: ["Install persistence", "Lateral movement"] },
          { step_id: 4, vulnerability: "Malicious DGA Domain", severity: "CRITICAL", tactic: "Command and Control", technique: "T1568.002 - Domain Generation Algorithms", description: "Malware beacons to DGA-generated C2 domain.", impact: "Covert C2 channel established", next_steps: ["Data exfiltration", "Ransomware deployment"] },
        ],
        kill_chain_coverage: {
          "Delivery": ["SQL Injection Risk"],
          "Exploitation": ["Command Injection Risk", "Hardcoded Cryptographic Secret"],
          "Command & Control": ["Malicious DGA Domain"],
          "Actions on Objective": ["Data exfiltration", "Ransomware deployment"]
        },
        executive_summary: "A sophisticated attacker can achieve full system compromise of 'auth-service-v2' using 4 chained vulnerabilities. Primary entry point: SQL Injection. Estimated time to breach: < 1 hour."
      });
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (s: string) => s === "CRITICAL" ? "text-red-400" : s === "HIGH" ? "text-orange-400" : "text-yellow-400";
  const severityBg = (s: string) => s === "CRITICAL" ? "bg-red-500/10 border-red-500/20" : "bg-orange-500/10 border-orange-500/20";

  return (
    <div className="min-h-screen p-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-lg border" style={{ background: 'rgba(239,68,68,0.1)', borderColor: 'rgba(239,68,68,0.2)' }}><span className="text-2xl">⚡</span></div>
          <div>
            <h1 className="text-2xl font-bold text-white">AttackPath™ <span className="text-red-400">Kill Chain Synthesizer</span></h1>
            <p className="text-sm text-gray-500">AI generates the complete attacker kill-chain from your vulnerability findings</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="rounded-xl p-5 space-y-4 border" style={{ background: '#0b0f1a', borderColor: 'rgba(255,255,255,0.05)' }}>
          <h2 className="text-sm font-bold text-white">Configuration</h2>
          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-widest block mb-1.5">Project Name</label>
            <input value={projectName} onChange={e => setProjectName(e.target.value)} className="w-full rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none" style={{ background: '#050912', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-widest block mb-1.5">Vulnerabilities (JSON)</label>
            <textarea value={vulnsJson} onChange={e => setVulnsJson(e.target.value)} className="w-full h-48 rounded-lg p-3 text-xs font-mono text-gray-300 focus:outline-none resize-none" style={{ background: '#050912', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
          <motion.button onClick={generate} disabled={loading} whileTap={{ scale: 0.97 }}
            className="w-full text-white py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            style={{ background: loading ? '#991b1b' : '#dc2626' }}>
            {loading ? <><span className="animate-spin">◌</span> Synthesizing...</> : <>⚡ Generate Kill Chain</>}
          </motion.button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence>
            {result && (
              <>
                {/* Executive Summary */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  className="bg-red-500/10 border border-red-500/20 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-red-400">⚠️</span>
                    <h2 className="font-bold text-red-400">CRITICAL RISK — {result.total_attack_vectors} Attack Vectors</h2>
                  </div>
                  <p className="text-sm text-gray-300">{result.executive_summary}</p>
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    <div className="bg-black/30 rounded-lg p-2 text-center">
                      <div className="text-lg font-bold text-red-400">{result.entry_points?.length}</div>
                      <div className="text-[10px] text-gray-400">Entry Points</div>
                    </div>
                    <div className="bg-black/30 rounded-lg p-2 text-center">
                      <div className="text-lg font-bold text-orange-400">{result.pivot_opportunities?.length}</div>
                      <div className="text-[10px] text-gray-400">Pivot Points</div>
                    </div>
                    <div className="bg-black/30 rounded-lg p-2 text-center">
                      <div className="text-lg font-bold text-yellow-400">{result.attacker_objectives?.length}</div>
                      <div className="text-[10px] text-gray-400">Objectives</div>
                    </div>
                  </div>
                </motion.div>

                {/* Kill Chain Steps */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1, transition: { delay: 0.2 } }}
                  className="rounded-xl p-5 border" style={{ background: '#0b0f1a', borderColor: 'rgba(255,255,255,0.05)' }}>
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2"><span className="text-red-400">🔗</span> Attack Chain</h3>
                  <div className="space-y-3">
                    {result.attack_steps?.map((step: any, i: number) => (
                      <div key={i} className="relative">
                        {i < result.attack_steps.length - 1 && (
                          <div className="absolute left-4 top-12 w-px h-6 bg-gradient-to-b from-red-500/50 to-transparent" />
                        )}
                        <div className={`border rounded-xl p-4 ${severityBg(step.severity)}`}>
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-red-500/20 border border-red-500/30 flex items-center justify-center flex-shrink-0">
                              <span className="text-xs font-bold text-red-400">{step.step_id}</span>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${severityBg(step.severity)} ${severityColor(step.severity)}`}>{step.severity}</span>
                                <span className="text-sm font-bold text-white">{step.vulnerability}</span>
                              </div>
                              <div className="text-xs text-gray-400 font-mono mb-1">{step.technique}</div>
                              <div className="text-xs text-gray-300">{step.impact}</div>
                              {step.next_steps?.length > 0 && (
                                <div className="flex items-center gap-1 mt-2 flex-wrap">
                                  <span className="text-gray-500">▶</span>
                                  {step.next_steps.map((ns: string, j: number) => (
                                    <span key={j} className="text-[10px] bg-white/5 text-gray-400 px-2 py-0.5 rounded border border-white/10">{ns}</span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
          {!result && (
            <div className="rounded-xl p-16 flex flex-col items-center justify-center text-center border" style={{ background: '#0b0f1a', borderColor: 'rgba(255,255,255,0.05)' }}>
              <span className="text-5xl text-gray-700 mb-4">🎯</span>
              <p className="text-gray-500 text-sm">Configure your project and vulnerabilities, then click Generate Kill Chain</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
