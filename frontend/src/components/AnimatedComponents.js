import React from 'react';
import { motion } from 'framer-motion';

export const WaterFlowAnimation = ({ isFlowing = true, flowRate = 50 }) => {
  const speed = isFlowing ? Math.max(0.8, 2.5 - (flowRate / 100) * 1.5) : 0;
  
  return (
    <div className="relative w-full h-32 rounded-2xl overflow-hidden shadow-2xl border border-blue-200">
      {/* Animated mesh gradient background - ultra modern */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.3), transparent 50%), radial-gradient(circle at 80% 50%, rgba(14, 165, 233, 0.3), transparent 50%)',
        }}
        animate={isFlowing ? {
          opacity: [0.4, 0.7, 0.4],
        } : {}}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Glassmorphism base */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-50" />

      {/* Dynamic liquid blob animation */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 50% 120%, rgba(59, 130, 246, 0.6) 0%, rgba(96, 165, 250, 0.4) 40%, transparent 70%)',
          filter: 'blur(20px)',
        }}
        animate={isFlowing ? {
          scale: [1, 1.2, 1],
          y: [0, -10, 0],
        } : {}}
        transition={{
          duration: speed * 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Fluid wave layers - smooth organic movement */}
      {isFlowing && [0, 1, 2].map((i) => (
        <motion.div
          key={`wave-layer-${i}`}
          className="absolute left-0 right-0 bottom-0 h-20"
          style={{
            background: `linear-gradient(to top, rgba(59, 130, 246, ${0.5 - i * 0.15}), transparent)`,
            borderRadius: '50% 50% 0 0 / 20% 20% 0 0',
          }}
          animate={{
            y: [-5, 5, -5],
            scaleX: [1, 1.05, 1],
          }}
          transition={{
            duration: speed * (1.2 + i * 0.3),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.2,
          }}
        />
      ))}

      {/* Energetic particles stream */}
      {isFlowing && [0, 1, 2, 3, 4].map((i) => (
        <motion.div
          key={`energy-particle-${i}`}
          className="absolute rounded-full"
          style={{
            width: `${4 + Math.random() * 6}px`,
            height: `${4 + Math.random() * 6}px`,
            left: `${10 + i * 20}%`,
            background: 'radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(147, 197, 253, 0.8) 100%)',
            boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)',
          }}
          animate={{
            y: [140, -20],
            opacity: [0, 1, 1, 0],
            scale: [0.3, 1, 1.2, 0.5],
            x: [0, (Math.random() - 0.5) * 40],
          }}
          transition={{
            duration: speed * 2,
            repeat: Infinity,
            delay: i * 0.4,
            ease: "easeOut"
          }}
        />
      ))}

      {/* Concentric pulse rings - sci-fi effect */}
      {isFlowing && [0, 1, 2].map((i) => (
        <motion.div
          key={`pulse-ring-${i}`}
          className="absolute left-1/2 bottom-4 w-20 h-20 border-2 rounded-full"
          style={{
            borderColor: 'rgba(59, 130, 246, 0.6)',
            transform: 'translateX(-50%)',
          }}
          animate={{
            scale: [0.5, 3],
            opacity: [0.8, 0],
            borderWidth: ['2px', '0px'],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            delay: i * 0.8,
            ease: "easeOut"
          }}
        />
      ))}

      {/* Shimmer light effect */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%)',
          width: '50%',
        }}
        animate={isFlowing ? {
          x: ['-100%', '250%'],
        } : {}}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Modern status badge with glow */}
      <motion.div 
        className="absolute top-4 right-4 flex items-center space-x-2 bg-white/90 backdrop-blur-md px-4 py-2 rounded-full shadow-xl border border-blue-200"
        animate={isFlowing ? {
          boxShadow: [
            '0 4px 20px rgba(59, 130, 246, 0.3)',
            '0 4px 30px rgba(59, 130, 246, 0.5)',
            '0 4px 20px rgba(59, 130, 246, 0.3)',
          ],
        } : {}}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        <motion.div
          className={`w-2.5 h-2.5 rounded-full ${isFlowing ? 'bg-green-500' : 'bg-gray-400'}`}
          animate={isFlowing ? {
            scale: [1, 1.3, 1],
            boxShadow: [
              '0 0 5px rgba(34, 197, 94, 0.5)',
              '0 0 15px rgba(34, 197, 94, 0.8)',
              '0 0 5px rgba(34, 197, 94, 0.5)',
            ],
          } : {}}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
        />
        <span className={`text-xs font-bold ${isFlowing ? 'text-blue-600' : 'text-gray-500'}`}>
          {isFlowing ? 'ACTIVE' : 'IDLE'}
        </span>
      </motion.div>

      {/* Flow rate visualization - modern progress bar */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-blue-600">Flow Rate</span>
          <span className="text-xs font-bold text-blue-700">{Math.round(flowRate)}%</span>
        </div>
        <div className="relative h-2.5 bg-white/60 backdrop-blur-sm rounded-full overflow-hidden shadow-inner">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              background: 'linear-gradient(90deg, #3b82f6 0%, #06b6d4 50%, #8b5cf6 100%)',
              boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)',
            }}
            initial={{ width: '0%' }}
            animate={{ width: `${flowRate}%` }}
            transition={{
              duration: 0.6,
              ease: "easeOut"
            }}
          />
          {/* Animated shimmer on progress bar */}
          {isFlowing && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.6) 50%, transparent 100%)',
                width: '30%',
              }}
              animate={{
                x: ['-30%', '130%'],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          )}
        </div>
      </div>

      {/* Ambient glow effect */}
      {isFlowing && (
        <motion.div
          className="absolute inset-0 rounded-2xl"
          style={{
            boxShadow: 'inset 0 0 50px rgba(59, 130, 246, 0.2)',
          }}
          animate={{
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}
    </div>
  );
};

export const AnimatedCounter = ({ value, suffix = '', decimals = 0 }) => {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {typeof value === 'number' ? value.toFixed(decimals) : value}{suffix}
    </motion.span>
  );
};

export const PulsingDot = ({ color = 'blue', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };
  
  return (
    <div className="relative inline-flex">
      <motion.div
        className={`${sizeClasses[size]} bg-${color}-500 rounded-full`}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [1, 0.8, 1]
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className={`absolute inset-0 bg-${color}-400 rounded-full`}
        animate={{
          scale: [1, 1.5, 2],
          opacity: [0.5, 0.3, 0]
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut"
        }}
      />
    </div>
  );
};

export const WaterDropletIcon = ({ className = '' }) => {
  return (
    <motion.svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      initial={{ scale: 0.9 }}
      animate={{ 
        scale: [0.9, 1.1, 0.9],
        y: [0, -2, 0]
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
    </motion.svg>
  );
};

export const LeakAlertAnimation = () => {
  return (
    <motion.div
      className="relative w-12 h-12"
      animate={{
        rotate: [0, -10, 10, -10, 0],
      }}
      transition={{
        duration: 0.5,
        repeat: Infinity,
        repeatDelay: 2
      }}
    >
      <motion.div
        className="absolute inset-0 bg-red-500 rounded-full opacity-20"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0, 0.2]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
    </motion.div>
  );
};

export const GaugeAnimation = ({ value = 0, max = 100, label = '' }) => {
  // Calculate angle for gauge (0-180 degrees)
  const angle = (value / max) * 180 - 90;
  const percentage = (value / max) * 100;
  
  // Determine color based on percentage
  const getColor = () => {
    if (percentage > 80) return 'text-red-500';
    if (percentage > 50) return 'text-yellow-500';
    return 'text-green-500';
  };
  
  return (
    <div className="relative w-full">
      <svg viewBox="0 0 200 120" className="w-full">
        {/* Background arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="12"
          strokeLinecap="round"
        />
        
        {/* Colored arc */}
        <motion.path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="currentColor"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray="251.2"
          initial={{ strokeDashoffset: 251.2 }}
          animate={{ strokeDashoffset: 251.2 - (251.2 * percentage / 100) }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={getColor()}
        />
        
        {/* Needle */}
        <motion.line
          x1="100"
          y1="100"
          x2="100"
          y2="30"
          stroke="#374151"
          strokeWidth="3"
          strokeLinecap="round"
          initial={{ rotate: -90 }}
          animate={{ rotate: angle }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{ transformOrigin: '100px 100px' }}
        />
        
        {/* Center dot */}
        <circle cx="100" cy="100" r="8" fill="#374151" />
      </svg>
      
      {/* Value display */}
      <div className="text-center -mt-8">
        <motion.div 
          className={`text-3xl font-bold ${getColor()}`}
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {value.toFixed(1)}
        </motion.div>
        <div className="text-sm text-gray-500">{label}</div>
      </div>
    </div>
  );
};
