"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { BinarySnakeBackground } from "@/components/ui/BinarySnakeBackground";
import { CyberSnakeOverlay } from "@/components/ui/CyberSnakeOverlay";
import React from "react";

// Pages that render their OWN full-screen layouts (no app shell)
const SHELL_EXCLUDED_PATHS = ["/", "/auth"];

export function ClientShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isExcluded = SHELL_EXCLUDED_PATHS.includes(pathname);

  if (isExcluded) {
    // For landing / auth — render only the cyber snake overlay
    // (landing page has its own CyberCanvas)
    return (
      <>
        <CyberSnakeOverlay />
        <main className="flex-1 w-full">{children}</main>
      </>
    );
  }

  return (
    <>
      <BinarySnakeBackground />
      <CyberSnakeOverlay />
      {/* Sidebar: handles its own mobile open/close state */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col min-h-screen min-w-0 md:ml-0">
        <Header onMenuToggle={() => setSidebarOpen((prev) => !prev)} />
        <main className="flex-1 overflow-auto relative z-10 p-6 lg:p-8">
          {children}
        </main>
      </div>
    </>
  );
}
