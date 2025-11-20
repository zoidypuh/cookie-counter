import React, { useState, useEffect } from 'react';
import './App.css';
import CookieDisplay from './components/CookieDisplay';
import PnLDisplay from './components/PnLDisplay';
import ChartDisplay from './components/ChartDisplay';
import ProgressBar from './components/ProgressBar';
import CircularProgress from './components/CircularProgress';
import RiskGauge from './components/RiskGauge';

const CACHE_KEY = 'bybit_cookie_data_cache';
const CACHE_HOUR_KEY = 'bybit_cookie_data_hour';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get current hour as a string identifier (YYYY-MM-DD-HH)
  const getCurrentHour = () => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}`;
  };

  // Load cached data from localStorage
  const loadCachedData = () => {
    try {
      const cachedHour = localStorage.getItem(CACHE_HOUR_KEY);
      const cachedData = localStorage.getItem(CACHE_KEY);
      
      if (cachedHour && cachedData) {
        const currentHour = getCurrentHour();
        // If we're still in the same hour, use cached data
        if (cachedHour === currentHour) {
          return JSON.parse(cachedData);
        }
      }
    } catch (err) {
      console.error("Error loading cached data:", err);
    }
    return null;
  };

  // Save data to localStorage
  const saveCachedData = (dataToCache) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(dataToCache));
      localStorage.setItem(CACHE_HOUR_KEY, getCurrentHour());
    } catch (err) {
      console.error("Error saving cached data:", err);
    }
  };

  useEffect(() => {
    // Try to load cached data first for immediate display
    const cachedData = loadCachedData();
    if (cachedData) {
      setData(cachedData);
      setLoading(false);
    }

    const fetchData = async () => {
      try {
        const response = await fetch('/api/data');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();
        setData(jsonData);
        saveCachedData(jsonData);
        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        // If fetch fails and we have cached data, use it
        const cached = loadCachedData();
        if (cached) {
          setData(cached);
        } else {
          setError("Failed to fetch data");
        }
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch immediately
    fetchData();

    // Fetch data every second to keep cookies counter and chart updated
    const interval = setInterval(() => {
      fetchData();
    }, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  // Update page title with cookie count
  useEffect(() => {
    if (data?.cookie_count !== undefined) {
      document.title = `${data.cookie_count.toFixed(2)} cookies`;
    }
  }, [data?.cookie_count]);

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
        height: 'auto',
        margin: 0,
        borderRadius: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        alignItems: 'center',
        padding: '0.5rem 2rem 0 2rem',
        background: 'transparent',
        marginBottom: 0
      }}>
        <div style={{ width: '90%', marginBottom: 0 }}>
          <ProgressBar
            value={data?.cookie_count || 0}
            max={100}
            label=""
            markers={[25, 50, 75, 100]}
            color="#C0C0C0"
            noMargin={true}
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
        <CookieDisplay 
          count={data?.cookie_count} 
          equity={data?.equity}
          unrealizedPnlCookies={data?.unrealized_pnl_cookies}
        />
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
