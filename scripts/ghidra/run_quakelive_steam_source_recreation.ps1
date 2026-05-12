param(
	[string]$GhidraHome = "C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC",
	[string]$BinaryPath = "C:\Program Files (x86)\Steam\steamapps\common\Quake Live\quakelive_steam.exe",
	[string]$OutputRoot = ".\src2\ghidra\quakelive_steam"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$pyghidraDist = Join-Path $GhidraHome "Ghidra\Features\PyGhidra\pypkg\dist"
if (-not (Test-Path $pyghidraDist)) {
	throw "Ghidra PyGhidra distribution directory not found: $pyghidraDist"
}

if ([System.IO.Path]::IsPathRooted($BinaryPath)) {
	$binaryAbs = $BinaryPath
}
else {
	$binaryAbs = Join-Path $repoRoot $BinaryPath
}

if (-not (Test-Path $binaryAbs)) {
	throw "Required binary not found: $binaryAbs"
}

if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
	$outputAbs = $OutputRoot
}
else {
	$outputAbs = Join-Path $repoRoot $OutputRoot
}

$buildRoot = Join-Path $repoRoot "build\re"
$projectRoot = Join-Path $buildRoot "ghidra-quakelive-steam-source-recreation-project"
$scriptPath = Join-Path $repoRoot "ghidra_scripts"
$aliasPath = Join-Path $repoRoot "references\analysis\quakelive_symbol_aliases.json"
$analysisPath = Join-Path $repoRoot "references\reverse-engineering\ghidra\quakelive_steam\analysis_symbols.txt"
$postprocessScript = Join-Path $repoRoot "scripts\ghidra\postprocess_quakelive_steam_src2.py"
$pyghidraVenv = Join-Path $buildRoot "pyghidra-venv"
$venvPython = Join-Path $pyghidraVenv "Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $outputAbs | Out-Null
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null

if (-not (Test-Path $venvPython)) {
	py -3.11 -m venv $pyghidraVenv
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to create PyGhidra virtual environment"
	}

	& $venvPython -m pip install --no-index -f $pyghidraDist pyghidra
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to install PyGhidra into $pyghidraVenv"
	}
}

& $venvPython -m pyghidra.ghidra_launch --install-dir $GhidraHome ghidra.app.util.headless.AnalyzeHeadless `
	$projectRoot `
	"QuakeLiveSteamRecreation" `
	-import $binaryAbs `
	-overwrite `
	-scriptPath $scriptPath `
	-postScript "ApplyQuakeLiveSteamMappings.py" $aliasPath $analysisPath

if ($LASTEXITCODE -ne 0) {
	throw "ApplyQuakeLiveSteamMappings.py failed"
}

& $venvPython -m pyghidra.ghidra_launch --install-dir $GhidraHome ghidra.app.util.headless.AnalyzeHeadless `
	$projectRoot `
	"QuakeLiveSteamRecreation" `
	-process "quakelive_steam.exe" `
	-scriptPath $scriptPath `
	-postScript "ExportQuakeLiveSteamSourceRecreation.py" $outputAbs `
	-deleteProject

if ($LASTEXITCODE -ne 0) {
	throw "ExportQuakeLiveSteamSourceRecreation.py failed"
}

py -3.11 $postprocessScript --repo-root $repoRoot --output-root $outputAbs
if ($LASTEXITCODE -ne 0) {
	throw "postprocess_quakelive_steam_src2.py failed"
}
