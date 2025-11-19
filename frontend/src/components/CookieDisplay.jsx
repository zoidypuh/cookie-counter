import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { NumericFormat } from 'react-number-format';

const CookieDisplay = ({ count }) => {
  const [displayCount, setDisplayCount] = useState(count || 0);

  useEffect(() => {
    if (count === undefined) return;

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
        <h1 className="cookie-number text-gradient-gold" style={{
          fontSize: '5rem',
          margin: 0,
          lineHeight: '1',
          textShadow: '0 0 40px rgba(255, 215, 0, 0.15)'
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
