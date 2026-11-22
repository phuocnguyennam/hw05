<#
.SYNOPSIS
  Reset the SUT between scenarios and (optionally) run one JMeter scenario in CLI mode.

  Reset = stop the node process listening on :3000 and start "node server.js" again.
  backend/database.js DROPs and re-seeds every table on start-up, so this also:
    - clears the account lockout (login_attempts / locked_until) of admin@eshop.com
    - removes all products imported by the previous run (back to 5 seed products)

.EXAMPLE
  .\run_scenario.ps1 -Scenario Load -Date 20261121
  .\run_scenario.ps1 -Scenario Load -Date 20261121 -ExtraArgs "-Jduration=900" -Tag Soak
  .\run_scenario.ps1 -ResetOnly
#>
param(
  [ValidateSet("Load", "Stress", "Spike")] [string]$Scenario = "Load",
  [string]$Date = (Get-Date -Format "yyyyMMdd"),
  [string]$Tag = "",
  [string]$ExtraArgs = "",
  [switch]$ResetOnly,
  [string]$JMeterBin = "C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat"
)
$ErrorActionPreference = "Stop"
$hw = Split-Path -Parent $PSScriptRoot
$backend = Join-Path (Split-Path -Parent $hw) "backend"

function Reset-Backend {
  $conn = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
  if ($conn) {
    Write-Host "[reset] stopping PID $($conn.OwningProcess) on :3000"
    Stop-Process -Id $conn.OwningProcess -Force
    Start-Sleep -Seconds 2
  }
  Write-Host "[reset] starting node server.js (DB will be dropped and re-seeded)"
  Start-Process -FilePath "node" -ArgumentList "server.js" -WorkingDirectory $backend -WindowStyle Normal
  for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
      $r = Invoke-RestMethod -Method Post -Uri "http://localhost:3000/api/login" -ContentType "application/json" `
        -Body '{"email":"admin@eshop.com","password":"Admin123!"}'
      if ($r.token) { Write-Host "[reset] backend up, admin login OK (not locked)"; return }
    } catch { }
  }
  throw "Backend did not come up on :3000"
}

Reset-Backend
if ($ResetOnly) { return }

$name = "23120073_${Scenario}_${Date}"
$label = if ($Tag) { "${name}_${Tag}" } else { $name }
$plan = Join-Path $hw "test_plans\$name.jmx"
$jtl = Join-Path $hw "results\$label.jtl"
$log = Join-Path $hw "results\$label.log"
$report = Join-Path $hw "reports\$label"
New-Item -ItemType Directory -Force -Path (Join-Path $hw "results"), (Join-Path $hw "reports") | Out-Null
if (Test-Path $jtl) { throw "$jtl already exists - never overwrite raw logs, use -Tag" }

Write-Host "[run] $plan -> $jtl"
$cmd = "`"$JMeterBin`" -n -t `"$plan`" -l `"$jtl`" -j `"$log`" -e -o `"$report`" $ExtraArgs"
cmd /c $cmd
Write-Host "[done] HTML report: $report\index.html"
