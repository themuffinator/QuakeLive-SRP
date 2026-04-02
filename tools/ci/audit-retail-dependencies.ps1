[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
	[string]$SteamInstallRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live',
	[switch]$Strict
)

$ErrorActionPreference = 'Stop'

function Get-RetailFileRecord {
	param(
		[string]$Root,
		[string]$RelativePath
	)

	$path = Join-Path $Root $RelativePath
	if (-not (Test-Path $path)) {
		throw "Retail dependency was not found: $path"
	}

	$item = Get-Item $path
	[pscustomobject]@{
		RelativePath = $RelativePath
		FullPath = $item.FullName
		Length = $item.Length
		FileVersion = $item.VersionInfo.FileVersion
		ProductVersion = $item.VersionInfo.ProductVersion
		ProductName = $item.VersionInfo.ProductName
		CompanyName = $item.VersionInfo.CompanyName
		Sha256 = (Get-FileHash $item.FullName -Algorithm SHA256).Hash
	}
}

function Get-NormalizedSteamDllRecord {
	param(
		[string]$InstallRoot,
		[System.IO.FileInfo]$File
	)

	$normalized = if ($File.FullName -match '\\[0-9]{17}\\baseq3\\') {
		Join-Path 'baseq3' $File.Name
	}
	else {
		$File.FullName.Substring($InstallRoot.Length).TrimStart('\')
	}

	[pscustomobject]@{
		NormalizedPath = $normalized
		FullPath = $File.FullName
		Sha256 = (Get-FileHash $File.FullName -Algorithm SHA256).Hash
	}
}

$assetRoot = Join-Path $RepoRoot 'assets/quakelive'
if (-not (Test-Path $assetRoot)) {
	throw "Retail asset root was not found: $assetRoot"
}

$retailFiles = @(
	'quakelive_steam.exe',
	'awesomium_process.exe',
	'awesomium.dll',
	'steam_api.dll',
	'avcodec-53.dll',
	'avformat-53.dll',
	'avutil-51.dll',
	'libEGL.dll',
	'libGLESv2.dll',
	'icudt.dll',
	'xinput9_1_0.dll',
	'baseq3\cgamex86.dll',
	'baseq3\qagamex86.dll',
	'baseq3\uix86.dll'
)

$assetRecords = $retailFiles | ForEach-Object {
	Get-RetailFileRecord -Root $assetRoot -RelativePath $_
}

Write-Host 'Retail asset manifest:'
$assetRecords |
	Select-Object RelativePath, Length, FileVersion, ProductVersion, ProductName, CompanyName |
	Format-Table -AutoSize

if (-not (Test-Path $SteamInstallRoot)) {
	$message = "Steam install root was not found: $SteamInstallRoot"
	if ($Strict) {
		throw $message
	}

	Write-Warning $message
	return
}

$steamDlls = Get-ChildItem -Path $SteamInstallRoot -Recurse -File -Filter *.dll
$steamRecords = $steamDlls | ForEach-Object {
	Get-NormalizedSteamDllRecord -InstallRoot $SteamInstallRoot -File $_
}

$comparisons = foreach ($record in $steamRecords) {
	$assetMatch = $assetRecords | Where-Object { $_.RelativePath -eq $record.NormalizedPath } | Select-Object -First 1
	[pscustomobject]@{
		NormalizedPath = $record.NormalizedPath
		SteamPath = $record.FullPath
		AssetFound = $null -ne $assetMatch
		HashMatch = ($null -ne $assetMatch -and $assetMatch.Sha256 -eq $record.Sha256)
	}
}

$missing = $comparisons | Where-Object { -not $_.AssetFound }
$mismatches = $comparisons | Where-Object { $_.AssetFound -and -not $_.HashMatch }

Write-Host ''
Write-Host "Steam install DLL summary: $($steamDlls.Count) files"
Write-Host "Matched retail asset payload: $(( $comparisons | Where-Object { $_.HashMatch } ).Count)"

if ($missing.Count -gt 0) {
	Write-Host ''
	Write-Host 'DLLs present in the Steam install but missing from assets/quakelive:'
	$missing | Select-Object NormalizedPath, SteamPath | Format-Table -AutoSize
}

if ($mismatches.Count -gt 0) {
	Write-Host ''
	Write-Host 'DLLs whose hashes differ from the committed retail assets:'
	$mismatches | Select-Object NormalizedPath, SteamPath | Format-Table -AutoSize
}

if ($Strict -and ($missing.Count -gt 0 -or $mismatches.Count -gt 0)) {
	throw 'Retail dependency audit failed.'
}

if ($missing.Count -eq 0 -and $mismatches.Count -eq 0) {
	Write-Host 'Steam install matches the committed retail dependency payload.'
}
