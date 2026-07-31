"use client";
import { useState, useEffect } from "react";
import { Copy, Trash2, Key, Check, Lock } from "lucide-react";

export default function SettingsPage() {
  const [tokens, setTokens] = useState([]);
  const [newTokenName, setNewTokenName] = useState("");
  const [generatedToken, setGeneratedToken] = useState("");
  const [copied, setCopied] = useState(false);

  // Password State
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwdMessage, setPwdMessage] = useState("");
  const [pwdLoading, setPwdLoading] = useState(false);

  useEffect(() => {
    fetchTokens();
  }, []);

  const getHeaders = () => ({
    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
    "Content-Type": "application/json"
  });

  const fetchTokens = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/apikeys/list`, {
        headers: getHeaders()
      });
      if (res.ok) setTokens(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const generateToken = async () => {
    if (!newTokenName) return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/apikeys/generate`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ name: newTokenName })
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedToken(data.token);
        setNewTokenName("");
        fetchTokens();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const revokeToken = async (id: number) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/apikeys/revoke/${id}`, {
        method: "DELETE",
        headers: getHeaders()
      });
      if (res.ok) fetchTokens();
    } catch (e) {
      console.error(e);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedToken);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const changePassword = async () => {
    if (newPassword !== confirmPassword) {
      setPwdMessage("Passwords do not match!");
      return;
    }
    if (!oldPassword || !newPassword) {
      setPwdMessage("Fields cannot be empty.");
      return;
    }
    setPwdLoading(true);
    setPwdMessage("");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/change-password`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to update password");
      setPwdMessage("Password updated successfully!");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (e: any) {
      setPwdMessage(e.message);
    } finally {
      setPwdLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Settings & API Keys</h1>
      
      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-6 mb-8 max-w-3xl">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Key className="w-5 h-5 text-blue-500" />
          Generate New API Token
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          API tokens allow you to authenticate with the DevShield API in your CI/CD pipelines.
        </p>
        
        <div className="flex gap-4 mb-4">
          <input 
            type="text" 
            placeholder="Token Name (e.g. GitHub Actions)" 
            className="flex-1 bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            value={newTokenName}
            onChange={(e) => setNewTokenName(e.target.value)}
          />
          <button 
            onClick={generateToken}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors"
          >
            Generate Token
          </button>
        </div>

        {generatedToken && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 mb-4">
            <p className="text-green-400 text-sm font-bold mb-2">Token Generated Successfully</p>
            <p className="text-gray-300 text-xs mb-3">Please copy this token now. You will not be able to see it again.</p>
            <div className="flex items-center gap-2 bg-[#050912] p-3 rounded border border-white/10">
              <code className="text-blue-400 flex-1 text-sm">{generatedToken}</code>
              <button onClick={copyToClipboard} className="text-gray-400 hover:text-white transition-colors">
                {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-6 max-w-3xl mb-8">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Lock className="w-5 h-5 text-indigo-500" />
          Account Security
        </h2>
        <p className="text-gray-400 text-sm mb-6">
          Update your master password to keep your Command Center secure.
        </p>

        {pwdMessage && (
          <div className={`p-3 rounded-lg mb-4 text-sm font-bold ${pwdMessage.includes("successfully") ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}>
            {pwdMessage}
          </div>
        )}

        <div className="space-y-4">
          <input 
            type="password" 
            placeholder="Current Password" 
            className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-4">
            <input 
              type="password" 
              placeholder="New Password" 
              className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <input 
              type="password" 
              placeholder="Confirm New Password" 
              className="w-full bg-[#050912] border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
          <button 
            onClick={changePassword}
            disabled={pwdLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg text-sm font-bold transition-colors disabled:opacity-50"
          >
            {pwdLoading ? "Updating..." : "Update Master Password"}
          </button>
        </div>
      </div>

      <div className="bg-[#0b0f1a] border border-white/5 rounded-xl p-6 max-w-3xl">
        <h2 className="text-lg font-bold text-white mb-4">Active Tokens</h2>
        <div className="space-y-3">
          {tokens.map((token: any) => (
            <div key={token.id} className="flex items-center justify-between bg-[#050912] p-4 rounded-lg border border-white/5">
              <div>
                <p className="text-white font-medium text-sm flex items-center gap-2">
                  {token.name}
                  {token.is_revoked && <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded">Revoked</span>}
                </p>
                <p className="text-gray-500 text-xs mt-1">ID: {token.id}</p>
              </div>
              {!token.is_revoked && (
                <button 
                  onClick={() => revokeToken(token.id)}
                  className="text-red-400 hover:text-red-300 transition-colors p-2 hover:bg-red-500/10 rounded"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
          {tokens.length === 0 && (
            <p className="text-gray-500 text-sm italic">No API tokens generated yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
