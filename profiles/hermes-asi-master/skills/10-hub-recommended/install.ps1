# install.ps1 — HERMES Hub Recommended — Install Top 5 Hub Skills
# Run: powershell -ExecutionPolicy Bypass -File skills/10-hub-recommended/install.ps1

Write-Host "=== HERMES Hub Recommended — Installing Top 5 Skills ===" -ForegroundColor Cyan
Write-Host "These augment your 9 Hermes Advanced skills with proven Hub implementations`n"

$skills = @(
  @{name="github-pr-workflow"; cmd="hermes skills install official/github/github-pr-workflow"; trust="builtin"},
  @{name="merge-reconciler"; cmd="hermes skills install official/ai-agents/merge-reconciler"; trust="builtin"},
  @{name="codebase-inspection"; cmd="hermes skills install official/devops/codebase-inspection"; trust="builtin"},
  @{name="git-worktree"; cmd="hermes skills install antjanus/skillbox --skill git-worktree"; trust="community - inspect first"},
  @{name="delegate-to-hermes"; cmd="npx skills add bassemZohdy/delegate-skills --skill delegate-to-hermes"; trust="community - inspect first"}
)

foreach($s in $skills){
  Write-Host "[$($s.trust)] $($s.name)" -ForegroundColor Yellow
  Write-Host "  $($s.cmd)" -ForegroundColor DarkGray
  Write-Host "  Run: $($s.cmd)" -ForegroundColor Green
  Write-Host ""
}

Write-Host "=== After installing, verify: ===" -ForegroundColor Cyan
Write-Host "hermes skills list | Select-String -Pattern 'github-pr-workflow|merge-reconciler|codebase-inspection|git-worktree|delegate-to-hermes'"
Write-Host ""
Write-Host "=== Security: Always inspect community skills first: ===" -ForegroundColor Yellow
Write-Host "hermes skills inspect antjanus/skillbox --skill git-worktree"
Write-Host "npx skills add bassemZohdy/delegate-skills --skill delegate-to-hermes --dry-run  # if available"
