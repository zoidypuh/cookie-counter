import os
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore, initialize_app

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

        # Initialize Firestore (only on GAE or if credentials available)
        self.db = self._init_firestore()

    def _init_firestore(self):
        """Initialize Firestore connection"""
        try:
            if os.getenv('GAE_ENV'):
                # Running on GAE - use default credentials
                try:
                    firebase_admin.get_app()
                except ValueError:
                    initialize_app()
                return firestore.client()
            else:
                # Local development - no Firestore
                return None
        except Exception:
            return None
    
    def get_wallet_balance(self) -> Dict:
        try:
            response = self.client.get_wallet_balance(
                accountType="UNIFIED",
                coin="USDT"
            )
            return response
        except:
            return None
    
    def get_24h_equity_data(self):
        """Get equity snapshots from the last 24 hours"""
        if not self.db:
            return []

        try:
            # Get snapshots from last 24 hours
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

            snapshots = self.db.collection('equity_snapshots') \
                .where('timestamp', '>=', cutoff_time) \
                .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                .stream()

            data = []
            for doc in snapshots:
                snap = doc.to_dict()
                data.append({
                    'timestamp': snap['timestamp'],
                    'equity': snap['equity']
                })

            return data

        except Exception as e:
            print(f"Error fetching 24h equity data: {e}")
            return []

    def get_account_info(self) -> Optional[Dict]:
        try:
            balance_response = self.get_wallet_balance()

            if not balance_response or balance_response['retCode'] != 0:
                return None

            account_data = balance_response['result']['list'][0]
            total_equity_usd = float(account_data['totalEquity'])

            # Try to get true 24h rolling P&L from stored equity data
            equity_24h_data = self.get_24h_equity_data()

            if equity_24h_data and len(equity_24h_data) >= 2:
                # Sort by timestamp (most recent first)
                equity_24h_data.sort(key=lambda x: x['timestamp'], reverse=True)

                # Current equity (most recent snapshot)
                current_equity = equity_24h_data[0]['equity']

                # Equity exactly 24 hours ago (oldest snapshot in range)
                equity_24h_ago = equity_24h_data[-1]['equity']

                # Calculate true 24h P&L and percentage
                pnl_24h = current_equity - equity_24h_ago
                pnl_percentage = (pnl_24h / equity_24h_ago) * 100 if equity_24h_ago > 0 else 0

                print(f"✅ Using true 24h data: Current ${current_equity:.2f}, 24h ago ${equity_24h_ago:.2f}, P&L ${pnl_24h:.2f} ({pnl_percentage:.2f}%)")

            else:
                # Fallback to approximate calculation if no 24h data available
                print("⚠️  No 24h data available, using approximate calculation")

                # Get cumulative realized P&L (lifetime) and session P&L
                cum_realized_pnl = float(account_data.get('cumRealisedPnl', '0'))
                total_perp_upl = float(account_data.get('totalPerpUPL', '0'))  # Current unrealized P&L

                # Get today's closed P&L
                pnl_data = self.get_pnl_data()
                today_realized_pnl = pnl_data.get('today_pnl', 0) if pnl_data else 0

                # Use session data for real-time updates
                pnl_24h = today_realized_pnl + (total_perp_upl * 0.05)  # 5% weight on unrealized

                # Calculate percentage based on typical account size
                typical_equity = total_equity_usd - pnl_24h  # Approximate yesterday's equity
                pnl_percentage = (pnl_24h / typical_equity) * 100 if typical_equity > 0 else 0

            return {
                'equity': total_equity_usd,
                'pnl_24h': pnl_24h,
                'pnl_24h_percentage': pnl_percentage,
                'currency': 'USD'
            }

        except Exception as e:
            print(f"Error in get_account_info: {e}")
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
    
