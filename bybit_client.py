import os
from typing import Dict, Optional
from pybit.unified_trading import HTTP
from dotenv import load_dotenv

load_dotenv()

class BybitClient:
    def __init__(self):
        api_key = os.getenv('key') or os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('secret') or os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("API credentials not found")
        
        self.client = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )
    
    def get_wallet_balance(self) -> Dict:
        try:
            response = self.client.get_wallet_balance(
                accountType="UNIFIED",
                coin="USDT"
            )
            return response
        except:
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        try:
            balance_response = self.get_wallet_balance()
            
            if not balance_response or balance_response['retCode'] != 0:
                return None
            
            account_data = balance_response['result']['list'][0]
            total_equity_usd = float(account_data['totalEquity'])
            
            # Get cumulative realized P&L (lifetime) and session P&L
            cum_realized_pnl = float(account_data.get('cumRealisedPnl', '0'))
            total_perp_upl = float(account_data.get('totalPerpUPL', '0'))  # Current unrealized P&L
            
            # Get today's closed P&L
            pnl_data = self.get_pnl_data()
            if pnl_data:
                today_realized_pnl = pnl_data.get('today_pnl', 0)
            else:
                today_realized_pnl = 0
            
            # Use session data for real-time updates
            # This combines today's closed P&L with a portion of current unrealized
            # The unrealized portion will update with market movements
            session_pnl = today_realized_pnl + (total_perp_upl * 0.05)  # 5% weight on unrealized
            
            # Calculate percentage based on typical account size
            # This will need adjustment based on your actual account
            typical_equity = total_equity_usd - session_pnl  # Approximate yesterday's equity
            if typical_equity > 0:
                pnl_percentage = (session_pnl / typical_equity) * 100
            else:
                pnl_percentage = 0
            
            return {
                'equity': total_equity_usd,
                'pnl_24h': session_pnl,
                'pnl_24h_percentage': pnl_percentage,
                'currency': 'USD'
            }
            
        except:
            return None
    
    
    def get_pnl_data(self) -> Optional[Dict]:
        try:
            response = self.client.get_closed_pnl(
                category="linear",
                settleCoin="USDT",
                limit=200
            )
            
            if response['retCode'] != 0:
                return None
            
            today_realized_pnl = 0
            from datetime import datetime, timezone
            
            today = datetime.now(timezone.utc).date()
            
            for trade in response['result']['list']:
                trade_time = datetime.fromtimestamp(int(trade['updatedTime']) / 1000, tz=timezone.utc)
                if trade_time.date() == today:
                    realized_pnl = float(trade.get('closedPnl', '0'))
                    today_realized_pnl += realized_pnl
            
            return {
                'today_pnl': today_realized_pnl,
                'realized_pnl': today_realized_pnl,
                'unrealized_pnl': 0
            }
            
        except:
            return None
    
