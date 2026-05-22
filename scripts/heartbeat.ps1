# Heartbeat script for yaqeen_manadger on Moltbook
# Run periodically to check in and maintain presence

. "$PSScriptRoot\credentials.ps1"

$stateFile = "$PSScriptRoot\..\memory\heartbeat-state.json"

function Get-State {
    if (Test-Path $stateFile) {
        return Get-Content $stateFile | ConvertFrom-Json
    }
    return @{ lastCheck = $null }
}

function Save-State($state) {
    $state | ConvertTo-Json | Set-Content $stateFile
}

function Do-Heartbeat {
    Write-Host "`n=== yaqeen_manadger Heartbeat $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="

    # Step 1: Check home
    $home = Invoke-Moltbook -Endpoint "home"
    if ($home) {
        Write-Host "[HOME] Karma: $($home.your_account.karma) | Notifications: $($home.your_account.unread_notification_count)"
    }

    # Step 2: Check status
    $status = Invoke-Moltbook -Endpoint "agents/status"
    if ($status -and $status.status -eq "claimed") {
        Write-Host "[STATUS] Active and claimed ✅"
    }

    # Step 3: Fetch fresh feed (general)
    $feed = Invoke-Moltbook -Endpoint "feed?sort=hot&limit=10"
    if ($feed -and $feed.posts) {
        Write-Host "[FEED] Latest hot posts: $($feed.posts.Count) loaded"
    }

    # Save state
    $state = Get-State
    $state.lastCheck = (Get-Date).ToString("o")
    Save-State $state

    Write-Host "[DONE] Heartbeat complete."
}

Do-Heartbeat
