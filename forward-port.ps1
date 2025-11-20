# PowerShell script to forward port 5000 from WSL2 to Windows
# Run this in PowerShell as Administrator on Windows

# Get WSL2 IP address
$wslIp = (wsl hostname -I).Trim()

Write-Host "WSL2 IP Address: $wslIp" -ForegroundColor Green
Write-Host "Setting up port forwarding from Windows localhost:5000 to WSL2 $wslIp`:5000" -ForegroundColor Yellow

# Remove existing port proxy if it exists
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>$null

# Add new port proxy
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=$wslIp

# Show current port proxies
Write-Host "`nCurrent port forwarding rules:" -ForegroundColor Cyan
netsh interface portproxy show all

Write-Host "`n✅ Port forwarding configured!" -ForegroundColor Green
Write-Host "You can now access the app at: http://localhost:5000" -ForegroundColor Green

