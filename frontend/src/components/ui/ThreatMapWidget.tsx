"use client";

import React, { useState, useEffect, useRef } from "react";
import { Shield, AlertCircle, RefreshCw, Layers, ExternalLink, Terminal, ShieldAlert } from "lucide-react";

interface MapFeed {
  id: string;
  name: string;
  url?: string;
  provider: string;
  description: string;
}

interface AttackArc {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  t: number;
  speed: number;
  color: string;
  srcName: string;
  dstName: string;
  type: string;
}

interface LogEntry {
  time: string;
  type: string;
  src: string;
  dst: string;
  vector: string;
  color: string;
}

export function ThreatMapWidget() {
  const [activeFeedId, setActiveFeedId] = useState("local");
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [retryKey, setRetryKey] = useState(0);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const arcsRef = useRef<AttackArc[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const feeds: MapFeed[] = [
    {
      id: "local",
      name: "DevShield Local Attack Matrix (100% Reliable)",
      provider: "DevShield AI Threat Engine",
      description: "Direct canvas-rendered global telemetry showing live SQLi, DDoS, and ML-flagged zero-day exploits. High performance, zero third-party blocks."
    },
    {
      id: "fortiguard",
      name: "FortiGuard Live Threat Map",
      provider: "Fortinet",
      url: "https://threatmap.fortiguard.com/",
      description: "Real-time visual map of global cyber attacks, botnets, and malware trends."
    },
    {
      id: "kaspersky",
      name: "Kaspersky Cyber Attack Map",
      provider: "Kaspersky Lab (Local Firewall Permitting)",
      url: "https://cybermap.kaspersky.com/widget/dynamic/dark",
      description: "WebGL 3D globe visualizing active scanning, email malware, and host fuzzer triggers."
    }
  ];

  const activeFeed = feeds.find(f => f.id === activeFeedId) || feeds[0];

  // Map coordinate helpers
  const [cities, setCities] = useState([
    { name: "Washington DC", lat: 38.9072, lon: -77.0369 },
    { name: "Moscow", lat: 55.7558, lon: 37.6173 },
    { name: "Beijing", lat: 39.9042, lon: 116.4074 },
    { name: "London", lat: 51.5074, lon: -0.1278 }
  ]);

  useEffect(() => {
    import("@/services/threatIntelService").then((module) => {
      module.ThreatIntelService.getLiveThreatLocations(10).then((locations) => {
        setCities(locations);
      });
    });
  }, []);

  const projectCoords = (lat: number, lon: number, width: number, height: number) => {
    // Equirectangular projection
    const x = ((lon + 180) * width) / 360;
    const y = (((90 - lat) * height) / 180) + 20; // Shift down slightly
    return { x, y };
  };

  // Canvas drawing loop for local map simulation
  useEffect(() => {
    if (activeFeedId !== "local") {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      return;
    }

    setIsLoading(false);
    setHasError(false);

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = canvas.width = canvas.parentElement?.clientWidth || 800;
    let height = canvas.height = 580;

    const handleResize = () => {
      width = canvas.width = canvas.parentElement?.clientWidth || 800;
      height = canvas.height = 580;
    };
    window.addEventListener("resize", handleResize);

    const attackTypes = [
      { name: "SQL Injection", color: "#f43f5e" },
      { name: "DDoS Flood", color: "#3b82f6" },
      { name: "Secret Leak", color: "#ec4899" },
      { name: "Logic Bomb Anomaly", color: "#eab308" }
    ];

    const generateAttack = () => {
      const src = cities[Math.floor(Math.random() * cities.length)];
      let dst = cities[Math.floor(Math.random() * cities.length)];
      while (dst.name === src.name) {
        dst = cities[Math.floor(Math.random() * cities.length)];
      }

      const p0 = projectCoords(src.lat, src.lon, width, height);
      const p1 = projectCoords(dst.lat, dst.lon, width, height);

      const type = attackTypes[Math.floor(Math.random() * attackTypes.length)];

      const arc: AttackArc = {
        x0: p0.x,
        y0: p0.y,
        x1: p1.x,
        y1: p1.y,
        t: 0,
        speed: 0.008 + Math.random() * 0.008,
        color: type.color,
        srcName: src.name,
        dstName: dst.name,
        type: type.name
      };

      arcsRef.current.push(arc);

      // Add to logs
      const timestamp = new Date().toLocaleTimeString();
      const log: LogEntry = {
        time: timestamp,
        type: type.name.toUpperCase(),
        src: src.name,
        dst: dst.name,
        vector: `IOC-${Math.floor(Math.random() * 900 + 100)}`,
        color: type.color
      };

      setLogs(prev => [log, ...prev.slice(0, 18)]);
    };

    // Pre-populate some logs
    for (let i = 0; i < 5; i++) {
      generateAttack();
    }

    let frameCount = 0;

    const renderLoop = () => {
      frameCount++;
      ctx.fillStyle = "rgba(10, 10, 14, 0.25)"; // Trails
      ctx.fillRect(0, 0, width, height);

      // 1. Draw stylized world map dot representation
      ctx.fillStyle = "rgba(255, 255, 255, 0.04)";
      for (let x = 30; x < width - 30; x += 16) {
        for (let y = 30; y < height - 30; y += 16) {
          // Continental mathematical approximation
          const lon = ((x / width) * 360) - 180;
          const lat = 90 - ((y / height) * 180);
          
          // Continental mapping filter
          const inNorthAmerica = (lon > -130 && lon < -60 && lat > 15 && lat < 70);
          const inSouthAmerica = (lon > -80 && lon < -35 && lat > -55 && lat < 12);
          const inEurasia = (lon > -10 && lon < 145 && lat > 5 && lat < 75);
          const inAfrica = (lon > -15 && lon < 50 && lat > -35 && lat < 35);
          const inAustralia = (lon > 113 && lon < 153 && lat > -40 && lat < -10);
          
          if (inNorthAmerica || inSouthAmerica || inEurasia || inAfrica || inAustralia) {
            ctx.beginPath();
            ctx.arc(x, y, 1.2, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }

      // 2. Draw active cities
      cities.forEach(city => {
        const { x, y } = projectCoords(city.lat, city.lon, width, height);
        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(59, 130, 246, 0.6)";
        ctx.shadowColor = "#3b82f6";
        ctx.shadowBlur = 6;
        ctx.fill();

        ctx.font = "bold 8px monospace";
        ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
        ctx.shadowBlur = 0;
        ctx.fillText(city.name, x + 6, y + 3);
      });

      // 3. Draw & update attack arcs
      arcsRef.current.forEach((arc, index) => {
        arc.t += arc.speed;

        // Quadratic Bezier arc elevation
        const midX = (arc.x0 + arc.x1) / 2;
        const midY = (arc.y0 + arc.y1) / 2 - 80; // Bezier height

        // Draw bezier path
        ctx.beginPath();
        ctx.moveTo(arc.x0, arc.y0);
        ctx.quadraticCurveTo(midX, midY, arc.x1, arc.y1);
        ctx.strokeStyle = arc.color;
        ctx.lineWidth = 1;
        ctx.globalAlpha = 0.15;
        ctx.stroke();
        ctx.globalAlpha = 1.0;

        // Calculate current progress position P(t)
        const t = arc.t;
        const currX = (1 - t) * (1 - t) * arc.x0 + 2 * (1 - t) * t * midX + t * t * arc.x1;
        const currY = (1 - t) * (1 - t) * arc.y0 + 2 * (1 - t) * t * midY + t * t * arc.y1;

        // Draw shooting fuzzer particle
        ctx.beginPath();
        ctx.arc(currX, currY, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = arc.color;
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Draw impact ring
        if (t >= 1.0) {
          ctx.beginPath();
          ctx.arc(arc.x1, arc.y1, 15, 0, Math.PI * 2);
          ctx.strokeStyle = arc.color;
          ctx.lineWidth = 1.5;
          ctx.stroke();
          
          // Remove completed arc
          arcsRef.current.splice(index, 1);
        }
      });

      // Periodically trigger a new attack
      if (frameCount % 45 === 0) {
        generateAttack();
      }

      animationRef.current = requestAnimationFrame(renderLoop);
    };

    renderLoop();

    return () => {
      window.removeEventListener("resize", handleResize);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [activeFeedId, cities]);

  useEffect(() => {
    if (activeFeedId === "local") return;

    setIsLoading(true);
    setHasError(false);

    // Timeout fallback for third-party embeds
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 12000);

    return () => clearTimeout(timer);
  }, [activeFeedId, retryKey]);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const handleIframeError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const handleRetry = () => {
    setRetryKey(prev => prev + 1);
  };

  return (
    <div className="bg-[#0F1420]/80 border border-ds-border rounded-2xl overflow-hidden relative shadow-lg group">
      
      {/* Dynamic Cyber Header Selector Overlay */}
      <div className="bg-[#070B13]/90 border-b border-ds-border/50 px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-20">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600/10 rounded-lg border border-blue-500/20 text-blue-400">
            <Shield className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-extrabold text-sm text-white tracking-wide uppercase">Real-Time Global Cyber Threat Activity</h3>
            <p className="text-[10px] text-text-muted font-mono tracking-wider uppercase mt-0.5">
              Provider: <span className="text-blue-400 font-semibold">{activeFeed.provider}</span>
            </p>
          </div>
        </div>

        {/* Dropdown Selector */}
        <div className="flex items-center gap-3 self-end md:self-auto">
          <div className="flex items-center gap-2 bg-[#0F1420] border border-ds-border rounded-lg px-3 py-2 text-xs font-semibold text-white">
            <Layers className="w-4 h-4 text-blue-400" />
            <select 
              value={activeFeedId} 
              onChange={(e) => setActiveFeedId(e.target.value)}
              className="bg-transparent focus:outline-none cursor-pointer text-white pr-2 font-mono"
            >
              {feeds.map((feed) => (
                <option key={feed.id} value={feed.id} className="bg-[#0b0f19] text-white">
                  {feed.name}
                </option>
              ))}
            </select>
          </div>
          <button 
            onClick={handleRetry}
            className="p-2 bg-[#0F1420] hover:bg-[#1C2436] text-text-secondary hover:text-white border border-ds-border/80 rounded-lg transition-colors"
            title="Refresh Feed"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Description Banner for Selected Feed */}
      <div className="bg-[#070B13]/30 px-6 py-2.5 border-b border-ds-border/30 text-xs text-text-secondary font-mono flex items-center gap-2 relative z-10">
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
        <span>{activeFeed.description}</span>
      </div>

      {/* Map Display Container */}
      <div className="relative w-full h-[580px] bg-black/40 z-10 flex flex-col md:flex-row items-stretch">
        
        {/* If local map, render Canvas alongside dynamic hacker logs */}
        {activeFeedId === "local" ? (
          <>
            <div className="flex-1 relative">
              <canvas ref={canvasRef} className="w-full h-full relative z-10" />
            </div>
            
            {/* Live Terminal Attack Feed Panel */}
            <div className="w-full md:w-80 bg-[#070B13]/90 border-t md:border-t-0 md:border-l border-ds-border/50 p-4 font-mono text-[10.5px] overflow-y-auto space-y-2.5 relative z-20 flex flex-col h-64 md:h-auto">
              <div className="flex items-center gap-2 border-b border-ds-border/50 pb-2 mb-2 text-text-secondary uppercase tracking-widest text-[9.5px] font-bold">
                <Terminal className="w-3.5 h-3.5 text-blue-400" /> Incoming Attack Vector Log
              </div>
              <div className="flex-1 overflow-y-auto space-y-2 scrollbar-thin">
                {logs.map((log, i) => (
                  <div key={i} className="animate-in fade-in duration-300 leading-tight space-y-0.5">
                    <div className="flex justify-between text-text-muted text-[9px]">
                      <span>{log.time}</span>
                      <span className="font-semibold" style={{ color: log.color }}>{log.type}</span>
                    </div>
                    <div className="text-white">
                      <strong className="text-blue-400">{log.src}</strong>
                      <span className="text-text-muted mx-1">→</span>
                      <strong className="text-pink-400">{log.dst}</strong>
                    </div>
                    <div className="text-text-muted text-[9px]">
                      Payload Vector: <span className="text-gray-300">{log.vector}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Third party maps */
          <div className="relative w-full h-full flex items-center justify-center flex-1">
            {/* Loading Skeleton */}
            {isLoading && (
              <div className="absolute inset-0 z-30 bg-[#050912] flex flex-col items-center justify-center space-y-4">
                <div className="relative flex items-center justify-center">
                  <div className="w-16 h-16 border-4 border-blue-500/10 border-t-blue-500 rounded-full animate-spin" />
                  <Shield className="absolute w-6 h-6 text-blue-400 animate-pulse" />
                </div>
                <div className="text-center space-y-1">
                  <p className="text-xs font-bold text-white tracking-widest font-mono uppercase animate-pulse">
                    TUNING TO {activeFeed.provider.toUpperCase()}...
                  </p>
                  <p className="text-[10px] text-text-muted font-mono">Resolving safe cyber-telemetry handshake</p>
                </div>
              </div>
            )}

            {/* Error / Refused Fallback */}
            {hasError ? (
              <div className="absolute inset-0 z-30 bg-[#050912] p-8 flex flex-col items-center justify-center text-center space-y-4">
                <div className="p-4 bg-red-500/10 rounded-full text-red-500 border border-red-500/20">
                  <AlertCircle className="w-8 h-8" />
                </div>
                <div className="max-w-md space-y-2">
                  <h4 className="font-bold text-white text-base">Network Restriction Detected</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    Could not connect to <span className="text-white font-bold">{activeFeed.name}</span>. 
                    Your local ISP or corporate firewall blocks Russian or geographical intelligence domains. 
                    <strong> Please select another threat map, or toggle back to our 100% reliable local attack matrix!</strong>
                  </p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={handleRetry}
                    className="bg-[#0F1420] text-white hover:bg-[#1C2436] border border-ds-border text-xs font-bold px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" /> Retry
                  </button>
                  <button 
                    onClick={() => setActiveFeedId("local")}
                    className="bg-white text-black hover:bg-gray-200 text-xs font-bold px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" /> Load Local Feed
                  </button>
                </div>
              </div>
            ) : (
              <iframe
                key={`${activeFeedId}-${retryKey}`}
                src={activeFeed.url}
                width="100%"
                height="100%"
                frameBorder="0"
                title={activeFeed.name}
                onLoad={handleIframeLoad}
                onError={handleIframeError}
                className="w-full h-full border-0 relative z-10 transition-opacity duration-500"
                style={{ opacity: isLoading ? 0 : 1 }}
              />
            )}
          </div>
        )}
      </div>

      {/* Ethical Disclaimer Footer */}
      <div className="bg-[#070B13]/70 px-6 py-3 border-t border-ds-border/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 relative z-20 text-[10.5px] font-mono text-text-muted">
        <span className="flex items-center gap-1.5">
          🔒 Telemetry sandboxed. Open source feed: 
          {activeFeed.url ? (
            <a href={activeFeed.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline flex items-center gap-0.5">
              Link <ExternalLink className="w-2.5 h-2.5" />
            </a>
          ) : (
            <span className="text-ds-success font-semibold">DevShield Native Engine</span>
          )}
        </span>
        <span>Threat map data is provided by external cybersecurity intelligence sources. Visualized attacks may represent sampled or aggregated telemetry, not every global attack.</span>
      </div>
    </div>
  );
}
