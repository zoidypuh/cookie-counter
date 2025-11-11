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
        line['text'] = f"24h change unavailable yet. Using today's performance: {cookies_text} {pct_text}".strip()
        return line

    if not line['text']:
        line['text'] = f"{cookies_text} in the {window_label} {pct_text}".strip()
    return line


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
                'cookie_grid': [],
                'chart_data': []
            }
        
        equity = account_info['equity']
        pnl_24h = account_info.get('pnl_24h')
        pnl_24h_percentage = account_info.get('pnl_24h_percentage')
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
        
        cookie_count = int(equity / 1000)
        
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
        three_day_line = format_change_line(
            pnl_72h, pnl_72h_percentage, 'last 72 hours', pnl_72h_source, pnl_72h_hours)
        lines.append(three_day_line)

        pnl_text = ' '.join(line['text'] for line in lines)
        
        cookie_grid = list(range(cookie_count))

        # Determine primary color/class using first non-neutral line; fallback to first line
        primary_line = next((line for line in lines if line['class'] != 'neutral'), lines[0])
        pnl_color = primary_line['color']
        pnl_class = primary_line['class']
        show_winning_gif = (one_hour_line['class'] == 'gain' and day_line['class'] == 'gain')
        
        headline_pct = pnl_24h_percentage if pnl_24h_source != 'missing' else pnl_1h_percentage

        return {
            'cookie_count': cookie_count,
            'equity': equity,
            'pnl_percentage': headline_pct,
            'pnl_text': pnl_text,
            'pnl_lines': lines,
            'pnl_color': pnl_color,
            'pnl_class': pnl_class,
            'cookie_grid': cookie_grid,
            'show_winning_gif': show_winning_gif,
            'chart_data': [] # Placeholder for chart data
        }
    
    except:
        return {
            'cookie_count': 0,
            'equity': 0,
            'pnl_percentage': 0,
            'pnl_text': 'No data available right now.',
            'pnl_lines': [{'text': 'No data available right now.', 'class': 'neutral', 'color': NEUTRAL_COLOR}],
            'pnl_color': 'gray',
            'pnl_class': 'neutral',
            'cookie_grid': [],
            'show_winning_gif': False,
            'chart_data': []
        }

@app.route('/')
def index():
    cookie_data = get_cookie_data()
    return render_template('index.html', **cookie_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
