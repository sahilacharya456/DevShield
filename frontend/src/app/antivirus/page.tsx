"use client";
import { useState } from "react";
import { UploadCloud, ShieldAlert, Lock, CheckCircle2, AlertTriangle, FileText, Activity } from "lucide-react";

export default function AegisAntivirusPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleScan = async () => {
    if (!file) return;
    setIsScanning(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/antivirus/scan", {
        method: "POST",
        headers: {
          "Authorization": "Bearer sahil_admin_token", // Simulated auth
        },
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      setResult({ error: "Scan failed to reach backend." });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-blue-500" />
          Aegis Antivirus™
        </h1>
        <p className="text-gray-400 mt-2">
          Military-grade heuristic analysis and YARA signature threat neutralization.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Zone */}
        <div 
          className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all ${
            file ? 'border-blue-500 bg-blue-500/5' : 'border-gray-700 bg-ds-charcoal/30 hover:border-blue-400/50 hover:bg-blue-900/10'
          }`}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <UploadCloud className={`w-16 h-16 mb-4 ${file ? 'text-blue-400' : 'text-gray-600'}`} />
          <h3 className="text-xl font-semibold text-white mb-2">
            {file ? file.name : 'Drag & Drop Suspicious File'}
          </h3>
          <p className="text-sm text-gray-400 mb-6">
            {file ? `${(file.size / 1024).toFixed(2)} KB` : 'Supports Executables, Scripts, and Archives'}
          </p>
          
          <input 
            type="file" 
            id="fileUpload" 
            className="hidden" 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <label 
            htmlFor="fileUpload" 
            className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg cursor-pointer transition text-sm font-medium border border-gray-600 mb-4"
          >
            Browse Files
          </label>

          <button
            onClick={handleScan}
            disabled={!file || isScanning}
            className={`w-full max-w-xs py-3 rounded-lg font-bold shadow-[0_0_15px_rgba(59,130,246,0.5)] flex justify-center items-center gap-2 ${
              !file || isScanning 
                ? 'bg-blue-900/50 text-blue-300 cursor-not-allowed shadow-none' 
                : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
          >
            {isScanning ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Analyzing Entropy & Signatures...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Initialize Aegis Scan
              </span>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="bg-ds-charcoal/40 border border-ds-border rounded-xl p-6 min-h-[400px]">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-gray-400" />
            Intelligence Report
          </h3>

          {!result && !isScanning && (
            <div className="h-full flex items-center justify-center text-gray-500 text-sm">
              Waiting for payload submission...
            </div>
          )}

          {isScanning && (
            <div className="space-y-4 animate-pulse">
              <div className="h-4 bg-gray-700 rounded w-3/4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-700 rounded w-full"></div>
            </div>
          )}

          {result && !result.error && (
            <div className="space-y-6">
              {/* Header Status */}
              <div className={`p-4 rounded-lg flex items-start gap-4 ${
                result.threat_detected ? 'bg-red-500/10 border border-red-500/20' : 'bg-green-500/10 border border-green-500/20'
              }`}>
                {result.threat_detected ? (
                  <AlertTriangle className="w-8 h-8 text-red-500 shrink-0" />
                ) : (
                  <CheckCircle2 className="w-8 h-8 text-green-500 shrink-0" />
                )}
                <div>
                  <h4 className={`font-bold text-lg ${result.threat_detected ? 'text-red-400' : 'text-green-400'}`}>
                    {result.threat_detected ? 'Malicious Payload Detected' : 'Payload is Clean'}
                  </h4>
                  <p className="text-sm text-gray-300 mt-1">{result.message}</p>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                  <div className="text-xs text-gray-400 font-mono mb-1">SHANNON ENTROPY</div>
                  <div className="text-2xl font-bold text-white flex items-baseline gap-2">
                    {result.entropy}
                    {result.is_packed && <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full border border-orange-500/20">PACKED</span>}
                  </div>
                </div>
                <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                  <div className="text-xs text-gray-400 font-mono mb-1">YARA MATCHES</div>
                  <div className="text-2xl font-bold text-white">
                    {result.yara_matches?.length || 0}
                  </div>
                </div>
              </div>

              {/* YARA Details */}
              {result.yara_matches?.length > 0 && (
                <div>
                  <div className="text-xs text-gray-400 font-mono mb-2">TRIGGERED SIGNATURES</div>
                  <div className="space-y-2">
                    {result.yara_matches.map((rule: string, idx: number) => (
                      <div key={idx} className="bg-red-900/20 text-red-300 border border-red-900/50 px-3 py-2 rounded-md font-mono text-sm">
                        [YARA] {rule}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Vault Status */}
              {result.vault_path && (
                <div className="bg-blue-900/20 border border-blue-500/30 p-4 rounded-lg flex items-center gap-4">
                  <Lock className="w-6 h-6 text-blue-400 shrink-0" />
                  <div>
                    <div className="text-sm font-bold text-blue-300">Quarantine Vault Activated</div>
                    <div className="text-xs text-gray-400 font-mono mt-1 break-all">
                      {result.vault_path}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {result?.error && (
            <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-lg text-red-400 text-sm">
              {result.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
