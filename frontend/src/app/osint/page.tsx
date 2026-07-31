"use client";
import { useState } from "react";
import { motion } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type OsintResult = {
  status: string;
  target: string;
  mode: string;
  surface_risk_score: number;
  open_ports: number[];
  nvd_cves: unknown[];
  shodan: unknown[];
  virustotal?: unknown;
};

export default function OsintRadarPage() {
  const [target, setTarget] = useState("example.com");
  const [cveKeyword, setCveKeyword] = useState("nginx");
  const [activeProbe, setActiveProbe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OsintResult | null>(null);
  const [error, setError] = useState("");

  const runTest = async () => {
    if (!target.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/v1/osint/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, options: { active_probe: activeProbe, cve_keyword: cveKeyword } }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "OSINT lookup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <h1 className="text-2xl font-bold text-white mb-2">OsintRadar</h1>
      <p className="text-gray-400 mb-6">Passive attack surface mapping with optional live enrichment</p>

      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
          <input value={target} onChange={e => setTarget(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none" placeholder="Domain, host, or IP" />
          <input value={cveKeyword} onChange={e => setCveKeyword(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none" placeholder="NVD CVE keyword" />
        </div>
        <label className="flex items-center gap-2 text-sm text-gray-300 mb-4">
          <input type="checkbox" checked={activeProbe} onChange={e => setActiveProbe(e.target.checked)} />
          Enable bounded active port probe
        </label>
        <button onClick={runTest} disabled={loading} className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
          {loading ? "Running..." : "Execute"}
        </button>
      </div>

      {error && <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-sm text-red-300">{error}</div>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-5">
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-white">{result.mode}</div>
              <div className="text-xs text-gray-400">Mode</div>
            </div>
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-red-400">{result.surface_risk_score}</div>
              <div className="text-xs text-gray-400">Risk</div>
            </div>
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-blue-400">{result.nvd_cves?.length ?? 0}</div>
              <div className="text-xs text-gray-400">NVD CVEs</div>
            </div>
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-purple-400">{result.open_ports?.length ?? 0}</div>
              <div className="text-xs text-gray-400">Open Ports</div>
            </div>
          </div>
          <pre className="text-xs text-green-400 font-mono overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
        </motion.div>
      )}
    </div>
  );
}
