[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
)

$ErrorActionPreference = 'Stop'

function Assert-FileContainsLiteral {
	param(
		[string]$RelativePath,
		[string]$Literal
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file not found: $RelativePath"
	}

	$content = Get-Content -LiteralPath $path -Raw
	if ($content -notlike "*$Literal*") {
		throw "Expected literal was not found in ${RelativePath}: $Literal"
	}

	Write-Host "Verified $RelativePath contains: $Literal"
}

function Assert-FileLacksLiteral {
	param(
		[string]$RelativePath,
		[string]$Literal
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file not found: $RelativePath"
	}

	$content = Get-Content -LiteralPath $path -Raw
	if ($content -like "*$Literal*") {
		throw "Unexpected literal was found in ${RelativePath}: $Literal"
	}

	Write-Host "Verified $RelativePath does not contain: $Literal"
}

function Assert-NormalizedFileEquals {
	param(
		[string]$RelativePath,
		[string]$ExpectedContent
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file not found: $RelativePath"
	}

	$actual = (Get-Content -LiteralPath $path -Raw).Replace("`r`n", "`n").Trim()
	$expected = $ExpectedContent.Replace("`r`n", "`n").Trim()

	if ($actual -ne $expected) {
		throw "Normalized content mismatch in ${RelativePath}"
	}

	Write-Host "Verified normalized content for $RelativePath"
}

Assert-FileContainsLiteral -RelativePath 'src/code/win32/winquake.rc' -Literal '1                       RT_MANIFEST             "quakelive_steam.manifest"'
Assert-FileContainsLiteral -RelativePath 'src/code/win32/winquake.rc' -Literal 'VALUE "InternalName", "Quake Live\0"'
Assert-FileContainsLiteral -RelativePath 'src/code/win32/winquake.rc' -Literal 'VALUE "OriginalFilename", "quake3.exe\0"'
Assert-FileContainsLiteral -RelativePath 'src/code/win32/winquake.rc' -Literal 'VALUE "ProductName", "quake3\0"'
Assert-FileLacksLiteral -RelativePath 'src/code/win32/winquake.rc' -Literal 'STRINGTABLE DISCARDABLE'

Assert-FileContainsLiteral -RelativePath 'src/code/win32/awesomium_process.rc' -Literal '1                       RT_MANIFEST             "awesomium_process.manifest"'
Assert-FileContainsLiteral -RelativePath 'src/code/quakelive_steam.vcxproj' -Literal '<GenerateManifest>false</GenerateManifest>'
Assert-FileContainsLiteral -RelativePath 'src/code/awesomium_process.vcxproj' -Literal '<GenerateManifest>false</GenerateManifest>'

$expectedLauncherManifest = @'
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"></requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2, PerMonitor</dpiAwareness>
    </windowsSettings>
  </application>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC80.CRT" version="8.0.50727.762" processorArchitecture="x86" publicKeyToken="1fc8b3b9a1e18e3b"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
'@

$expectedAwesomiumManifest = @'
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"></requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
'@

Assert-NormalizedFileEquals -RelativePath 'src/code/win32/quakelive_steam.manifest' -ExpectedContent $expectedLauncherManifest
Assert-NormalizedFileEquals -RelativePath 'src/code/win32/awesomium_process.manifest' -ExpectedContent $expectedAwesomiumManifest
