import React from 'react';
import { motion } from 'framer-motion';

const PnLDisplay = ({ lines, pnlClass }) => {
    return (
        <div className="pnl-container">
            {lines && lines.map((line, index) => {
                // Determine status based on class
                let statusIcon = '●';
                let statusColor = 'var(--text-secondary)';

                if (line.class === 'gain') {
                    statusIcon = '▲';
                    statusColor = 'var(--accent-green)';
                } else if (line.class === 'loss') {
                    statusIcon = '▼';
                    statusColor = 'var(--accent-red)';
                }

                return (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            padding: '1rem',
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: '12px',
                            marginBottom: '0.8rem',
                            border: '1px solid rgba(255,255,255,0.05)'
                        }}
                    >
                        <div style={{
                            marginRight: '1rem',
                            color: statusColor,
                            fontSize: '1.2rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '32px',
                            height: '32px',
                            background: `rgba(255,255,255,0.05)`,
                            borderRadius: '50%'
                        }}>
                            {statusIcon}
                        </div>
                        <div style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>
                            {line.text}
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
};

export default PnLDisplay;
