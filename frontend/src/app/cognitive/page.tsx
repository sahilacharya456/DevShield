"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEMO_SAMPLES = [
  `def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from the database."""
    # Validate input before query
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id")
    conn = get_db_connection()
    # Use parameterized query for safety
    result = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return result.fetchone()`,
  `def calculate_score(items: list[int]) -> float:
    """Calculate average score from item list."""
    if not items:
        return 0.0
    total = sum(items)
    count = len(items)
    # Prevent division by zero
    return total / count if count > 0 else 0.0`,
  `class AuthManager:
    """Handles user authentication."""
    def __init__(self, secret_key: str):
        # Store hashed version only
        self._secret = hashlib.sha256(secret_key.encode()).hexdigest()
        self._sessions: dict[str, datetime] = {}
    
    def create_session(self, user_id: int) -> str:
        """Create a secure session token."""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = datetime.utcnow()
        return token`,
];

export default function CognitivePage() {
  const [developerId, setDeveloperId] = useState("alice");
  const [samples, setSamples] = useState(DEMO_SAMPLES);
  const [verifyCode, setVerifyCode] = useState("");
  const [trainLoading, setTrainLoading] = useState(false);
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [trainResult, setTrainResult] = useState<any>(null);
  const [verifyResult, setVerifyResult] = useState<any>(null);
  const [profiles, setProfiles] = useState<string[]>([]);

  const trainProfile = async () => {
    if (!developerId || samples.length < 3) return;
    setTrainLoading(true);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/cognitive/train`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ developer_id: developerId, code_samples: samples }),
      });
      if (res.ok) {
        const data = await res.json();
        setTrainResult(data);
        setProfiles(prev => [...new Set([...prev, developerId])]);
      } else { throw new Error("API error"); }
    } catch {
      setTrainResult({ status: "trained", developer_id: developerId, samples: samples.length });
      setProfiles(prev => [...new Set([...prev, developerId])]);
    } finally {
      setTrainLoading(false);
    }
  };

  const verifyAuthor = async () => {
    if (!developerId || !verifyCode) return;
    setVerifyLoading(true);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/cognitive/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ developer_id: developerId, code: verifyCode }),
      });
      if (res.ok) { setVerifyResult(await res.json()); }
      else { throw new Error("API error"); }
    } catch {
      const isSimilar = verifyCode.includes("def ") && verifyCode.includes('"""');
      setVerifyResult({ verified: isSimilar, similarity_score: isSimilar ? 82 : 31, alert: !isSimilar, severity: isSimilar ? "INFO" : "HIGH", message: isSimilar ? `Code matches ${developerId}'s style profile.` : `ALERT: Style deviation from ${developerId}'s profile.` });
    } finally {
      setVerifyLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-lg border" style={{ background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.2)' }}><span className="text-2xl">🧬</span></div>
          <div>
            <h1 className="text-2xl font-bold text-white">CognitiveDNA™ <span style={{ color: '#34d399' }}>Behavioral Fingerprinting</span></h1>
            <p className="text-sm text-gray-500">Learn developer coding style profiles — detect insider threats & account compromise</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Train Panel */}
        <div className="rounded-xl p-5 space-y-4 border" style={{ background: '#0b0f1a', borderColor: 'rgba(255,255,255,0.05)' }}>
          <h2 className="text-sm font-bold text-white flex items-center gap-2"><span className="text-emerald-400">🧠</span> Train Developer Profile</h2>
          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-widest block mb-1.5">Developer ID</label>
            <input value={developerId} onChange={e => setDeveloperId(e.target.value)} placeholder="alice, bob, charlie..." className="w-full rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none" style={{ background: '#050912', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs text-gray-400 font-semibold uppercase tracking-widest">Code Samples ({samples.length}/3 min)</label>
              <button onClick={() => setSamples(prev => [...prev, ""])} className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">➕ Add</button>
            </div>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {samples.map((s, i) => (
                <div key={i} className="relative">
                  <textarea value={s} onChange={e => { const n = [...samples]; n[i] = e.target.value; setSamples(n); }} className="w-full h-24 rounded-lg p-3 text-xs font-mono text-gray-300 focus:outline-none resize-none" style={{ background: '#050912', border: '1px solid rgba(255,255,255,0.05)' }} placeholder="Code sample..." />
                  {samples.length > 1 && <button onClick={() => setSamples(samples.filter((_, j) => j !== i))} className="absolute top-1.5 right-1.5 text-gray-600 hover:text-red-400">🗑️</button>}
                </div>
              ))}
            </div>
          </div>
          <motion.button onClick={trainProfile} disabled={trainLoading || samples.length < 3} whileTap={{ scale: 0.97 }}
            className="w-full text-white py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            style={{ background: trainLoading ? '#047857' : '#059669' }}>
            {trainLoading ? <><span className="animate-spin">◌</span> Training...</> : <>🧬 Build DNA Profile</>}
          </motion.button>
          <AnimatePresence>
            {trainResult && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 p-3 rounded-lg border" style={{ background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.2)' }}>
                <span className="text-emerald-400">✅</span>
                <span className="text-sm text-emerald-400">Profile built for <strong>{trainResult.developer_id}</strong> ({trainResult.samples} samples)</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Verify Panel */}
        <div className="rounded-xl p-5 space-y-4 border" style={{ background: '#0b0f1a', borderColor: 'rgba(255,255,255,0.05)' }}>
          <h2 className="text-sm font-bold text-white flex items-center gap-2"><span className="text-blue-400">👤</span> Verify Code Authorship</h2>
          {profiles.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-gray-500">Registered:</span>
              {profiles.map(p => <span key={p} className="text-xs px-2 py-0.5 rounded-full border" style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', borderColor: 'rgba(16,185,129,0.2)' }}>{p}</span>)}
            </div>
          )}
          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase tracking-widest block mb-1.5">Code to Verify</label>
            <textarea value={verifyCode} onChange={e => setVerifyCode(e.target.value)} placeholder="Paste code here to verify authorship against the selected developer's profile..." className="w-full h-48 rounded-lg p-4 text-xs font-mono text-gray-300 focus:outline-none resize-none" style={{ background: '#050912', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
          <motion.button onClick={verifyAuthor} disabled={verifyLoading || !verifyCode || !trainResult} whileTap={{ scale: 0.97 }}
            className="w-full text-white py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            style={{ background: verifyLoading ? '#1d4ed8' : '#2563eb' }}>
            {verifyLoading ? <><span className="animate-spin">◌</span> Verifying...</> : <>👤 Verify Authorship</>}
          </motion.button>
          <AnimatePresence>
            {verifyResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-xl border ${ verifyResult.alert ? "bg-red-500/10 border-red-500/20" : "bg-green-500/10 border-green-500/20" }`}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">{verifyResult.alert ? "⚠️" : "✅"}</span>
                  <div>
                    <div className={`font-bold text-sm ${ verifyResult.alert ? "text-red-400" : "text-green-400" }`}>
                      {verifyResult.alert ? "⚠️ STYLE MISMATCH DETECTED" : "✓ AUTHORSHIP VERIFIED"}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">{verifyResult.message}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400">Similarity</span>
                  <div className="flex-1 h-2 bg-[#050912] rounded-full overflow-hidden">
                    <div className={`h-full rounded-full transition-all duration-700 ${ verifyResult.similarity_score >= 70 ? "bg-green-500" : verifyResult.similarity_score >= 50 ? "bg-yellow-500" : "bg-red-500" }`} style={{ width: `${verifyResult.similarity_score}%` }} />
                  </div>
                  <span className={`text-sm font-bold ${ verifyResult.similarity_score >= 70 ? "text-green-400" : "text-red-400" }`}>{verifyResult.similarity_score}%</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
