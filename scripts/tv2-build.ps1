<#
.SYNOPSIS
  Builds the TV1 samples (through scripts/tv1-build.ps1, unchanged), the TV2 proposed
  controls and the compiler-variant probes, then records provenance.
.NOTES
  Output binaries stay under artifacts/ (git-ignored). The manifest is copied to
  evidence/TV2-shared/build/<build_id>/ so results stay traceable.
  A new run creates NEW binaries with a NEW build_id; it never replaces an older one.
#>
param([string]$BuildId = (Get-Date -Format 'yyyyMMdd-HHmmss'))
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent

# --- Real x64 developer environment: vcvars64.bat sets every variable itself.
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vs) { throw 'No Visual Studio installation with the x64 C++ tools was found.' }
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'
foreach ($line in (& $env:ComSpec /d /c "`"$vcvars`" >nul 2>&1 && set")) {
    $i = $line.IndexOf('=')
    if ($i -gt 0) { Set-Item -Path ("Env:" + $line.Substring(0, $i)) -Value $line.Substring($i + 1) }
}
if ($env:VSCMD_ARG_TGT_ARCH -ne 'x64') { throw 'vcvars64.bat did not produce an x64 environment.' }
$cl = (Get-Command cl.exe).Source
$clVersion = (Get-Item $cl).VersionInfo.FileVersion
$gcc = 'C:\msys64\mingw64\bin\gcc.exe'

function Get-Sha([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
function Get-Rel([string]$Path) { [IO.Path]::GetRelativePath($root, $Path).Replace('\', '/') }
function Get-Inputs([string]$Source) {
    $files = @($Source) + @(Get-ChildItem (Join-Path $root 'samples/common'), (Join-Path $root 'samples/tv2_controls') -Filter *.h -File | ForEach-Object FullName)
    $map = [ordered]@{}
    foreach ($f in $files) { $map[(Get-Rel $f)] = Get-Sha $f }
    return $map
}

# --- TV1 samples: use the TV1 script as written.
$tv1Root = Join-Path $root 'artifacts/builds/tv1'
$before = @(if (Test-Path $tv1Root) { Get-ChildItem $tv1Root -Directory | ForEach-Object Name })
& (Join-Path $root 'scripts/tv1-build.ps1') -Sample All | Out-Null
$tv1Dir = Get-ChildItem $tv1Root -Directory | Where-Object { $before -notcontains $_.Name } | Sort-Object Name | Select-Object -Last 1
if (-not $tv1Dir) { throw 'tv1-build.ps1 did not create a build directory.' }

$rows = New-Object System.Collections.ArrayList
$tv1Sources = [ordered]@{
    B1='benign/B1_static_import'; B2='benign/B2_dynamic_name'; P1='api_hashing/P1_djb2'
    P2='api_hashing/P2_fnv1a'; P3='api_hashing/P3_crc32'; P4='api_hashing/P4_changed_seed'
    P5='api_hashing/P5_changed_order'; E1='error_cases/E1_wrong_hash'; E2='error_cases/E2_early_exit'
}
$tv1Flags = '/nologo /TC /W4 /Od /MD /utf-8 /link /INCREMENTAL:NO'
function Add-Row($Id, $Group, $Exe, $Log, $Source, $Compiler, $Flags, $SubBuild) {
    [void]$rows.Add([ordered]@{
        build_key = $Id; group = $Group; sha256 = (Get-Sha $Exe); size = (Get-Item $Exe).Length
        binary = (Get-Rel $Exe); build_log = (Get-Rel $Log); source = (Get-Rel $Source)
        compiler = $Compiler; flags = $Flags; sub_build_id = $SubBuild; inputs = (Get-Inputs $Source)
    })
}
foreach ($id in $tv1Sources.Keys) {
    $d = Join-Path $tv1Dir.FullName $id
    Add-Row $id 'tv1_sample' (Join-Path $d "$id.exe") (Join-Path $d 'build.log') `
        (Join-Path $root ("samples/" + $tv1Sources[$id] + '/main.c')) "MSVC cl.exe $clVersion" $tv1Flags $tv1Dir.Name
}

# --- TV2 controls and compiler probes.
$outRoot = Join-Path $root "artifacts/builds/tv2/$BuildId"
if (Test-Path $outRoot) { throw "Build directory already exists: $outRoot" }
New-Item -ItemType Directory -Path $outRoot -Force | Out-Null

function Invoke-Cl($Id, $Source, [string[]]$Flags) {
    $dest = Join-Path $outRoot $Id
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    $list = @('/nologo', '/TC', '/W4') + $Flags + @('/MD', '/utf-8', "/Fe$Id.exe", "/Fo$Id.obj", $Source, '/link', '/INCREMENTAL:NO')
    $quoted = ($list | ForEach-Object { '"' + $_ + '"' }) -join ' '
    Push-Location $dest
    try {
        & $env:ComSpec /d /c "cl.exe $quoted > build.log 2>&1"
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $Id; read $dest/build.log" }
    } finally { Pop-Location }
    return @{ exe = (Join-Path $dest "$Id.exe"); log = (Join-Path $dest 'build.log'); flags = ($list[0..($list.Count - 1)] -join ' ').Replace($Source, '<source>') }
}
function Invoke-Gcc($Id, $Source) {
    $dest = Join-Path $outRoot $Id
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    $saved = $env:PATH
    $env:PATH = 'C:\msys64\mingw64\bin;' + $env:PATH
    Push-Location $dest
    try {
        & $env:ComSpec /d /c "`"$gcc`" -O2 -Wall -o $Id.exe `"$Source`" > build.log 2>&1"
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $Id; read $dest/build.log" }
    } finally { Pop-Location; $env:PATH = $saved }
    return @{ exe = (Join-Path $dest "$Id.exe"); log = (Join-Path $dest 'build.log'); flags = 'gcc -O2 -Wall' }
}

$controls = [ordered]@{
    'TV2C-B3' = 'samples/tv2_controls/B3_name_table/main.c'
    'TV2C-B4' = 'samples/tv2_controls/B4_data_hash/main.c'
    'TV2C-B5' = 'samples/tv2_controls/B5_hash_and_named_resolve/main.c'
    'TV2C-B6' = 'samples/tv2_controls/B6_export_strcmp/main.c'
}
foreach ($id in $controls.Keys) {
    $src = Join-Path $root $controls[$id]
    $r = Invoke-Cl $id $src @('/Od')
    Add-Row $id 'tv2_control_proposed' $r.exe $r.log $src "MSVC cl.exe $clVersion" $r.flags $BuildId
}
$p1 = Join-Path $root 'samples/api_hashing/P1_djb2/main.c'
$p3 = Join-Path $root 'samples/api_hashing/P3_crc32/main.c'
$b6 = Join-Path $root $controls['TV2C-B6']
foreach ($v in @(@('VAR-P1-MSVC-O2', $p1), @('VAR-P3-MSVC-O2', $p3), @('VAR-B6-MSVC-O2', $b6))) {
    $r = Invoke-Cl $v[0] $v[1] @('/O2')
    Add-Row $v[0] 'compiler_probe' $r.exe $r.log $v[1] "MSVC cl.exe $clVersion" $r.flags $BuildId
}
$gccVersion = (& $gcc --version | Select-Object -First 1)
foreach ($v in @(@('VAR-P1-GCC-O2', $p1), @('VAR-B6-GCC-O2', $b6))) {
    $r = Invoke-Gcc $v[0] $v[1]
    Add-Row $v[0] 'compiler_probe' $r.exe $r.log $v[1] $gccVersion $r.flags $BuildId
}

# --- Provenance. HEAD alone does not identify a dirty tree, so inputs are hashed too.
Push-Location $root
try {
    $head = (git rev-parse HEAD).Trim()
    $branch = (git branch --show-current).Trim()
    $status = @(git status --porcelain=v1)
} finally { Pop-Location }
$manifest = [ordered]@{
    schema = 'tv2-build-manifest/1'; build_id = $BuildId
    created_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
    host = 'developer host (not a lab VM); binaries were built, not executed, by this script'
    git_branch = $branch; git_head = $head; source_tree_dirty = ($status.Count -gt 0)
    git_status_entries = $status.Count
    compiler_msvc = "cl.exe $clVersion"; compiler_gcc = $gccVersion; vcvars = $vcvars
    tv1_build_dir = (Get-Rel $tv1Dir.FullName); tv2_build_dir = (Get-Rel $outRoot)
    samples = $rows
}
$json = $manifest | ConvertTo-Json -Depth 6
$json | Set-Content -LiteralPath (Join-Path $outRoot 'build-manifest.json') -Encoding UTF8
$evidence = Join-Path $root "evidence/TV2-shared/build/$BuildId"
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$json | Set-Content -LiteralPath (Join-Path $evidence 'build-manifest.json') -Encoding UTF8
foreach ($row in $rows) {
    Copy-Item -LiteralPath (Join-Path $root $row.build_log) -Destination (Join-Path $evidence ($row.build_key + '.build.log'))
}
Write-Host "BUILD ID: $BuildId"
Write-Host "MANIFEST: evidence/TV2-shared/build/$BuildId/build-manifest.json"
$rows | ForEach-Object { '{0,-16} {1}  {2}' -f $_.build_key, $_.sha256.Substring(0, 16), $_.binary } | Write-Host
