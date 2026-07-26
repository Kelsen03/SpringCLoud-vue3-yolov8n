param(
    [string]$Token
)

function Post-Form-Auth($Url, $Token, $Body) {
    $Headers = @{"Authorization"=$Token}
    try {
        $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body $Body
        return $Response
    } catch {
        return $_.Exception.Response
    }
}

function Get-Json-Auth($Url, $Token) {
    $Headers = @{"Authorization"=$Token}
    try {
        $Response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers
        return $Response
    } catch {
        return $_.Exception.Response
    }
}

Write-Host "Using Token: $Token"

# 1. Deduct Stock to Trigger Replenish (Stock 33 -> 1)
# Sales for Product 1 is 2. So we need Stock < 2.
Write-Host "`n1. Deducting Stock (32)..."
$DeductBody = @{
    productId = 1
    storeId = 1
    count = 32
}
$Res = Post-Form-Auth "http://localhost:8000/inventory/deduct" $Token $DeductBody
Write-Host "Deduct Result: $Res"

# 2. Check Replenish Suggestion
Write-Host "`n2. Checking Replenish Suggestion..."
$Replenish = Get-Json-Auth "http://localhost:8000/analysis/replenish" $Token
if ($Replenish -is [System.Array] -or $Replenish -is [System.Collections.ArrayList]) {
    $Replenish | Format-Table
} else {
    Write-Host "Replenish: $Replenish"
}
