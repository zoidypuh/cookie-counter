import os
from flask import Flask, render_template, jsonify, request
from bybit_client import BybitClient

app = Flask(__name__)

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
    else:
        count = data.get('cookie_count', 0)
        lines = data.get('pnl_lines') or [data.get('pnl_text', '')]
        summary = ' '.join(line for line in lines if line)

        if count == 0:
            message = "You have no cookies in the jar right now."
        else:
            message = f"You have {count} cookies still in the jar."
            if summary:
                message += f" {summary}"

    if 'json' in (request.args.get('format') or '').lower():
        return jsonify({
            'message': message,
            'cookie_count': data.get('cookie_count') if data else None,
            'pnl_text': data.get('pnl_text') if data else None,
            'pnl_lines': data.get('pnl_lines') if data else None,
            'pnl_percentage': data.get('pnl_percentage') if data else None,
        })

    return message, 200, {'Content-Type': 'text/plain; charset=utf-8'}

def format_change_line(pnl_value, pnl_pct, window_label, source='true', hours=None):
    """
    Generate a descriptive line for performance text.
    pnl_value: USD difference
    pnl_pct: percentage difference
    window_label: description such as 'last hour'
    source: 'true', 'approx', 'fallback', 'missing'
    hours: number of hours between snapshots (for fallback messaging)
    """
    if pnl_value is None or source == 'missing':
        return f"{window_label.capitalize()} change unavailable yet."

    cookies_delta = pnl_value / 1000  # 1 cookie = $1,000
    pct_text = f"({pnl_pct:+.2f}%)" if pnl_pct is not None else ""

    if abs(cookies_delta) < 0.01:
        if source == 'approx':
            return f"No meaningful change in the {window_label} yet (approximate)."
        return f"No meaningful change in the {window_label}."

    direction = "gained" if cookies_delta > 0 else "lost"
    cookies_text = f"{abs(cookies_delta):.2f} cookies {direction}"

    if source == 'true':
        return f"{cookies_text} in the {window_label} {pct_text}".strip()
    if source == 'fallback':
        if hours:
            return f"{cookies_text} since {hours:.1f} hours ago {pct_text} (closest snapshot available).".strip()
        return f"{cookies_text} since the previous snapshot {pct_text} (closest snapshot available).".strip()
    if source == 'approx':
        return f"24h change unavailable yet. Using today's performance: {cookies_text} {pct_text}".strip()

    return f"{cookies_text} in the {window_label} {pct_text}".strip()


def get_cookie_data():
    try:
        # Try to get real data
        try:
            client = BybitClient()
            account_info = client.get_account_info()
        except:
            # If API fails, use demo data
            account_info = None
        
        if not account_info:
            return {
                'cookie_count': 0,
                'equity': 0,
                'pnl_percentage': 0,
                'pnl_text': '0.00 cookies gained in the last 24hs (0.00%)',
                'pnl_color': 'gray',
                'pnl_class': 'neutral',
                'cookie_grid': []
            }
        
        equity = account_info['equity']
        pnl_24h = account_info.get('pnl_24h', 0)
        pnl_24h_percentage = account_info.get('pnl_24h_percentage', 0)
        pnl_24h_source = account_info.get('pnl_24h_source', 'approx')
        pnl_24h_hours = account_info.get('pnl_24h_hours')

        pnl_1h = account_info.get('pnl_1h', 0)
        pnl_1h_percentage = account_info.get('pnl_1h_percentage', 0)
        pnl_1h_source = account_info.get('pnl_1h_source', 'missing')
        pnl_1h_hours = account_info.get('pnl_1h_hours')
        
        cookie_count = int(equity / 1000)
        
        # Determine display color/class using 24h if available, otherwise 1h
        primary_pnl = pnl_24h if pnl_24h_source != 'missing' else pnl_1h
        pnl_color = '#4CAF50' if primary_pnl > 0 else '#F44336' if primary_pnl < 0 else '#9E9E9E'
        pnl_class = 'gain' if primary_pnl > 0 else 'loss' if primary_pnl < 0 else 'neutral'

        # Build descriptive lines
        lines = []
        lines.append(format_change_line(pnl_1h, pnl_1h_percentage, 'last hour', pnl_1h_source, pnl_1h_hours))
        lines.append(format_change_line(pnl_24h, pnl_24h_percentage, 'last 24 hours', pnl_24h_source, pnl_24h_hours))

        pnl_text = ' '.join(lines)
        
        cookie_grid = list(range(cookie_count))
        
        return {
            'cookie_count': cookie_count,
            'equity': equity,
            'pnl_percentage': pnl_24h_percentage if pnl_24h_source != 'missing' else pnl_1h_percentage,
            'pnl_text': pnl_text,
            'pnl_lines': lines,
            'pnl_color': pnl_color,
            'pnl_class': pnl_class,
            'cookie_grid': cookie_grid
        }
    
    except:
        return {
            'cookie_count': 0,
            'equity': 0,
            'pnl_percentage': 0,
            'pnl_text': 'No data available right now.',
            'pnl_lines': ['No data available right now.'],
            'pnl_color': 'gray',
            'pnl_class': 'neutral',
            'cookie_grid': []
        }

@app.route('/')
def index():
    cookie_data = get_cookie_data()
    return render_template('index.html', **cookie_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
