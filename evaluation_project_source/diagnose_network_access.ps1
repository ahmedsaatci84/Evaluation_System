param(
    [int]$Port = 8000
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Network Access Diagnostic Report" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ipv4 = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -ne '127.0.0.1' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ipv4) {
    $ipv4 = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.IPAddress -notlike '169.254.*' } |
        Select-Object -First 1 -ExpandProperty IPAddress)
}

if (-not $ipv4) {
    Write-Host "[FAIL] Could not detect a LAN IPv4 address." -ForegroundColor Red
    Write-Host "Connect to Wi-Fi or Ethernet and run again." -ForegroundColor Yellow
    exit 1
}

$url = "http://$ipv4`:$Port"

$activeProfile = Get-NetConnectionProfile -ErrorAction SilentlyContinue |
    Where-Object { $_.InterfaceAlias -like 'Wi-Fi*' -or $_.IPv4Connectivity -eq 'Internet' } |
    Select-Object -First 1

Write-Host "[INFO] Local IPv4: $ipv4" -ForegroundColor White
Write-Host "[INFO] Port: $Port" -ForegroundColor White
Write-Host "[INFO] URL for other devices: $url" -ForegroundColor Green

if ($activeProfile) {
    Write-Host "[INFO] Network profile: $($activeProfile.NetworkCategory) ($($activeProfile.InterfaceAlias))" -ForegroundColor White
    if ($activeProfile.NetworkCategory -eq 'Public') {
        Write-Host "[WARN] Network is Public. This can block access from other devices." -ForegroundColor Yellow
        Write-Host "[FIX ] Run PowerShell as Administrator then execute:" -ForegroundColor Yellow
        Write-Host "       Set-NetConnectionProfile -InterfaceAlias '$($activeProfile.InterfaceAlias)' -NetworkCategory Private" -ForegroundColor Yellow
    }
}

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listeners) {
    $pids = ($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
    Write-Host "[OK] Server is listening on port $Port." -ForegroundColor Green
    Write-Host "[INFO] Listening process IDs: $($pids -join ', ')" -ForegroundColor White
}
else {
    Write-Host "[FAIL] No process is listening on port $Port." -ForegroundColor Red
    Write-Host "Start server using: python manage.py runserver 0.0.0.0:$Port" -ForegroundColor Yellow
}

$allowRules = Get-NetFirewallRule -Direction Inbound -Enabled True -Action Allow -ErrorAction SilentlyContinue |
    Where-Object {
        $rule = $_
        $portFilters = Get-NetFirewallPortFilter -AssociatedNetFirewallRule $rule -ErrorAction SilentlyContinue
        if (-not $portFilters) { return $false }

        foreach ($filter in $portFilters) {
            if ($filter.Protocol -ne 'TCP' -and $filter.Protocol -ne 'Any') { continue }
            if ($filter.LocalPort -eq "$Port") { return $true }
        }
        return $false
    }

if ($allowRules) {
    Write-Host "[OK] Firewall has inbound allow rule for port $Port." -ForegroundColor Green
    $ruleNames = $allowRules | Select-Object -ExpandProperty DisplayName -Unique
    Write-Host "[INFO] Matching firewall rules: $($ruleNames -join '; ')" -ForegroundColor White
}
else {
    Write-Host "[FAIL] No inbound allow firewall rule found for port $Port." -ForegroundColor Red
    Write-Host "Run allow_firewall.ps1 as Administrator." -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 8
    Write-Host "[OK] Localhost HTTP check passed (status: $($response.StatusCode))." -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Localhost HTTP check failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $responseLan = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 8
    Write-Host "[OK] LAN URL check from this PC passed (status: $($responseLan.StatusCode))." -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] LAN URL check from this PC failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "" 
Write-Host "Quick checks on phone/another PC:" -ForegroundColor Cyan
Write-Host "1) Connect to same Wi-Fi network (not Guest)." -ForegroundColor White
Write-Host "2) Open: $url" -ForegroundColor White
Write-Host "3) If blocked, disable AP Isolation in router settings." -ForegroundColor White
