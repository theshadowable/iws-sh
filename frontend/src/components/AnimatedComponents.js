import React from 'react';
import { motion } from 'framer-motion';

export const WaterFlowAnimation = ({ isFlowing = true, flowRate = 50 }) => {
  // Calculate animation speed based on flow rate (0-100)
  const animationDuration = Math.max(1, 3 - (flowRate / 100) * 2);
  
  return (
    <div className="relative w-full h-32 bg-gradient-to-b from-blue-50 via-blue-100 to-blue-200 rounded-lg overflow-hidden shadow-inner">
      {/* Multiple wave layers for ripple effect */}
      <motion.div
        className="absolute bottom-0 left-0 right-0 h-20"
        style={{
          background: 'linear-gradient(to top, rgba(59, 130, 246, 0.8), rgba(96, 165, 250, 0.6))',
        }}
      >
        {/* First wave layer */}
        <motion.div
          className="absolute inset-0"
          animate={isFlowing ? {
            backgroundPosition: ['0% 0%', '100% 0%'],
          } : {}}
          transition={{
            duration: animationDuration * 1.5,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{
            background: 'repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(255,255,255,0.1) 40px, rgba(255,255,255,0.1) 80px)',
            backgroundSize: '80px 100%',
          }}
        />
        
        {/* Animated ripple waves */}
        {isFlowing && [...Array(3)].map((_, i) => (
          <motion.div
            key={`ripple-${i}`}
            className="absolute inset-0"
            initial={{ 
              y: '100%',
              opacity: 0.4
            }}
            animate={{
              y: ['-100%', '-100%'],
              opacity: [0.4, 0]
            }}
            transition={{
              duration: animationDuration,
              repeat: Infinity,
              delay: i * (animationDuration / 3),
              ease: "linear"
            }}
            style={{
              background: `radial-gradient(ellipse at 50% 50%, rgba(147, 197, 253, 0.4) 0%, transparent 60%)`,
              transform: `scaleX(${1 + i * 0.3})`
            }}
          />
        ))}
      </motion.div>
      
      {/* Top wave border with organic movement */}
      <svg className="absolute bottom-16 left-0 right-0 w-full" style={{ height: '40px' }} preserveAspectRatio="none">
        <motion.path
          d="M0,20 Q25,10 50,20 T100,20 T150,20 T200,20 T250,20 T300,20 T350,20 T400,20 V40 H0 Z"
          fill="rgba(59, 130, 246, 0.9)"
          animate={isFlowing ? {
            d: [
              "M0,20 Q25,10 50,20 T100,20 T150,20 T200,20 T250,20 T300,20 T350,20 T400,20 V40 H0 Z",
              "M0,20 Q25,30 50,20 T100,20 T150,20 T200,20 T250,20 T300,20 T350,20 T400,20 V40 H0 Z",
              "M0,20 Q25,10 50,20 T100,20 T150,20 T200,20 T250,20 T300,20 T350,20 T400,20 V40 H0 Z"
            ]
          } : {}}
          transition={{
            duration: animationDuration,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </svg>
      
      {/* Secondary wave for depth */}
      <svg className="absolute bottom-16 left-0 right-0 w-full opacity-60" style={{ height: '40px' }} preserveAspectRatio="none">
        <motion.path
          d="M0,25 Q30,15 60,25 T120,25 T180,25 T240,25 T300,25 T360,25 T420,25 V40 H0 Z"
          fill="rgba(96, 165, 250, 0.7)"
          animate={isFlowing ? {
            d: [
              "M0,25 Q30,15 60,25 T120,25 T180,25 T240,25 T300,25 T360,25 T420,25 V40 H0 Z",
              "M0,25 Q30,35 60,25 T120,25 T180,25 T240,25 T300,25 T360,25 T420,25 V40 H0 Z",
              "M0,25 Q30,15 60,25 T120,25 T180,25 T240,25 T300,25 T360,25 T420,25 V40 H0 Z"
            ]
          } : {}}
          transition={{
            duration: animationDuration * 1.2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.3
          }}
        />
      </svg>
      
      {/* Animated water droplets/bubbles rising */}
      {isFlowing && [...Array(5)].map((_, i) => (
        <motion.div
          key={`bubble-${i}`}
          className="absolute rounded-full bg-white opacity-30"
          style={{
            width: `${6 + Math.random() * 8}px`,
            height: `${6 + Math.random() * 8}px`,
            left: `${15 + i * 18}%`,
          }}
          animate={{
            y: [130, -10],
            opacity: [0, 0.4, 0.6, 0],
            scale: [0.8, 1, 1.2, 0.8]
          }}
          transition={{
            duration: animationDuration * 0.8,
            repeat: Infinity,
            delay: i * (animationDuration / 5),
            ease: "easeOut"
          }}
        />
      ))}
      
      {/* Flow rate indicator with pulsing effect */}
      <motion.div 
        className="absolute top-4 right-4 bg-white bg-opacity-95 px-4 py-2 rounded-full text-sm font-bold shadow-md"
        animate={isFlowing ? {
          scale: [1, 1.05, 1],
        } : {}}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        <span className={`${isFlowing ? 'text-blue-600' : 'text-gray-500'}`}>
          {isFlowing ? `${flowRate}% Flow` : 'No Flow'}
        </span>
      </motion.div>
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
