Write-Host "Please follow these steps to restart external services:"
Write-Host "1. Close the existing CMD windows for 'Product Service' and 'Inventory Service'."
Write-Host "2. Wait a few seconds for ports 9001/9002 to release."
Write-Host "3. I will relaunch them for you."

# Ask user to confirm
$confirmation = Read-Host "Have you closed the external CMD windows? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Aborted. Please close them and run this script again."
    exit
}

$services = @(
    @{Name="Product Service"; Path="supermarket-cloud\supermarket-product"},
    @{Name="Inventory Service"; Path="supermarket-cloud\supermarket-inventory"}
)

foreach ($svc in $services) {
    $fullPath = Join-Path (Get-Location) $svc.Path
    Write-Host "Launching $($svc.Name) in a new window..."
    Start-Process cmd -ArgumentList "/k title $($svc.Name) & cd /d $fullPath & mvn spring-boot:run"
}

Write-Host "Services relaunched."
