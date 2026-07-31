import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Code2,
  Shield,
  FileText,
  History,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react';
import { useSidebarStore } from '../store';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/generate', label: 'Code Generator', icon: Code2 },
  { path: '/security', label: 'Security Analyzer', icon: Shield },
  { path: '/docs', label: 'Documentation', icon: FileText },
  { path: '/history', label: 'History', icon: History },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const { collapsed, toggle } = useSidebarStore();
  const location = useLocation();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-0 top-0 h-screen z-40 flex flex-col"
      style={{
        background: 'linear-gradient(180deg, #111114 0%, #0D0D0F 100%)',
        borderRight: '1px solid rgba(42, 42, 48, 0.5)',
      }}
      id="sidebar-nav"
    >
      {/* Logo Section */}
      <div className="flex items-center gap-3 px-5 py-6 min-h-[72px]">
        <motion.div
          className="relative flex-shrink-0"
          whileHover={{ rotate: 15, scale: 1.1 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <motion.div
            className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-[#10B981]"
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </motion.div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <h1 className="text-lg font-bold tracking-tight">
                <span className="text-[#F1F5F9]">Dev</span>
                <span className="text-gradient-blue">Shield</span>
              </h1>
              <p className="text-[10px] text-[#475569] font-medium tracking-wider uppercase">
                AI Security Platform
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto" aria-label="Main navigation">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              id={`nav-${item.path.replace('/', '') || 'dashboard'}`}
              className="block relative"
            >
              <motion.div
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer
                  transition-colors duration-200 relative group
                  ${isActive
                    ? 'bg-gradient-to-r from-[#3B82F6]/15 to-[#8B5CF6]/10 text-[#F1F5F9]'
                    : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#202025]'
                  }
                `}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
                transition={{ duration: 0.15 }}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 bg-gradient-to-b from-[#3B82F6] to-[#8B5CF6] rounded-full"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
                <Icon
                  className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-[#3B82F6]' : ''}`}
                />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 0.2 }}
                      className="text-sm font-medium whitespace-nowrap overflow-hidden"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            </NavLink>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="px-3 pb-4">
        <div
          className={`
            flex items-center gap-3 px-3 py-3 rounded-xl
            bg-[#141416] border border-[#2A2A30]/50
            ${collapsed ? 'justify-center' : ''}
          `}
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#3B82F6] flex items-center justify-center flex-shrink-0 text-xs font-bold text-white">
            S
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-sm font-medium text-[#F1F5F9] truncate">Sahil</p>
                <div className="flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-[#F59E0B]" />
                  <span className="text-[10px] text-[#94A3B8]">Pro Plan</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Collapse Toggle */}
        <motion.button
          onClick={toggle}
          className="w-full mt-3 flex items-center justify-center py-2 rounded-lg
                     text-[#475569] hover:text-[#94A3B8] hover:bg-[#202025]
                     transition-colors duration-200"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </motion.button>
      </div>
    </motion.aside>
  );
}
