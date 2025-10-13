import React from 'react';
import { motion } from 'framer-motion';

export const WaterFlowAnimation = ({ isFlowing = true, flowRate = 50 }) => {
  // Calculate animation speed based on flow rate (0-100)
  const animationDuration = Math.max(0.5, 2 - (flowRate / 100) * 1.5);
  
  return (
    <div className="relative w-full h-32 bg-gradient-to-b from-blue-50 to-blue-100 rounded-lg overflow-hidden">
      {/* Animated water drops */}
      {isFlowing && [...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-3 bg-blue-400 rounded-full opacity-70"
          initial={{ 
            x: `${10 + i * 12}%`, 
            y: -20,
            scale: 0.8 + Math.random() * 0.4
          }}
          animate={{ 
            y: 140,
            opacity: [0, 1, 1, 0]
          }}
          transition={{
            duration: animationDuration,
            repeat: Infinity,
            delay: i * (animationDuration / 8),
            ease: "easeIn"
          }}
        />
      ))}
      
      {/* Animated waves at the bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-16">
        <motion.div
          className="absolute inset-0 bg-gradient-to-t from-blue-400 to-blue-300"
          animate={{
            y: isFlowing ? [0, -4, 0] : 0,
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            borderRadius: "50% 50% 0 0"
          }}
        />
        
        {/* Secondary wave */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-t from-blue-300 to-transparent opacity-50"
          animate={{
            y: isFlowing ? [-2, 2, -2] : 0,
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.5
          }}
          style={{
            borderRadius: "50% 50% 0 0"
          }}
        />
      </div>
      
      {/* Flow rate indicator */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-90 px-3 py-1 rounded-full text-xs font-semibold text-blue-600">
        {isFlowing ? `${flowRate}%` : 'No Flow'}
      </div>
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
