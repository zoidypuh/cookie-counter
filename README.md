# Bybit Cookie Tracker 🍪

A web application that displays your Bybit perpetual account equity using cookies instead of dollar amounts.

## Features

- 🍪 Displays account equity as cookies (1 cookie = $1,000 USD)
- 📊 Shows cookies gained/lost in the last 24 hours
- 🎮 Trump GIF reactions based on P&L
- 📱 Responsive design for mobile and desktop

## Setup

1. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   - Create a `.env` file in the project root
   - Add your Bybit read-only API credentials:
     ```
     key=your_api_key_here
     secret=your_api_secret_here
     ```

3. **Run the application**:
   ```bash
   source venv/bin/activate
   python app.py
   ```

4. **Access the website**:
   - Open your browser and navigate to `http://localhost:5000`

## How it Works

- Each cookie represents $1,000 USD of your account equity
- Shows cookies gained/lost in the last 24 hours
- Trump winning/losing GIF based on your P&L
- "cookies still in jar" shows your current holdings

## Security Note

- API credentials are stored in `.env` file and never exposed
- Only read-only API keys should be used
