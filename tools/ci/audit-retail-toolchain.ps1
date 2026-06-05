[CmdletBinding()]
param(
	[string]$RepoRoot = '',
	[switch]$Strict
)

$ErrorActionPreference = 'Stop'

$ToolchainAuditScriptRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ToolchainAuditScriptRoot) -and $PSCommandPath) {
	$ToolchainAuditScriptRoot = Split-Path -Parent $PSCommandPath
}
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
	if ([string]::IsNullOrWhiteSpace($ToolchainAuditScriptRoot)) {
		throw 'Unable to determine repository root. Provide -RepoRoot explicitly.'
	}

	$RepoRoot = (Resolve-Path (Join-Path $ToolchainAuditScriptRoot '../..')).Path
}
else {
	$RepoRoot = (Resolve-Path $RepoRoot).Path
}

function Get-ProjectXml {
	param(
		[string]$ProjectRelativePath
	)

	$projectPath = Join-Path $RepoRoot $ProjectRelativePath
	if (-not (Test-Path $projectPath)) {
		throw "Project file not found: $ProjectRelativePath"
	}

	return [xml](Get-Content -LiteralPath $projectPath)
}

function Assert-ProjectAttribute {
	param(
		[xml]$ProjectXml,
		[string]$ProjectRelativePath,
		[string]$AttributeName,
		[string]$ExpectedValue
	)

	$actualValue = $ProjectXml.Project.GetAttribute($AttributeName)
	if ([string]::IsNullOrEmpty($actualValue)) {
		throw "Missing root attribute '$AttributeName' in $ProjectRelativePath"
	}

	if ($actualValue -ne $ExpectedValue) {
		throw "Attribute mismatch in ${ProjectRelativePath}: expected $AttributeName='$ExpectedValue', found '$actualValue'"
	}

	Write-Host "Verified $ProjectRelativePath $AttributeName='$ExpectedValue'"
}

function Assert-NodeValues {
	param(
		[xml]$ProjectXml,
		[string]$ProjectRelativePath,
		[string]$XPath,
		[string]$ExpectedValue,
		[switch]$AllowMissing
	)

	$ns = New-Object System.Xml.XmlNamespaceManager($ProjectXml.NameTable)
	$ns.AddNamespace('msb', 'http://schemas.microsoft.com/developer/msbuild/2003')
	$nodes = $ProjectXml.SelectNodes($XPath, $ns)

	if (($null -eq $nodes -or $nodes.Count -eq 0) -and -not $AllowMissing) {
		throw "Missing expected nodes in $ProjectRelativePath for XPath: $XPath"
	}

	foreach ($node in $nodes) {
		if ($node.InnerText -ne $ExpectedValue) {
			throw "Value mismatch in ${ProjectRelativePath} for ${XPath}: expected '$ExpectedValue', found '$($node.InnerText)'"
		}
	}

	if ($nodes.Count -gt 0) {
		Write-Host "Verified $ProjectRelativePath $XPath => '$ExpectedValue' ($($nodes.Count) node(s))"
	}
}

function Test-V100ToolsetInstalled {
	$roots = @(
		${env:ProgramFiles(x86)},
		$env:ProgramFiles
	) | Where-Object { $_ }

	$candidatePaths = @()
	foreach ($root in $roots) {
		$candidatePaths += Join-Path $root 'MSBuild\Microsoft.Cpp\v4.0\Platforms\Win32\PlatformToolsets\v100'
	}

	$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
	if (Test-Path $vswhere) {
		$installRoot = & $vswhere -latest -products * -property installationPath 2>$null
		if ($LASTEXITCODE -eq 0 -and $installRoot) {
			$vcRoot = Join-Path $installRoot 'MSBuild\Microsoft\VC'
			if (Test-Path $vcRoot) {
				$candidatePaths += Get-ChildItem -LiteralPath $vcRoot -Directory -ErrorAction SilentlyContinue |
					ForEach-Object { Join-Path $_.FullName 'Platforms\Win32\PlatformToolsets\v100' }
			}
		}
	}

	foreach ($candidate in $candidatePaths | Select-Object -Unique) {
		if (Test-Path $candidate) {
			return $candidate
		}
	}

	return $null
}

$retailProjects = @(
	@{
		Path = 'src/code/quakelive_steam.vcxproj'
		RuntimeReleaseXPath = '//msb:ItemDefinitionGroup[@Condition and not(contains(@Condition, ''Debug''))]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeReleaseValue = 'MultiThreadedDLL'
		RuntimeDebugXPath = '//msb:ItemDefinitionGroup[contains(@Condition, ''Debug'')]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeDebugValue = 'MultiThreadedDebugDLL'
		ExtraChecks = @(
			@{ XPath = '//msb:PlatformToolset'; Value = 'v100' }
			@{ XPath = '//msb:Link/msb:GenerateManifest'; Value = 'false' }
			@{ XPath = '//msb:Link/msb:MinimumRequiredVersion'; Value = '5.01' }
			@{ XPath = '//msb:Link/msb:RandomizedBaseAddress'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:DataExecutionPrevention'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:TerminalServerAware'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:StackReserveSize'; Value = '1048576' }
		)
	}
	@{
		Path = 'src/code/game/qagamex86.vcxproj'
		RuntimeReleaseXPath = '//msb:ItemDefinitionGroup[@Condition and not(contains(@Condition, ''Debug''))]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeReleaseValue = 'MultiThreadedDLL'
		RuntimeDebugXPath = '//msb:ItemDefinitionGroup[contains(@Condition, ''Debug'')]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeDebugValue = 'MultiThreadedDebugDLL'
		ExtraChecks = @(
			@{ XPath = '//msb:PlatformToolset'; Value = 'v100' }
			@{ XPath = '//msb:Link/msb:MinimumRequiredVersion'; Value = '5.01' }
			@{ XPath = '//msb:Link/msb:RandomizedBaseAddress'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:DataExecutionPrevention'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:ImageHasSafeExceptionHandlers'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:BaseAddress'; Value = '0x10000000' }
			@{ XPath = '//msb:Link/msb:ProgramDatabaseFile'; Value = '$(OutDir)game.pdb' }
		)
	}
	@{
		Path = 'src/code/cgame/cgamex86.vcxproj'
		RuntimeReleaseXPath = '//msb:ItemDefinitionGroup[@Condition and not(contains(@Condition, ''Debug''))]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeReleaseValue = 'MultiThreadedDLL'
		RuntimeDebugXPath = '//msb:ItemDefinitionGroup[contains(@Condition, ''Debug'')]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeDebugValue = 'MultiThreadedDebugDLL'
		ExtraChecks = @(
			@{ XPath = '//msb:PlatformToolset'; Value = 'v100' }
			@{ XPath = '//msb:Link/msb:MinimumRequiredVersion'; Value = '5.01' }
			@{ XPath = '//msb:Link/msb:RandomizedBaseAddress'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:DataExecutionPrevention'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:ImageHasSafeExceptionHandlers'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:BaseAddress'; Value = '0x10000000' }
		)
	}
	@{
		Path = 'src/code/ui/ui.vcxproj'
		RuntimeReleaseXPath = '//msb:ItemDefinitionGroup[@Condition and not(contains(@Condition, ''Debug''))]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeReleaseValue = 'MultiThreadedDLL'
		RuntimeDebugXPath = '//msb:ItemDefinitionGroup[contains(@Condition, ''Debug'')]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeDebugValue = 'MultiThreadedDebugDLL'
		ExtraChecks = @(
			@{ XPath = '//msb:PlatformToolset'; Value = 'v100' }
			@{ XPath = '//msb:Link/msb:MinimumRequiredVersion'; Value = '5.01' }
			@{ XPath = '//msb:Link/msb:RandomizedBaseAddress'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:DataExecutionPrevention'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:ImageHasSafeExceptionHandlers'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:BaseAddress'; Value = '0x10000000' }
		)
	}
	@{
		Path = 'src/code/awesomium_process.vcxproj'
		RuntimeReleaseXPath = '//msb:ItemDefinitionGroup[@Condition and not(contains(@Condition, ''Debug''))]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeReleaseValue = 'MultiThreaded'
		RuntimeDebugXPath = '//msb:ItemDefinitionGroup[contains(@Condition, ''Debug'')]/msb:ClCompile/msb:RuntimeLibrary'
		RuntimeDebugValue = 'MultiThreadedDebug'
		ExtraChecks = @(
			@{ XPath = '//msb:PlatformToolset'; Value = 'v100' }
			@{ XPath = '//msb:Link/msb:GenerateManifest'; Value = 'false' }
			@{ XPath = '//msb:Link/msb:MinimumRequiredVersion'; Value = '5.01' }
			@{ XPath = '//msb:Link/msb:RandomizedBaseAddress'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:DataExecutionPrevention'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:TerminalServerAware'; Value = 'true' }
			@{ XPath = '//msb:Link/msb:ImageHasSafeExceptionHandlers'; Value = 'true' }
		)
	}
)

foreach ($entry in $retailProjects) {
	$xml = Get-ProjectXml -ProjectRelativePath $entry.Path

	Assert-ProjectAttribute -ProjectXml $xml -ProjectRelativePath $entry.Path -AttributeName 'ToolsVersion' -ExpectedValue '4.0'
	Assert-NodeValues -ProjectXml $xml -ProjectRelativePath $entry.Path -XPath $entry.RuntimeReleaseXPath -ExpectedValue $entry.RuntimeReleaseValue
	Assert-NodeValues -ProjectXml $xml -ProjectRelativePath $entry.Path -XPath $entry.RuntimeDebugXPath -ExpectedValue $entry.RuntimeDebugValue

	foreach ($check in $entry.ExtraChecks) {
		Assert-NodeValues -ProjectXml $xml -ProjectRelativePath $entry.Path -XPath $check.XPath -ExpectedValue $check.Value
	}
}

$toolsetPath = Test-V100ToolsetInstalled
if ($toolsetPath) {
	Write-Host "Found Visual C++ 2010 toolset: $toolsetPath"
}
else {
	$message = 'Visual C++ 2010 (v100) platform toolset was not found on this machine.'
	if ($Strict) {
		throw $message
	}

	Write-Warning $message
}
