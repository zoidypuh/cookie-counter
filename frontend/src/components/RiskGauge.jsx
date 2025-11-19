import React from 'react';
import { motion } from 'framer-motion';

const RiskGauge = ({ value, max = 100 }) => {
    // Calculate rotation: -90deg (0%) to 90deg (100%)
    const percentage = Math.min(Math.max(value, 0), max) / max;
    const rotation = -90 + (percentage * 180);

    let color = '#00ff9d'; // Green
    let statusText = 'Safe';

    if (percentage > 0.5) {
        color = '#ffb84d'; // Orange
        statusText = 'Caution';
    }
    if (percentage > 0.8) {
        color = '#ff4d4d'; // Red
        statusText = 'Critical';
    }

    return (
        <div style={{
            position: 'relative',
            width: '200px',
            height: '100px',
            margin: '0 auto',
            overflow: 'hidden'
        }}>
            {/* Background Arc */}
            <div style={{
                position: 'absolute',
                bottom: 0,
                left: '10px',
                width: '180px',
                height: '180px',
                borderRadius: '50%',
                border: '20px solid rgba(255,255,255,0.05)',
                borderBottomColor: 'transparent',
                borderLeftColor: 'transparent', // We only want the top half, but rotated
                transform: 'rotate(-45deg)', // Adjust to make it a semi-circle arc
                boxSizing: 'border-box'
            }} />

            {/* Needle */}
            <motion.div
                initial={{ rotate: -90 }}
                animate={{ rotate: rotation }}
                transition={{ type: "spring", stiffness: 60, damping: 15 }}
                style={{
                    position: 'absolute',
                    bottom: '0',
                    left: '50%',
                    width: '4px',
                    height: '80px',
                    background: color,
                    transformOrigin: 'bottom center',
                    borderRadius: '2px 2px 0 0',
                    boxShadow: `0 0 10px ${color}`,
                    zIndex: 10
                }}
            />

            {/* Center Pivot */}
            <div style={{
                position: 'absolute',
                bottom: '-10px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '20px',
                height: '20px',
                background: '#fff',
                borderRadius: '50%',
                zIndex: 11,
                boxShadow: '0 0 10px rgba(0,0,0,0.5)'
            }} />

            {/* Labels */}
            <div style={{ position: 'absolute', bottom: '5px', left: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>0%</div>
            <div style={{ position: 'absolute', bottom: '5px', right: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>100%</div>

            {/* Value Text */}
            <div style={{
                position: 'absolute',
                bottom: '25px',
                left: '50%',
                transform: 'translateX(-50%)',
                textAlign: 'center'
            }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: color }}>{value.toFixed(1)}%</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{statusText}</div>
            </div>
        </div>
    );
};

export default RiskGauge;
