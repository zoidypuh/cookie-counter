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

## Notes

- The WebSocket connection will remain open until you stop the script (Ctrl+C)
- Updates only appear when actual wallet changes occur (deposits, trades, etc.)
- You may need to wait for trading activity to see updates
- For testnet, make sure you have testnet API keys configured
