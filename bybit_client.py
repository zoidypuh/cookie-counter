import os
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
from google.cloud import datastore

load_dotenv()

KIND_EQUITY = 'EquitySnapshot'

class BybitClient:
    def __init__(self, use_datastore: Optional[bool] = None):
        api_key = os.getenv('key') or os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('secret') or os.getenv('BYBIT_API_SECRET')

        if not api_key or not api_secret:
            raise ValueError("API credentials not found")

        self.client = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )

        # Determine whether to use Datastore
        if use_datastore is None:
            use_datastore = bool(os.getenv('GAE_ENV'))

        self.datastore_client = self._init_datastore() if use_datastore else None

    def _init_datastore(self):
        """Initialize Datastore client"""
        try:
            return datastore.Client()
        except Exception as e:
            print(f"⚠️  Datastore init failed: {e}")
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
    
    def get_24h_equity_data(self) -> List[Dict]:
        """Get equity snapshots from the last 24 hours"""
        if not self.datastore_client:
            return []

        try:
            # Get snapshots from last 24 hours
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

            data = []
            query = self.datastore_client.query(kind=KIND_EQUITY)
            query.add_filter('timestamp', '>=', cutoff_time)
            query.order = ['-timestamp']

            for entity in query.fetch():
                data.append({
                    'timestamp': entity['timestamp'],
                    'equity': float(entity['equity'])
                })

            return data

        except Exception as e:
            print(f"Error fetching 24h equity data: {e}")
            return []

    def get_account_info(self, datastore_override: bool = False) -> Optional[Dict]:
        try:
            balance_response = self.get_wallet_balance()

            if not balance_response or balance_response['retCode'] != 0:
                return None

            account_data = balance_response['result']['list'][0]
            total_equity_usd = float(account_data['totalEquity'])

            # Try to get true 24h rolling P&L from stored equity data
            use_datastore = datastore_override or self.datastore_client is not None
            equity_24h_data = self.get_24h_equity_data() if use_datastore else []

            if equity_24h_data and len(equity_24h_data) >= 2:
                # Sort by timestamp (most recent first)
                equity_24h_data.sort(key=lambda x: x['timestamp'], reverse=True)

                # Current equity (most recent snapshot)
                current_equity = equity_24h_data[0]['equity']

                # Equity approximately 24 hours ago (oldest snapshot in range)
                equity_24h_ago = equity_24h_data[-1]['equity']

                # Calculate true 24h P&L and percentage
                pnl_24h = current_equity - equity_24h_ago
                pnl_percentage = (pnl_24h / equity_24h_ago) * 100 if equity_24h_ago > 0 else 0

                print(f"✅ Using true 24h data: Current ${current_equity:.2f}, 24h ago ${equity_24h_ago:.2f}, P&L ${pnl_24h:.2f} ({pnl_percentage:.2f}%)")

            else:
                # Fallback to approximate calculation if no 24h data available
                print("⚠️  No 24h data available, using approximate calculation")

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
    
