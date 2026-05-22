$script:API_KEY = "moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1"
$script:BASE_URL = "https://www.moltbook.com/api/v1"

function Get-ApiKey { return $script:API_KEY }
function Get-BaseUrl { return $script:BASE_URL }

function Invoke-Moltbook {
    param(
        [string]$Method = "GET",
        [string]$Endpoint,
        [object]$Body = $null,
        [string]$ContentType = "application/json"
    )
    $url = "$BASE_URL/$Endpoint"
    $headers = @{
        "Authorization" = "Bearer $(Get-ApiKey)"
        "User-Agent" = "yaqeen_manadger/1.0 (ManadgerTech)"
    }
    $params = @{
        Uri = $url
        Method = $Method
        Headers = $headers
    }
    if ($Body -and $Method -ne "GET") {
        $params.Body = ($Body | ConvertTo-Json -Depth 10)
        $params.ContentType = $ContentType
    }
    try {
        $result = Invoke-RestMethod @params
        return $result
    } catch {
        Write-Error "[ERROR] $($_.Exception.Message)"
        return $null
    }
}
