#!/usr/bin/env python3
"""
Bybit WebSocket Position Monitor
Connects to Bybit's private position stream and displays formatted real-time updates
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

class PositionMonitor:
    def __init__(self, testnet=False):
        """Initialize the position monitor with API credentials from .env"""
        self.testnet = testnet
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            console.print("[red]Error: BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env file[/red]")
            exit(1)
            
        self.ws = None
        self.positions = {}  # Store positions by symbol
        
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
        """Handle incoming position messages"""
        if 'data' in message:
            for position in message['data']:
                symbol = position.get('symbol', 'Unknown')
                self.positions[symbol] = {
                    'data': position,
                    'timestamp': message.get('creationTime', 0)
                }
    
    def format_position_data(self):
        """Format position data for display"""
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="positions"),
            Layout(name="footer", size=3)
        )
        
        # Header with timestamp
        timestamp = datetime.now()
        header_text = Text(f"Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", style="cyan")
        layout["header"].update(Panel(header_text, title="Bybit Position Monitor"))
        
        # Position Table
        position_table = Table(title="Open Positions")
        position_table.add_column("Symbol", style="yellow")
        position_table.add_column("Side", justify="center")
        position_table.add_column("Size", justify="right")
        position_table.add_column("Entry Price", justify="right")
        position_table.add_column("Mark Price", justify="right")
        position_table.add_column("Unrealized PnL", justify="right")
        position_table.add_column("Realized PnL", justify="right")
        position_table.add_column("Liq Price", justify="right", style="red")
        position_table.add_column("Leverage", justify="center")
        position_table.add_column("Status", justify="center")
        
        # Format numbers
        def format_price(value):
            try:
                return f"{float(value):.4f}" if float(value) != 0 else "-"
            except:
                return value or "-"
        
        def format_pnl(value):
            try:
                val = float(value)
                color = "green" if val >= 0 else "red"
                return f"[{color}]{val:.2f}[/{color}]"
            except:
                return value or "0.00"
        
        # Add positions to table
        if not self.positions:
            position_table.add_row(
                "[dim]No positions[/dim]", "", "", "", "", "", "", "", "", ""
            )
        else:
            for symbol, pos_info in sorted(self.positions.items()):
                pos = pos_info['data']
                
                # Skip empty positions
                if float(pos.get('size', 0)) == 0:
                    continue
                
                # Determine side color
                side = pos.get('side', '')
                side_color = "green" if side == "Buy" else "red" if side == "Sell" else "dim"
                
                # Position status color
                status = pos.get('positionStatus', 'Normal')
                status_color = "green" if status == "Normal" else "red"
                
                position_table.add_row(
                    pos.get('symbol', 'Unknown'),
                    f"[{side_color}]{side}[/{side_color}]",
                    pos.get('size', '0'),
                    format_price(pos.get('entryPrice', '0')),
                    format_price(pos.get('markPrice', '0')),
                    format_pnl(pos.get('unrealisedPnl', '0')),
                    format_pnl(pos.get('curRealisedPnl', '0')),
                    format_price(pos.get('liqPrice', '0')),
                    f"{pos.get('leverage', '1')}x",
                    f"[{status_color}]{status}[/{status_color}]"
                )
        
        # Add summary row if there are positions
        if self.positions and any(float(p['data'].get('size', 0)) > 0 for p in self.positions.values()):
            position_table.add_row(
                "[bold]Total[/bold]", "", "", "", "",
                format_pnl(sum(float(p['data'].get('unrealisedPnl', 0)) for p in self.positions.values())),
                format_pnl(sum(float(p['data'].get('curRealisedPnl', 0)) for p in self.positions.values())),
                "", "", "",
                style="bold"
            )
        
        layout["positions"].update(Panel(position_table))
        
        # Footer
        footer_text = Text("Press Ctrl+C to exit | Updates on every order action", style="dim")
        layout["footer"].update(Panel(footer_text))
        
        return layout
    
    def start_monitoring(self):
        """Start monitoring position updates"""
        if not self.connect():
            return
        
        # Subscribe to position stream
        self.ws.position_stream(callback=self.handle_message)
        console.print("[green]Subscribed to position stream[/green]")
        console.print("[yellow]Note: Position updates occur when you create/amend/cancel orders[/yellow]")
        
        # Live display
        with Live(self.format_position_data(), refresh_per_second=1, console=console) as live:
            try:
                while True:
                    live.update(self.format_position_data())
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
        "[bold cyan]Bybit Position Monitor[/bold cyan]\n"
        "Real-time position updates via WebSocket",
        border_style="cyan"
    ))
    
    # Ask for testnet/mainnet
    use_testnet = console.input("\nUse testnet? (y/N): ").lower() == 'y'
    
    # Ask for topic type
    console.print("\nSelect position topic:")
    console.print("1. All positions (linear, inverse, option)")
    console.print("2. Linear positions only")
    console.print("3. Inverse positions only")
    console.print("4. Option positions only")
    
    choice = console.input("\nEnter choice (1-4) [1]: ").strip() or "1"
    
    monitor = PositionMonitor(testnet=use_testnet)
    
    # Note: The pybit library handles the topic subscription internally
    # based on the position_stream method, so we just need to start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
