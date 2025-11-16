# Bybit WebSocket Monitor Scripts

Scripts for monitoring your Bybit wallet and positions in real-time via WebSocket connection.

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

### 3. websocket_position_monitor.py
Real-time position monitor with formatted tables showing all your open positions.

**Features:**
- Real-time position updates
- Detailed position information (size, entry price, mark price, PnL)
- Liquidation price warnings
- Color-coded profit/loss indicators
- Position status tracking
- Total unrealized/realized PnL summary
- Support for all position types (linear, inverse, option)

**Usage:**
```bash
python3 websocket_position_monitor.py
```

### 4. websocket_position_simple.py
Simple position monitor that shows raw JSON responses with key metrics.

**Features:**
- Raw JSON display with syntax highlighting
- Key position metrics extraction
- Active positions summary
- Minimal interface

**Usage:**
```bash
python3 websocket_position_simple.py
```

## WebSocket Stream Details

### Wallet Stream
According to the [Bybit documentation](https://bybit-exchange.github.io/docs/v5/websocket/private/wallet), the wallet stream provides:

- **Real-time updates** when wallet changes occur
- **No snapshot** on initial connection (only updates)
- **No updates** for unrealized PnL changes alone

**Key Data Fields:**
- `totalEquity`: Total account equity in USD
- `totalWalletBalance`: Sum of all asset balances in USD
- `totalAvailableBalance`: Available balance for trading
- `accountMMRate`: Account maintenance margin rate
- `totalMaintenanceMargin`: Total maintenance margin required
- Individual coin balances with collateral status

### Position Stream
According to the [Bybit documentation](https://bybit-exchange.github.io/docs/v5/websocket/private/position), the position stream provides:

- **Real-time updates** when positions change
- **Updates trigger** on every order create/amend/cancel (even if no actual position change)
- **Support for all position types**: linear, inverse, option
- **All-In-One topic** or categorized topics available

**Key Data Fields:**
- `symbol`: Trading pair
- `side`: Buy (long) or Sell (short)
- `size`: Position size
- `entryPrice`: Average entry price
- `markPrice`: Current mark price
- `unrealisedPnl`: Unrealized profit/loss
- `liqPrice`: Liquidation price
- `leverage`: Position leverage
- `positionStatus`: Normal, Liq, or Adl

## Important: Why You Don't See Data Initially

**Both wallet and position streams do NOT send current state when connecting!**

### Wallet Stream
You will only see updates when wallet changes occur:
- Place or cancel an order
- Execute a trade  
- Deposit or withdraw funds
- Any other action that changes wallet balance

### Position Stream
You will see updates when:
- You create, modify, or cancel an order
- A position is opened or closed
- Position parameters change (leverage, margin, etc.)
- Note: Updates occur even if the order doesn't result in actual position change

**The scripts are NOT stuck** - they're waiting for changes to report.

## Testing

To test if your connection is working:
1. Run `websocket_wallet_test.py` to see a demo of what wallet updates look like
2. Run `websocket_position_monitor.py` to monitor your positions
3. Go to Bybit and place a small limit order
4. Cancel the order
5. You should see both wallet and position updates appear

## Notes

- The WebSocket connection will remain open until you stop the script (Ctrl+C)
- Updates only appear when actual wallet changes occur (deposits, trades, etc.)
- You may need to wait for trading activity to see updates
- For testnet, make sure you have testnet API keys configured
- Price movements alone do NOT trigger wallet updates (unrealized PnL changes are not sent)
