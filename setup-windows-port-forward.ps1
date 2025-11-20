# PowerShell script to set up port forwarding from Windows to WSL2
# Run this in PowerShell as Administrator

Write-Host "Setting up port forwarding from Windows to WSL2..." -ForegroundColor Cyan

# Get WSL2 IP address
$wslIp = (wsl hostname -I).Trim()
Write-Host "WSL2 IP Address: $wslIp" -ForegroundColor Green

# Remove existing port proxy if it exists
Write-Host "`nRemoving existing port proxy rules..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=127.0.0.1 2>$null

# Add new port proxy
Write-Host "Adding new port proxy rule..." -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=$wslIp

# Show current port proxies
Write-Host "`nCurrent port forwarding rules:" -ForegroundColor Cyan
netsh interface portproxy show all

# Check Windows Firewall
Write-Host "`nChecking Windows Firewall..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "WSL2 Flask Port 5000" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    Write-Host "Creating Windows Firewall rule..." -ForegroundColor Yellow
    New-NetFirewallRule -DisplayName "WSL2 Flask Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Firewall rule created!" -ForegroundColor Green
} else {
    Write-Host "Firewall rule already exists." -ForegroundColor Green
}

Write-Host "`n✅ Port forwarding configured!" -ForegroundColor Green
Write-Host "You can now access the app at: http://localhost:5000" -ForegroundColor Green
Write-Host "Or directly via WSL2 IP: http://$wslIp`:5000" -ForegroundColor Green

