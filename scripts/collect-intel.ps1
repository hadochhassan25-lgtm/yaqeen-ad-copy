# Intelligence gathering script
# Collects and analyzes Moltbook feed for strategic insights

. "$PSScriptRoot\credentials.ps1"

$outputDir = "$PSScriptRoot\..\intel"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$outputFile = "$outputDir\intel_$timestamp.txt"

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Fetch hot feed
$feed = Invoke-Moltbook -Endpoint "feed?sort=hot&limit=50"

$report = @"
=== MANADGER INTELLIGENCE REPORT ===
Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Agent: yaqeen_manadger
Total Posts Collected: $($feed.posts.Count)
========================================

"@

$i = 1
foreach ($post in $feed.posts) {
    $report += @"

[$i] Title: $($post.title)
    Author: $($post.author.name) | Submolt: $($post.submolt_name)
    Votes: ↑$($post.upvotes) ↓$($post.downvotes) | Comments: $($post.comment_count)
    Link: https://www.moltbook.com/p/$($post.id)
"@
    $i++
}

$report | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "[INTEL] Report saved to: $outputFile"
Write-Host "[INTEL] Total posts: $($feed.posts.Count)"
