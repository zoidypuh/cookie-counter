import React from 'react';
import { motion } from 'framer-motion';

const ProgressBar = ({ value, max = 100, color = 'var(--accent-green)', label, markers = [], noMargin = false }) => {
    const percentage = Math.min((value / max) * 100, 100);

    return (
        <div style={{ marginBottom: noMargin ? 0 : '1.5rem', textAlign: 'left', width: '100%' }}>
            {label && (
                <div style={{
                    marginBottom: '0.8rem',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    fontWeight: '600'
                }}>
                    {label}
                </div>
            )}

            <div style={{
                height: '12px',
                background: 'rgba(255,255,255,0.05)',
                borderRadius: '6px',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
            }}>
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    style={{
                        height: '100%',
                        background: color,
                        borderRadius: '6px',
                        boxShadow: `0 0 15px ${color}`,
                        position: 'relative'
                    }}
                >
                    {/* Shimmer effect */}
                    <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                        transform: 'skewX(-20deg)',
                        animation: 'shimmer 2s infinite'
                    }} />
                </motion.div>

                {markers.map((marker, i) => (
                    <div key={i} style={{
                        position: 'absolute',
                        left: `${marker}%`,
                        top: 0,
                        bottom: 0,
                        width: '1px',
                        background: 'rgba(255,255,255,0.1)',
                        zIndex: 2
                    }}>
                        <div style={{
                            position: 'absolute',
                            top: '14px',
                            left: '-50%',
                            transform: 'translateX(-50%)',
                            fontSize: '0.7rem',
                            color: 'var(--text-muted)'
                        }}>
                            {marker}%
                        </div>
                    </div>
                ))}
            </div>
            <style>{`
        @keyframes shimmer {
            0% { transform: translateX(-100%) skewX(-20deg); }
            100% { transform: translateX(200%) skewX(-20deg); }
        }
      `}</style>
        </div>
    );
};

export default ProgressBar;
