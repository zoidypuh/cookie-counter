#!/usr/bin/env python3
"""
Simple Bybit WebSocket Position Monitor
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
    """Handle and display incoming position messages"""
    console.clear()
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    console.print(f"[cyan]Timestamp: {timestamp}[/cyan]")
    
    # Format and display JSON
    json_str = json.dumps(message, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Position Update", border_style="green"))
    
    # Extract and display key position info
    if 'data' in message and message['data']:
        console.print("\n[bold]Active Positions:[/bold]")
        for pos in message['data']:
            symbol = pos.get('symbol', 'Unknown')
            side = pos.get('side', '')
            size = float(pos.get('size', 0))
            
            if size > 0:  # Only show non-zero positions
                entry_price = float(pos.get('entryPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                unrealized_pnl = float(pos.get('unrealisedPnl', 0))
                leverage = pos.get('leverage', '1')
                
                pnl_color = "green" if unrealized_pnl >= 0 else "red"
                side_color = "green" if side == "Buy" else "red"
                
                console.print(f"\n{symbol}:")
                console.print(f"  Side: [{side_color}]{side}[/{side_color}] | Size: {size}")
                console.print(f"  Entry: ${entry_price:.4f} | Mark: ${mark_price:.4f}")
                console.print(f"  PnL: [{pnl_color}]${unrealized_pnl:.2f}[/{pnl_color}] | Leverage: {leverage}x")

def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]Simple Bybit Position Monitor[/bold cyan]\n"
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
        console.print("[yellow]Subscribing to position stream...[/yellow]")
        console.print("[dim]Updates occur when you create/modify/cancel orders[/dim]\n")
        
        # Subscribe to position stream
        ws.position_stream(callback=handle_message)
        
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
