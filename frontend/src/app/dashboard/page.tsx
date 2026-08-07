"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Shield, Activity, Lock, AlertTriangle, Zap, Server, ChevronRight, CheckCircle, Package, Fingerprint } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FADE_UP: any = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchDashboard = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setLoading(false);
        router.push("/auth");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/api/v1/dashboard/metrics`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (res.status === 401) {
          localStorage.removeItem("access_token");
          setLoading(false);
          router.push("/auth");
          return;
        }

        if (res.ok) {
          setStats(await res.json());
        }
      } catch (err) {
        console.error("Dashboard fetch failed", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        <div className="w-12 h-12 rounded-full border-4 border-ds-accent-blue/30 border-t-ds-accent-blue animate-spin" />
      </div>
    );
  }

  return (
    <motion.div 
      initial="hidden" 
      animate="show" 
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="p-8 pb-20 max-w-7xl mx-auto"
    >
      <motion.header variants={FADE_UP} className="mb-10 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Shield className="w-10 h-10 text-ds-accent-blue" />
            Command Center
          </h1>
          <p className="text-ds-text-secondary mt-2 text-lg">DevShield AI X // Global Security Overview</p>
        </div>
        <div className="flex gap-3">
          <div className="glass-panel px-4 py-2 rounded-xl flex items-center gap-3 border border-ds-success/20">
            <div className="w-2.5 h-2.5 rounded-full bg-ds-success animate-pulse shadow-[0_0_12px_#10b981]" />
            <span className="text-sm font-mono text-ds-success font-semibold tracking-wider">SYSTEM ONLINE</span>
          </div>
        </div>
      </motion.header>

      {/* Dynamic Stats Grid */}
      <motion.div variants={FADE_UP} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {stats?.metrics?.map((metric: any, i: number) => {
          const colorMap: any = {
            blue: "from-blue-600/20 to-blue-900/10 border-blue-500/20 text-blue-400",
            danger: "from-red-600/20 to-red-900/10 border-red-500/20 text-red-400",
            success: "from-emerald-600/20 to-emerald-900/10 border-emerald-500/20 text-emerald-400",
            indigo: "from-indigo-600/20 to-indigo-900/10 border-indigo-500/20 text-indigo-400"
          };
          const style = colorMap[metric.color] || colorMap.blue;
          
          return (
            <motion.div 
              key={i}
              whileHover={{ y: -5, scale: 1.02 }}
              className={`bg-gradient-to-br ${style.split(' ')[0]} ${style.split(' ')[1]} border ${style.split(' ')[2]} p-6 rounded-2xl relative overflow-hidden group glass-panel`}
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 blur-[50px] group-hover:bg-white/10 transition-all" />
              <div className="flex justify-between items-start mb-4 relative z-10">
                <div className={`p-3 rounded-xl bg-black/40 border border-white/5`}>
                  <span className="text-2xl">{metric.icon}</span>
                </div>
                {metric.trend && (
                  <span className="text-xs font-bold px-2.5 py-1 bg-black/40 rounded-full border border-white/10">
                    {metric.trend}
                  </span>
                )}
              </div>
              <div className="text-5xl font-black text-white mb-2 relative z-10 tracking-tight">{metric.value}</div>
              <div className={`text-sm font-semibold uppercase tracking-wider ${style.split(' ')[3]} relative z-10`}>
                {metric.title}
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Module Quick Access */}
        <motion.div variants={FADE_UP} className="glass-panel border border-ds-border rounded-3xl p-8 relative overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-ds-accent-blue/10 blur-[100px] rounded-full" />
          <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
            <Zap className="w-6 h-6 text-yellow-400" /> Rapid Access Modules
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 relative z-10">
            {[
              { name: "Arsenal", path: "/arsenal", icon: "🗡️", color: "bg-red-500/10 text-red-400 border-red-500/20" },
              { name: "QuantumVault", path: "/quantum", icon: "🔮", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
              { name: "CognitiveDNA", path: "/cognitive", icon: "🧬", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
              { name: "AttackPath", path: "/attack-path", icon: "⚡", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
              { name: "Threat Map", path: "/live-threat-map", icon: "🌍", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
              { name: "Auto-Fix Studio", path: "/studio/autofix", icon: "🔧", color: "bg-teal-500/10 text-teal-400 border-teal-500/20" },
            ].map(mod => (
              <Link href={mod.path} key={mod.name}>
                <motion.div 
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-5 rounded-2xl border border-white/5 bg-black/40 hover:bg-white/10 transition-colors group flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 flex items-center justify-center rounded-xl border ${mod.color} shadow-inner`}>
                      <span className="text-xl">{mod.icon}</span>
                    </div>
                    <span className="font-bold text-gray-200 group-hover:text-white text-lg">{mod.name}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
                </motion.div>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* System Activity (Dynamic SOC Alerts) */}
        <motion.div variants={FADE_UP} className="glass-panel border border-ds-border rounded-3xl p-8 relative overflow-hidden">
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-ds-critical/10 blur-[100px] rounded-full" />
          <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3 relative z-10">
            <Activity className="w-6 h-6 text-ds-critical" /> Live SOC Activity
          </h2>
          <div className="space-y-4 relative z-10">
            {stats?.soc_alerts?.length > 0 ? stats.soc_alerts.map((alert: any, i: number) => (
              <motion.div 
                key={i} 
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-4 p-4 rounded-xl bg-black/30 border border-white/5 hover:border-white/10 transition-colors"
              >
                <div className="mt-1">
                  <div className={`w-2.5 h-2.5 rounded-full ${alert.severity === 'danger' ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-yellow-500 shadow-[0_0_10px_#f59e0b]'}`} />
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-semibold ${alert.severity === 'danger' ? 'text-red-400' : 'text-yellow-400'}`}>{alert.title}</p>
                  <div className="flex items-center gap-2 mt-2 text-xs text-gray-500 font-mono bg-black/50 p-2 rounded-lg border border-white/5">
                    <Fingerprint className="w-3 h-3" />
                    {alert.location}
                  </div>
                </div>
              </motion.div>
            )) : (
              <div className="p-8 text-center text-gray-500 flex flex-col items-center gap-4">
                <CheckCircle className="w-12 h-12 text-ds-success/50" />
                <p>No active critical alerts. System is secure.</p>
              </div>
            )}

            {/* Fallback to Recent Scans if not many alerts */}
            {stats?.recent_scans?.length > 0 && (
              <div className="pt-6 mt-6 border-t border-white/10">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Recent Scans</h3>
                {stats.recent_scans.map((scan: any, i: number) => (
                  <div key={i} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0">
                    <div className="flex items-center gap-3">
                      <Package className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-200 font-medium">{scan.name}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-gray-500">{scan.time}</span>
                      <span className={`text-xs font-bold px-2 py-1 rounded border ${scan.score >= 90 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : scan.score >= 70 ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                        Score: {scan.score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
