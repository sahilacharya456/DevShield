import { motion } from 'framer-motion';
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Code2,
  Shield,
  FileText,
  Activity,
  TrendingUp,
  Bug,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Clock,
} from 'lucide-react';
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import ParticleBackground from '../components/ParticleBackground';
import SecurityBadge from '../components/SecurityBadge';
import NeuralCore from '../components/NeuralCore';
import type { DashboardMetrics, Session } from '../types';

// ==========================================
// Mock Data (used when backend unavailable)
// ==========================================
const mockMetrics: DashboardMetrics = {
  total_sessions: 247,
  vulnerabilities_fixed: 1832,
  avg_security_score: 87,
  lines_generated: 45290,
  security_health: 87,
  recent_sessions: [
    {
      id: '1', task: 'Build REST API with authentication middleware', language: 'python',
      security_score: 92, rating: 5, created_at: new Date(Date.now() - 1800000).toISOString(),
      status: 'completed', code_preview: '', vulnerabilities_found: 3, vulnerabilities_fixed: 3,
    },
    {
      id: '2', task: 'Create React dashboard with data visualization', language: 'typescript',
      security_score: 78, rating: 4, created_at: new Date(Date.now() - 7200000).toISOString(),
      status: 'completed', code_preview: '', vulnerabilities_found: 5, vulnerabilities_fixed: 4,
    },
    {
      id: '3', task: 'Implement WebSocket server for real-time chat', language: 'javascript',
      security_score: 65, rating: 3, created_at: new Date(Date.now() - 14400000).toISOString(),
      status: 'completed', code_preview: '', vulnerabilities_found: 7, vulnerabilities_fixed: 5,
    },
    {
      id: '4', task: 'Build gRPC microservice with health checks', language: 'go',
      security_score: 95, rating: 5, created_at: new Date(Date.now() - 28800000).toISOString(),
      status: 'completed', code_preview: '', vulnerabilities_found: 1, vulnerabilities_fixed: 1,
    },
    {
      id: '5', task: 'Design database schema migration system', language: 'python',
      security_score: 88, rating: 4, created_at: new Date(Date.now() - 43200000).toISOString(),
      status: 'in_progress', code_preview: '', vulnerabilities_found: 2, vulnerabilities_fixed: 1,
    },
  ],
};

// ==========================================
// Animated Counter Hook
// ==========================================
function useAnimatedCounter(target: number, duration = 2000) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
      start = Math.floor(eased * target);
      setCount(start);
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [target, duration]);

  return count;
}

// ==========================================
// Typing Effect Hook
// ==========================================
function useTypingEffect(text: string, speed = 80) {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    let index = 0;
    setDisplayed('');
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayed(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(timer);
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);

  return displayed;
}

// ==========================================
// Sub-Components
// ==========================================

function MetricCard({
  icon: Icon,
  label,
  value,
  suffix,
  color,
  delay,
}: {
  icon: typeof Activity;
  label: string;
  value: number;
  suffix?: string;
  color: string;
  delay: number;
}) {
  const animatedValue = useAnimatedCounter(value);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="glass-card-hover p-6 relative overflow-hidden group"
    >
      <div
        className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-[0.07] -translate-y-1/2 translate-x-1/2 transition-opacity group-hover:opacity-[0.12]"
        style={{ background: `radial-gradient(circle, ${color}, transparent)` }}
      />
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: `${color}15`, border: `1px solid ${color}30` }}
        >
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        <TrendingUp className="w-4 h-4 text-[#10B981]" />
      </div>
      <div className="text-3xl font-bold text-[#F1F5F9] mb-1 tabular-nums">
        {animatedValue.toLocaleString()}
        {suffix && <span className="text-lg text-[#94A3B8] ml-1">{suffix}</span>}
      </div>
      <p className="text-sm text-[#94A3B8]">{label}</p>
    </motion.div>
  );
}

function SessionCard({ session, index }: { session: Session; index: number }) {
  const statusConfig = {
    completed: { icon: CheckCircle2, color: '#10B981', label: 'Completed' },
    failed: { icon: XCircle, color: '#EF4444', label: 'Failed' },
    in_progress: { icon: Clock, color: '#F59E0B', label: 'In Progress' },
  };

  const config = statusConfig[session.status];
  const StatusIcon = config.icon;
  const timeAgo = getTimeAgo(session.created_at);

  const scoreColor =
    session.security_score >= 80 ? '#10B981' :
    session.security_score >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      whileHover={{ x: 4 }}
      className="flex items-center gap-4 p-4 rounded-xl bg-[#141416]/50 hover:bg-[#202025] transition-all cursor-pointer border border-transparent hover:border-[#2A2A30]/50"
    >
      <div className="flex-shrink-0">
        <StatusIcon className="w-5 h-5" style={{ color: config.color }} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-[#F1F5F9] truncate">{session.task}</p>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-xs text-[#475569]">{timeAgo}</span>
          <span className="badge badge-info !py-0 !text-[9px]">{session.language}</span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-sm font-semibold tabular-nums" style={{ color: scoreColor }}>
            {session.security_score}
          </div>
          <div className="text-[10px] text-[#475569]">score</div>
        </div>
        {session.security_score < 70 && <SecurityBadge severity="Medium" size="sm" />}
      </div>
    </motion.div>
  );
}

function getTimeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

// ==========================================
// Threat Ticker
// ==========================================
function ThreatTicker() {
  const [messages, setMessages] = useState<string[]>(['Initialize DevShield Ticker...']);
  
  useEffect(() => {
    const logs = [
      '[SHIELD] 0x48FA Blocked SQL Injection attempt from 192.168.1.4',
      '[GEN] Optimizing Python AST...',
      '[SEC] Analyzing dependencies for CVE-2023-XXXX',
      '[SHIELD] Sandbox active. Restricting OS-level calls.',
      '[AUTH] JWT Token issued successfully',
      '[GEN] Refactoring complete. 2 vulnerabilities patched.',
      '[SYS] psutil: CPU 4% | RAM 16GB / 64GB',
    ];
    let i = 0;
    const interval = setInterval(() => {
      setMessages(prev => {
        const next = [...prev, logs[i % logs.length]];
        if (next.length > 5) next.shift();
        return next;
      });
      i++;
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed bottom-0 left-0 right-0 h-8 bg-[#080809] border-t border-[rgba(255,255,255,0.06)] flex items-center px-4 font-mono text-[10px] uppercase text-[#64748B] overflow-hidden z-50">
      <div className="flex items-center gap-2 text-[#10B981] font-bold mr-4">
        <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
        LIVE
      </div>
      <div className="flex flex-col flex-1 overflow-hidden h-full justify-center">
        <motion.div
           key={messages[messages.length - 1]}
           initial={{ y: 20, opacity: 0 }}
           animate={{ y: 0, opacity: 1 }}
           className="truncate"
        >
          {messages[messages.length - 1]}
        </motion.div>
      </div>
    </div>
  );
}

// ==========================================
// Dashboard Page
// ==========================================
export default function Dashboard() {
  const navigate = useNavigate();
  const [metrics] = useState<DashboardMetrics>(mockMetrics);
  const greeting = useTypingEffect('Welcome back, Sahil', 60);

  const healthData = [
    {
      name: 'Security',
      value: metrics.security_health,
      fill: metrics.security_health >= 80 ? '#10B981' : metrics.security_health >= 60 ? '#F59E0B' : '#EF4444',
    },
  ];

  const quickActions = [
    { label: 'Generate Code', icon: Code2, path: '/generate', color: '#3B82F6' },
    { label: 'Scan Code', icon: Shield, path: '/security', color: '#8B5CF6' },
    { label: 'Generate Docs', icon: FileText, path: '/docs', color: '#10B981' },
  ];

  const handleQuickAction = useCallback((path: string) => {
    navigate(path);
  }, [navigate]);

  return (
    <div className="page-container relative pb-12">
      <ParticleBackground />
      <NeuralCore />

      <div className="relative z-10 space-y-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-6 h-6 text-[#F59E0B]" />
            <h1 className="text-3xl md:text-4xl font-bold text-[#F1F5F9]">
              {greeting}
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="inline-block w-0.5 h-8 bg-[#3B82F6] ml-1 align-middle"
              />
            </h1>
          </div>
          <p className="text-[#94A3B8] text-base">
            Your AI-powered security co-pilot is ready. Here's your development overview.
          </p>
        </motion.div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <MetricCard
            icon={Activity}
            label="Total Sessions"
            value={metrics.total_sessions}
            color="#3B82F6"
            delay={0.1}
          />
          <MetricCard
            icon={Bug}
            label="Vulnerabilities Fixed"
            value={metrics.vulnerabilities_fixed}
            color="#EF4444"
            delay={0.2}
          />
          <MetricCard
            icon={Shield}
            label="Security Score Avg"
            value={metrics.avg_security_score}
            suffix="%"
            color="#10B981"
            delay={0.3}
          />
          <MetricCard
            icon={Code2}
            label="Lines Generated"
            value={metrics.lines_generated}
            color="#8B5CF6"
            delay={0.4}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Feed */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="lg:col-span-2 glass-card p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-[#F1F5F9]">Recent Activity</h2>
              <button
                onClick={() => navigate('/history')}
                className="text-sm text-[#3B82F6] hover:text-[#60A5FA] transition-colors flex items-center gap-1"
              >
                View all <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="space-y-2">
              {metrics.recent_sessions.map((session, i) => (
                <SessionCard key={session.id} session={session} index={i} />
              ))}
            </div>
          </motion.div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Security Health Chart */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="glass-card p-6"
            >
              <h2 className="text-lg font-semibold text-[#F1F5F9] mb-4">Security Health</h2>
              <div className="relative">
                <ResponsiveContainer width="100%" height={200}>
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="60%"
                    outerRadius="90%"
                    barSize={12}
                    data={healthData}
                    startAngle={210}
                    endAngle={-30}
                  >
                    <RadialBar
                      dataKey="value"
                      cornerRadius={10}
                      background={{ fill: '#1A1A1E' }}
                    />
                    <Tooltip />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-[#F1F5F9]">{metrics.security_health}</span>
                  <span className="text-sm text-[#94A3B8]">/ 100</span>
                </div>
              </div>
              <div className="text-center mt-2">
                <SecurityBadge
                  severity={
                    metrics.security_health >= 80 ? 'Low' :
                    metrics.security_health >= 60 ? 'Medium' : 'High'
                  }
                />
                <p className="text-xs text-[#475569] mt-2">
                  {metrics.security_health >= 80 ? 'Your code is well-secured' : 'Room for improvement'}
                </p>
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="glass-card p-6"
            >
              <h2 className="text-lg font-semibold text-[#F1F5F9] mb-4">Quick Actions</h2>
              <div className="space-y-3">
                {quickActions.map((action) => {
                  const ActionIcon = action.icon;
                  return (
                    <motion.button
                      key={action.path}
                      onClick={() => handleQuickAction(action.path)}
                      className="w-full flex items-center gap-3 p-3 rounded-xl bg-[#141416]
                                 hover:bg-[#202025] border border-[#2A2A30]/50
                                 hover:border-opacity-100 transition-all text-left group"
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div
                        className="w-9 h-9 rounded-lg flex items-center justify-center"
                        style={{ background: `${action.color}15`, border: `1px solid ${action.color}30` }}
                      >
                        <ActionIcon className="w-4 h-4" style={{ color: action.color }} />
                      </div>
                      <span className="text-sm font-medium text-[#94A3B8] group-hover:text-[#F1F5F9] transition-colors">
                        {action.label}
                      </span>
                      <ArrowRight className="w-4 h-4 text-[#475569] ml-auto group-hover:text-[#94A3B8] transition-colors" />
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
      
      <ThreatTicker />
    </div>
  );
}
