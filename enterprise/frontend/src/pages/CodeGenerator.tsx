import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useCallback, useRef } from 'react';
import Editor from '@monaco-editor/react';
import {
  Play,
  Copy,
  Download,
  Shield,
  FileText,
  Sparkles,
  Check,
  ChevronDown,
  Gauge,
  Coins,
  Hash,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useCodeGeneratorStore } from '../store';
import type { Language, SecurityLevel } from '../types';

// ==========================================
// Constants
// ==========================================
const LANGUAGES: { value: Language; label: string; extension: string }[] = [
  { value: 'python', label: 'Python', extension: 'py' },
  { value: 'javascript', label: 'JavaScript', extension: 'js' },
  { value: 'typescript', label: 'TypeScript', extension: 'ts' },
  { value: 'java', label: 'Java', extension: 'java' },
  { value: 'cpp', label: 'C++', extension: 'cpp' },
  { value: 'go', label: 'Go', extension: 'go' },
  { value: 'rust', label: 'Rust', extension: 'rs' },
];

const SECURITY_LEVELS: { value: SecurityLevel; label: string; color: string }[] = [
  { value: 'low', label: 'Low', color: '#3B82F6' },
  { value: 'medium', label: 'Medium', color: '#F59E0B' },
  { value: 'high', label: 'High', color: '#EF4444' },
  { value: 'critical', label: 'Critical', color: '#DC2626' },
];



const LANGUAGE_MAP: Record<Language, string> = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  java: 'java',
  cpp: 'cpp',
  go: 'go',
  rust: 'rust',
};

// ==========================================
// Mock code generation
// ==========================================
// Removed MOCK_CODE block as it was unused and contained legacy TODOs

// ==========================================
// Confidence Gauge
// ==========================================
function ConfidenceGauge({ value }: { value: number }) {
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const progress = (value / 100) * circumference;
  const color = value >= 80 ? '#10B981' : value >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <div className="relative w-28 h-28">
      <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#1A1A1E" strokeWidth="6" />
        <motion.circle
          cx="50" cy="50" r={radius}
          fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-[#F1F5F9]">{value}</span>
        <span className="text-[10px] text-[#475569]">confidence</span>
      </div>
    </div>
  );
}

// ==========================================
// Code Generator Page
// ==========================================
export default function CodeGenerator() {
  const store = useCodeGeneratorStore();
  const [copied, setCopied] = useState(false);
  const [showLanguages, setShowLanguages] = useState(false);
  const [displayedCode, setDisplayedCode] = useState('');
  const [hasGenerated, setHasGenerated] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedLang = LANGUAGES.find((l) => l.value === store.language);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowLanguages(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Typewriter effect for generated code
  useEffect(() => {
    if (!store.generatedCode) {
      setDisplayedCode('');
      return;
    }

    let index = 0;
    const code = store.generatedCode;
    setDisplayedCode('');

    const timer = setInterval(() => {
      if (index < code.length) {
        const chunkSize = Math.min(3, code.length - index);
        setDisplayedCode(code.slice(0, index + chunkSize));
        index += chunkSize;
      } else {
        clearInterval(timer);
      }
    }, 5);

    return () => clearInterval(timer);
  }, [store.generatedCode]);

  const handleGenerate = useCallback(async () => {
    if (!store.task.trim()) {
      toast.error('Please describe what you want to build');
      return;
    }

    store.setIsGenerating(true);
    store.setGeneratedCode('');
    setDisplayedCode('');

    try {
      store.setGenerationPhase('Analyzing request...');
      
      const { api } = await import('../services/api');
      const response = await api.generateCode(store.task);

      store.setGeneratedCode(response.code);
      store.setConfidenceScore(response.confidence_score || 85);
      store.setTokenCount(response.token_cost || 0);
      store.setEstimatedCost(parseFloat(((response.token_cost || 0) * 0.00001).toFixed(4)));
      setHasGenerated(true);
      toast.success('Code generated successfully!');
    } catch (error) {
      toast.error('Failed to generate code.');
    } finally {
      store.setIsGenerating(false);
      store.setGenerationPhase('');
    }
  }, [store]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(store.generatedCode);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  }, [store.generatedCode]);

  const handleDownload = useCallback(() => {
    const ext = selectedLang?.extension || 'txt';
    const blob = new Blob([store.generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `devshield_generated.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('File downloaded');
  }, [store.generatedCode, selectedLang]);

  return (
    <div className="page-container">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-120px)]">
        {/* LEFT PANEL — Input */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col gap-5 overflow-y-auto pr-2"
        >
          {/* Header */}
          <div>
            <h2 className="text-2xl font-bold text-[#F1F5F9] flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-[#F59E0B]" />
              Code Generator
            </h2>
            <p className="text-sm text-[#94A3B8] mt-1">
              Describe your task and let AI write secure, production-ready code.
            </p>
          </div>

          {/* Task Description */}
          <div>
            <label className="text-sm font-medium text-[#94A3B8] mb-2 block">Task Description</label>
            <textarea
              className="input-field min-h-[160px] resize-none font-sans"
              placeholder="Describe what you want to build... (e.g., 'Build a REST API with JWT authentication and rate limiting')"
              value={store.task}
              onChange={(e) => store.setTask(e.target.value)}
              id="task-description"
            />
          </div>

          {/* Language Selector */}
          <div className="relative" ref={dropdownRef}>
            <label className="text-sm font-medium text-[#94A3B8] mb-2 block">Language</label>
            <button
              onClick={() => setShowLanguages(!showLanguages)}
              className="input-field flex items-center justify-between"
              id="language-selector"
            >
              <span className="text-[#F1F5F9]">{selectedLang?.label}</span>
              <ChevronDown className={`w-4 h-4 text-[#475569] transition-transform ${showLanguages ? 'rotate-180' : ''}`} />
            </button>
            <AnimatePresence>
              {showLanguages && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="absolute z-20 mt-1 w-full rounded-xl overflow-hidden"
                  style={{ background: '#1A1A1E', border: '1px solid #2A2A30', boxShadow: '0 16px 48px rgba(0,0,0,0.4)' }}
                >
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.value}
                      onClick={() => { store.setLanguage(lang.value); setShowLanguages(false); }}
                      className={`w-full px-4 py-2.5 text-left text-sm hover:bg-[#202025] transition-colors
                        ${store.language === lang.value ? 'text-[#3B82F6] bg-[#3B82F6]/10' : 'text-[#94A3B8]'}`}
                    >
                      {lang.label}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Security Level */}
          <div>
            <label className="text-sm font-medium text-[#94A3B8] mb-3 block">Security Level</label>
            <div className="flex gap-2">
              {SECURITY_LEVELS.map((level) => (
                <motion.button
                  key={level.value}
                  onClick={() => store.setSecurityLevel(level.value)}
                  className={`flex-1 py-2.5 px-3 rounded-xl text-xs font-semibold uppercase tracking-wider
                    transition-all border ${
                      store.securityLevel === level.value
                        ? 'border-opacity-100'
                        : 'border-transparent bg-[#141416] text-[#475569] hover:text-[#94A3B8]'
                    }`}
                  style={
                    store.securityLevel === level.value
                      ? {
                          background: `${level.color}15`,
                          color: level.color,
                          borderColor: `${level.color}40`,
                        }
                      : undefined
                  }
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {level.label}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <motion.button
            onClick={handleGenerate}
            disabled={store.isGenerating || !store.task.trim()}
            className={`w-full py-4 rounded-xl font-semibold text-base flex items-center justify-center gap-3
              transition-all relative overflow-hidden
              ${store.isGenerating
                ? 'bg-[#3B82F6]/20 text-[#3B82F6] cursor-wait'
                : 'btn-primary disabled:opacity-40 disabled:cursor-not-allowed'
              }`}
            whileHover={!store.isGenerating ? { scale: 1.01 } : undefined}
            whileTap={!store.isGenerating ? { scale: 0.99 } : undefined}
            id="generate-button"
          >
            {store.isGenerating ? (
              <>
                <motion.div
                  className="w-5 h-5 border-2 border-[#3B82F6] border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                <motion.span
                  key={store.generationPhase}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {store.generationPhase}
                </motion.span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Generate Secure Code
              </>
            )}
            {store.isGenerating && (
              <motion.div
                className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6]"
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{ duration: 4, ease: 'easeInOut' }}
              />
            )}
          </motion.button>

          {/* Stats Row */}
          <AnimatePresence>
            {hasGenerated && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center gap-6"
              >
                <ConfidenceGauge value={store.confidenceScore} />
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4 text-[#8B5CF6]" />
                    <span className="text-sm text-[#94A3B8]">
                      <span className="font-semibold text-[#F1F5F9]">{store.tokenCount.toLocaleString()}</span> tokens
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Coins className="w-4 h-4 text-[#F59E0B]" />
                    <span className="text-sm text-[#94A3B8]">
                      Est. <span className="font-semibold text-[#F1F5F9]">${store.estimatedCost}</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Gauge className="w-4 h-4 text-[#10B981]" />
                    <span className="text-sm text-[#94A3B8]">
                      Security: <span className="font-semibold text-[#10B981]">{store.securityLevel}</span>
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* RIGHT PANEL — Output */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col glass-card overflow-hidden"
        >
          {/* Editor Toolbar */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A30]/50">
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
                <div className="w-3 h-3 rounded-full bg-[#10B981]" />
              </div>
              <span className="text-xs font-mono text-[#475569]">
                devshield.{selectedLang?.extension || 'py'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <motion.button
                onClick={handleCopy}
                disabled={!store.generatedCode}
                className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Copy code"
              >
                {copied ? <Check className="w-4 h-4 text-[#10B981]" /> : <Copy className="w-4 h-4" />}
              </motion.button>
              <motion.button
                onClick={handleDownload}
                disabled={!store.generatedCode}
                className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Download file"
              >
                <Download className="w-4 h-4" />
              </motion.button>
              <motion.button
                disabled={!store.generatedCode}
                className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Scan for vulnerabilities"
              >
                <Shield className="w-4 h-4" />
              </motion.button>
              <motion.button
                disabled={!store.generatedCode}
                className="p-1.5 rounded-md hover:bg-[#202025] text-[#94A3B8] disabled:opacity-30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Generate documentation"
              >
                <FileText className="w-4 h-4" />
              </motion.button>
            </div>
          </div>

          {/* Monaco Editor */}
          <div className="flex-1 min-h-0">
            {store.isGenerating ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <motion.div
                    className="w-16 h-16 mx-auto rounded-full border-2 border-[#3B82F6] border-t-transparent"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                  />
                  <motion.p
                    key={store.generationPhase}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-[#94A3B8]"
                  >
                    {store.generationPhase}
                  </motion.p>
                </div>
              </div>
            ) : displayedCode ? (
              <Editor
                height="100%"
                language={LANGUAGE_MAP[store.language]}
                value={displayedCode}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: "'JetBrains Mono', monospace",
                  lineHeight: 22,
                  padding: { top: 16, bottom: 16 },
                  scrollBeyondLastLine: false,
                  renderLineHighlight: 'none',
                  overviewRulerBorder: false,
                  hideCursorInOverviewRuler: true,
                  scrollbar: {
                    verticalSliderSize: 4,
                    horizontalSliderSize: 4,
                  },
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-center px-8">
                <div>
                  <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-[#141416] border border-[#2A2A30]/50 flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-[#475569]" />
                  </div>
                  <p className="text-[#475569] text-sm">
                    Your generated code will appear here.
                  </p>
                  <p className="text-[#475569]/60 text-xs mt-1">
                    Describe a task and hit Generate.
                  </p>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
