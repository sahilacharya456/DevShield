"use client";
import { useState } from "react";
import { motion } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RedAgentResult = {
  status: string;
  status_detail?: string;
  target: string;
  authorization_confirmed: boolean;
  attack_plan: Array<{ step: number; tool: string; description: string }>;
  open_ports: number[];
  executed_steps: unknown[];
};

export default function RedAgentPage() {
  const [target, setTarget] = useState("127.0.0.1");
  const [authorized, setAuthorized] = useState(false);
  const [executeTools, setExecuteTools] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RedAgentResult | null>(null);
  const [error, setError] = useState("");

  const runTest = async () => {
    if (!target.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/v1/redteam/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target,
          options: {
            authorization_confirmed: authorized,
            execute_tools: executeTools,
            intensity: "safe",
          },
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "RedAgent run failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <h1 className="text-2xl font-bold text-white mb-2">RedAgent</h1>
      <p className="text-gray-400 mb-6">Authorized reconnaissance orchestrator with bounded execution controls</p>

      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5 mb-6">
        <input value={target} onChange={e => setTarget(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white mb-4 focus:outline-none" placeholder="Target host or URL" />
        <div className="flex flex-wrap gap-4 mb-4 text-sm text-gray-300">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={authorized} onChange={e => setAuthorized(e.target.checked)} />
            I confirm authorization
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={executeTools} onChange={e => setExecuteTools(e.target.checked)} disabled={!authorized} />
            Run installed recon tools
          </label>
        </div>
        <button onClick={runTest} disabled={loading} className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
          {loading ? "Running..." : "Execute"}
        </button>
      </div>

      {error && <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-sm text-red-300">{error}</div>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-white">{result.authorization_confirmed ? "Authorized" : "Plan Only"}</div>
              <div className="text-xs text-gray-400">Mode</div>
            </div>
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-blue-400">{result.open_ports?.length ?? 0}</div>
              <div className="text-xs text-gray-400">Open Ports</div>
            </div>
            <div className="bg-[#050912] border border-white/5 rounded-lg p-3">
              <div className="text-lg font-bold text-purple-400">{result.executed_steps?.length ?? 0}</div>
              <div className="text-xs text-gray-400">Tool Steps</div>
            </div>
          </div>
          {result.status_detail && <p className="text-sm text-gray-400 mb-4">{result.status_detail}</p>}
          <pre className="text-xs text-green-400 font-mono overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
        </motion.div>
      )}
    </div>
  );
}
