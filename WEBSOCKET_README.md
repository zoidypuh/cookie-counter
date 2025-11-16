# Bybit WebSocket Wallet Monitor Scripts

Two scripts for monitoring your Bybit wallet in real-time via WebSocket connection.

## Prerequisites

1. Install required dependencies:
```bash
pip install pybit python-dotenv rich
```

2. Make sure your `.env` file contains your Bybit API credentials:
```
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here
```

## Scripts

### 1. websocket_wallet_monitor.py
Full-featured wallet monitor with formatted tables and live updates.

**Features:**
- Real-time wallet balance updates
- Account summary with key metrics
- Individual coin balances with USD values
- Maintenance margin and risk indicators
- Color-coded unrealized PnL
- Live updating display

**Usage:**
```bash
python3 websocket_wallet_monitor.py
```

### 2. websocket_wallet_simple.py
Simple monitor that shows raw JSON responses with syntax highlighting.

**Features:**
- Raw JSON display with syntax highlighting
- Key metrics extraction
- Coin balance summary
- Minimal interface

**Usage:**
```bash
python3 websocket_wallet_simple.py
```

## WebSocket Wallet Stream Details

According to the [Bybit documentation](https://bybit-exchange.github.io/docs/v5/websocket/private/wallet), the wallet stream provides:

- **Real-time updates** when wallet changes occur
- **No snapshot** on initial connection (only updates)
- **No updates** for unrealized PnL changes alone

### Key Data Fields:
- `totalEquity`: Total account equity in USD
- `totalWalletBalance`: Sum of all asset balances in USD
- `totalAvailableBalance`: Available balance for trading
- `accountMMRate`: Account maintenance margin rate
- `totalMaintenanceMargin`: Total maintenance margin required
- Individual coin balances with collateral status

## Important: Why You Don't See Data Initially

**The wallet stream does NOT send your current wallet state when connecting!**

You will only see updates when wallet changes occur:
- Place or cancel an order
- Execute a trade  
- Deposit or withdraw funds
- Any other action that changes wallet balance

**The script is NOT stuck** - it's waiting for wallet changes to report.

## Testing

To test if your connection is working:
1. Run `websocket_wallet_test.py` to see a demo of what updates look like
2. Go to Bybit and place a small limit order
3. Cancel the order
4. You should see wallet updates appear

## Notes

- The WebSocket connection will remain open until you stop the script (Ctrl+C)
- Updates only appear when actual wallet changes occur (deposits, trades, etc.)
- You may need to wait for trading activity to see updates
- For testnet, make sure you have testnet API keys configured
- Price movements alone do NOT trigger wallet updates (unrealized PnL changes are not sent)
