"use client";
import { useState } from "react";
import { Check, Zap, Shield } from "lucide-react";

export default function BillingPage() {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async (plan: string) => {
    setLoading(true);
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/billing/checkout`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ plan })
        });
        const data = await res.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            console.error("No checkout url returned", data);
            setLoading(false);
        }
    } catch (e) {
        console.error(e);
        setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="max-w-4xl mx-auto pt-10">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-white mb-4">Upgrade to DevShield Pro</h1>
          <p className="text-gray-400">Unlock the full power of the AI Intelligence Modules and continuous Red-Teaming.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Free Tier */}
          <div className="bg-[#0b0f1a] border border-white/5 rounded-2xl p-8 relative overflow-hidden">
            <h3 className="text-xl font-bold text-white mb-2">Developer</h3>
            <div className="text-3xl font-bold text-white mb-6">Free</div>
            <ul className="space-y-4 mb-8">
              <li className="flex gap-3 text-gray-300">
                <Check className="w-5 h-5 text-gray-500" /> Basic SAST Scanning
              </li>
              <li className="flex gap-3 text-gray-300">
                <Check className="w-5 h-5 text-gray-500" /> OSV Dependency Checks
              </li>
              <li className="flex gap-3 text-gray-300">
                <Check className="w-5 h-5 text-gray-500" /> 10 AI Fixes / Month
              </li>
            </ul>
            <button disabled className="w-full bg-white/5 text-gray-400 py-3 rounded-xl font-bold">
              Current Plan
            </button>
          </div>

          {/* Pro Tier */}
          <div className="bg-gradient-to-b from-[#1a1b26] to-[#0b0f1a] border border-blue-500/30 rounded-2xl p-8 relative overflow-hidden shadow-[0_0_40px_-10px_rgba(59,130,246,0.3)]">
            <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
              POPULAR
            </div>
            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-400" /> Enterprise Pro
            </h3>
            <div className="text-3xl font-bold text-white mb-6">$49<span className="text-lg text-gray-400 font-normal">/mo</span></div>
            <ul className="space-y-4 mb-8">
              <li className="flex gap-3 text-white">
                <Shield className="w-5 h-5 text-blue-400" /> All 10 AI Intelligence Modules
              </li>
              <li className="flex gap-3 text-white">
                <Shield className="w-5 h-5 text-blue-400" /> Continuous RedAgent Testing
              </li>
              <li className="flex gap-3 text-white">
                <Shield className="w-5 h-5 text-blue-400" /> CI/CD API Token Integration
              </li>
              <li className="flex gap-3 text-white">
                <Shield className="w-5 h-5 text-blue-400" /> Unlimited AI Auto-Fixes
              </li>
            </ul>
            <button 
              onClick={() => handleCheckout("pro")}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-bold transition-all shadow-[0_0_20px_-5px_rgba(59,130,246,0.5)]"
            >
              {loading ? "Redirecting to Stripe..." : "Upgrade to Pro"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
