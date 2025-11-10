#!/usr/bin/env python3
"""
Hourly equity collector for Bybit Cookie Counter
Stores equity snapshots in Datastore (Firestore Datastore mode) for 24h rolling window calculations
"""

import os
from datetime import datetime, timezone, timedelta
from google.cloud import datastore
from dotenv import load_dotenv
from bybit_client import BybitClient

# Load environment variables
load_dotenv()

KIND = 'EquitySnapshot'

def init_datastore():
    """Initialize Datastore client"""
    if os.getenv('GAE_ENV'):
        return datastore.Client()
    else:
        print("⚠️  Local mode - Datastore not initialized")
        return None

def collect_equity_snapshot():
    """Collect and store current equity snapshot"""
    try:
        # Get current equity
        client = BybitClient(use_datastore=True)
        account_info = client.get_account_info(datastore_override=True)

        if not account_info:
            print("❌ Failed to get account info")
            return False

        current_equity = account_info['equity']
        now = datetime.now(timezone.utc)

        # Create hour key for easy querying (YYYY-MM-DD-HH)
        hour_key = now.strftime('%Y-%m-%d-%H')

        # Store in Datastore
        ds = init_datastore()
        if ds:
            key = ds.key(KIND, hour_key)
            entity = datastore.Entity(key=key)
            entity.update({
                'timestamp': now,
                'equity': current_equity,
                'hour_key': hour_key,
            })
            ds.put(entity)

            print(f"✅ Stored equity snapshot: ${current_equity:.2f} at {now}")
        else:
            # Local mode - just print
            print(f"📊 Local mode - would store: ${current_equity:.2f} at {now}")

        # Clean up old snapshots (keep only last 25 hours)
        cleanup_old_snapshots(ds, now)

        return True

    except Exception as e:
        print(f"❌ Error collecting equity: {e}")
        return False

def cleanup_old_snapshots(ds, current_time):
    """Remove snapshots older than 25 hours"""
    if not ds:
        return

    try:
        cutoff_time = current_time - timedelta(hours=25)

        query = ds.query(kind=KIND)
        query.add_filter('timestamp', '<', cutoff_time)

        deleted = 0
        for entity in query.fetch():
            ds.delete(entity.key)
            deleted += 1

        if deleted > 0:
            print(f"🧹 Cleaned up {deleted} old snapshots")

    except Exception as e:
        print(f"⚠️  Error cleaning up snapshots: {e}")

def get_24h_equity_data(ds=None):
    """Get equity data for the last 24 hours (for testing/debugging)"""
    ds = ds or init_datastore()
    if not ds:
        return []

    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        query = ds.query(kind=KIND)
        query.add_filter('timestamp', '>=', cutoff_time)
        query.order = ['-timestamp']

        data = []
        for entity in query.fetch():
            data.append({
                'timestamp': entity['timestamp'],
                'equity': entity['equity']
            })

        return data

    except Exception as e:
        print(f"❌ Error fetching 24h data: {e}")
        return []

if __name__ == '__main__':
    print("🍪 Bybit Equity Collector")
    print("=" * 30)

    success = collect_equity_snapshot()

    if success:
        ds = init_datastore()
        data_24h = get_24h_equity_data(ds)
        if data_24h:
            print(f"\n📈 Last 24h equity data ({len(data_24h)} snapshots):")
            for snap in data_24h[:5]:
                print(f"  {snap['timestamp'].strftime('%Y-%m-%d %H:%M')} UTC: ${snap['equity']:.2f}")
            if len(data_24h) > 5:
                print(f"  ... and {len(data_24h) - 5} more")
        else:
            print("\n📊 No 24h data available yet")
    else:
        print("\n❌ Collection failed")
