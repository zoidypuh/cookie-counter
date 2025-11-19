import React, { useState, useEffect } from 'react';
import './App.css';
import CookieDisplay from './components/CookieDisplay';
import PnLDisplay from './components/PnLDisplay';
import ChartDisplay from './components/ChartDisplay';
import ProgressBar from './components/ProgressBar';
import CircularProgress from './components/CircularProgress';
import RiskGauge from './components/RiskGauge';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);

    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ color: 'var(--text-secondary)' }}>Initializing connection...</div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ color: 'var(--accent-red)' }}>Connection Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      padding: 0,
      gap: 0
    }}>
      {/* Progress Bar - 10% (at top) */}
      <div style={{
        height: '10vh',
        margin: 0,
        borderRadius: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        alignItems: 'center',
        padding: '1rem 2rem 0 2rem',
        background: 'transparent'
      }}>
        <div style={{ width: '90%' }}>
          <ProgressBar
            value={data?.cookie_count || 0}
            max={100}
            label=""
            markers={[25, 50, 75]}
            color="var(--accent-orange)"
          />
        </div>
      </div>

      {/* Risk Metrics - 30% */}
      <div className="glass-card" style={{
        height: '30vh',
        margin: 0,
        borderRadius: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '3rem',
          flex: 1
        }}>
          <CircularProgress
            value={data?.maintenance_margin_percentage || 0}
            max={100}
            size={140}
            strokeWidth={12}
          />

          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '2px',
              marginBottom: '0.5rem'
            }}>
              Effective Leverage
            </div>
            <div style={{
              fontSize: '3rem',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #fff 0%, #a5a5a5 100%)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: '1'
            }}>
              {data?.effective_leverage?.toFixed(2)}x
            </div>
          </div>
        </div>
      </div>

      {/* Cookie Display - 30% */}
      <div className="glass-card" style={{
        height: '30vh',
        margin: 0,
        borderRadius: 0,
        textAlign: 'center',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}>
        <CookieDisplay count={data?.cookie_count} />
      </div>

      {/* Performance Chart + PnL - 30% */}
      <div style={{
        height: '30vh',
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: 0,
        margin: 0
      }}>
        <div className="glass-card" style={{ margin: 0, borderRadius: 0, padding: '1rem' }}>
          <ChartDisplay data={data?.chart_data} />
        </div>

        <div className="glass-card" style={{ margin: 0, borderRadius: 0, padding: '1rem' }}>
          <PnLDisplay lines={data?.pnl_lines} pnlClass={data?.pnl_class} />
        </div>
      </div>
    </div>
  );
}

export default App;
