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
    
    def get_snapshot_data(self, hours: int, ds=None) -> List[Dict]:
        """Get equity snapshots from the last `hours` hours."""
        ds = ds or self.datastore_client
        if not ds:
            return []

        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            data = []
            query = ds.query(kind=KIND_EQUITY)
            query.add_filter('timestamp', '>=', cutoff_time)
            query.order = ['-timestamp']

            for entity in query.fetch():
                data.append({
                    'timestamp': entity['timestamp'],
                    'equity': float(entity['equity'])
                })

            return data

        except Exception as e:
            print(f"Error fetching {hours}h equity data: {e}")
            return []

    def get_account_info(self, datastore_override: bool = False) -> Optional[Dict]:
        try:
            balance_response = self.get_wallet_balance()

            if not balance_response or balance_response['retCode'] != 0:
                return None

            account_data = balance_response['result']['list'][0]
            total_equity_usd = float(account_data['totalEquity'])
            
            # Extract maintenance margin data
            total_maintenance_margin = float(account_data.get('totalMaintenanceMargin', 0))
            account_mm_rate = float(account_data.get('accountMMRate', 0))
            total_available_balance = float(account_data.get('totalAvailableBalance', 0))

            now = datetime.now(timezone.utc)

            gross_position_value = 0.0
            effective_leverage = None

            # Prepare default values
            pnl_1h = None
            pnl_1h_pct = None
            pnl_1h_source = 'missing'
            pnl_1h_hours = None

            pnl_24h = None
            pnl_24h_pct = None
            pnl_24h_source = 'approx'
            pnl_24h_hours = None

            pnl_72h = None
            pnl_72h_pct = None
            pnl_72h_source = 'missing'
            pnl_72h_hours = None

            # Try to get true rolling data from Datastore
            ds_client = self.datastore_client
            if datastore_override and not ds_client:
                ds_client = self._init_datastore()

            equity_data = self.get_snapshot_data(72, ds_client) if ds_client else []

            if equity_data:
                equity_data.sort(key=lambda x: x['timestamp'], reverse=True)
                current_equity_snapshot = equity_data[0]
                current_equity = total_equity_usd  # Live equity

                def find_snapshot(hours: float):
                    target = now - timedelta(hours=hours)
                    for entry in equity_data:
                        if entry['timestamp'] <= target:
                            return entry
                    return None

                # 1 hour change
                snap_1h = find_snapshot(1.0)
                if not snap_1h and len(equity_data) > 1:
                    snap_1h = equity_data[1]
                if snap_1h:
                    base_equity = snap_1h['equity']
                    pnl_1h = current_equity - base_equity
                    pnl_1h_pct = (pnl_1h / base_equity) * 100 if base_equity > 0 else 0
                    pnl_1h_hours = max(0.01, (now - snap_1h['timestamp']).total_seconds() / 3600)
                    pnl_1h_source = 'true' if (now - snap_1h['timestamp']).total_seconds() >= 3600 else 'fallback'

                # 24 hour change
                snap_24h = find_snapshot(24.0)
                if snap_24h:
                    base_24h = snap_24h['equity']
                    pnl_24h = current_equity - base_24h
                    pnl_24h_pct = (pnl_24h / base_24h) * 100 if base_24h > 0 else 0
                    pnl_24h_hours = max(0.01, (now - snap_24h['timestamp']).total_seconds() / 3600)
                    pnl_24h_source = 'true'

                # 72 hour change
                pnl_72h = None
                pnl_72h_pct = None
                pnl_72h_source = 'missing'
                pnl_72h_hours = None

                snap_72h = find_snapshot(72.0)
                if snap_72h:
                    base_72h = snap_72h['equity']
                    pnl_72h = current_equity - base_72h
                    pnl_72h_pct = (pnl_72h / base_72h) * 100 if base_72h > 0 else 0
                    pnl_72h_hours = max(0.01, (now - snap_72h['timestamp']).total_seconds() / 3600)
                    pnl_72h_source = 'true'

            # Calculate effective leverage from open positions
            try:
                linear_response = self.client.get_positions(
                    category="linear",
                    settleCoin="USDT"
                )
                if linear_response and linear_response.get('retCode') == 0:
                    positions = linear_response.get('result', {}).get('list', [])
                    for pos in positions:
                        pos_value = pos.get('positionValue')
                        if pos_value and pos_value != '0':
                            gross_position_value += abs(float(pos_value))
                
                if total_equity_usd > 0:
                    effective_leverage = gross_position_value / total_equity_usd
                else:
                    effective_leverage = 0.0
            except Exception as e:
                print(f"Error calculating leverage: {e}")
                effective_leverage = None

            # Fallbacks when datastore is unavailable or incomplete
            if pnl_1h is None:
                pnl_1h = 0.0
                pnl_1h_pct = 0.0
                pnl_1h_source = 'missing'

            if pnl_24h is None:
                print("⚠️  No 24h data available, using approximate calculation")
                total_perp_upl = float(account_data.get('totalPerpUPL', '0'))  # Current unrealized P&L
                pnl_data = self.get_pnl_data()
                today_realized_pnl = pnl_data.get('today_pnl', 0) if pnl_data else 0
                pnl_24h = today_realized_pnl + (total_perp_upl * 0.05)  # Approximate
                typical_equity = total_equity_usd - pnl_24h
                pnl_24h_pct = (pnl_24h / typical_equity) * 100 if typical_equity > 0 else 0
                pnl_24h_source = 'approx'
                pnl_72h = pnl_24h
                pnl_72h_pct = pnl_24h_pct
                pnl_72h_source = 'approx'

            if pnl_72h is None:
                pnl_72h = pnl_24h
                pnl_72h_pct = pnl_24h_pct
                pnl_72h_source = 'approx'

            return {
                'equity': total_equity_usd,
                'pnl_1h': pnl_1h,
                'pnl_1h_percentage': pnl_1h_pct,
                'pnl_1h_source': pnl_1h_source,
                'pnl_1h_hours': pnl_1h_hours,
                'pnl_24h': pnl_24h,
                'pnl_24h_percentage': pnl_24h_pct,
                'pnl_24h_source': pnl_24h_source,
                'pnl_24h_hours': pnl_24h_hours,
                'pnl_72h': pnl_72h,
                'pnl_72h_percentage': pnl_72h_pct,
                'pnl_72h_source': pnl_72h_source,
                'pnl_72h_hours': pnl_72h_hours,
                'equity_snapshots': equity_data,
                'currency': 'USD',
                'effective_leverage': effective_leverage,
                'maintenance_margin': total_maintenance_margin,
                'maintenance_margin_rate': account_mm_rate,
                'available_balance': total_available_balance
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
    
