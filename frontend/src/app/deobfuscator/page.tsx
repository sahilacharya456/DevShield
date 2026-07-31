"use client";
import { useState } from "react";
import { motion } from "framer-motion";

export default function MalwareForgePage() {
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runTest = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/v1/deobfuscator/run", {
        method: "POST", headers: {"Content-Type": "application/json", "Authorization": `Bearer ${token}`}, body: JSON.stringify({target})
      });
      setResult(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <h1 className="text-2xl font-bold text-white mb-2">MalwareForge</h1>
      <p className="text-gray-400 mb-6">Neural AST-based code deobfuscation</p>
      
      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5 mb-6">
        <input value={target} onChange={e => setTarget(e.target.value)} className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white mb-4 focus:outline-none" placeholder="Target..." />
        <button onClick={runTest} disabled={loading} className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors">
          {loading ? "Running..." : "Execute"}
        </button>
      </div>
      
      {result && (
        <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-5">
          <pre className="text-xs text-green-400 font-mono">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
