<#
.SYNOPSIS
  Imports the binaries of one TV2 build into a Ghidra project (headless), runs
  auto-analysis, and exports Ghidra's imports, strings, calls and decompilation.
.EXAMPLE
  pwsh -NoProfile -File scripts/tv2-ghidra.ps1 -BuildId 20261118-094956 -Samples 'B1,B2,P1'
#>
param(
    [Parameter(Mandatory)] [string]$BuildId,
    [Parameter(Mandatory)] [string[]]$Samples,
    [string]$GhidraHome,
    [string]$JavaHome
)
$ErrorActionPreference = 'Stop'
# pwsh -File passes a comma list as one string.
$Samples = @($Samples | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
$root = Split-Path $PSScriptRoot -Parent
if (-not $GhidraHome) { $GhidraHome = Join-Path $root 'artifacts/tools/ghidra_12.2_PUBLIC' }
# Ghidra 12.2 needs JDK 25+. The portable JDK stays inside the ignored artifacts folder.
if (-not $JavaHome) { $JavaHome = (Get-ChildItem (Join-Path $root 'artifacts/tools') -Directory -Filter 'jdk-25*' | Select-Object -First 1).FullName }
$headless = Join-Path $GhidraHome 'support/analyzeHeadless.bat'
if (-not (Test-Path $headless)) { throw "analyzeHeadless not found: $headless" }
if (-not (Test-Path (Join-Path $JavaHome 'bin/javac.exe'))) { throw "JDK not found: $JavaHome" }
$env:JAVA_HOME = $JavaHome
$env:PATH = (Join-Path $JavaHome 'bin') + ';' + $env:PATH

$manifest = Get-Content -Raw (Join-Path $root "evidence/TV2-shared/build/$BuildId/build-manifest.json") | ConvertFrom-Json
$work = Join-Path $root "artifacts/ghidra/$BuildId"
$projects = Join-Path $work 'projects'
$export = Join-Path $work 'export'
$logs = Join-Path $work 'logs'
New-Item -ItemType Directory -Force $projects, $export, $logs | Out-Null
$project = 'TV2'
$existing = @()
$listing = Join-Path $work 'imported.txt'
if (Test-Path $listing) { $existing = @(Get-Content $listing) }

foreach ($key in $Samples) {
    $row = $manifest.samples | Where-Object build_key -eq $key
    if (-not $row) { throw "Sample is not in the build manifest: $key" }
    $binary = Join-Path $root $row.binary
    if ((Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash -ne $row.sha256) { throw "SHA-256 mismatch: $key" }
    $name = Split-Path $binary -Leaf
    $mode = if ($existing -contains $key) { @('-process', $name, '-noanalysis') } else { @('-import', $binary, '-overwrite') }
    $arguments = @($projects, $project) + $mode + @(
        '-scriptPath', (Join-Path $root 'scripts/ghidra'),
        '-postScript', 'Tv2Export.java', $export,
        '-log', (Join-Path $logs "$key.application.log"),
        '-scriptlog', (Join-Path $logs "$key.script.log"))
    & $headless @arguments *> (Join-Path $logs "$key.console.log")
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "Ghidra failed for $key (exit $code); read $logs/$key.console.log" }
    if (-not (Test-Path (Join-Path $export "$($name -replace '\.exe$', '')/summary.json"))) {
        throw "Ghidra produced no export for $key; read $logs/$key.script.log"
    }
    if ($existing -notcontains $key) { Add-Content -LiteralPath $listing -Value $key; $existing += $key }
    Write-Host "ghidra ok: $key"
}
Write-Host "PROJECT: $projects/$project.gpr"
Write-Host "EXPORT:  $export"
