import { motion } from 'framer-motion';
import { useState } from 'react';
import { Star, Clock, CheckCircle2, XCircle, Code2, ShieldAlert } from 'lucide-react';
import type { Session } from '../types';

const MOCK_HISTORY: Session[] = [
  {
    id: '1',
    task: 'Build REST API with authentication middleware',
    language: 'python',
    security_score: 92,
    rating: 5,
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'completed',
    code_preview: 'import hashlib...',
    vulnerabilities_found: 3,
    vulnerabilities_fixed: 3,
  },
  {
    id: '2',
    task: 'Create React dashboard with data visualization',
    language: 'typescript',
    security_score: 78,
    rating: 4,
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    status: 'completed',
    code_preview: 'import React...',
    vulnerabilities_found: 5,
    vulnerabilities_fixed: 4,
  },
  {
    id: '3',
    task: 'Implement WebSocket server for chat',
    language: 'javascript',
    security_score: 65,
    rating: 0,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    status: 'failed',
    code_preview: 'const ws = new WebSocket...',
    vulnerabilities_found: 7,
    vulnerabilities_fixed: 5,
  },
];

function StarRating({ rating, onRate }: { rating: number; onRate: (r: number) => void }) {
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <motion.button
          key={star}
          onMouseEnter={() => setHoverRating(star)}
          onMouseLeave={() => setHoverRating(0)}
          onClick={() => onRate(star)}
          className="p-1 -m-1 focus:outline-none"
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.9 }}
        >
          <Star
            className={`w-4 h-4 transition-colors ${
              star <= (hoverRating || rating)
                ? 'fill-[#F59E0B] text-[#F59E0B]'
                : 'text-[#475569]'
            }`}
          />
        </motion.button>
      ))}
    </div>
  );
}

export default function History() {
  const [history, setHistory] = useState(MOCK_HISTORY);

  const handleRate = (id: string, rating: number) => {
    setHistory((prev) =>
      prev.map((session) => (session.id === id ? { ...session, rating } : session))
    );
  };

  const getTimeAgo = (dateStr: string) => {
    const hours = Math.floor((Date.now() - new Date(dateStr).getTime()) / 3600000);
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h2 className="text-2xl font-bold text-[#F8FAFC] flex items-center gap-2">
          <Clock className="w-6 h-6 text-[#3B82F6]" />
          Session History
        </h2>
        <p className="text-sm text-[#64748B] mt-1">
          Review past generations, scans, and provide feedback to improve the DevShield AI.
        </p>
      </motion.div>

      <div className="relative">
        <div className="absolute left-6 top-0 bottom-0 w-px bg-[#2A2A30]" />

        <div className="space-y-8">
          {history.map((session, index) => {
            const isSuccess = session.status === 'completed';
            const StatusIcon = isSuccess ? CheckCircle2 : XCircle;
            const statusColor = isSuccess ? '#10B981' : '#EF4444';

            return (
              <motion.div
                key={session.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="relative pl-16 group"
              >
                {/* Timeline Dot */}
                <div
                  className="absolute left-[24px] top-6 w-3 h-3 rounded-full -translate-x-1/2 outline outline-4 outline-[#080809] z-10 transition-transform group-hover:scale-125"
                  style={{ backgroundColor: statusColor }}
                />

                {/* Card hover lift */}
                <motion.div
                  className="glass-card p-5 hover:border-[rgba(59,130,246,0.3)] transition-all bg-[#0F0F12]"
                  whileHover={{ y: -4, boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }}
                >
                  <div className="flex flex-col md:flex-row justify-between gap-4 mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <StatusIcon className="w-4 h-4" style={{ color: statusColor }} />
                        <h3 className="text-base font-semibold text-[#F8FAFC]">{session.task}</h3>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-[#64748B] ml-7">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {getTimeAgo(session.created_at)}
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-[#16161A] border border-[rgba(255,255,255,0.06)] text-[#CBD5E1] uppercase tracking-widest text-[9px] font-bold">
                          {session.language}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-row md:flex-col items-center md:items-end gap-3 md:gap-1 pl-7 md:pl-0">
                      <div className="text-xs font-medium text-[#64748B]">Security Score</div>
                      <div
                        className="text-xl font-bold tabular-nums leading-none"
                        style={{
                          color:
                            session.security_score >= 80
                              ? '#10B981'
                              : session.security_score >= 60
                              ? '#F59E0B'
                              : '#EF4444',
                        }}
                      >
                        {session.security_score}
                      </div>
                    </div>
                  </div>

                  <div className="ml-7 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between border-t border-[rgba(255,255,255,0.06)] pt-4">
                    <div className="flex items-center gap-4 text-sm text-[#CBD5E1]">
                      <div className="flex items-center gap-1.5" title="Generate Code Length">
                        <Code2 className="w-4 h-4 text-[#8B5CF6]" />
                        <span>Code gen</span>
                      </div>
                      <div className="flex items-center gap-1.5" title="Vulnerabilities fixed">
                        <ShieldAlert className="w-4 h-4 text-[#F59E0B]" />
                        <span>{session.vulnerabilities_fixed}/{session.vulnerabilities_found} fixed</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs text-[#64748B]">Rate this session</span>
                      <StarRating
                        rating={session.rating}
                        onRate={(r) => handleRate(session.id, r)}
                      />
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
