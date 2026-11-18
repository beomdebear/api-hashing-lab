<#
.SYNOPSIS
  Runs the locked detectors on the chosen splits, evaluates them, and copies the
  raw features, predictions and result tables into evidence/.
.EXAMPLE
  pwsh -NoProfile -File scripts/tv2-evaluate-all.ps1 -Splits 'dev,test,probe'
#>
param(
    [string[]]$Splits = @('dev', 'test', 'probe'),
    [string]$Lock = 'configs/tv2/locks/rule-lock-1.0.1.json'
)
$ErrorActionPreference = 'Stop'
$Splits = @($Splits | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$python = Join-Path $root 'artifacts/tools/venv/Scripts/python.exe'
$targets = @{ dev = 'evidence/G2/TV2/G2-TV2-01/runs'; test = 'evidence/G3/TV2/G3-TV2-01/runs'; probe = 'evidence/G3/TV2/G3-TV2-01/runs' }
& $python detectors/tv2/tv2freeze.py verify $Lock
if ($LASTEXITCODE -ne 0) { throw 'The rule lock does not match the current files.' }
foreach ($split in $Splits) {
    $run = (& $python detectors/tv2/tv2run.py --split $split --lock $Lock | Select-Object -Last 1)
    if ($LASTEXITCODE -ne 0) { throw "Run failed for split $split" }
    & $python detectors/tv2/tv2evaluate.py $run | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Evaluation failed for split $split" }
    $target = Join-Path $targets[$split] (Split-Path $run -Leaf)
    New-Item -ItemType Directory -Force $target | Out-Null
    Copy-Item (Join-Path $run '*') $target -Recurse -Force
    Write-Host "$split -> $target"
}
