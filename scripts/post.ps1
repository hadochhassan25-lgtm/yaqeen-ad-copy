# Create a post on Moltbook
# Usage: .\scripts\post.ps1 -Title "..." -Content "..." [-Submolt "general"]

param(
    [string]$Title,
    [string]$Content,
    [string]$Submolt = "general"
)

. "$PSScriptRoot\credentials.ps1"

if (-not $Title) {
    Write-Host "Usage: .\post.ps1 -Title "Your title" -Content "Your content" [-Submolt "general"]"
    exit
}

$body = @{
    submolt_name = $Submolt
    title = $Title
    content = $Content
}

$result = Invoke-Moltbook -Method POST -Endpoint "posts" -Body $body

if ($result -and $result.success) {
    Write-Host "[SUCCESS] Post created!"
    Write-Host "Post ID: $($result.post.id)"

    # Check if verification is required
    if ($result.post.verification -and $result.post.verification.verification_status -eq "pending") {
        Write-Host "[WARN] Verification required! Solve the challenge and POST /api/v1/verify"
        Write-Host "Challenge: $($result.post.verification.challenge_text)"
    } else {
        Write-Host "Published: https://www.moltbook.com/p/$($result.post.id)"
    }
} else {
    Write-Host "[ERROR] Failed to create post."
}
