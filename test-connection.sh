#!/bin/bash
# Test script to diagnose connection issues

echo "=========================================="
echo "Connection Diagnostic Test"
echo "=========================================="
echo ""

WSL_IP=$(hostname -I | awk '{print $1}')
echo "WSL2 IP: $WSL_IP"
echo ""

echo "Testing from inside WSL2:"
echo "1. Testing localhost:5000..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/api/health

echo "2. Testing WSL2 IP:5000..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://$WSL_IP:5000/api/health

echo ""
echo "=========================================="
echo "Windows Access Instructions:"
echo "=========================================="
echo ""
echo "From Windows PowerShell (run as Administrator), execute:"
echo ""
echo "# Get WSL2 IP"
echo "\$wslIp = (wsl hostname -I).Trim()"
echo ""
echo "# Add firewall rule"
echo "New-NetFirewallRule -DisplayName 'WSL2 Flask' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow"
echo ""
echo "# Set up port forwarding"
echo "netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=\$wslIp"
echo ""
echo "Then try: http://localhost:5000"
echo ""

