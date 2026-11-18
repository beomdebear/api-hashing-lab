<#
.SYNOPSIS
  Opens the real Ghidra window and captures the TV2 evidence images.
  Run it yourself from the project root. See tv2/HUONG-DAN-CHUP-ANH.md.
.EXAMPLE
  pwsh -NoProfile -File scripts/tv2-capture-gui.ps1
  pwsh -NoProfile -File scripts/tv2-capture-gui.ps1 -Only P1
#>
param([string]$Only = '')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root 'artifacts/tools/venv/Scripts/python.exe'
$arguments = @((Join-Path $root 'scripts/ghidra/tv2_gui_capture.py'))
if ($Only) { $arguments += @('--only', $Only) }
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "Capture failed with exit code $LASTEXITCODE. Copy the console text above into the next session." }
Write-Host 'Capture finished. The list of images is in artifacts/ghidra/20261118-094956/gui-capture-result.json'
