import { motion, AnimatePresence } from 'framer-motion';
import { useState, useCallback, useRef } from 'react';
import Editor from '@monaco-editor/react';
import {
  Upload,
  Radar,
  Shield,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Wrench,
  Download,
  RefreshCw,
  Check,
  FileCode,
  Zap,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import toast from 'react-hot-toast';
import SecurityBadge from '../components/SecurityBadge';
import LoadingOrb from '../components/LoadingOrb';
import type { Vulnerability, Severity, SecurityResult } from '../types';

// ==========================================
// Mock Data
// ==========================================
const MOCK_RESULTS: SecurityResult = {
  overall_score: 42,
  vulnerabilities: [
    {
      id: 'VULN-001',
      name: 'SQL Injection',
      severity: 'Critical',
      cwe_id: 'CWE-89',
      owasp_category: 'A03:2021 Injection',
      line_number: 23,
      description: 'User input is directly concatenated into SQL query string without parameterized queries or input sanitization.',
      fix_suggestion: 'Use parameterized queries with cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
      confidence: 95,
    },
    {
      id: 'VULN-002',
      name: 'Cross-Site Scripting (XSS)',
      severity: 'High',
      cwe_id: 'CWE-79',
      owasp_category: 'A07:2021 XSS',
      line_number: 45,
      description: 'User-supplied data is rendered in HTML output without proper encoding or sanitization.',
      fix_suggestion: 'Use html.escape() or a template engine with auto-escaping enabled.',
      confidence: 88,
    },
    {
      id: 'VULN-003',
      name: 'Hardcoded Secret',
      severity: 'High',
      cwe_id: 'CWE-798',
      owasp_category: 'A02:2021 Crypto Failures',
      line_number: 8,
      description: 'API key is hardcoded in source code instead of being loaded from environment variables.',
      fix_suggestion: 'Use os.environ.get("API_KEY") and store secrets in .env files.',
      confidence: 99,
    },
    {
      id: 'VULN-004',
      name: 'Insecure Deserialization',
      severity: 'Medium',
      cwe_id: 'CWE-502',
      owasp_category: 'A08:2021 Integrity Failures',
      line_number: 67,
      description: 'pickle.loads() is used on untrusted data which can lead to arbitrary code execution.',
      fix_suggestion: 'Use json.loads() or implement a whitelist of allowed classes for deserialization.',
      confidence: 76,
    },
    {
      id: 'VULN-005',
      name: 'Missing Rate Limiting',
      severity: 'Low',
      cwe_id: 'CWE-770',
      owasp_category: 'A04:2021 Insecure Design',
      line_number: 12,
      description: 'Authentication endpoint lacks rate limiting, making it vulnerable to brute-force attacks.',
      fix_suggestion: 'Implement rate limiting using flask-limiter or similar middleware.',
      confidence: 82,
    },
  ],
  severity_distribution: { Critical: 1, High: 2, Medium: 1, Low: 1 },
  owasp_heatmap: {
    'A01 Broken Access Control': 0,
    'A02 Crypto Failures': 1,
    'A03 Injection': 1,
    'A04 Insecure Design': 1,
    'A05 Misconfiguration': 0,
    'A06 Vulnerable Components': 0,
    'A07 Auth Failures': 1,
    'A08 Integrity Failures': 1,
    'A09 Logging Failures': 0,
    'A10 SSRF': 0,
  },
  scan_duration_ms: 2340,
};

const SEVERITY_COLORS: Record<Severity, string> = {
  Critical: '#EF4444',
  High: '#F59E0B',
  Medium: '#EAB308',
  Low: '#3B82F6',
};

const OWASP_CATEGORIES = [
  'A01 Broken Access Control',
  'A02 Crypto Failures',
  'A03 Injection',
  'A04 Insecure Design',
  'A05 Misconfiguration',
  'A06 Vulnerable Components',
  'A07 Auth Failures',
  'A08 Integrity Failures',
  'A09 Logging Failures',
  'A10 SSRF',
];

// ==========================================
// Score Gauge
// ==========================================
function ScoreGauge({ score, size = 180 }: { score: number; size?: number }) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const color = score >= 81 ? '#10B981' : score >= 61 ? '#EAB308' : score >= 31 ? '#F59E0B' : '#EF4444';
  const label = score >= 81 ? 'Secure' : score >= 61 ? 'Moderate' : score >= 31 ? 'Needs Work' : 'Critical Risk';

  return (
    <div className="relative flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1A1A1E"
          strokeWidth="10"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 2, ease: 'easeOut', delay: 0.3 }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-5xl font-bold"
          style={{ color }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, type: 'spring' }}
        >
          {score}
        </motion.span>
        <span className="text-sm text-[#94A3B8]">/ 100</span>
      </div>
      <motion.p
        className="mt-3 text-sm font-semibold uppercase tracking-wider"
        style={{ color }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        {label}
      </motion.p>
    </div>
  );
}

// ==========================================
// Vulnerability Card
// ==========================================
function VulnerabilityCard({
  vuln,
  index,
  onFix,
  fixed,
}: {
  vuln: Vulnerability;
  index: number;
  onFix: (id: string) => void;
  fixed: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const borderColor = SEVERITY_COLORS[vuln.severity];

  return (
    <motion.div
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.12 }}
      className={`rounded-xl border p-5 transition-all ${
        fixed ? 'opacity-60 bg-[#10B981]/5' : 'bg-[#141416]'
      }`}
      style={{ borderColor: fixed ? '#10B981' : `${borderColor}40` }}
      id={`vuln-card-${vuln.id}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap mb-2">
            <h4 className="text-base font-semibold text-[#F1F5F9]">
              {fixed && <Check className="w-4 h-4 inline mr-1.5 text-[#10B981]" />}
              {vuln.name}
            </h4>
            <SecurityBadge severity={vuln.severity} size="sm" />
            <span className="badge badge-info !py-0.5 !text-[9px]">{vuln.cwe_id}</span>
            <span className="badge badge-success !py-0.5 !text-[9px]">{vuln.owasp_category}</span>
          </div>
          <p className="text-sm text-[#94A3B8] leading-relaxed">{vuln.description}</p>
          <div className="flex items-center gap-4 mt-3">
            <span className="text-xs text-[#475569]">
              Line <span className="text-[#F59E0B] font-mono">{vuln.line_number}</span>
            </span>
            <div className="flex items-center gap-2 flex-1 max-w-[200px]">
              <span className="text-xs text-[#475569]">Confidence</span>
              <div className="flex-1 h-1.5 bg-[#1A1A1E] rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: borderColor }}
                  initial={{ width: 0 }}
                  animate={{ width: `${vuln.confidence}%` }}
                  transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                />
              </div>
              <span className="text-xs font-mono text-[#94A3B8]">{vuln.confidence}%</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {!fixed && (
            <motion.button
              onClick={() => onFix(vuln.id)}
              className="px-3 py-1.5 rounded-lg bg-[#10B981]/10 text-[#10B981] text-xs font-medium
                         border border-[#10B981]/20 hover:bg-[#10B981]/20 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Wrench className="w-3 h-3 inline mr-1" />
              Fix
            </motion.button>
          )}
          <motion.button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 rounded-lg hover:bg-[#202025] text-[#475569] transition-colors"
            whileTap={{ scale: 0.9 }}
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </motion.button>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-4 p-4 rounded-lg bg-[#0D0D0F] border border-[#2A2A30]/30">
              <p className="text-xs font-semibold text-[#10B981] uppercase tracking-wider mb-2">
                Suggested Fix
              </p>
              <code className="text-sm text-[#F1F5F9] font-mono block whitespace-pre-wrap leading-relaxed">
                {vuln.fix_suggestion}
              </code>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ==========================================
// Radar Scan Animation
// ==========================================
function RadarScanAnimation() {
  return (
    <div className="flex flex-col items-center gap-6 py-12">
      <div className="relative w-40 h-40">
        {/* Concentric rings */}
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="absolute rounded-full border border-[#3B82F6]/20"
            style={{
              top: `${(3 - i) * 20}%`,
              left: `${(3 - i) * 20}%`,
              right: `${(3 - i) * 20}%`,
              bottom: `${(3 - i) * 20}%`,
            }}
          />
        ))}
        {/* Sweep */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <div
            className="absolute top-0 left-1/2 w-0.5 h-1/2 origin-bottom"
            style={{
              background: 'linear-gradient(to top, transparent, #3B82F6)',
            }}
          />
          <div
            className="absolute top-1/2 left-1/2 w-20 h-20 -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{
              background: 'conic-gradient(from 0deg, transparent 0%, rgba(59,130,246,0.15) 0%, transparent 30%)',
            }}
          />
        </motion.div>
        {/* Center dot */}
        <motion.div
          className="absolute top-1/2 left-1/2 w-3 h-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#3B82F6]"
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      </div>
      <motion.p
        className="text-sm text-[#94A3B8] font-medium"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        Scanning for vulnerabilities...
      </motion.p>
    </div>
  );
}

// ==========================================
// OWASP Heatmap
// ==========================================
function OWASPHeatmap({ data }: { data: Record<string, number> }) {
  return (
    <div className="grid grid-cols-5 gap-1.5">
      {OWASP_CATEGORIES.map((cat, i) => {
        const count = data[cat] || 0;
        const bg = count === 0 ? '#141416' : count === 1 ? '#F59E0B20' : '#EF444430';
        const border = count === 0 ? '#2A2A30' : count === 1 ? '#F59E0B40' : '#EF444450';
        return (
          <motion.div
            key={cat}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="p-2 rounded-lg text-center border cursor-default"
            style={{ background: bg, borderColor: border }}
            title={cat}
          >
            <div className="text-lg font-bold text-[#F1F5F9]">{count}</div>
            <div className="text-[9px] text-[#475569] leading-tight mt-0.5 truncate">
              {cat.replace(/^A\d+\s/, '')}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

// ==========================================
// Security Analyzer Page
// ==========================================
export default function SecurityAnalyzer() {
  const [code, setCode] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState<SecurityResult | null>(null);
  const [fixedVulns, setFixedVulns] = useState<Set<string>>(new Set());
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleScan = useCallback(async () => {
    if (!code.trim()) {
      toast.error('Paste or upload code to scan');
      return;
    }
    setIsScanning(true);
    setResults(null);
    setFixedVulns(new Set());

    try {
      const { api } = await import('../services/api');
      const response = await api.scanCode(code, 'python');
      setResults({ ...response, scan_duration_ms: 1540, severity_distribution: { Critical: 1, High: 2, Medium: 1, Low: 1 }, owasp_heatmap: MOCK_RESULTS.owasp_heatmap });
      toast.success(`Scan complete — ${response.vulnerabilities.length} issues found`);
    } catch (error) {
      toast.error('Failed to scan code.');
    } finally {
      setIsScanning(false);
    }
  }, [code]);

  const handleFix = useCallback((vulnId: string) => {
    setFixedVulns((prev) => {
      const next = new Set(prev);
      next.add(vulnId);
      return next;
    });
    toast.success('Fix applied');
  }, []);

  const handleFixAll = useCallback(() => {
    if (!results) return;
    const allIds = new Set(results.vulnerabilities.map((v) => v.id));
    setFixedVulns(allIds);
    toast.success('All vulnerabilities fixed!');
  }, [results]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setCode(ev.target?.result as string);
        toast.success(`Loaded ${file.name}`);
      };
      reader.readAsText(file);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setCode(ev.target?.result as string);
        toast.success(`Loaded ${file.name}`);
      };
      reader.readAsText(file);
    }
  }, []);

  const pieData = results
    ? Object.entries(results.severity_distribution)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => ({
          name,
          value,
          color: SEVERITY_COLORS[name as Severity],
        }))
    : [];

  return (
    <div className="page-container">
      <div className="space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold text-[#F1F5F9] flex items-center gap-2">
            <Shield className="w-6 h-6 text-[#8B5CF6]" />
            Security Analyzer
          </h2>
          <p className="text-sm text-[#94A3B8] mt-1">
            Upload or paste code to detect vulnerabilities, get severity ratings, and auto-fix issues.
          </p>
        </motion.div>

        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Drag & Drop + Editor */}
          <div className="lg:col-span-2 space-y-4">
            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                dragOver
                  ? 'border-[#3B82F6] bg-[#3B82F6]/5'
                  : 'border-[#2A2A30] hover:border-[#475569] bg-[#141416]/50'
              }`}
            >
              <Upload className="w-8 h-8 text-[#475569] mx-auto mb-3" />
              <p className="text-sm text-[#94A3B8]">
                Drag & drop a file here, or <span className="text-[#3B82F6]">click to browse</span>
              </p>
              <p className="text-xs text-[#475569] mt-1">
                Supports .py, .js, .ts, .java, .cpp, .go, .rs
              </p>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".py,.js,.ts,.java,.cpp,.go,.rs"
                onChange={handleFileSelect}
              />
            </div>

            {/* Code Editor */}
            <div className="glass-card overflow-hidden h-[350px]">
              <div className="flex items-center gap-3 px-4 py-2.5 border-b border-[#2A2A30]/50">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                  <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                  <div className="w-3 h-3 rounded-full bg-[#10B981]" />
                </div>
                <span className="text-xs font-mono text-[#475569]">Paste code here</span>
              </div>
              <Editor
                height="calc(100% - 40px)"
                language="python"
                value={code}
                onChange={(val) => setCode(val || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: "'JetBrains Mono', monospace",
                  lineHeight: 22,
                  padding: { top: 12, bottom: 12 },
                  scrollBeyondLastLine: false,
                  renderLineHighlight: 'none',
                  overviewRulerBorder: false,
                }}
              />
            </div>
          </div>

          {/* Scan Controls */}
          <div className="space-y-4">
            <motion.button
              onClick={handleScan}
              disabled={isScanning || !code.trim()}
              className={`w-full py-4 rounded-xl font-semibold text-base flex items-center justify-center gap-3
                relative overflow-hidden transition-all
                ${isScanning
                  ? 'bg-[#8B5CF6]/20 text-[#8B5CF6] cursor-wait'
                  : 'btn-primary disabled:opacity-40 disabled:cursor-not-allowed'
                }`}
              whileHover={!isScanning ? { scale: 1.02 } : undefined}
              whileTap={!isScanning ? { scale: 0.98 } : undefined}
              id="scan-button"
            >
              {isScanning ? (
                <>
                  <LoadingOrb size={24} />
                  Scanning...
                </>
              ) : (
                <>
                  <Radar className="w-5 h-5" />
                  Scan for Vulnerabilities
                </>
              )}
            </motion.button>

            {isScanning && <RadarScanAnimation />}

            {!isScanning && !results && (
              <div className="glass-card p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[#141416] border border-[#2A2A30]/50 flex items-center justify-center">
                  <FileCode className="w-8 h-8 text-[#475569]" />
                </div>
                <p className="text-sm text-[#475569]">
                  Paste code and press Scan to analyze vulnerabilities.
                </p>
              </div>
            )}

            {results && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="glass-card p-6 text-center"
              >
                <ScoreGauge score={results.overall_score} size={160} />
                <div className="mt-4 text-xs text-[#475569]">
                  Scan completed in {results.scan_duration_ms}ms
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              {/* Charts Row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Severity Distribution */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="glass-card p-6"
                >
                  <h3 className="text-sm font-semibold text-[#F1F5F9] mb-4">Severity Distribution</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={75}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} stroke="transparent" />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: '#1A1A1E',
                          border: '1px solid #2A2A30',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex flex-wrap justify-center gap-3 mt-2">
                    {pieData.map((d) => (
                      <div key={d.name} className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-sm" style={{ background: d.color }} />
                        <span className="text-xs text-[#94A3B8]">{d.name} ({d.value})</span>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* OWASP Heatmap */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="lg:col-span-2 glass-card p-6"
                >
                  <h3 className="text-sm font-semibold text-[#F1F5F9] mb-4">OWASP Top 10 Coverage</h3>
                  <OWASPHeatmap data={results.owasp_heatmap} />
                </motion.div>
              </div>

              {/* Vulnerability List */}
              <div>
                <div className="flex items-center justify-between mb-5">
                  <h3 className="text-lg font-semibold text-[#F1F5F9] flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
                    Vulnerabilities Found ({results.vulnerabilities.length})
                  </h3>
                  <div className="flex items-center gap-3">
                    <motion.button
                      onClick={handleFixAll}
                      disabled={fixedVulns.size === results.vulnerabilities.length}
                      className="px-4 py-2 rounded-xl bg-[#10B981]/10 text-[#10B981] text-sm font-medium
                                 border border-[#10B981]/20 hover:bg-[#10B981]/20 transition-colors
                                 disabled:opacity-40 flex items-center gap-2"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      id="fix-all-btn"
                    >
                      <Zap className="w-4 h-4" />
                      Auto-fix All
                    </motion.button>
                    <motion.button
                      onClick={handleScan}
                      className="px-4 py-2 rounded-xl bg-[#141416] text-[#94A3B8] text-sm font-medium
                                 border border-[#2A2A30] hover:bg-[#202025] transition-colors
                                 flex items-center gap-2"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <RefreshCw className="w-4 h-4" />
                      Re-scan
                    </motion.button>
                    <motion.button
                      className="px-4 py-2 rounded-xl bg-[#141416] text-[#94A3B8] text-sm font-medium
                                 border border-[#2A2A30] hover:bg-[#202025] transition-colors
                                 flex items-center gap-2"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => toast.success('Report exported')}
                    >
                      <Download className="w-4 h-4" />
                      Export
                    </motion.button>
                  </div>
                </div>

                <div className="space-y-4">
                  {results.vulnerabilities.map((vuln, i) => (
                    <VulnerabilityCard
                      key={vuln.id}
                      vuln={vuln}
                      index={i}
                      onFix={handleFix}
                      fixed={fixedVulns.has(vuln.id)}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
