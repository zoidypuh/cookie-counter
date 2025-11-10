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
        pnl_text = data.get('pnl_text', '')

        if count == 0:
            message = "You have no cookies in the jar right now."
        else:
            message = f"You have {count} cookies still in the jar. {pnl_text}"

    if 'json' in (request.args.get('format') or '').lower():
        return jsonify({
            'message': message,
            'cookie_count': data.get('cookie_count') if data else None,
            'pnl_text': data.get('pnl_text') if data else None,
            'pnl_percentage': data.get('pnl_percentage') if data else None,
        })

    return message, 200, {'Content-Type': 'text/plain; charset=utf-8'}

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
        pnl_percentage = account_info['pnl_24h_percentage']
        today_pnl = account_info['pnl_24h']
        
        cookie_count = int(equity / 1000)
        cookies_changed = abs(today_pnl) / 1000
        
        if today_pnl > 0:
            pnl_text = f"{cookies_changed:.2f} cookies gained in the last 24hs ({pnl_percentage:+.2f}%)"
            pnl_color = '#4CAF50'
            pnl_class = 'gain'
        elif today_pnl < 0:
            pnl_text = f"{cookies_changed:.2f} cookies lost in the last 24hs ({pnl_percentage:.2f}%)"
            pnl_color = '#F44336'
            pnl_class = 'loss'
        else:
            pnl_text = "0.00 cookies gained in the last 24hs (0.00%)"
            pnl_color = '#9E9E9E'
            pnl_class = 'neutral'
        
        cookie_grid = list(range(cookie_count))
        
        return {
            'cookie_count': cookie_count,
            'equity': equity,
            'pnl_percentage': pnl_percentage,
            'pnl_text': pnl_text,
            'pnl_color': pnl_color,
            'pnl_class': pnl_class,
            'cookie_grid': cookie_grid
        }
    
    except:
        return {
            'cookie_count': 0,
            'equity': 0,
            'pnl_percentage': 0,
            'pnl_text': '0.00 cookies gained in the last 24hs (0.00%)',
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
