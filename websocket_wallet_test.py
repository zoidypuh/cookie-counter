#!/usr/bin/env python3
"""
Test Bybit WebSocket Wallet Monitor
Shows how the wallet stream works with demo data
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import WebSocket
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from time import sleep
import threading

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

# Flag to track if we've received any messages
message_received = threading.Event()

def handle_message(message):
    """Handle and display incoming wallet messages"""
    message_received.set()  # Signal that we got a message
    
    console.clear()
    console.print("[green]✓ Wallet Update Received![/green]\n")
    
    # Format and display JSON
    json_str = json.dumps(message, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Wallet Update", border_style="green"))
    
    # Extract and display key metrics
    if 'data' in message and message['data']:
        data = message['data'][0]
        console.print("\n[bold]Key Changes:[/bold]")
        console.print(f"Total Equity: [green]${float(data.get('totalEquity', 0)):,.2f}[/green]")
        console.print(f"Available Balance: [green]${float(data.get('totalAvailableBalance', 0)):,.2f}[/green]")
        console.print(f"Maintenance Margin: [yellow]${float(data.get('totalMaintenanceMargin', 0)):,.2f}[/yellow]")

def show_demo_data():
    """Show what a typical wallet update looks like"""
    demo_message = {
        "id": "592324d2bce751-ad38-48eb-8f42-4671d1fb4d4e",
        "topic": "wallet",
        "creationTime": int(datetime.now().timestamp() * 1000),
        "data": [{
            "accountType": "UNIFIED",
            "accountIMRate": "0.3789",
            "accountMMRate": "0.1686",
            "totalEquity": "32801.55",
            "totalWalletBalance": "32801.55",
            "totalAvailableBalance": "20369.78",
            "totalMaintenanceMargin": "5531.11",
            "totalPerpUPL": "-69256.92",
            "coin": [{
                "coin": "USDT",
                "walletBalance": "32801.55",
                "equity": "32801.55",
                "usdValue": "32801.55",
                "unrealisedPnl": "-69256.92",
                "marginCollateral": True
            }]
        }]
    }
    
    console.print("\n[yellow]Example of what a wallet update looks like:[/yellow]")
    json_str = json.dumps(demo_message, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Demo Wallet Update", border_style="yellow"))

def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]Bybit Wallet WebSocket Test[/bold cyan]\n"
        "Understanding how wallet updates work",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Important:[/bold] The wallet stream only sends updates when changes occur!")
    console.print("You will [red]NOT[/red] see any data until you:")
    console.print("  • Place or cancel an order")
    console.print("  • Execute a trade")
    console.print("  • Deposit or withdraw funds")
    console.print("  • Any other action that changes wallet balance\n")
    
    # Show demo data first
    show_demo = console.input("Show example wallet update first? (Y/n): ").lower() != 'n'
    if show_demo:
        show_demo_data()
    
    # Get API credentials
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        console.print("\n[red]Error: BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env file[/red]")
        return
    
    # Ask for testnet/mainnet
    use_testnet = console.input("\nConnect to testnet? (y/N): ").lower() == 'y'
    
    console.print(f"\n[yellow]Connecting to {'testnet' if use_testnet else 'mainnet'}...[/yellow]")
    
    try:
        # Connect to WebSocket
        ws = WebSocket(
            testnet=use_testnet,
            channel_type="private",
            api_key=api_key,
            api_secret=api_secret,
        )
        
        console.print(f"[green]✓ Connected to Bybit WebSocket[/green]")
        
        # Subscribe to wallet stream
        ws.wallet_stream(callback=handle_message)
        console.print("[green]✓ Subscribed to wallet stream[/green]")
        
        console.print("\n[bold yellow]Waiting for wallet changes...[/bold yellow]")
        console.print("[dim]Go to Bybit and place/cancel an order to see updates[/dim]")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
        
        # Show spinner while waiting
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Monitoring wallet for changes...", total=None)
            
            while not message_received.is_set():
                sleep(0.5)
                
        # After first message, just wait
        console.print("\n[dim]Continue monitoring... Press Ctrl+C to exit[/dim]")
        while True:
            sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
    finally:
        if 'ws' in locals():
            ws.exit()
            console.print("[dim]Connection closed[/dim]")

if __name__ == "__main__":
    main()
