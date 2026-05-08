function Get-Token() {
    $Res = Invoke-RestMethod -Uri "http://localhost:8000/auth/login?username=admin&password=123456" -Method Post
    return $Res.token
}

function Post-Json-Auth($Url, $Token, $Body) {
    $Headers = @{"Content-Type"="application/json"; "Authorization"=$Token}
    $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 5)
    return $Response
}

function Get-Json-Auth($Url, $Token) {
    $Headers = @{"Authorization"=$Token}
    $Response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers
    return $Response
}

Write-Host "Waiting for services to start..."

# 1. Login
Write-Host "1. Getting Token..."
$Token = Get-Token
Write-Host "Token: $Token"

# 2. Check Inventory Before Order
Write-Host "`n2. Checking Inventory Before Order (Store 1, Product 1)..."
$InvBefore = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
$InvBefore | Format-Table

# 3. Create Order
Write-Host "`n3. Creating Order (Store 1, Product 1, Qty 2)..."
$OrderBody = @{
    storeId = 1
    items = @(
        @{
            productId = 1
            price = 3.00
            quantity = 2
        }
    )
}
try {
    $OrderRes = Post-Json-Auth "http://localhost:8000/order/create" $Token $OrderBody
    Write-Host "Result: $OrderRes"
} catch {
    Write-Host "Order Failed: $_"
}

# 4. Check Inventory After Order
Write-Host "`n4. Checking Inventory After Order (Store 1, Product 1)..."
$InvAfter = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
$InvAfter | Format-Table

# 5. Create Order with Insufficient Stock
Write-Host "`n5. Creating Order with Insufficient Stock (Store 1, Product 1, Qty 1000)..."
$OrderBodyFail = @{
    storeId = 1
    items = @(
        @{
            productId = 1
            price = 3.00
            quantity = 1000
        }
    )
}
try {
    $OrderResFail = Post-Json-Auth "http://localhost:8000/order/create" $Token $OrderBodyFail
    Write-Host "Result: $OrderResFail"
} catch {
    # Extracting error message from the exception if possible
    $ErrorMsg = $_.Exception.Message
    if ($_.Exception.Response) {
        $Stream = $_.Exception.Response.GetResponseStream()
        $Reader = New-Object System.IO.StreamReader($Stream)
        $ErrorBody = $Reader.ReadToEnd()
        $ErrorMsg = "$ErrorMsg - Body: $ErrorBody"
    }
    Write-Host "Expected Failure: $ErrorMsg"
}
