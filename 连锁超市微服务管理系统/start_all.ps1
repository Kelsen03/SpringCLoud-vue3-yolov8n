# Stop existing java processes to ensure clean slate
Write-Host "Stopping existing Java processes..."
Get-Process -Name java -ErrorAction SilentlyContinue | Stop-Process -Force

# Start Nacos
Write-Host "Starting Nacos (Standalone)..."
$nacosPath = "nacos\bin\startup.cmd"
if (Test-Path $nacosPath) {
    Start-Process cmd -ArgumentList "/c start $nacosPath -m standalone" -WindowStyle Minimized
} else {
    Write-Error "Nacos startup script not found at $nacosPath"
}

Write-Host "Waiting 15 seconds for Nacos to initialize..."
Start-Sleep -Seconds 15

# Services list
$services = @(
    @{Name="Gateway Service"; Path="supermarket-cloud\supermarket-gateway"},
    @{Name="Auth Service"; Path="supermarket-cloud\supermarket-auth"},
    @{Name="Product Service"; Path="supermarket-cloud\supermarket-product"},
    @{Name="Inventory Service"; Path="supermarket-cloud\supermarket-inventory"},
    @{Name="Order Service"; Path="supermarket-cloud\supermarket-order"},
    @{Name="Analysis Service"; Path="supermarket-cloud\supermarket-analysis"}
)

foreach ($svc in $services) {
    $fullPath = Join-Path (Get-Location) $svc.Path
    if (Test-Path $fullPath) {
        Write-Host "Launching $($svc.Name)..."
        # cmd /k keeps window open. & connects commands.
        Start-Process cmd -ArgumentList "/k title $($svc.Name) & cd /d ""$fullPath"" & mvn spring-boot:run"
    } else {
        Write-Error "Path not found: $fullPath"
    }
}

Write-Host "All launch commands issued. Please check the new CMD windows for startup status."
