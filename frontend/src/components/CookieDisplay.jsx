import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { NumericFormat } from 'react-number-format';

const CookieDisplay = ({ count }) => {
  const [displayCount, setDisplayCount] = useState(count || 0);
  const [color, setColor] = useState('#4CAF50'); // Default green
  const previousCountRef = useRef(count || 0);

  useEffect(() => {
    if (count === undefined) return;

    // Determine color based on change direction
    const previousCount = previousCountRef.current;
    if (count > previousCount) {
      setColor('#4CAF50'); // Green for going up
    } else if (count < previousCount) {
      setColor('#F44336'); // Red for going down
    }
    // If equal, keep the previous color

    // Update previous count
    previousCountRef.current = count;

    // Animate the number change
    const startValue = displayCount;
    const endValue = count;
    const duration = 1000; // 1 second
    const startTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);

      // Easing function for smooth animation
      const easeOutQuad = (t) => t * (2 - t);
      const easedProgress = easeOutQuad(progress);

      const currentValue = startValue + (endValue - startValue) * easedProgress;
      setDisplayCount(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [count]);

  return (
    <div className="cookie-display">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <h1 className="cookie-number" style={{
          fontSize: '5rem',
          margin: 0,
          lineHeight: '1',
          color: color,
          textShadow: `0 0 40px ${color}40`,
          transition: 'color 0.3s ease, text-shadow 0.3s ease'
        }}>
          <NumericFormat
            value={displayCount}
            displayType={'text'}
            thousandSeparator={true}
            decimalScale={3}
            fixedDecimalScale={true}
          />
        </h1>
      </motion.div>
    </div>
  );
};

export default CookieDisplay;
