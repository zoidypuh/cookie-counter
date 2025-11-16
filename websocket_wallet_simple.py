#!/usr/bin/env python3
"""
Simple Bybit WebSocket Wallet Monitor
Shows raw JSON responses in a formatted way
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import WebSocket
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from time import sleep

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

def handle_message(message):
    """Handle and display incoming wallet messages"""
    console.clear()
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    console.print(f"[cyan]Timestamp: {timestamp}[/cyan]")
    
    # Format and display JSON
    json_str = json.dumps(message, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Wallet Update", border_style="green"))
    
    # Extract and display key metrics
    if 'data' in message and message['data']:
        data = message['data'][0]
        console.print("\n[bold]Key Metrics:[/bold]")
        console.print(f"Total Equity: [green]${float(data.get('totalEquity', 0)):,.2f}[/green]")
        console.print(f"Available Balance: [green]${float(data.get('totalAvailableBalance', 0)):,.2f}[/green]")
        console.print(f"Maintenance Margin: [yellow]${float(data.get('totalMaintenanceMargin', 0)):,.2f}[/yellow]")
        console.print(f"Account MM Rate: [yellow]{data.get('accountMMRate', 'N/A')}%[/yellow]")
        
        # Show coin balances
        if 'coin' in data:
            console.print("\n[bold]Coin Balances:[/bold]")
            for coin in data['coin']:
                balance = float(coin.get('walletBalance', 0))
                usd_value = float(coin.get('usdValue', 0))
                if balance > 0:
                    console.print(f"{coin['coin']}: {balance:.8f} (${usd_value:,.2f})")

def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]Simple Bybit Wallet Monitor[/bold cyan]\n"
        "Shows raw WebSocket responses",
        border_style="cyan"
    ))
    
    # Get API credentials
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        console.print("[red]Error: BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env file[/red]")
        return
    
    # Ask for testnet/mainnet
    use_testnet = console.input("\nUse testnet? (y/N): ").lower() == 'y'
    
    try:
        # Connect to WebSocket
        ws = WebSocket(
            testnet=use_testnet,
            channel_type="private",
            api_key=api_key,
            api_secret=api_secret,
        )
        
        console.print(f"[green]Connected to Bybit WebSocket ({'Testnet' if use_testnet else 'Mainnet'})[/green]")
        console.print("[yellow]Subscribing to wallet stream...[/yellow]\n")
        
        # Subscribe to wallet stream
        ws.wallet_stream(callback=handle_message)
        
        # Keep running
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
        while True:
            sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        if 'ws' in locals():
            ws.exit()
            console.print("[dim]Connection closed[/dim]")

if __name__ == "__main__":
    main()
