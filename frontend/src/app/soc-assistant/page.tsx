"use client";

import { useState, useRef, useEffect } from "react";

export default function SocAssistant() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: "user" | "bot", content: string }[]>([
    { role: "bot", content: "DevShield AI initialized. I have context on your infrastructure, CI/CD pipelines, and SAST findings. How can I assist you with remediation or threat hunting today?" }
  ]);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!query.trim()) return;
    const userMessage = query;
    setQuery("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${apiUrl}/api/v1/soc/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "bot", content: data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "bot", content: "Connection to SOC API failed. Running in offline fallback mode." }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] animate-in fade-in duration-500 max-w-5xl mx-auto">
      
      {/* Clean Enterprise Header */}
      <div className="border-b border-ds-border/50 pb-6 mb-6">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-3">
          Security Operations
        </div>
        <h1 className="text-3xl font-medium text-white tracking-tight">DevShield AI</h1>
      </div>

      <div className="flex-1 bg-ds-elevated/30 border border-ds-border rounded-xl overflow-hidden flex flex-col relative shadow-sm">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-xl text-[14px] leading-relaxed shadow-sm ${
                m.role === 'user' 
                  ? 'bg-white text-black rounded-tr-sm' 
                  : 'bg-ds-navy border border-ds-border text-text-primary rounded-tl-sm'
              }`}>
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] p-4 rounded-xl rounded-tl-sm bg-ds-navy border border-ds-border text-text-secondary flex items-center gap-2">
                <span className="animate-spin text-text-muted">◌</span> Analyzing threat context...
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        <div className="p-4 bg-ds-elevated border-t border-ds-border">
          <div className="relative">
            <input 
              type="text" 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about compliance, vulnerabilities, or remediation steps..." 
              className="w-full bg-[#0B0F19] border border-ds-border rounded-lg py-3 pl-4 pr-12 text-sm text-white focus:outline-none focus:border-text-muted transition-colors placeholder:text-text-muted"
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !query.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-white text-black rounded-md disabled:opacity-50 hover:bg-gray-200 transition-colors"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
