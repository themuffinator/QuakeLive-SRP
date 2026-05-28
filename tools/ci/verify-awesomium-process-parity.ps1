[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$BuiltBinary = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path 'build/win32/Release/bin/awesomium_process.exe')
)

$ErrorActionPreference = 'Stop'

function Get-DumpbinPath {
    $command = Get-Command dumpbin.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $vsWhereCandidates = @(
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'),
        (Join-Path ${env:ProgramFiles} 'Microsoft Visual Studio/Installer/vswhere.exe')
    )

    foreach ($candidate in $vsWhereCandidates) {
        if (-not (Test-Path $candidate)) {
            continue
        }

        $json = & $candidate -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $json) {
            continue
        }

        $data = $json | ConvertFrom-Json
        foreach ($install in $data) {
            $search = Join-Path $install.installationPath 'VC/Tools/MSVC'
            if (-not (Test-Path $search)) {
                continue
            }

            $match = Get-ChildItem -Path $search -Directory | Sort-Object Name -Descending | ForEach-Object {
                Join-Path $_.FullName 'bin/Hostx64/x86/dumpbin.exe'
            } | Where-Object { Test-Path $_ } | Select-Object -First 1

            if ($match) {
                return $match
            }
        }
    }

    return $null
}

function Assert-Matches {
    param(
        [string]$Text,
        [string]$Pattern,
        [string]$Failure
    )

    if ($Text -notmatch $Pattern) {
        throw $Failure
    }
}

if (-not (Test-Path $BuiltBinary)) {
    throw "Built awesomium_process.exe was not found at '$BuiltBinary'."
}

$dumpbin = Get-DumpbinPath
if (-not $dumpbin) {
    throw 'dumpbin.exe is required to validate awesomium_process.exe parity.'
}

$headers = (& $dumpbin /nologo /headers $BuiltBinary 2>&1) -join "`n"
if ($LASTEXITCODE -ne 0) {
    throw "dumpbin /headers failed for '$BuiltBinary'."
}

$imports = (& $dumpbin /nologo /imports $BuiltBinary 2>&1) -join "`n"
if ($LASTEXITCODE -ne 0) {
    throw "dumpbin /imports failed for '$BuiltBinary'."
}

$version = (Get-Item $BuiltBinary).VersionInfo
$expectedVersionFields = @{
    CompanyName = 'Quake Live Reverse'
    FileDescription = 'Quake Live Reverse Awesomium child-process host'
    FileVersion = '1.0.0.0'
    InternalName = 'awesomium_process.exe'
    OriginalFilename = 'awesomium_process.exe'
    ProductName = 'Quake Live Reverse'
    ProductVersion = '1.0.0.0'
}

foreach ($entry in $expectedVersionFields.GetEnumerator()) {
    if ($version.($entry.Key) -ne $entry.Value) {
        throw "Version info mismatch for $($entry.Key): expected '$($entry.Value)', found '$($version.($entry.Key))'."
    }
}

Assert-Matches -Text $headers -Pattern 'machine \(x86\)' -Failure 'Expected x86 machine type.'
Assert-Matches -Text $headers -Pattern '10\.00 linker version' -Failure 'Expected LINK 10.00 output.'
Assert-Matches -Text $headers -Pattern '5\.01 operating system version' -Failure 'Expected OS version 5.01.'
Assert-Matches -Text $headers -Pattern '5\.01 subsystem version' -Failure 'Expected subsystem version 5.01.'
Assert-Matches -Text $headers -Pattern 'Application can handle Terminal Server' -Failure 'Expected Terminal Server Aware flag.'
Assert-Matches -Text $headers -Pattern 'Dynamic base' -Failure 'Expected /DYNAMICBASE.'
Assert-Matches -Text $headers -Pattern 'NX compatible' -Failure 'Expected /NXCOMPAT.'

Assert-Matches -Text $imports -Pattern 'KERNEL32\.dll' -Failure 'Expected KERNEL32.dll import.'
Assert-Matches -Text $imports -Pattern 'awesomium\.dll' -Failure 'Expected awesomium.dll import.'
Assert-Matches -Text $imports -Pattern '\?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z' -Failure 'Expected Awesomium::ChildProcessMain import.'

$unexpectedImports = @('VCRUNTIME140.dll', 'MSVCR100.dll', 'MSVCP100.dll', 'api-ms-win-crt-runtime-l1-1-0.dll')
foreach ($library in $unexpectedImports) {
    if ($imports -match [regex]::Escape($library)) {
        throw "Unexpected import library present: $library"
    }
}

Write-Host 'awesomium_process.exe matches the expected external-SDK import, linker, and project-owned version surface.'
