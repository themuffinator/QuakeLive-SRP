[CmdletBinding()]
param(
	[string]$Configuration = 'Debug',
	[string]$BasePath = '',
	[switch]$EnableAwesomium,
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

function Get-LaunchSafeArgument {
	param([string]$Path)

	if ([string]::IsNullOrWhiteSpace($Path)) {
		return ''
	}

	$command = 'for %I in ("' + $Path + '") do @echo %~sI'
	$shortPath = (& cmd /c $command 2>$null | Select-Object -First 1).Trim()
	if (-not [string]::IsNullOrWhiteSpace($shortPath) -and $shortPath -notmatch '\s') {
		return $shortPath
	}

	return $Path
}

function Format-LaunchArgument {
	param([string]$Argument)

	if ($null -eq $Argument) {
		return '""'
	}

	if ($Argument -notmatch '[\s"]') {
		return $Argument
	}

	$escaped = $Argument -replace '(\\*)"', '$1$1\"'
	$escaped = $escaped -replace '(\\+)$', '$1$1'
	return '"' + $escaped + '"'
}

$steamBasePath = $BasePath
if (-not $steamBasePath) {
	$steamBasePath = $env:QLR_STEAM_BASEPATH
}
if (-not $steamBasePath) {
	$steamBasePath = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live'
}
$steamBasePath = [System.IO.Path]::GetFullPath($steamBasePath)
$retailPakPath = Join-Path $steamBasePath 'baseq3\pak00.pk3'
$assetCdPath = Join-Path $repoRoot 'assets\quakelive'

if (-not (Test-Path $steamBasePath -PathType Container)) {
	throw "Quake Live base path was not found: $steamBasePath. Update .vscode\\launch.json or set QLR_STEAM_BASEPATH."
}

if (-not (Test-Path $retailPakPath -PathType Leaf)) {
	throw "Quake Live base path is missing retail data: $retailPakPath. Point the launcher at the Steam install root that contains baseq3\\pak00.pk3."
}

$workingDirectory = $steamBasePath
$steamBasePathArg = Get-LaunchSafeArgument -Path $steamBasePath
$runtimeBinDirArg = Get-LaunchSafeArgument -Path $runtimeBinDir
$assetCdPathArg = Get-LaunchSafeArgument -Path $assetCdPath

$arguments = @(
	'+set', 'developer', '1',
	'+set', 'logfile', '2',
	'+set', 'g_logfile', '1',
	'+set', 'com_noErrorInterrupt', '1',
	'+set', 'fs_basepath', $steamBasePathArg,
	'+set', 'fs_homepath', $runtimeBinDirArg,
	'+set', 'fs_cdpath', $assetCdPathArg,
	'+set', 'r_fullscreen', '0',
	'+set', 'r_ext_multitexture', '0'
)

if ($EnableAwesomium) {
	$arguments += @(
		'+set', 'ui_browserAwesomium', '1'
	)
} else {
	$arguments += @(
		'+set', 'ui_browserAwesomium', '0',
		'+set', 'web_browserActive', '0'
	)
}

if ($ExtraArgs.Count -gt 0) {
	$arguments += $ExtraArgs
}

$env:QLR_DUMP_PATH = Join-Path $repoRoot "build\win32\$Configuration\dumps"
$env:QL_DISABLE_STEAMWORKS = '1'
if ($EnableAwesomium) {
	Remove-Item Env:QL_DISABLE_EXTERNAL_ECOSYSTEMS -ErrorAction SilentlyContinue
	Remove-Item Env:QL_DISABLE_AWESOMIUM -ErrorAction SilentlyContinue
} else {
	$env:QL_DISABLE_EXTERNAL_ECOSYSTEMS = '1'
	$env:QL_DISABLE_AWESOMIUM = '1'
}

Write-Host "Launching: $program"
Write-Host "Working directory: $workingDirectory"
Write-Host "Awesomium enabled: $EnableAwesomium"
$commandLine = ($arguments | ForEach-Object { Format-LaunchArgument $_ }) -join ' '
Write-Host "Arguments: $commandLine"

Push-Location $workingDirectory
try {
	$process = Start-Process -FilePath $program -WorkingDirectory $workingDirectory -ArgumentList $commandLine -PassThru
	Write-Host "quakelive_steam.exe PID: $($process.Id)"
	Wait-Process -Id $process.Id
	$process.Refresh()
	exit $process.ExitCode
} finally {
	Pop-Location
}
