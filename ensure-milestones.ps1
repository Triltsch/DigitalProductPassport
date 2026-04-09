$ErrorActionPreference='Stop'

function Get-StatusCode {
  param([string]$Text)
  if ($Text -match 'HTTP\s+(\d{3})') { return $matches[1] }
  return ''
}

$repo = 'Triltsch/DigitalProductPassport'
$endpoint = "repos/$repo/milestones"
$desired = @(
  @{ title='M1: Foundation'; description='Running dev environment, CI/CD' },
  @{ title='M2: AAS Core'; description='AAS CRUD with auth' },
  @{ title='M3: Full Submodels'; description='TechnicalData + Sustainability submodels' },
  @{ title='M4: Access Control'; description='RBAC + access grants enforced' },
  @{ title='M5: Certification'; description='End-to-end certification workflow' },
  @{ title='M6: MVP'; description='Complete, tested, deployable MVP' },
  @{ title='M7: Phase 2'; description='Supplier workflow, notifications, webhooks' },
  @{ title='M8: Compliance'; description='EU Battery Regulation export' }
)

# 1) list existing milestones (all states)
$listCmd = "gh api `"${endpoint}?state=all`" --paginate"
$listOut = & gh api "${endpoint}?state=all" --paginate 2>&1
if ($LASTEXITCODE -ne 0) {
  $t = $listOut | Out-String
  "API_ERROR|$listCmd|$(Get-StatusCode $t)|$t"
  exit 1
}
$existing = $listOut | Out-String | ConvertFrom-Json
if ($null -eq $existing) { $existing = @() }
$titles = @($existing | ForEach-Object { $_.title })

# 2) create missing only
foreach ($m in $desired) {
  if ($titles -contains $m.title) {
    "EXISTS|$($m.title)"
  } else {
    $createCmd = "gh api $endpoint -f title=`"$($m.title)`" -f description=`"$($m.description)`""
    $createOut = & gh api $endpoint -f "title=$($m.title)" -f "description=$($m.description)" 2>&1
    if ($LASTEXITCODE -ne 0) {
      $t = $createOut | Out-String
      "API_ERROR|$createCmd|$(Get-StatusCode $t)|$t"
      exit 1
    }
    "CREATED|$($m.title)"
    $titles += $m.title
  }
}

# 3) list again and compact table
$finalCmd = "gh api `"${endpoint}?state=all`" --paginate"
$finalOut = & gh api "${endpoint}?state=all" --paginate 2>&1
if ($LASTEXITCODE -ne 0) {
  $t = $finalOut | Out-String
  "API_ERROR|$finalCmd|$(Get-StatusCode $t)|$t"
  exit 1
}
$final = $finalOut | Out-String | ConvertFrom-Json
$final | Sort-Object number | Select-Object number,title,state,html_url | Format-Table -AutoSize
