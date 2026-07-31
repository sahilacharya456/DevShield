"use client";

export function InfinityLogo({ className = "w-10 h-10" }: { className?: string }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Background Ambient Glow */}
      <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full mix-blend-screen" />
      
      <svg 
        viewBox="0 0 100 50" 
        className="w-full h-full overflow-visible drop-shadow-[0_0_15px_rgba(59,130,246,0.6)]"
      >
        <defs>
          <linearGradient id="infinityGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6">
              <animate attributeName="stop-color" values="#3b82f6;#8b5cf6;#0ea5e9;#3b82f6" dur="4s" repeatCount="indefinite" />
            </stop>
            <stop offset="50%" stopColor="#c084fc" />
            <stop offset="100%" stopColor="#ec4899">
              <animate attributeName="stop-color" values="#ec4899;#8b5cf6;#db2777;#ec4899" dur="4s" repeatCount="indefinite" />
            </stop>
          </linearGradient>
          <filter id="ultraGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        {/* Core Structure Track */}
        <path
          d="M 25 25 C 5 5, 5 45, 25 25 C 45 5, 55 5, 75 25 C 95 45, 95 5, 75 25 C 55 45, 45 45, 25 25"
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="6"
          strokeLinecap="round"
        />
        
        {/* Energy Pulse Line */}
        <path
          d="M 25 25 C 5 5, 5 45, 25 25 C 45 5, 55 5, 75 25 C 95 45, 95 5, 75 25 C 55 45, 45 45, 25 25"
          fill="none"
          stroke="url(#infinityGrad)"
          strokeWidth="4"
          strokeLinecap="round"
          filter="url(#ultraGlow)"
          strokeDasharray="180"
          strokeDashoffset="180"
        >
          <animate 
            attributeName="stroke-dashoffset" 
            values="360; 0" 
            dur="2.5s" 
            repeatCount="indefinite" 
          />
        </path>
        
        {/* Starlight Core Particle */}
        <circle cx="25" cy="25" r="1.5" fill="#fff" filter="url(#ultraGlow)">
          <animateMotion 
            dur="2.5s" 
            repeatCount="indefinite"
            path="M 0 0 C -20 -20, -20 20, 0 0 C 20 -20, 30 -20, 50 0 C 70 20, 70 -20, 50 0 C 30 20, 20 20, 0 0" 
          />
        </circle>
      </svg>
      
      {/* Central Singularity */}
      <div className="absolute inset-0 m-auto w-1 h-1 bg-white rounded-full shadow-[0_0_20px_5px_#fff] animate-ping opacity-50" />
    </div>
  );
}
