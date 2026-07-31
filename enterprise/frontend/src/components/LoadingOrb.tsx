import { motion } from 'framer-motion';

interface LoadingOrbProps {
  size?: number;
  text?: string;
}

export default function LoadingOrb({ size = 80, text }: LoadingOrbProps) {
  return (
    <div className="flex flex-col items-center gap-4" role="status" aria-label="Loading">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Outer ring */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            border: '2px solid transparent',
            borderTopColor: '#3B82F6',
            borderRightColor: '#8B5CF6',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        />

        {/* Middle ring */}
        <motion.div
          className="absolute rounded-full"
          style={{
            top: size * 0.1,
            left: size * 0.1,
            right: size * 0.1,
            bottom: size * 0.1,
            border: '2px solid transparent',
            borderBottomColor: '#8B5CF6',
            borderLeftColor: '#3B82F6',
          }}
          animate={{ rotate: -360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />

        {/* Inner ring */}
        <motion.div
          className="absolute rounded-full"
          style={{
            top: size * 0.2,
            left: size * 0.2,
            right: size * 0.2,
            bottom: size * 0.2,
            border: '1.5px solid transparent',
            borderTopColor: '#10B981',
            borderRightColor: '#3B82F6',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />

        {/* Glowing core */}
        <motion.div
          className="absolute rounded-full"
          style={{
            top: size * 0.3,
            left: size * 0.3,
            right: size * 0.3,
            bottom: size * 0.3,
            background: 'radial-gradient(circle, rgba(59,130,246,0.6) 0%, rgba(139,92,246,0.3) 60%, transparent 100%)',
          }}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.6, 1, 0.6],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Central dot */}
        <motion.div
          className="absolute rounded-full bg-white"
          style={{
            top: '50%',
            left: '50%',
            width: size * 0.08,
            height: size * 0.08,
            marginTop: -(size * 0.04),
            marginLeft: -(size * 0.04),
          }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      </div>

      {text && (
        <motion.p
          className="text-sm font-medium text-[#94A3B8]"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          {text}
        </motion.p>
      )}
    </div>
  );
}
