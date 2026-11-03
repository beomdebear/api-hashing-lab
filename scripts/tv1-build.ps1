param(
    [ValidateSet('All','B1','B2','P1','P2','P3','P4','P5','E1','E2')]
    [string]$Sample = 'All',
    [switch]$Audit
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    throw 'Open x64 Native Tools Command Prompt for Visual Studio, then enter powershell -NoProfile.'
}
if ($env:VSCMD_ARG_TGT_ARCH -ne 'x64') {
    throw 'Use the x64 MSVC developer environment for this PE32+ lab.'
}
$paths = [ordered]@{
    B1='benign/B1_static_import'; B2='benign/B2_dynamic_name'
    P1='api_hashing/P1_djb2'; P2='api_hashing/P2_fnv1a'
    P3='api_hashing/P3_crc32'; P4='api_hashing/P4_changed_seed'
    P5='api_hashing/P5_changed_order'; E1='error_cases/E1_wrong_hash'
    E2='error_cases/E2_early_exit'
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$buildRoot = Join-Path $root "artifacts/builds/tv1/$stamp"
New-Item -ItemType Directory -Path $buildRoot -Force | Out-Null
$compilerPath = (Get-Command cl.exe).Source
$compilerVersion = (Get-Item $compilerPath).VersionInfo.FileVersion
$rows = @()

function Build-One([string]$Name, [string]$Source, [string[]]$Defines) {
    $dest = Join-Path $buildRoot $Name
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    # /MD avoids statically linking the entire CRT. /Od makes the first Ghidra pass easier.
    $argsList = @('/nologo','/TC','/W4','/Od','/MD','/utf-8',"/Fe$Name.exe","/Fo$Name.obj")
    $argsList += $Defines
    $argsList += @($Source, '/link', '/INCREMENTAL:NO')
    Push-Location $dest
    try {
        # cmd redirects native stderr without PowerShell 5.1 NativeCommandError handling.
        $quoted = ($argsList | ForEach-Object { '"' + $_ + '"' }) -join ' '
        $cmdLine = 'cl.exe ' + $quoted + ' > build.log 2>&1'
        & $env:ComSpec /d /c $cmdLine
        $code = $LASTEXITCODE
        Get-Content 'build.log' | Out-Host
        if ($code -ne 0) { throw "Build failed for $Name. Read $dest/build.log" }
    } finally { Pop-Location }
    $exe = Join-Path $dest "$Name.exe"
    return [pscustomobject]@{
        sample_id=$Name; sha256=(Get-FileHash $exe -Algorithm SHA256).Hash
        executable=$exe; compiler=$compilerVersion; compiler_path=$compilerPath
        architecture='x64'; build_flags='/Od /MD /W4 /TC; no PDB'; build_id=$stamp
    }
}

if ($Audit) {
    $src = Join-Path $root 'tests/resolver/tv1-audit.c'
    $rows += Build-One 'audit-djb2' $src @('/DTV1_ALGORITHM=1','/DTV1_SEED=5381u')
    $rows += Build-One 'audit-fnv1a' $src @('/DTV1_ALGORITHM=2','/DTV1_SEED=2166136261u')
    $rows += Build-One 'audit-crc32' $src @('/DTV1_ALGORITHM=3','/DTV1_SEED=4294967295u')
    $rows += Build-One 'audit-seed1337' $src @('/DTV1_ALGORITHM=1','/DTV1_SEED=1337u')
} else {
    $ids = if ($Sample -eq 'All') { @($paths.Keys) } else { @($Sample) }
    foreach ($id in $ids) {
        $src = Join-Path $root ("samples/" + $paths[$id] + '/main.c')
        $rows += Build-One $id $src @()
    }
}
$rows | Export-Csv (Join-Path $buildRoot 'build-manifest.csv') -NoTypeInformation -Encoding UTF8
Write-Host "BUILD DIRECTORY: $buildRoot"
Write-Host 'Keep this build folder: it identifies the exact binaries used in the experiment.'
