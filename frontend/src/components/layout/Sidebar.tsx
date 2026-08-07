"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { InfinityLogo } from "@/components/ui/InfinityLogo";
import { X } from "lucide-react";

const NAV_SECTIONS = [
  {
    title: "Core",
    items: [{ href: "/dashboard", icon: "📊", label: "Command Center" }],
  },
  {
    title: "Scanners",
    items: [
      { href: "/projects", icon: "📦", label: "Repositories" },
      { href: "/secrets", icon: "🔑", label: "Secret Leaks" },
      { href: "/scanners/docker", icon: "🐳", label: "Docker Security" },
      { href: "/scanners/api", icon: "🌐", label: "API Security" },
    ],
  },
  {
    title: "AI Intelligence",
    items: [
      { href: "/cognitive", icon: "🧬", label: "CognitiveDNA™", badge: "NEW" },
      { href: "/attack-path", icon: "⚡", label: "AttackPath™", badge: "NEW" },
      { href: "/quantum", icon: "🔮", label: "QuantumVault™", badge: "NEW" },
      { href: "/prompt-lab", icon: "🎭", label: "PromptShield™", badge: "NEW" },
      { href: "/osint", icon: "🔭", label: "OsintRadar™", badge: "NEW" },
    ],
  },
  {
    title: "Arsenal",
    items: [{ href: "/arsenal", icon: "🗡️", label: "Kali Tool Hub", badge: "HOT" }],
  },
  {
    title: "AI Studios",
    items: [
      { href: "/studio", icon: "🔧", label: "Auto-Fix Studio" },
      { href: "/threat-model", icon: "🎯", label: "Threat Model" },
      { href: "/soc-assistant", icon: "🤖", label: "SOC Copilot" },
      { href: "/deobfuscator", icon: "🧩", label: "MalwareForge™", badge: "NEW" },
      { href: "/red-team", icon: "🔴", label: "RedAgent™", badge: "NEW" },
      { href: "/antivirus", icon: "🛡️", label: "Aegis Antivirus™", badge: "NEW" },
    ],
  },
  {
    title: "Threat Intel",
    items: [
      { href: "/live-threat-map", icon: "🌍", label: "Live Threat Map" },
      { href: "/supply-chain", icon: "🕸️", label: "ChainBreaker™", badge: "NEW" },
      { href: "/phantom", icon: "👻", label: "PhantomScan™", badge: "NEW" },
    ],
  },
  {
    title: "Platform",
    items: [
      { href: "/users", icon: "👥", label: "Users & Access" },
      { href: "/compliance", icon: "📋", label: "Compliance" },
      { href: "/reports", icon: "📑", label: "Reports Center" },
      { href: "/billing", icon: "💳", label: "Billing & Pro" },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden"
          onClick={onClose}
        />
      )}

      <div
        className={[
          "w-64 border-r border-ds-border bg-ds-charcoal/60 backdrop-blur-xl flex flex-col h-screen sticky top-0 overflow-hidden z-40 transition-transform duration-300",
          "fixed md:relative",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        ].join(" ")}
      >
        {/* Logo */}
        <div className="p-5 border-b border-ds-border/50 flex-shrink-0 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <InfinityLogo className="w-10 h-10" />
            <div>
              <h1 className="font-bold text-sm leading-tight tracking-tight text-white">DevShield</h1>
              <p className="text-[10px] text-blue-400 font-semibold uppercase tracking-widest">AI X v2.0</p>
            </div>
          </div>
          {/* Close button on mobile */}
          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/5 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin scrollbar-thumb-white/10">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title} className="mb-4">
              <div className="text-[10px] font-bold text-gray-600 uppercase tracking-widest px-2 mb-1.5">
                {section.title}
              </div>
              {section.items.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/" && pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onClose}
                    className={[
                      "flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 relative",
                      isActive
                        ? "bg-blue-600/20 text-white border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                        : "text-gray-400 hover:text-white hover:bg-white/5 border border-transparent",
                    ].join(" ")}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-blue-500 rounded-full" />
                    )}
                    <span className="text-base leading-none">{item.icon}</span>
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span
                        className={[
                          "text-[9px] font-bold px-1.5 py-0.5 rounded-full border",
                          item.badge === "NEW"
                            ? "bg-blue-500/20 text-blue-400 border-blue-500/20"
                            : item.badge === "HOT"
                            ? "bg-red-500/20 text-red-400 border-red-500/20"
                            : "",
                        ].join(" ")}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-ds-border/50 flex-shrink-0 space-y-1">
          <Link
            href="/settings"
            onClick={onClose}
            className={[
              "flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all",
              pathname === "/settings"
                ? "bg-blue-600/20 text-white"
                : "text-gray-400 hover:text-white hover:bg-white/5",
            ].join(" ")}
          >
            <span>⚙️</span>
            <span>Settings</span>
          </Link>
          <div className="flex items-center gap-2 px-2.5 py-2">
            <div
              className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"
              style={{ boxShadow: "0 0 6px #22c55e" }}
            />
            <span className="text-[10px] text-gray-500 font-mono">All 15 Engines Active</span>
          </div>
        </div>
      </div>
    </>
  );
}
