#!/usr/bin/env python3
"""
Bybit WebSocket Wallet Monitor
Connects to Bybit's private wallet stream and displays formatted real-time updates
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import WebSocket
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from time import sleep

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

class WalletMonitor:
    def __init__(self, testnet=False):
        """Initialize the wallet monitor with API credentials from .env"""
        self.testnet = testnet
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            console.print("[red]Error: BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env file[/red]")
            exit(1)
            
        self.ws = None
        self.latest_data = None
        
    def connect(self):
        """Connect to Bybit WebSocket"""
        try:
            self.ws = WebSocket(
                testnet=self.testnet,
                channel_type="private",
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
            console.print(f"[green]Connected to Bybit WebSocket ({'Testnet' if self.testnet else 'Mainnet'})[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")
            return False
    
    def handle_message(self, message):
        """Handle incoming wallet messages"""
        self.latest_data = message
        
    def format_wallet_data(self):
        """Format wallet data for display"""
        if not self.latest_data or 'data' not in self.latest_data:
            return Panel("[yellow]Waiting for wallet updates...[/yellow]", title="Wallet Status")
        
        data = self.latest_data['data'][0]
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="account", size=10),
            Layout(name="coins"),
            Layout(name="footer", size=3)
        )
        
        # Header with timestamp
        timestamp = datetime.fromtimestamp(self.latest_data['creationTime'] / 1000)
        header_text = Text(f"Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", style="cyan")
        layout["header"].update(Panel(header_text, title="Bybit Wallet Monitor"))
        
        # Account Summary Table
        account_table = Table(title="Account Summary")
        account_table.add_column("Metric", style="cyan")
        account_table.add_column("Value", justify="right")
        
        # Format numbers to 2 decimal places
        def format_number(value):
            try:
                return f"${float(value):,.2f}"
            except:
                return value
        
        # Key account metrics
        account_table.add_row("Account Type", data['accountType'])
        account_table.add_row("Total Equity", format_number(data['totalEquity']))
        account_table.add_row("Wallet Balance", format_number(data['totalWalletBalance']))
        account_table.add_row("Available Balance", format_number(data['totalAvailableBalance']))
        account_table.add_row("Unrealized PnL", format_number(data['totalPerpUPL']))
        account_table.add_row("Initial Margin", format_number(data['totalInitialMargin']))
        account_table.add_row("Maintenance Margin", format_number(data['totalMaintenanceMargin']))
        account_table.add_row("IM Rate", f"{data['accountIMRate']}%")
        account_table.add_row("MM Rate", f"{data['accountMMRate']}%")
        
        layout["account"].update(Panel(account_table))
        
        # Coin Details Table
        coin_table = Table(title="Coin Balances")
        coin_table.add_column("Coin", style="yellow")
        coin_table.add_column("Balance", justify="right")
        coin_table.add_column("USD Value", justify="right", style="green")
        coin_table.add_column("Equity", justify="right")
        coin_table.add_column("Unrealized PnL", justify="right")
        coin_table.add_column("Collateral", justify="center")
        
        for coin in data.get('coin', []):
            pnl_style = "green" if float(coin['unrealisedPnl']) >= 0 else "red"
            coin_table.add_row(
                coin['coin'],
                f"{float(coin['walletBalance']):.8f}",
                format_number(coin['usdValue']),
                f"{float(coin['equity']):.8f}",
                f"[{pnl_style}]{format_number(coin['unrealisedPnl'])}[/{pnl_style}]",
                "✓" if coin.get('marginCollateral', False) else "✗"
            )
        
        layout["coins"].update(Panel(coin_table))
        
        # Footer
        footer_text = Text("Press Ctrl+C to exit", style="dim")
        layout["footer"].update(Panel(footer_text))
        
        return layout
    
    def start_monitoring(self):
        """Start monitoring wallet updates"""
        if not self.connect():
            return
        
        # Subscribe to wallet stream
        self.ws.wallet_stream(callback=self.handle_message)
        console.print("[green]Subscribed to wallet stream[/green]")
        
        # Live display
        with Live(self.format_wallet_data(), refresh_per_second=1, console=console) as live:
            try:
                while True:
                    live.update(self.format_wallet_data())
                    sleep(0.5)
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped by user[/yellow]")
            finally:
                if self.ws:
                    self.ws.exit()
                    console.print("[dim]WebSocket connection closed[/dim]")

def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]Bybit Wallet Monitor[/bold cyan]\n"
        "Real-time wallet updates via WebSocket",
        border_style="cyan"
    ))
    
    # Ask for testnet/mainnet
    use_testnet = console.input("\nUse testnet? (y/N): ").lower() == 'y'
    
    monitor = WalletMonitor(testnet=use_testnet)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
