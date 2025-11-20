#!/bin/bash
# Script to get WSL2 IP and provide port forwarding instructions

echo "=========================================="
echo "WSL2 Port Forwarding Helper"
echo "=========================================="
echo ""

# Get WSL2 IP
WSL_IP=$(hostname -I | awk '{print $1}')
echo "WSL2 IP Address: $WSL_IP"
echo "Flask app is running on port: 5000"
echo ""

echo "Option 1: Access directly via WSL2 IP (may change on restart):"
echo "  http://$WSL_IP:5000"
echo ""

echo "Option 2: Set up port forwarding on Windows (recommended):"
echo ""
echo "  Run this in PowerShell as Administrator on Windows:"
echo ""
echo "  \$wslIp = (wsl hostname -I).Trim()"
echo "  netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=\$wslIp"
echo ""
echo "  Or run the forward-port.ps1 script from Windows PowerShell"
echo ""

echo "Option 3: Use WSL hostname (if available):"
echo "  http://$(hostname).local:5000"
echo ""

