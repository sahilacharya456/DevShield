"use client";
import { useState } from "react";
import { motion } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DEMO_MANIFEST = "requests==2.25.1\nDjango==3.1.4\n";

type SupplyChainResult = {
  status: string;
  analyzed_packages?: number;
  vulnerabilities_found?: number;
  findings?: unknown[];
};

export default function ChainBreakerPage() {
  const [target, setTarget] = useState("requests==2.25.1,Django==3.1.4");
  const [manifestName, setManifestName] = useState("requirements.txt");
  const [manifestContent, setManifestContent] = useState(DEMO_MANIFEST);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState("");
  const [result, setResult] = useState<SupplyChainResult | null>(null);
  const [error, setError] = useState("");

  const pollJob = async (id: string) => {
    for (let attempt = 0; attempt < 60; attempt += 1) {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/jobs/${id}`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) }
      });
      if (!res.ok) throw new Error(await res.text());

      const job = await res.json();
      if (job.status === "SUCCESS") {
        setResult(job.result);
        return;
      }
      if (job.status === "FAILURE") {
        throw new Error(job.error || "Supply-chain scan failed");
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    throw new Error("Supply-chain scan timed out");
  };

  const runQueuedScan = async () => {
    if (!manifestName.trim() || !manifestContent.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    setJobId("");
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/jobs/scans/supply-chain`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ manifest_name: manifestName, manifest_content: manifestContent }),
      });
      if (!res.ok) throw new Error(await res.text());
      const job = await res.json();
      setJobId(job.job_id);
      await pollJob(job.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Supply-chain scan failed");
    } finally {
      setLoading(false);
    }
  };

  const runSyncScan = async () => {
    if (!target.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    setJobId("");
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/supplychain/run`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ target }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Supply-chain scan failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <h1 className="text-2xl font-bold text-white mb-2">ChainBreaker</h1>
      <p className="text-gray-400 mb-6">Dependency vulnerability mapping with queued OSV-backed scans</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white mb-3">Manifest Scan</h2>
          <input value={manifestName} onChange={e => setManifestName(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white mb-3 focus:outline-none" placeholder="requirements.txt, package.json, or package-lock.json" />
          <textarea value={manifestContent} onChange={e => setManifestContent(e.target.value)} className="w-full h-48 bg-[#050912] border border-white/10 rounded-lg p-3 text-xs text-white font-mono mb-4 focus:outline-none resize-none" />
          <button onClick={runQueuedScan} disabled={loading} className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
            {loading ? "Scanning..." : "Run Queued Scan"}
          </button>
          {jobId && <div className="mt-3 text-xs text-gray-500 font-mono">Job {jobId}</div>}
        </div>

        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <h2 className="text-sm font-bold text-white mb-3">Quick Package Scan</h2>
          <input value={target} onChange={e => setTarget(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white mb-4 focus:outline-none" placeholder="requests==2.25.1,Django==3.1.4" />
          <button onClick={runSyncScan} disabled={loading} className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
            {loading ? "Running..." : "Run Sync Scan"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <div className="grid grid-cols-3 gap-3 mb-5">
            <div className="bg-[#050912] rounded-lg p-3 border border-white/5">
              <div className="text-xl font-bold text-white">{result.analyzed_packages ?? 0}</div>
              <div className="text-xs text-gray-400">Packages</div>
            </div>
            <div className="bg-[#050912] rounded-lg p-3 border border-white/5">
              <div className="text-xl font-bold text-red-400">{result.vulnerabilities_found ?? 0}</div>
              <div className="text-xs text-gray-400">Findings</div>
            </div>
            <div className="bg-[#050912] rounded-lg p-3 border border-white/5">
              <div className="text-xl font-bold text-blue-400">{result.status}</div>
              <div className="text-xs text-gray-400">Status</div>
            </div>
          </div>
          <pre className="text-xs text-green-400 font-mono overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
        </motion.div>
      )}
    </div>
  );
}
