# PowerShell script to fix Windows access to WSL2 Flask app
# Run this in PowerShell as Administrator

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "WSL2 Flask Access Fix" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get WSL2 IP
Write-Host "Getting WSL2 IP address..." -ForegroundColor Yellow
$wslIp = (wsl hostname -I).Trim()
Write-Host "WSL2 IP: $wslIp" -ForegroundColor Green
Write-Host ""

# Remove existing port proxy rules
Write-Host "Cleaning up existing port proxy rules..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=127.0.0.1 2>$null
Write-Host "Done." -ForegroundColor Green

# Add port forwarding
Write-Host "Setting up port forwarding..." -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "Port forwarding configured successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to configure port forwarding!" -ForegroundColor Red
    exit 1
}

# Remove existing firewall rule if it exists
Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "WSL2 Flask Port 5000" -ErrorAction SilentlyContinue

# Add firewall rule
New-NetFirewallRule -DisplayName "WSL2 Flask Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -ErrorAction Stop
Write-Host "Firewall rule added successfully!" -ForegroundColor Green

# Show current port proxies
Write-Host ""
Write-Host "Current port forwarding rules:" -ForegroundColor Cyan
netsh interface portproxy show all

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Try accessing the app at:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "If you still get errors, try:" -ForegroundColor Yellow
Write-Host "  http://$wslIp`:5000" -ForegroundColor White
Write-Host ""

