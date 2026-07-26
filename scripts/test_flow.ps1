$ErrorActionPreference = "Stop"

function Post-Json($Url, $Body, $Token) {
    $Headers = @{"Content-Type"="application/json"}
    if ($Token) { $Headers["Authorization"] = $Token }
    
    if ($Body) {
        $JsonBody = $Body | ConvertTo-Json -Depth 10 -Compress
        $Response = Invoke-RestMethod -Uri $Url -Method Post -Body $JsonBody -Headers $Headers
    } else {
        $Response = Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers
    }
    return $Response
}

function Put-Json($Url, $Body, $Token) {
    $Headers = @{"Content-Type"="application/json"}
    if ($Token) { $Headers["Authorization"] = $Token }
    try {
        $JsonBody = $Body | ConvertTo-Json -Depth 10 -Compress
        $Response = Invoke-RestMethod -Uri $Url -Method Put -Body $JsonBody -Headers $Headers
        return $Response
    } catch {
        # Return the response stream if available, else status code
        $Stream = $_.Exception.Response.GetResponseStream()
        if ($Stream) {
            $Reader = New-Object System.IO.StreamReader($Stream)
            return $Reader.ReadToEnd()
        }
        return $_.Exception.Message
    }
}

function Get-Json($Url, $Token) {
    $Headers = @{}
    if ($Token) { $Headers["Authorization"] = $Token }
    $Response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers
    return $Response
}

Write-Host "1. HQ Login..."
try {
    $HqLogin = Post-Json "http://localhost:8000/auth/login?username=admin&password=123456" $null $null
    $HqToken = $HqLogin.token
    Write-Host "HQ Token: $HqToken"
} catch {
    Write-Error "HQ Login Failed: $_"
    exit
}

Write-Host "`n2. Store Login..."
try {
    $StoreLogin = Post-Json "http://localhost:8000/auth/login?username=store01&password=123456" $null $null
    $StoreToken = $StoreLogin.token
    Write-Host "Store Token: $StoreToken"
} catch {
    Write-Error "Store Login Failed: $_"
    exit
}

Write-Host "`n3. HQ Add Product (Global)..."
$Product1 = @{name="HQ Cola"; price=3.0; promo_price=2.5}
$Res1 = Post-Json "http://localhost:8000/product/add" $Product1 $HqToken
Write-Host "Result: $Res1"

Write-Host "`n4. HQ Update Product (Global)..."
# Assuming ID 2 because data.sql inserted ID 1 already? 
# Wait, data.sql in Product Service? I created one.
# INSERT INTO product VALUES (1,'可乐',3.00,2.50,0,NULL);
# So ID 1 exists.
# HQ Add Product will likely be ID 2.
# Let's update ID 1.
$Product1Update = @{id=1; name="Cola Updated"; price=3.5; promo_price=3.0}
$Res2 = Put-Json "http://localhost:8000/product/update" $Product1Update $HqToken
Write-Host "Result: $Res2"

Write-Host "`n5. Store Add Product (Local)..."
$Product2 = @{name="Store Bread"; price=5.0; promo_price=4.5}
$Res3 = Post-Json "http://localhost:8000/product/add" $Product2 $StoreToken
Write-Host "Result: $Res3"

Write-Host "`n6. Store List Products..."
$List = Get-Json "http://localhost:8000/product/list" $StoreToken
$List | Format-Table

Write-Host "`n7. Store Update HQ Product (Should Fail)..."
$Product1TryUpdate = @{id=1; name="Hacked Price"; price=0.01}
$Res4 = Put-Json "http://localhost:8000/product/update" $Product1TryUpdate $StoreToken
Write-Host "Result: $Res4"
