[CmdletBinding()]
param(
	[string]$Configuration = 'Debug',
	[string[]]$ExtraArgs = @()
)

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..'))
$runtimeBinDir = Join-Path $repoRoot "build\win32\$Configuration\bin"
$program = Join-Path $runtimeBinDir 'quakelive_steam.exe'

if (-not (Test-Path $program)) {
	throw "Launch target was not found: $program. Run the Build Debug task first."
}

$steamBasePath = $env:QLR_STEAM_BASEPATH
if (-not $steamBasePath) {
	$steamBasePath = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live'
}
$workingDirectory = if (Test-Path $steamBasePath) { $steamBasePath } else { $repoRoot }

$arguments = @(
	'+set', 'developer', '1',
	'+set', 'logfile', '2',
	'+set', 'g_logfile', '1',
	'+set', 'com_noErrorInterrupt', '1',
	'+set', 'fs_basepath', $steamBasePath,
	'+set', 'fs_homepath', $runtimeBinDir,
	'+set', 'fs_cdpath', (Join-Path $repoRoot 'assets\quakelive'),
	'+set', 'r_fullscreen', '0',
	'+set', 'r_ext_multitexture', '0',
	'+set', 'ui_browserAwesomium', '0',
	'+set', 'web_browserActive', '0'
)

if ($ExtraArgs.Count -gt 0) {
	$arguments += $ExtraArgs
}

$env:QLR_DUMP_PATH = Join-Path $repoRoot "build\win32\$Configuration\dumps"
$env:QL_DISABLE_EXTERNAL_ECOSYSTEMS = '1'
$env:QL_DISABLE_STEAMWORKS = '1'
$env:QL_DISABLE_AWESOMIUM = '1'

Write-Host "Launching: $program"
Write-Host "Working directory: $workingDirectory"
Write-Host "Arguments: $($arguments -join ' ')"

Push-Location $workingDirectory
try {
	$process = Start-Process -FilePath $program -WorkingDirectory $workingDirectory -ArgumentList $arguments -PassThru
	Write-Host "quakelive_steam.exe PID: $($process.Id)"
	Wait-Process -Id $process.Id
	$process.Refresh()
	exit $process.ExitCode
} finally {
	Pop-Location
}
