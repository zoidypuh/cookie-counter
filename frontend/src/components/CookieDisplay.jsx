import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { NumericFormat } from 'react-number-format';

const CookieDisplay = ({ count, equity, unrealizedPnlCookies }) => {
  const [displayCount, setDisplayCount] = useState(count || 0);
  const [displayEquityPlusAbsPnl, setDisplayEquityPlusAbsPnl] = useState(0);
  const [displayPnl, setDisplayPnl] = useState(0);
  const [color, setColor] = useState('#4CAF50'); // Default green
  const previousCountRef = useRef(count || 0);

  // Calculate values
  const equityCookies = equity ? equity / 1000 : 0;
  const absPnlCookies = Math.abs(unrealizedPnlCookies || 0);
  const totalCookies = equityCookies + absPnlCookies;
  const pnlCookies = unrealizedPnlCookies || 0;

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

  // Animate equity + abs(pnl)
  useEffect(() => {
    const startValue = displayEquityPlusAbsPnl;
    const endValue = totalCookies;
    const duration = 1000;
    const startTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const easeOutQuad = (t) => t * (2 - t);
      const easedProgress = easeOutQuad(progress);
      const currentValue = startValue + (endValue - startValue) * easedProgress;
      setDisplayEquityPlusAbsPnl(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [totalCookies]);

  // Animate PnL
  useEffect(() => {
    const startValue = displayPnl;
    const endValue = pnlCookies;
    const duration = 1000;
    const startTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const easeOutQuad = (t) => t * (2 - t);
      const easedProgress = easeOutQuad(progress);
      const currentValue = startValue + (endValue - startValue) * easedProgress;
      setDisplayPnl(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [pnlCookies]);

  // Determine PnL color
  const pnlColor = pnlCookies >= 0 ? '#81C784' : '#E57373'; // Light green or light red

  const numberStyle = {
    fontSize: '5rem',
    margin: 0,
    lineHeight: '1',
    transition: 'color 0.3s ease, text-shadow 0.3s ease'
  };

  return (
    <div className="cookie-display" style={{
      display: 'flex',
      width: '100%',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: '1rem'
    }}>
      {/* Left: Equity + Abs(PnL) - Light Grey */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{ flex: '1', textAlign: 'center' }}
      >
        <h1 style={{
          ...numberStyle,
          color: '#9E9E9E',
          textShadow: '0 0 20px rgba(158, 158, 158, 0.3)'
        }}>
          <NumericFormat
            value={displayEquityPlusAbsPnl}
            displayType={'text'}
            thousandSeparator={true}
            decimalScale={3}
            fixedDecimalScale={true}
          />
        </h1>
      </motion.div>

      {/* Center: Current Cookies - Green/Red based on direction */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{ flex: '1', textAlign: 'center' }}
      >
        <h1 style={{
          ...numberStyle,
          color: color,
          textShadow: `0 0 40px ${color}40`
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

      {/* Right: PnL - Light Green/Red */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{ flex: '1', textAlign: 'center' }}
      >
        <h1 style={{
          ...numberStyle,
          color: pnlColor,
          textShadow: `0 0 20px ${pnlColor}40`
        }}>
          <NumericFormat
            value={displayPnl}
            displayType={'text'}
            thousandSeparator={true}
            decimalScale={3}
            fixedDecimalScale={true}
            prefix={displayPnl >= 0 ? '+' : ''}
          />
        </h1>
      </motion.div>
    </div>
  );
};

export default CookieDisplay;
