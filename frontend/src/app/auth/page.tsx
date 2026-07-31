"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { Lock, Mail, Key } from "lucide-react";
import { useRouter } from "next/navigation";
import { InfinityLogo } from "@/components/ui/InfinityLogo";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [isForgot, setIsForgot] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isForgot) {
        // Reset Password
        const res = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, new_password: newPassword }),
        });
        
        if (!res.ok) throw new Error("Email not found or reset failed");
        
        setIsForgot(false);
        setIsLogin(true);
        setPassword("");
        setNewPassword("");
        setError("Password reset successfully! Please log in.");
      } else if (isLogin) {
        // OAuth2 Password Request
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const res = await fetch(`${API_URL}/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData.toString(),
        });

        if (!res.ok) throw new Error("Invalid credentials");
        
        const data = await res.json();
        localStorage.setItem("access_token", data.access_token);
        router.push("/dashboard");
      } else {
        // Register
        const res = await fetch(`${API_URL}/api/v1/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: email.split('@')[0], email, password }),
        });

        if (!res.ok) throw new Error("Registration failed. Email may exist.");
        
        // Auto-login after register
        setIsLogin(true);
        setError("Registration successful! Please log in.");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#050505] relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-[20%] left-[30%] w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[20%] right-[30%] w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 relative z-10 shadow-2xl"
      >
        <div className="flex flex-col items-center mb-8">
          <InfinityLogo className="w-16 h-16 mb-4" />
          <h1 className="text-2xl font-bold text-white tracking-tight">DevShield AI X</h1>
          <p className="text-sm text-gray-500 mt-1">{isForgot ? "Recover Master Access" : isLogin ? "Sign in to Command Center" : "Create your Security Profile"}</p>
        </div>

        {error && (
          <div className={`p-3 rounded-lg mb-6 text-sm font-medium ${error.includes("successful") ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Email Address</label>
            <div className="relative">
              <Mail className="w-5 h-5 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="email" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
                placeholder="commander@devshield.ai"
              />
            </div>
          </div>

          {!isForgot && (
            <div>
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Master Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                  type="password" 
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
                  placeholder="••••••••••••"
                />
              </div>
            </div>
          )}

          {isForgot && (
            <div>
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">New Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                  type="password" 
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  required
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
                  placeholder="Enter new password"
                />
              </div>
            </div>
          )}

          {!isForgot && isLogin && (
            <div className="flex justify-end mt-1">
              <button 
                type="button" 
                onClick={() => { setIsForgot(true); setError(""); }} 
                className="text-xs text-blue-500 hover:text-blue-400 transition-colors"
              >
                Forgot Password?
              </button>
            </div>
          )}

          <motion.button 
            whileTap={{ scale: 0.98 }}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3.5 rounded-lg flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] disabled:opacity-50"
          >
            {loading ? <span className="animate-spin">◌</span> : <Key className="w-5 h-5" />}
            {loading ? "Processing..." : isForgot ? "Reset Master Password" : isLogin ? "Initialize Session" : "Deploy DevShield Account"}
          </motion.button>
        </form>

        <div className="mt-6 text-center">
          {isForgot ? (
            <button 
              type="button"
              onClick={() => { setIsForgot(false); setError(""); }}
              className="text-sm text-gray-500 hover:text-white transition-colors"
            >
              Back to Login
            </button>
          ) : (
            <button 
              type="button"
              onClick={() => { setIsLogin(!isLogin); setError(""); }}
              className="text-sm text-gray-500 hover:text-white transition-colors"
            >
              {isLogin ? "Need access? Request deployment." : "Already deployed? Initialize session."}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}
