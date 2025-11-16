import os
from flask import Flask, render_template, jsonify, request
from bybit_client import BybitClient
import time
from threading import Lock
from datetime import datetime, timedelta

app = Flask(__name__)

# Global cache for API data
cache = {
    'data': None,
    'timestamp': None
}
cache_lock = Lock()
CACHE_DURATION = 1  # seconds

# Global chart data storage
chart_history = []
chart_lock = Lock()
MAX_CHART_POINTS = 600  # 10 minutes at 1s intervals (600s / 1s)

# Global Bybit client instance
bybit_client = None
client_lock = Lock()

def get_bybit_client():
    """Get or create a cached Bybit client instance"""
    global bybit_client
    with client_lock:
        if bybit_client is None:
            try:
                bybit_client = BybitClient()
            except Exception as e:
                print(f"Error creating Bybit client: {e}")
                return None
    return bybit_client

def update_chart_history(cookie_count):
    """Update chart history with new data point"""
    global chart_history
    with chart_lock:
        timestamp = time.time()
        chart_history.append({
            'timestamp': timestamp,
            'value': cookie_count
        })
        
        # Keep only last MAX_CHART_POINTS
        if len(chart_history) > MAX_CHART_POINTS:
            chart_history = chart_history[-MAX_CHART_POINTS:]

def get_chart_data():
    """Get chart data for frontend"""
    with chart_lock:
        if not chart_history:
            return []
        
        # Return data in format suitable for Chart.js
        return [{
            'x': point['timestamp'] * 1000,  # Convert to milliseconds for JavaScript
            'y': point['value']
        } for point in chart_history]

@app.route('/collect-equity')
def collect_equity():
    """Endpoint for hourly equity collection (called by Cloud Scheduler)"""
    try:
        # Import here to avoid circular imports
        from collect_equity import collect_equity_snapshot

        success = collect_equity_snapshot()

        if success:
            return jsonify({'status': 'success', 'message': 'Equity snapshot collected'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to collect equity'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/siri')
def siri_summary():
    """
    Lightweight endpoint for Siri Shortcuts to fetch cookie status.
    Returns plain text by default; add ?format=json for a JSON response.
    """
    data = get_cookie_data()

    if not data:
        message = "I couldn't reach the cookie tracker right now."
        line_dicts = []
    else:
        count = data.get('cookie_count', 0)
        line_dicts = data.get('pnl_lines') or []
        line_texts = [line.get('text') for line in line_dicts if line and line.get('text')]
        summary = ' '.join(line_texts)

        if count == 0:
            message = "You have no cookies in the jar right now."
        else:
            message = f"You have {count} cookies still in the jar."
            if summary:
                message += f" {summary}"

    line_json = [
        {
            'text': line.get('text'),
            'class': line.get('class'),
            'color': line.get('color')
        }
        for line in line_dicts
    ] if line_dicts else []

    if 'json' in (request.args.get('format') or '').lower():
        return jsonify({
            'message': message,
            'cookie_count': data.get('cookie_count') if data else None,
            'pnl_text': data.get('pnl_text') if data else None,
            'pnl_lines': line_json,
            'pnl_percentage': data.get('pnl_percentage') if data else None,
        })

    return message, 200, {'Content-Type': 'text/plain; charset=utf-8'}

GAIN_COLOR = '#4CAF50'
LOSS_COLOR = '#F44336'
NEUTRAL_COLOR = '#9E9E9E'


def classify_change(value):
    if value is None:
        return 'neutral', NEUTRAL_COLOR
    if value > 0:
        return 'gain', GAIN_COLOR
    if value < 0:
        return 'loss', LOSS_COLOR
    return 'neutral', NEUTRAL_COLOR


def format_change_line(pnl_value, pnl_pct, window_label, source='true', hours=None):
    """
    Generate a descriptive line for performance text.
    pnl_value: USD difference
    pnl_pct: percentage difference
    window_label: description such as 'last hour'
    source: 'true', 'approx', 'fallback', 'missing'
    hours: number of hours between snapshots (for fallback messaging)
    """
    line = {'text': '', 'class': 'neutral', 'color': NEUTRAL_COLOR}

    if pnl_value is None or source == 'missing':
        line['text'] = f"{window_label.capitalize()} change unavailable yet."
        return line

    line['class'], line['color'] = classify_change(pnl_value)
    cookies_delta = pnl_value / 1000  # 1 cookie = $1,000
    pct_text = f"({pnl_pct:+.2f}%)" if pnl_pct is not None else ""

    if abs(cookies_delta) < 0.01:
        if source == 'approx':
            line['text'] = f"No meaningful change in the {window_label} yet (approximate)."
        else:
            line['text'] = f"No meaningful change in the {window_label}."
        line['class'], line['color'] = 'neutral', NEUTRAL_COLOR
        return line

    direction = "gained" if cookies_delta > 0 else "lost"
    cookies_text = f"{abs(cookies_delta):.2f} cookies {direction}"

    if source == 'true':
        line['text'] = f"{cookies_text} in the {window_label} {pct_text}".strip()
    if source == 'fallback':
        if hours:
            line['text'] = f"{cookies_text} since {hours:.1f} hours ago {pct_text} (closest snapshot available).".strip()
        else:
            line['text'] = f"{cookies_text} since the previous snapshot {pct_text} (closest snapshot available).".strip()
    if source == 'approx':
        line['text'] = f"{window_label.capitalize()} change unavailable yet."
        line['class'], line['color'] = 'neutral', NEUTRAL_COLOR
        return line

    if not line['text']:
        line['text'] = f"{cookies_text} in the {window_label} {pct_text}".strip()
    return line


def get_cookie_data(use_cache=True):
    """Get cookie data with optional caching to prevent duplicate API calls"""
    global cache
    
    # Check cache first
    if use_cache:
        with cache_lock:
            if cache['data'] is not None and cache['timestamp'] is not None:
                age = time.time() - cache['timestamp']
                if age < CACHE_DURATION:
                    return cache['data']
    
    try:
        # Try to get real data
        client = get_bybit_client()
        if client:
            account_info = client.get_account_info()
        else:
            account_info = None
        
        if not account_info:
            return {
                'cookie_count': 0,
                'equity': 0,
                'pnl_percentage': 0,
                'pnl_text': '0.00 cookies gained in the last 24hs (0.00%)',
                'pnl_color': 'gray',
                'pnl_class': 'neutral',
                'cookie_grid': [],
                'chart_data': []
            }
        
        equity = account_info['equity']
        pnl_24h = account_info.get('pnl_24h')
        pnl_24h_percentage = account_info.get('pnl_24h_percentage')
        
        # Get maintenance margin data
        maintenance_margin = account_info.get('maintenance_margin', 0)
        maintenance_margin_rate = account_info.get('maintenance_margin_rate', 0)
        available_balance = account_info.get('available_balance', 0)
        
        # Calculate maintenance margin used percentage
        # This shows how much of your equity is being used for maintenance margin
        mm_used_percentage = (maintenance_margin / equity * 100) if equity > 0 else 0
        pnl_24h_source = account_info.get('pnl_24h_source', 'approx')
        pnl_24h_hours = account_info.get('pnl_24h_hours')

        pnl_1h = account_info.get('pnl_1h')
        pnl_1h_percentage = account_info.get('pnl_1h_percentage')
        pnl_1h_source = account_info.get('pnl_1h_source', 'missing')
        pnl_1h_hours = account_info.get('pnl_1h_hours')
        
        pnl_72h = account_info.get('pnl_72h')
        pnl_72h_percentage = account_info.get('pnl_72h_percentage')
        pnl_72h_source = account_info.get('pnl_72h_source', 'approx')
        pnl_72h_hours = account_info.get('pnl_72h_hours')

        effective_leverage = account_info.get('effective_leverage')
        leverage_display = None
        leverage_class = 'leverage-neutral'
        if effective_leverage is not None:
            leverage_display = f"{effective_leverage:.2f}x"
            if effective_leverage > 3:
                leverage_class = 'leverage-high'
            else:
                leverage_class = 'leverage-low'
        
        cookie_count = equity / 1000  # Keep as float for decimal display
        
        # Update chart history
        update_chart_history(cookie_count)
        
        # Determine primary window (prefer 72h, then 24h, then 1h)
        if pnl_72h_source == 'true':
            primary_pnl = pnl_72h
        elif pnl_24h_source != 'missing':
            primary_pnl = pnl_24h
        else:
            primary_pnl = pnl_1h

        pnl_color = '#4CAF50' if primary_pnl and primary_pnl > 0 else '#F44336' if primary_pnl and primary_pnl < 0 else '#9E9E9E'
        pnl_class = 'gain' if primary_pnl and primary_pnl > 0 else 'loss' if primary_pnl and primary_pnl < 0 else 'neutral'

        # Build descriptive lines
        lines = []
        one_hour_line = format_change_line(
            pnl_1h, pnl_1h_percentage, 'last hour', pnl_1h_source, pnl_1h_hours)
        lines.append(one_hour_line)
        day_line = format_change_line(
            pnl_24h, pnl_24h_percentage, 'last 24 hours', pnl_24h_source, pnl_24h_hours)
        lines.append(day_line)

        pnl_text = ' '.join(line['text'] for line in lines)
        
        cookie_grid = list(range(int(cookie_count)))  # Grid shows whole cookies only

        # Determine primary color/class using first non-neutral line; fallback to first line
        primary_line = next((line for line in lines if line['class'] != 'neutral'), lines[0])
        pnl_color = primary_line['color']
        pnl_class = primary_line['class']
        
        headline_pct = pnl_24h_percentage if pnl_24h_source != 'missing' else pnl_1h_percentage

        result = {
            'cookie_count': cookie_count,
            'equity': equity,
            'pnl_percentage': headline_pct,
            'pnl_text': pnl_text,
            'pnl_lines': lines,
            'pnl_color': pnl_color,
            'pnl_class': pnl_class,
            'cookie_grid': cookie_grid,
            'chart_data': get_chart_data(),
            'effective_leverage': effective_leverage,
            'leverage_display': leverage_display,
            'leverage_class': leverage_class,
            'maintenance_margin_percentage': mm_used_percentage
        }
        
        # Cache the result
        with cache_lock:
            cache['data'] = result
            cache['timestamp'] = time.time()
        
        return result
    
    except Exception as e:
        print(f"Error in get_cookie_data: {e}")
        error_result = {
            'cookie_count': 0,
            'equity': 0,
            'pnl_percentage': 0,
            'pnl_text': 'No data available right now.',
            'pnl_lines': [{'text': 'No data available right now.', 'class': 'neutral', 'color': NEUTRAL_COLOR}],
            'pnl_color': 'gray',
            'pnl_class': 'neutral',
            'cookie_grid': [],
            'chart_data': get_chart_data(),
            'effective_leverage': None,
            'leverage_display': None,
            'leverage_class': 'leverage-neutral',
            'maintenance_margin_percentage': 0
        }
        
        # Cache even error results to prevent rapid retries
        with cache_lock:
            cache['data'] = error_result
            cache['timestamp'] = time.time()
        
        return error_result

@app.route('/api/data')
def api_data():
    """API endpoint for fetching updated data without page reload"""
    data = get_cookie_data()
    return jsonify(data)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'cache_duration': CACHE_DURATION})

@app.route('/')
def index():
    cookie_data = get_cookie_data(use_cache=False)  # Don't use cache on initial page load
    return render_template('index.html', **cookie_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
