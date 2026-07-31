import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { Bell, Sun, Moon, Wifi, WifiOff } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useAIStatusStore, useNotificationStore, usePreferencesStore } from '../store';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/generate': 'Code Generator',
  '/security': 'Security Analyzer',
  '/docs': 'Documentation',
  '/history': 'Session History',
  '/analytics': 'Usage Analytics',
  '/settings': 'Settings',
};

export default function TopBar() {
  const location = useLocation();
  const { status, provider, tokensRemaining } = useAIStatusStore();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotificationStore();
  const { preferences, updatePreference } = usePreferencesStore();
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  const title = pageTitles[location.pathname] || 'DevShield';

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const statusColor = status === 'active' ? '#10B981' : status === 'fallback' ? '#F59E0B' : '#EF4444';
  const statusLabel = status === 'active' ? `${provider === 'gemini' ? 'Gemini' : 'Claude'} Active` : status === 'fallback' ? 'Claude Fallback' : 'Offline';

  const formatTokens = (tokens: number): string => {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(0)}K`;
    return tokens.toString();
  };

  return (
    <header
      className="sticky top-0 z-30 flex items-center justify-between px-8 py-4"
      style={{
        background: 'rgba(13, 13, 15, 0.8)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(42, 42, 48, 0.3)',
      }}
      id="top-bar"
    >
      {/* Page Title */}
      <motion.h1
        key={location.pathname}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="text-xl font-semibold text-[#F1F5F9]"
      >
        {title}
      </motion.h1>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* AI Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141416] border border-[#2A2A30]/50">
          {status === 'offline' ? (
            <WifiOff className="w-3.5 h-3.5 text-[#EF4444]" />
          ) : (
            <Wifi className="w-3.5 h-3.5" style={{ color: statusColor }} />
          )}
          <motion.div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: statusColor }}
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span className="text-xs font-medium text-[#94A3B8]">{statusLabel}</span>
        </div>

        {/* Token Budget */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141416] border border-[#2A2A30]/50">
          <div className="w-1.5 h-1.5 rounded-full bg-[#8B5CF6]" />
          <span className="text-xs font-medium text-[#94A3B8]">
            {formatTokens(tokensRemaining)} tokens
          </span>
        </div>

        {/* Notification Bell */}
        <div className="relative" ref={notifRef}>
          <motion.button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg hover:bg-[#202025] transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="Notifications"
            id="notification-bell"
          >
            <Bell className="w-5 h-5 text-[#94A3B8]" />
            {unreadCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#EF4444] rounded-full
                           text-[10px] font-bold text-white flex items-center justify-center"
              >
                {unreadCount}
              </motion.span>
            )}
          </motion.button>

          {/* Notification Dropdown */}
          <AnimatePresence>
            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 mt-2 w-80 rounded-xl overflow-hidden"
                style={{
                  background: '#1A1A1E',
                  border: '1px solid #2A2A30',
                  boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
                }}
              >
                <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A30]">
                  <span className="text-sm font-semibold text-[#F1F5F9]">Notifications</span>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-[#3B82F6] hover:text-[#60A5FA] transition-colors"
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-8 text-center text-sm text-[#475569]">
                      No notifications
                    </div>
                  ) : (
                    notifications.map((notif) => (
                      <motion.div
                        key={notif.id}
                        onClick={() => markAsRead(notif.id)}
                        className={`px-4 py-3 cursor-pointer hover:bg-[#202025] transition-colors
                          border-b border-[#2A2A30]/50 ${!notif.read ? 'bg-[#3B82F6]/5' : ''}`}
                        whileHover={{ x: 4 }}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                              notif.read ? 'bg-transparent' : 'bg-[#3B82F6]'
                            }`}
                          />
                          <div>
                            <p className="text-sm font-medium text-[#F1F5F9]">{notif.title}</p>
                            <p className="text-xs text-[#94A3B8] mt-0.5">{notif.message}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Theme Toggle */}
        <motion.button
          onClick={() =>
            updatePreference('theme', preferences.theme === 'dark' ? 'light' : 'dark')
          }
          className="p-2 rounded-lg hover:bg-[#202025] transition-colors"
          whileHover={{ scale: 1.05, rotate: 15 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Toggle theme"
          id="theme-toggle"
        >
          {preferences.theme === 'dark' ? (
            <Sun className="w-5 h-5 text-[#F59E0B]" />
          ) : (
            <Moon className="w-5 h-5 text-[#8B5CF6]" />
          )}
        </motion.button>
      </div>
    </header>
  );
}
