# Fetch and display Moltbook feed
# Usage: .\scripts\check-feed.ps1 [-Sort hot|new|top] [-Limit 25]

param(
    [string]$Sort = "hot",
    [int]$Limit = 15
)

. "$PSScriptRoot\credentials.ps1"

$feed = Invoke-Moltbook -Endpoint "feed?sort=$Sort&limit=$Limit"

if (-not $feed -or -not $feed.posts) {
    Write-Host "No posts found or error fetching feed."
    exit
}

Write-Host "`n=== FEED ($Sort) — $Limit posts ==="
$i = 1
foreach ($post in $feed.posts) {
    Write-Host "`n--- #$i ---"
    Write-Host "Title: $($post.title)"
    Write-Host "Author: $($post.author.name) | Submolt: $($post.submolt_name)"
    Write-Host "Votes: ↑$($post.upvotes) ↓$($post.downvotes) | Comments: $($post.comment_count)"
    Write-Host "ID: $($post.id)"
    $i++
}
Write-Host "`n========================="
