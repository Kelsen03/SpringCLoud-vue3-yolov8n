param(
    [string]$Token
)

function Post-Json-Auth($Url, $Token, $Body) {
    $Headers = @{"Content-Type"="application/json"; "Authorization"=$Token}
    try {
        $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 5)
        return $Response
    } catch {
        return $_.Exception.Response
    }
}

function Get-Json-Auth($Url, $Token) {
    $Headers = @{"Authorization"=$Token}
    $Response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers
    return $Response
}

Write-Host "Using Token: $Token"

# 2. Check Inventory Before Order
Write-Host "`n2. Checking Inventory Before Order (Store 1, Product 1)..."
$InvBefore = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
$InvBefore | Format-Table

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

$OrderResFail = Post-Json-Auth "http://localhost:8000/order/create" $Token $OrderBodyFail

if ($OrderResFail -is [System.Net.HttpWebResponse]) {
    Write-Host "Expected Failure Status: $($OrderResFail.StatusCode)"
    $Stream = $OrderResFail.GetResponseStream()
    $Reader = New-Object System.IO.StreamReader($Stream)
    $ErrorBody = $Reader.ReadToEnd()
    Write-Host "Error Body: $ErrorBody"
} else {
    Write-Host "Unexpected Success: $OrderResFail"
}

# 4. Check Inventory After Order (Should be same)
Write-Host "`n4. Checking Inventory After Order (Store 1, Product 1)..."
$InvAfter = Get-Json-Auth "http://localhost:8000/inventory/list?storeId=1" $Token
$InvAfter | Format-Table
