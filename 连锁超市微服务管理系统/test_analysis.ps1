param(
    [string]$Token
)

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

# 1. Store Rank
Write-Host "`n1. Testing Store Sales Rank..."
$StoreRank = Get-Json-Auth "http://localhost:8000/analysis/storeRank" $Token
if ($StoreRank -is [System.Array] -or $StoreRank -is [System.Collections.ArrayList]) {
    $StoreRank | Format-Table
} else {
    Write-Host "Store Rank: $StoreRank"
}

# 2. Product Rank
Write-Host "`n2. Testing Product Sales Rank..."
$ProductRank = Get-Json-Auth "http://localhost:8000/analysis/productRank" $Token
if ($ProductRank -is [System.Array] -or $ProductRank -is [System.Collections.ArrayList]) {
    $ProductRank | Format-Table
} else {
    Write-Host "Product Rank: $ProductRank"
}

# 3. Replenish Suggestion
Write-Host "`n3. Testing Replenish Suggestion..."
$Replenish = Get-Json-Auth "http://localhost:8000/analysis/replenish" $Token
if ($Replenish -is [System.Array] -or $Replenish -is [System.Collections.ArrayList]) {
    $Replenish | Format-Table
} else {
    Write-Host "Replenish: $Replenish"
}
