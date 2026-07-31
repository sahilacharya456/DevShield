"use client";

import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Shield, Code, Zap, ChevronRight, Lock, Activity, Brain, Eye, Cpu } from "lucide-react";
import Link from "next/link";

// Animated Cyber Matrix/Particle Background
const CyberCanvas = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const particles: any[] = [];
    for (let i = 0; i < 120; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 1.2,
        vy: (Math.random() - 0.5) * 1.2,
        radius: Math.random() * 2 + 0.5,
      });
    }

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Subtle Grid
      ctx.strokeStyle = "rgba(59, 130, 246, 0.04)";
      ctx.lineWidth = 1;
      for (let i = 0; i < width; i += 60) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
      }
      for (let i = 0; i < height; i += 60) {
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(width, i); ctx.stroke();
      }

      // Particles & connections
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(59, 130, 246, 0.7)";
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 140) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(139, 92, 246, ${(1 - dist / 140) * 0.5})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

const FEATURES = [
  {
    icon: <Code className="w-7 h-7 text-blue-400" />,
    title: "Native SAST",
    desc: "Tree-sitter AST parsing tracks exact data flow from sources to dangerous sinks across 15+ languages.",
    color: "from-blue-600/20 to-blue-900/5",
    border: "border-blue-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(59,130,246,0.15)]",
  },
  {
    icon: <Brain className="w-7 h-7 text-purple-400" />,
    title: "Zero-Day ML",
    desc: "Scikit-Learn Isolation Forests automatically flag logic bombs, obfuscation, and DGA-encoded threats.",
    color: "from-purple-600/20 to-purple-900/5",
    border: "border-purple-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(139,92,246,0.15)]",
  },
  {
    icon: <Zap className="w-7 h-7 text-cyan-400" />,
    title: "FAISS RAG",
    desc: "SentenceTransformers encode past fixes into a vector store to guide the LLM's strict JSON patching.",
    color: "from-cyan-600/20 to-cyan-900/5",
    border: "border-cyan-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(6,182,212,0.15)]",
  },
  {
    icon: <Eye className="w-7 h-7 text-pink-400" />,
    title: "OsintRadar™",
    desc: "Real-time OSINT aggregation across 20+ sources: social media, paste sites, dark web monitors.",
    color: "from-pink-600/20 to-pink-900/5",
    border: "border-pink-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(236,72,153,0.15)]",
  },
  {
    icon: <Lock className="w-7 h-7 text-emerald-400" />,
    title: "QuantumVault™",
    desc: "Post-quantum cryptography analysis and secret neural network for credential entropy scoring.",
    color: "from-emerald-600/20 to-emerald-900/5",
    border: "border-emerald-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(16,185,129,0.15)]",
  },
  {
    icon: <Cpu className="w-7 h-7 text-orange-400" />,
    title: "RedAgent™",
    desc: "Autonomous AI red-teaming agent that continuously probes your attack surface 24/7.",
    color: "from-orange-600/20 to-orange-900/5",
    border: "border-orange-500/10",
    glow: "group-hover:shadow-[0_0_40px_rgba(251,146,60,0.15)]",
  },
];

const STATS = [
  { value: "15+", label: "AI Engines" },
  { value: "99.9%", label: "Uptime SLA" },
  { value: "0-day", label: "ML Detection" },
  { value: "SOC2", label: "Compliant" },
];

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 },
    },
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number] },
    },
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start p-8 pt-24 relative overflow-hidden bg-[#050505]">
      <CyberCanvas />

      {/* Global Glowing Orbs */}
      <div className="absolute top-[10%] left-[15%] w-[600px] h-[600px] rounded-full bg-blue-600/8 blur-[180px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[10%] w-[600px] h-[600px] rounded-full bg-purple-600/8 blur-[180px] pointer-events-none" />
      <div className="absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-cyan-600/5 blur-[150px] pointer-events-none" />

      <motion.div
        className="z-10 w-full max-w-6xl text-center relative"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Badge */}
        <motion.div variants={itemVariants} className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-xs font-bold text-gray-300 uppercase tracking-widest">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]" />
            AI X v2.0 — Now Live
          </div>
        </motion.div>

        {/* Logo Icon */}
        <motion.div variants={itemVariants} className="flex justify-center mb-8">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl blur-lg opacity-20 group-hover:opacity-40 transition duration-700" />
            <div className="relative p-6 rounded-3xl bg-black/60 border border-white/10 backdrop-blur-xl flex items-center justify-center shadow-2xl">
              <Shield className="w-20 h-20 text-blue-400 drop-shadow-[0_0_20px_rgba(96,165,250,0.9)]" />
            </div>
          </div>
        </motion.div>

        {/* Headline */}
        <motion.h1
          variants={itemVariants}
          className="text-6xl md:text-8xl lg:text-9xl font-extrabold mb-6 tracking-tighter leading-none"
        >
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-gray-400">
            DevShield
          </span>
          <span className="text-blue-500">.</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-pink-600">
            AI X
          </span>
        </motion.h1>

        {/* Tagline */}
        <motion.p
          variants={itemVariants}
          className="text-xl md:text-2xl text-gray-400 mb-6 max-w-3xl mx-auto font-light leading-relaxed"
        >
          The Next-Generation Enterprise Security Platform.{" "}
          Powered by <strong className="text-white">Isolation Forests</strong>,{" "}
          <strong className="text-white">DGA ML Detectors</strong>, and{" "}
          <strong className="text-white">True RAG Auto-Fixing</strong>.
        </motion.p>

        {/* Stats Bar */}
        <motion.div variants={itemVariants} className="flex items-center justify-center gap-8 mb-12 flex-wrap">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-black text-white">{stat.value}</div>
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-24"
        >
          <Link href="/dashboard">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className="group relative flex items-center gap-3 bg-white text-black px-8 py-4 rounded-full font-bold text-lg shadow-[0_0_30px_rgba(255,255,255,0.15)] hover:shadow-[0_0_50px_rgba(255,255,255,0.25)] transition-all"
            >
              Launch Platform
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </Link>
          <Link href="/threat-model">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-3 bg-transparent text-white border border-white/20 hover:border-white/50 hover:bg-white/5 px-8 py-4 rounded-full font-semibold text-lg transition-all"
            >
              <Activity className="w-5 h-5 text-purple-400" />
              View Threat Matrix
            </motion.button>
          </Link>
          <Link href="/auth">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-3 bg-transparent text-gray-400 hover:text-white border border-white/10 hover:border-white/30 px-8 py-4 rounded-full font-semibold text-lg transition-all"
            >
              Sign In →
            </motion.button>
          </Link>
        </motion.div>

        {/* Feature Grid */}
        <motion.div
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 text-left"
        >
          {FEATURES.map((feature, idx) => (
            <motion.div
              key={idx}
              variants={itemVariants}
              whileHover={{ y: -6, transition: { duration: 0.2 } }}
              className={`relative group rounded-2xl p-[1px] overflow-hidden bg-gradient-to-br ${feature.color} ${feature.glow} transition-shadow duration-500`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              <div className={`relative h-full bg-black/60 backdrop-blur-xl border ${feature.border} rounded-2xl p-7 hover:border-white/15 transition-colors`}>
                <div className="mb-5 p-3 rounded-xl bg-black/40 border border-white/5 inline-flex">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-white">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed text-sm">{feature.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div variants={itemVariants} className="mt-20 pb-20">
          <div className="glass-panel border border-white/10 rounded-3xl p-10 relative overflow-hidden">
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-blue-600/10 blur-[80px] rounded-full" />
            <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-purple-600/10 blur-[80px] rounded-full" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-black text-white mb-4 tracking-tight">
                Ready to Secure Your Pipeline?
              </h2>
              <p className="text-gray-400 mb-8 max-w-xl mx-auto">
                Join the next generation of DevSecOps. Deploy in minutes, secure in seconds.
              </p>
              <Link href="/auth">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.98 }}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-10 py-4 rounded-full font-bold text-lg transition-all shadow-[0_0_40px_rgba(59,130,246,0.4)] hover:shadow-[0_0_60px_rgba(59,130,246,0.6)]"
                >
                  Deploy DevShield for Free →
                </motion.button>
              </Link>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
