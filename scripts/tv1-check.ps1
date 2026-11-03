param(
    [Parameter(Mandatory=$true)][string]$BuildDir,
    [ValidateSet('All','B1','B2','P1','P2','P3','P4','P5','E1','E2')]
    [string]$Sample = 'All',
    [ValidateRange(1,3)][int]$Repeat = 1
)
$ErrorActionPreference = 'Stop'
Write-Host 'TV1 checker v2 - direct .NET Process'
$root = Split-Path $PSScriptRoot -Parent
$build = (Resolve-Path $BuildDir).Path
$manifest = @(Import-Csv (Join-Path $build 'build-manifest.csv'))
$selected = @($manifest | Where-Object {
    $_.sample_id -match '^(B[12]|P[1-5]|E[12])$' -and ($Sample -eq 'All' -or $_.sample_id -eq $Sample)
})
if ($selected.Count -eq 0) { throw 'No matching sample in this build manifest.' }
$batch = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$batchDir = Join-Path $root "artifacts/runs/tv1/$batch"
New-Item -ItemType Directory -Path $batchDir -Force | Out-Null
$results = @()
foreach ($item in $selected) {
    $id = $item.sample_id
    $exe = Join-Path $build "$id/$id.exe"
    $actualHash = (Get-FileHash $exe -Algorithm SHA256).Hash
    if ($actualHash -ne $item.sha256) { throw "Binary changed after build: $id" }
    for ($r = 1; $r -le $Repeat; $r++) {
        $runId = "$batch-$id-$r"
        $runDir = Join-Path $batchDir $runId
        New-Item -ItemType Directory -Path $runDir | Out-Null
        $expectedExit = switch ($id) { 'E1' {10} 'E2' {20} default {0} }
        $expectedMarker = $expectedExit -eq 0
        $start = [DateTime]::UtcNow
        # Start and retain the Process instance directly; avoid Start-Process
        # returning an object without a usable exit code on some Windows versions.
        $info = New-Object System.Diagnostics.ProcessStartInfo
        $info.FileName = $exe
        $info.WorkingDirectory = $runDir
        $info.UseShellExecute = $false
        $info.CreateNoWindow = $true
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        $proc = New-Object System.Diagnostics.Process
        $proc.StartInfo = $info
        try {
            if (-not $proc.Start()) { throw "Could not start $exe" }
            $samplePid = $proc.Id
            # Drain BOTH streams concurrently so a full pipe cannot block exit.
            $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
            $stderrTask = $proc.StandardError.ReadToEndAsync()
            $timeout = -not $proc.WaitForExit(10000)
            if ($timeout) {
                try { $proc.Kill() }
                catch { if (-not $proc.HasExited) { throw } }
                if (-not $proc.WaitForExit(5000)) {
                    throw "Timed-out sample could not be stopped: $samplePid"
                }
            }
            if (-not $proc.HasExited) { throw 'Process has not exited.' }
            $exitCode = $proc.ExitCode
            if ($null -eq $exitCode) { throw 'Exit code was not captured; cannot grade this run.' }
            # Bound the stream wait as well; these lab samples create no children.
            $streams = [System.Threading.Tasks.Task[]]@($stdoutTask, $stderrTask)
            if (-not [System.Threading.Tasks.Task]::WaitAll($streams, 5000)) {
                throw 'Output streams did not close after process exit.'
            }
            $utf8 = New-Object System.Text.UTF8Encoding($false)
            [IO.File]::WriteAllText((Join-Path $runDir 'stdout.txt'), $stdoutTask.Result, $utf8)
            [IO.File]::WriteAllText((Join-Path $runDir 'stderr.txt'), $stderrTask.Result, $utf8)
        } catch {
            # Preserve runner failures rather than converting them into exit 0.
            $_.ToString() | Set-Content (Join-Path $runDir 'runner-error.txt') -Encoding UTF8
            throw
        } finally {
            $proc.Dispose()
        }
        $marker = Join-Path $runDir 'marker.txt'
        $exists = Test-Path $marker
        $contentOK = $false
        if ($exists) {
            $bytes = [IO.File]::ReadAllBytes($marker)
            $contentOK = [Convert]::ToBase64String($bytes) -eq `
                [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("D08 LAB MARKER`r`n"))
        }
        $pass = (-not $timeout) -and ($exitCode -eq $expectedExit) -and `
            ($exists -eq $expectedMarker) -and ((-not $expectedMarker) -or $contentOK)
        $record = [ordered]@{
            run_id=$runId; sample_id=$id; sha256=$actualHash; pid=$samplePid
            started_utc=$start.ToString('o'); finished_utc=[DateTime]::UtcNow.ToString('o')
            exit_code=$exitCode; expected_exit=$expectedExit; timeout=$timeout
            marker_exists=$exists; marker_content_ok=$contentOK; correctness_pass=$pass
            collector_status='not_collected'; build_id=$item.build_id
        }
        $record | ConvertTo-Json | Set-Content (Join-Path $runDir 'run-metadata.json') -Encoding UTF8
        $results += [pscustomobject]$record
        Write-Host "$id run $r : correctness_pass=$pass ; exit=$exitCode ; marker=$exists"
    }
}
$results | Export-Csv (Join-Path $batchDir 'correctness-summary.csv') -NoTypeInformation -Encoding UTF8
Write-Host "RUN DIRECTORY: $batchDir"
Write-Host 'This checks sample correctness only. No independent API trace was collected.'
if (@($results | Where-Object { -not $_.correctness_pass }).Count -gt 0) {
    throw 'Some sample checks failed. Preserve the logs and investigate before handoff.'
}
