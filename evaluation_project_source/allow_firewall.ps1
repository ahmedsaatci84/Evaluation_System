# Run this script as Administrator to allow Django server through firewall
# Right-click and select "Run with PowerShell" (as Administrator)

Write-Host "Adding firewall rule for Django Development Server..." -ForegroundColor Yellow
$localIp = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -ne '127.0.0.1' } |
    Select-Object -First 1 -ExpandProperty IPAddress)
if (-not $localIp) { $localIp = '127.0.0.1' }

try {
    New-NetFirewallRule -DisplayName "Django Development Server" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 8000 `
        -Action Allow `
        -Profile Any `
        -ErrorAction Stop
    
    Write-Host "Firewall rule added successfully!" -ForegroundColor Green
    Write-Host "You can now access the website from other devices using: http://$localIp`:8000" -ForegroundColor Cyan
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nPlease run this script as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click on the file" -ForegroundColor Yellow
    Write-Host "2. Select 'Run with PowerShell' as Administrator" -ForegroundColor Yellow
}

Read-Host "`nPress Enter to exit"
