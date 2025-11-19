import React from 'react';
import { motion } from 'framer-motion';

const CircularProgress = ({ value, max, size = 200, strokeWidth = 12 }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const percentage = (value / max) * 100;
    const offset = circumference - (percentage / 100) * circumference;

    // Color based on risk level - green is safe (low %), red is dangerous (high %)
    const getColor = () => {
        if (percentage < 20) return 'var(--accent-green)';
        if (percentage < 50) return 'var(--accent-orange)';
        return 'var(--accent-red)';
    };

    return (
        <div style={{ position: 'relative', width: size, height: size }}>
            <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth={strokeWidth}
                    fill="none"
                />

                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke={getColor()}
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1, ease: 'easeInOut' }}
                    style={{
                        filter: `drop-shadow(0 0 8px ${getColor()})`
                    }}
                />
            </svg>

            {/* Center text - only percentage */}
            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center'
            }}>
                <div style={{
                    fontSize: '2rem',
                    fontWeight: '700',
                    color: getColor(),
                    textShadow: `0 0 20px ${getColor()}40`
                }}>
                    {percentage.toFixed(1)}%
                </div>
                <div style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    marginTop: '0.5rem'
                }}>
                    {percentage < 20 ? 'Safe' : percentage < 50 ? 'Moderate' : 'High Risk'}
                </div>
            </div>
        </div>
    );
};

export default CircularProgress;
