import React from 'react';
import { motion } from 'framer-motion';

// Color mapping for cookie milestones
const getMarkerColor = (value) => {
    if (value === 25) return '#8B4513'; // Brown
    if (value === 50) return '#CD7F32'; // Bronze
    if (value === 75) return '#C0C0C0'; // Silver
    if (value === 100) return '#FFD700'; // Gold
    return '#9E9E9E'; // Default gray
};

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
                    
                    {/* Percentage display inside the progress bar */}
                    <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        fontSize: '0.7rem',
                        fontWeight: '600',
                        color: '#fff',
                        textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                        whiteSpace: 'nowrap',
                        zIndex: 10
                    }}>
                        {percentage.toFixed(1)}%
                    </div>
                </motion.div>

                {/* Cookie milestone markers (no labels) */}
                {markers.map((marker, i) => {
                    const markerPercentage = (marker / max) * 100;
                    const markerColor = getMarkerColor(marker);
                    return (
                        <div key={i} style={{
                            position: 'absolute',
                            left: `${markerPercentage}%`,
                            top: 0,
                            bottom: 0,
                            width: '2px',
                            background: markerColor,
                            zIndex: 2,
                            boxShadow: `0 0 4px ${markerColor}`
                        }} />
                    );
                })}
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
