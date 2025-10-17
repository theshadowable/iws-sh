import React from 'react';
import { motion } from 'framer-motion';

export const WaterFlowAnimation = ({ isFlowing = true, flowRate = 50 }) => {
  const speed = isFlowing ? Math.max(1, 3 - (flowRate / 100) * 1.5) : 0;
  const intensity = flowRate / 100;
  
  return (
    <div className="relative w-full h-32 rounded-2xl overflow-hidden shadow-2xl" style={{
      background: 'linear-gradient(180deg, rgba(14, 116, 144, 0.1) 0%, rgba(6, 182, 212, 0.2) 100%)',
      perspective: '1000px',
    }}>
      {/* 3D Water Surface Base */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at center, rgba(6, 182, 212, 0.15) 0%, rgba(14, 165, 233, 0.25) 50%, rgba(59, 130, 246, 0.2) 100%)',
          transformStyle: 'preserve-3d',
        }}
      />

      {/* 3D Liquid Layers with Depth */}
      {isFlowing && [0, 1, 2, 3].map((i) => (
        <motion.div
          key={`liquid-layer-${i}`}
          className="absolute inset-0"
          style={{
            background: `radial-gradient(ellipse at 50% ${100 + i * 10}%, 
              rgba(59, 130, 246, ${0.3 - i * 0.06}) 0%, 
              rgba(14, 165, 233, ${0.25 - i * 0.05}) 40%, 
              transparent 70%)`,
            transform: `translateZ(${-i * 15}px) rotateX(${i * 2}deg)`,
            transformStyle: 'preserve-3d',
            filter: `blur(${i * 3}px)`,
          }}
          animate={{
            y: [i * -2, i * 2, i * -2],
            scale: [1, 1 + i * 0.02, 1],
            rotateX: [i * 2, i * 2 + 1, i * 2],
          }}
          transition={{
            duration: speed * (1.5 + i * 0.3),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.15,
          }}
        />
      ))}

      {/* 3D Water Waves - Multiple Layers */}
      {isFlowing && [0, 1, 2].map((i) => (
        <motion.div
          key={`wave-3d-${i}`}
          className="absolute left-0 right-0"
          style={{
            bottom: `${10 + i * 5}%`,
            height: '40%',
            background: `linear-gradient(to top, 
              rgba(59, 130, 246, ${0.4 - i * 0.1}), 
              rgba(96, 165, 250, ${0.3 - i * 0.08}), 
              transparent)`,
            borderRadius: '50% 50% 0 0 / 30% 30% 0 0',
            transform: `translateZ(${-i * 20}px) rotateX(${5 + i * 3}deg)`,
            transformStyle: 'preserve-3d',
            boxShadow: `0 ${-4 - i * 2}px ${20 + i * 5}px rgba(59, 130, 246, 0.3)`,
          }}
          animate={{
            y: [-8 + i * 2, 8 - i * 2, -8 + i * 2],
            scaleX: [1, 1.03 + i * 0.01, 1],
            rotateX: [5 + i * 3, 6 + i * 3, 5 + i * 3],
          }}
          transition={{
            duration: speed * (1.8 + i * 0.4),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.25,
          }}
        />
      ))}

      {/* 3D Bubbles Rising */}
      {isFlowing && [0, 1, 2, 3, 4, 5, 6].map((i) => {
        const size = 8 + Math.random() * 12;
        const leftPos = 10 + i * 13;
        return (
          <motion.div
            key={`bubble-3d-${i}`}
            className="absolute rounded-full"
            style={{
              width: `${size}px`,
              height: `${size}px`,
              left: `${leftPos}%`,
              background: 'radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.9), rgba(147, 197, 253, 0.6))',
              boxShadow: `
                inset -2px -2px 4px rgba(59, 130, 246, 0.3),
                0 0 ${size}px rgba(147, 197, 253, 0.4),
                0 ${size/2}px ${size}px rgba(59, 130, 246, 0.2)
              `,
              transform: `translateZ(${Math.random() * 30}px)`,
              transformStyle: 'preserve-3d',
            }}
            animate={{
              y: [150, -30],
              opacity: [0, 0.9, 1, 0.8, 0],
              scale: [0.3, 1, 1.1, 1.2, 0.8],
              x: [0, (Math.random() - 0.5) * 50],
              z: [0, Math.random() * 20],
            }}
            transition={{
              duration: speed * (2 + Math.random()),
              repeat: Infinity,
              delay: i * 0.5,
              ease: "easeOut"
            }}
          />
        );
      })}

      {/* 3D Ripple Rings - Perspective Effect */}
      {isFlowing && [0, 1, 2, 3].map((i) => (
        <motion.div
          key={`ripple-3d-${i}`}
          className="absolute left-1/2"
          style={{
            bottom: '20%',
            width: '80px',
            height: '40px',
            border: '2px solid rgba(59, 130, 246, 0.4)',
            borderRadius: '50%',
            transform: `translateX(-50%) translateZ(${-i * 10}px) rotateX(75deg)`,
            transformStyle: 'preserve-3d',
          }}
          animate={{
            scale: [0.5, 3.5],
            opacity: [0.7, 0],
            borderWidth: ['2px', '0px'],
            rotateX: [75, 70],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.75,
            ease: "easeOut"
          }}
        />
      ))}

      {/* 3D Light Rays from Depth */}
      {isFlowing && [0, 1, 2].map((i) => (
        <motion.div
          key={`light-ray-${i}`}
          className="absolute"
          style={{
            bottom: '0',
            left: `${20 + i * 30}%`,
            width: '2px',
            height: '100%',
            background: `linear-gradient(to top, 
              rgba(147, 197, 253, 0.6), 
              transparent)`,
            transform: `translateZ(${-20 - i * 10}px) rotateX(10deg)`,
            transformStyle: 'preserve-3d',
            filter: 'blur(2px)',
          }}
          animate={{
            opacity: [0.3, 0.7, 0.3],
            scaleY: [0.8, 1.2, 0.8],
          }}
          transition={{
            duration: speed * 1.5,
            repeat: Infinity,
            delay: i * 0.5,
            ease: "easeInOut"
          }}
        />
      ))}

      {/* 3D Caustic Light Effect */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse at 30% 40%, rgba(147, 197, 253, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 70% 60%, rgba(59, 130, 246, 0.25) 0%, transparent 50%)
          `,
          transform: 'translateZ(-30px)',
          transformStyle: 'preserve-3d',
          mixBlendMode: 'screen',
        }}
        animate={isFlowing ? {
          x: ['-5%', '5%', '-5%'],
          y: ['-3%', '3%', '-3%'],
          scale: [1, 1.05, 1],
        } : {}}
        transition={{
          duration: speed * 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* 3D Water Droplets */}
      {isFlowing && [0, 1, 2, 3].map((i) => (
        <motion.div
          key={`droplet-${i}`}
          className="absolute rounded-full"
          style={{
            width: '6px',
            height: '8px',
            left: `${25 + i * 20}%`,
            background: 'radial-gradient(ellipse at 30% 30%, rgba(255, 255, 255, 0.8), rgba(96, 165, 250, 0.6))',
            boxShadow: '0 2px 4px rgba(59, 130, 246, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.5)',
            transform: `translateZ(${10 + i * 5}px)`,
            transformStyle: 'preserve-3d',
          }}
          animate={{
            y: [120, -10],
            opacity: [0, 0.9, 0],
            scaleY: [1.2, 1, 1.2],
          }}
          transition={{
            duration: speed * 1.2,
            repeat: Infinity,
            delay: i * 0.3,
            ease: "easeIn"
          }}
        />
      ))}

      {/* Status Badge - 3D Effect */}
      <motion.div 
        className="absolute top-4 right-4 flex items-center space-x-2 backdrop-blur-lg px-4 py-2 rounded-full border shadow-xl"
        style={{
          background: 'rgba(255, 255, 255, 0.85)',
          borderColor: 'rgba(59, 130, 246, 0.3)',
          transform: 'translateZ(50px)',
          transformStyle: 'preserve-3d',
          boxShadow: `
            0 8px 32px rgba(59, 130, 246, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.8)
          `,
        }}
        animate={isFlowing ? {
          boxShadow: [
            '0 8px 32px rgba(59, 130, 246, 0.25)',
            '0 12px 40px rgba(59, 130, 246, 0.4)',
            '0 8px 32px rgba(59, 130, 246, 0.25)',
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
          style={{
            boxShadow: isFlowing ? '0 0 10px rgba(34, 197, 94, 0.6), 0 0 20px rgba(34, 197, 94, 0.3)' : 'none',
          }}
          animate={isFlowing ? {
            scale: [1, 1.4, 1],
          } : {}}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
        />
        <span className={`text-xs font-bold ${isFlowing ? 'text-blue-600' : 'text-gray-500'}`}>
          {isFlowing ? 'FLOWING' : 'IDLE'}
        </span>
        <span className="text-xs font-semibold text-blue-500">
          {Math.round(flowRate)}%
        </span>
      </motion.div>

      {/* 3D Depth Overlay */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.05) 100%)',
          transform: 'translateZ(40px)',
          transformStyle: 'preserve-3d',
        }}
      />
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
