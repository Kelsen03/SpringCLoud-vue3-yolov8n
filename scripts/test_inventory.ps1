$ErrorActionPreference = "Stop"

function Post-Json($Url, $Body) {
    $Headers = @{"Content-Type"="application/json"}
    # Inventory service doesn't require Auth header for these internal endpoints as per prompt logic (simplified)
    # But usually Gateway might require it if configured. 
    # The prompt says "Gateway route supplement", doesn't explicitly say secure it.
    # But previous AuthFilter might block it.
    # Let's assume we need a token or the endpoints are public?
    # The prompt for Gateway Auth Config said: "Public path: /auth/login".
    # So /inventory/** might be protected.
    # Let's get a token first.
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers
    return $Response
}

# Helper to get token
function Get-Token() {
    $Body = @{username="admin"; password="123456"} | ConvertTo-Json
    $Res = Invoke-RestMethod -Uri "http://localhost:8000/auth/login?username=admin&password=123456" -Method Post
    return $Res.token
}

function Post-Json-Auth($Url, $Token) {
    $Headers = @{"Content-Type"="application/json"; "Authorization"=$Token}
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers
    return $Response
}

function Get-Json-Auth($Url, $Token) {
    $Headers = @{"Authorization"=$Token}
    $Response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers
    return $Response
}

Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 5

Write-Host "1. Getting Token..."
try {
    $Token = Get-Token
    Write-Host "Token: $Token"
} catch {
    Write-Warning "Failed to get token. Services might not be ready. Check Gateway/Auth."
    exit
}

Write-Host "`n2. List Inventory (Store 1)..."
try {
    $List = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
    $List | Format-Table
} catch {
    Write-Error "List Failed: $_"
}

Write-Host "`n3. Deduct Stock (Product 1, Store 1, Count 5)..."
try {
    $Res = Post-Json-Auth "http://localhost:8000/inventory/deduct?productId=1&storeId=1&count=5" $Token
    Write-Host "Result: $Res"
} catch {
    Write-Error "Deduct Failed: $_"
}

Write-Host "`n4. List Inventory (Store 1) - Check Deduction..."
$List = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
$List | Format-Table

Write-Host "`n5. Deduct Excessive Stock (100)..."
try {
    $Res = Post-Json-Auth "http://localhost:8000/inventory/deduct?productId=1&storeId=1&count=100" $Token
    Write-Host "Result: $Res"
} catch {
    # It might return 200 OK with body "库存不足" or error code?
    # Controller returns String "库存不足".
    Write-Host "Result (Error): $_"
}

Write-Host "`n6. Transfer Stock (10 from Store 1 to Store 2)..."
try {
    $Res = Post-Json-Auth "http://localhost:8000/inventory/transfer?productId=1&fromStore=1&toStore=2&count=10" $Token
    Write-Host "Result: $Res"
} catch {
    Write-Error "Transfer Failed: $_"
}

Write-Host "`n7. List Store 1 and Store 2..."
Write-Host "Store 1:"
(Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token) | Format-Table
Write-Host "Store 2:"
(Get-Json-Auth "http://localhost:8000/inventory/list?storeId=2" $Token) | Format-Table
