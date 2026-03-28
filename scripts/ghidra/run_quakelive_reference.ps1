param(
	[string]$GhidraHome = "C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC",
	[string]$QuakeLiveRoot = ".\assets\quakelive",
	[string]$OutputRoot = ".\references\reverse-engineering\ghidra",
	[int]$MaxDecompFunctions = 180
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$analyzeHeadless = Join-Path $GhidraHome "support\analyzeHeadless.bat"
if (-not (Test-Path $analyzeHeadless)) {
	throw "Ghidra analyzeHeadless not found: $analyzeHeadless"
}

if ([System.IO.Path]::IsPathRooted($QuakeLiveRoot)) {
	$quakeliveRootAbs = $QuakeLiveRoot
}
else {
	$quakeliveRootAbs = Join-Path $repoRoot $QuakeLiveRoot
}

$binaries = @(
	(Join-Path $quakeliveRootAbs "quakelive_steam.exe"),
	(Join-Path $quakeliveRootAbs "awesomium_process.exe"),
	(Join-Path $quakeliveRootAbs "baseq3\cgamex86.dll"),
	(Join-Path $quakeliveRootAbs "baseq3\qagamex86.dll"),
	(Join-Path $quakeliveRootAbs "baseq3\uix86.dll")
)

foreach ($bin in $binaries) {
	if (-not (Test-Path $bin)) {
		throw "Required binary not found: $bin"
	}
}

if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
	$outputAbs = $OutputRoot
}
else {
	$outputAbs = Join-Path $repoRoot $OutputRoot
}

$projectRoot = Join-Path $outputAbs "tmp-ghidra-project"
$scriptPath = Join-Path $repoRoot "scripts\ghidra"

New-Item -ItemType Directory -Force -Path $outputAbs | Out-Null
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null

$args = @(
	$projectRoot,
	"QuakeLiveReference",
	"-import", $binaries[0],
	"-import", $binaries[1],
	"-import", $binaries[2],
	"-import", $binaries[3],
	"-import", $binaries[4],
	"-overwrite",
	"-scriptPath", $scriptPath,
	"-postScript", "ExportQuakeLiveReference.java", $outputAbs, "$MaxDecompFunctions",
	"-deleteProject"
)

& $analyzeHeadless @args
