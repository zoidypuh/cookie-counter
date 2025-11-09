#!/usr/bin/env python3
"""
Hourly equity collector for Bybit Cookie Counter
Stores equity snapshots in Firestore for 24h rolling window calculations
"""

import os
from datetime import datetime, timezone, timedelta
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
from bybit_client import BybitClient

# Load environment variables
load_dotenv()

def init_firestore():
    """Initialize Firestore connection"""
    # For Google Cloud App Engine, credentials are automatically available
    if os.getenv('GAE_ENV'):
        # Running on GAE - use default credentials
        initialize_app()
    else:
        # Local development - would need service account key
        # For now, we'll skip Firestore locally and just print
        print("⚠️  Local mode - Firestore not initialized")
        return None

    return firestore.client()

def collect_equity_snapshot():
    """Collect and store current equity snapshot"""
    try:
        # Get current equity
        client = BybitClient()
        account_info = client.get_account_info()

        if not account_info:
            print("❌ Failed to get account info")
            return False

        current_equity = account_info['equity']
        now = datetime.now(timezone.utc)

        # Create hour key for easy querying (YYYY-MM-DD-HH)
        hour_key = now.strftime('%Y-%m-%d-%H')

        # Store in Firestore
        db = init_firestore()
        if db:
            doc_ref = db.collection('equity_snapshots').document(hour_key)

            doc_ref.set({
                'timestamp': now,
                'equity': current_equity,
                'hour_key': hour_key
            })

            print(f"✅ Stored equity snapshot: ${current_equity:.2f} at {now}")
        else:
            # Local mode - just print
            print(f"📊 Local mode - would store: ${current_equity:.2f} at {now}")

        # Clean up old snapshots (keep only last 25 hours)
        cleanup_old_snapshots(db, now)

        return True

    except Exception as e:
        print(f"❌ Error collecting equity: {e}")
        return False

def cleanup_old_snapshots(db, current_time):
    """Remove snapshots older than 25 hours"""
    if not db:
        return

    try:
        cutoff_time = current_time - timedelta(hours=25)

        # Query for old snapshots
        old_snapshots = db.collection('equity_snapshots') \
            .where('timestamp', '<', cutoff_time) \
            .stream()

        deleted_count = 0
        for doc in old_snapshots:
            doc.reference.delete()
            deleted_count += 1

        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old snapshots")

    except Exception as e:
        print(f"⚠️  Error cleaning up snapshots: {e}")

def get_24h_equity_data():
    """Get equity data for the last 24 hours (for testing/debugging)"""
    db = init_firestore()
    if not db:
        return []

    try:
        # Get snapshots from last 24 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        snapshots = db.collection('equity_snapshots') \
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
        print(f"❌ Error fetching 24h data: {e}")
        return []

if __name__ == '__main__':
    print("🍪 Bybit Equity Collector")
    print("=" * 30)

    success = collect_equity_snapshot()

    if success:
        # Show current 24h data for debugging
        data_24h = get_24h_equity_data()
        if data_24h:
            print(f"\n📈 Last 24h equity data ({len(data_24h)} snapshots):")
            for snap in data_24h[:5]:  # Show first 5
                print(f"  {snap['timestamp'].strftime('%Y-%m-%d %H:%M')} UTC: ${snap['equity']:.2f}")
            if len(data_24h) > 5:
                print(f"  ... and {len(data_24h) - 5} more")
        else:
            print("\n📊 No 24h data available yet")
    else:
        print("\n❌ Collection failed")
