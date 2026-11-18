<#
.SYNOPSIS
  Saves a handoff report as tv2/ban-giao/DD-MM-YYYY_HH-mm.md using the real UTC+7 time.
  Replaces {{NOW}} in the draft and never overwrites an existing report.
#>
param([Parameter(Mandatory)] [string]$Draft)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$now = [DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7))
$stem = $now.ToString('dd-MM-yyyy_HH-mm')
$target = Join-Path $root "tv2/ban-giao/$stem.md"
$index = 2
while (Test-Path -LiteralPath $target) {
    $target = Join-Path $root ("tv2/ban-giao/{0}_{1:00}.md" -f $stem, $index)
    $index++
}
$text = (Get-Content -LiteralPath $Draft -Raw -Encoding UTF8).Replace('{{NOW}}', $now.ToString("yyyy-MM-ddTHH:mm:sszzz"))
[IO.File]::WriteAllText($target, $text, [Text.UTF8Encoding]::new($false))
Write-Output ([IO.Path]::GetRelativePath($root, $target).Replace('\', '/'))
