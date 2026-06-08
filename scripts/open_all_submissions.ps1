# Open all submission URLs for Iliass
# Run this from PowerShell on your desktop

Write-Host "Opening Bugcrowd (OpenAI Safety Bounty)..." -ForegroundColor Cyan
Start-Process "https://bugcrowd.com/engagements/openai-safety"

Write-Host "Opening Huntr..." -ForegroundColor Cyan
Start-Process "https://huntr.com/bounties/submit"

Write-Host "Opening PR #16..." -ForegroundColor Cyan
Start-Process "https://github.com/aLexzzz430/Cognitive-OS/pull/16"

Write-Host "Opening LinkedIn..." -ForegroundColor Cyan
Start-Process "https://www.linkedin.com/feed/"

Write-Host ""
Write-Host "========== FILES TO SUBMIT ==========" -ForegroundColor Green
Write-Host "1. Bugcrowd OpenAI Safety: openai_safety_bounty_report.md"
Write-Host "2. Huntr MCP RCE: agentscope_mcp_rce_report.md"
Write-Host "3. Huntr MCP SSRF: agentscope_mcp_ssrf_report.md"
Write-Host "4. Huntr SSRF Defense: huntr_ssrf_defense_response.md"
Write-Host "5. PR #16: Just comment: 'Any update?'"
Write-Host "6. LinkedIn: ghostwriter_linkedin_post.md"
Write-Host ""
Write-Host "Total potential: `$4,100 - `$9,500" -ForegroundColor Yellow
Write-Host "Time needed: ~30 minutes" -ForegroundColor Yellow
