"use client";
import { useState, useEffect, useRef } from "react";
import { Search, Bell, ShieldAlert, ChevronDown, LogOut, Settings, CreditCard, Menu, AlertTriangle, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";

interface HeaderProps {
  onMenuToggle?: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const router = useRouter();

  const [searchFocused, setSearchFocused] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === "Escape") {
        setSearchFocused(false);
        setShowNotifications(false);
        setShowProfile(false);
        searchInputRef.current?.blur();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Outside click handler for dropdowns
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notificationsRef.current && !notificationsRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfile(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/auth");
  };

  return (
    <header className="h-16 border-b border-ds-border bg-[#0B0F19]/80 backdrop-blur-xl sticky top-0 z-50 flex items-center justify-between px-4 lg:px-8 shadow-sm">
      <div className="flex items-center gap-3 flex-1">
        {/* Mobile Menu Toggle */}
        <button
          onClick={onMenuToggle}
          className="md:hidden p-2 text-text-muted hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Status Indicator */}
        <div className="hidden md:flex items-center gap-3 bg-ds-navy border border-ds-border px-3 py-1.5 rounded-full">
          <div className="h-2 w-2 rounded-full bg-ds-success animate-pulse shadow-[0_0_8px_#10b981]"></div>
          <span className="text-xs font-semibold text-text-secondary tracking-wide uppercase">System Online</span>
        </div>

        {/* Global Search Bar */}
        <div className="relative max-w-md w-full hidden sm:block">
          <Search
            className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors ${
              searchFocused ? "text-blue-400" : "text-text-muted"
            }`}
          />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setTimeout(() => setSearchFocused(false), 200)}
            placeholder="Search vulnerabilities, projects, engines (Press '/')"
            className="w-full bg-[#111827]/50 border border-ds-border text-sm text-white placeholder-text-muted rounded-lg pl-10 pr-12 py-2 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 pointer-events-none">
            <kbd className="hidden lg:inline-block text-[10px] bg-ds-elevated border border-ds-border px-1.5 rounded text-text-muted font-mono font-bold">
              /
            </kbd>
          </div>

          {/* Search Dropdown Results */}
          {searchFocused && searchQuery.length > 0 && (
            <div className="absolute top-full left-0 w-full mt-2 bg-[#0B0F19] border border-ds-border rounded-xl shadow-2xl py-2 z-[60] animate-in fade-in slide-in-from-top-2">
              <div className="px-3 pb-2 mb-2 border-b border-ds-border/50">
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Top Results</span>
              </div>
              <button onClick={() => router.push("/studio")} className="w-full text-left px-4 py-2 hover:bg-white/5 flex items-center gap-3">
                <Search className="w-4 h-4 text-blue-400" />
                <div>
                  <div className="text-sm text-white font-medium">Auto-Fix Studio</div>
                  <div className="text-xs text-text-muted">AI Code Generation</div>
                </div>
              </button>
              <button onClick={() => router.push("/scanners")} className="w-full text-left px-4 py-2 hover:bg-white/5 flex items-center gap-3">
                <Search className="w-4 h-4 text-purple-400" />
                <div>
                  <div className="text-sm text-white font-medium">Docker Security</div>
                  <div className="text-xs text-text-muted">Scanner modules</div>
                </div>
              </button>
              <button onClick={() => router.push("/arsenal")} className="w-full text-left px-4 py-2 hover:bg-white/5 flex items-center gap-3">
                <Search className="w-4 h-4 text-red-400" />
                <div>
                  <div className="text-sm text-white font-medium">Arsenal</div>
                  <div className="text-xs text-text-muted">Kali Tool Hub</div>
                </div>
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 lg:gap-4 relative">
        {/* Actions */}
        <div className="flex items-center gap-2">
          <button className="relative p-2 text-text-muted hover:text-white transition-colors rounded-full hover:bg-white/5">
            <ShieldAlert className="w-5 h-5" />
          </button>

          {/* Notifications */}
          <div className="relative" ref={notificationsRef}>
            <button
              onClick={() => { setShowNotifications(!showNotifications); setShowProfile(false); }}
              className="relative p-2 text-text-muted hover:text-white transition-colors rounded-full hover:bg-white/5"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-ds-critical rounded-full border border-[#0B0F19]"></span>
            </button>

            {showNotifications && (
              <div className="absolute right-0 top-full mt-2 w-80 bg-[#0B0F19] border border-ds-border rounded-xl shadow-2xl z-[60] animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center justify-between px-4 py-3 border-b border-ds-border">
                  <span className="text-sm font-bold text-white">Notifications</span>
                  <button className="text-xs text-blue-400 hover:text-blue-300 font-semibold">Mark all read</button>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  <div className="p-4 border-b border-ds-border/50 hover:bg-white/5 cursor-pointer flex gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                    <div>
                      <div className="text-sm text-white font-medium">Critical Secret Leaked</div>
                      <div className="text-xs text-text-muted mt-1">AWS Access Key found in API router branch. Action required immediately.</div>
                      <div className="text-[10px] text-gray-500 mt-2">2 minutes ago</div>
                    </div>
                  </div>
                  <div className="p-4 hover:bg-white/5 cursor-pointer flex gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                    <div>
                      <div className="text-sm text-white font-medium">Scan Completed</div>
                      <div className="text-xs text-text-muted mt-1">Docker image passed security baseline.</div>
                      <div className="text-[10px] text-gray-500 mt-2">1 hour ago</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="h-6 w-px bg-ds-border hidden sm:block"></div>

        {/* User Profile */}
        <div className="relative" ref={profileRef}>
          <button
            onClick={() => { setShowProfile(!showProfile); setShowNotifications(false); }}
            className="flex items-center gap-2 hover:bg-white/5 p-1 pr-2 rounded-full transition-colors group"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 p-[1px]">
              <div className="h-full w-full rounded-full bg-[#0B0F19] flex items-center justify-center text-white font-bold text-sm">
                S
              </div>
            </div>
            <div className="text-left hidden md:block">
              <div className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">Sahil</div>
              <div className="text-[10px] text-text-muted uppercase tracking-wider font-bold">Admin</div>
            </div>
            <ChevronDown className="w-4 h-4 text-text-muted group-hover:text-white transition-colors hidden md:block" />
          </button>

          {showProfile && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-[#0B0F19] border border-ds-border rounded-xl shadow-2xl py-2 z-[60] animate-in fade-in slide-in-from-top-2">
              <div className="px-4 py-2 border-b border-ds-border/50 mb-2">
                <div className="text-sm font-bold text-white">sahil123@gmail.com</div>
                <div className="text-xs text-text-muted">Master Commander</div>
              </div>
              <button onClick={() => { router.push("/settings"); setShowProfile(false); }} className="w-full text-left px-4 py-2 hover:bg-white/5 flex items-center gap-3 text-sm text-gray-300 hover:text-white">
                <Settings className="w-4 h-4" /> Account Settings
              </button>
              <button onClick={() => { router.push("/billing"); setShowProfile(false); }} className="w-full text-left px-4 py-2 hover:bg-white/5 flex items-center gap-3 text-sm text-gray-300 hover:text-white">
                <CreditCard className="w-4 h-4" /> Billing & Plan
              </button>
              <div className="h-px bg-ds-border/50 my-2"></div>
              <button onClick={handleLogout} className="w-full text-left px-4 py-2 hover:bg-red-500/10 flex items-center gap-3 text-sm text-red-400 hover:text-red-300 transition-colors">
                <LogOut className="w-4 h-4" /> Logout Session
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
