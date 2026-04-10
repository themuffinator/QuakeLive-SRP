@echo off
setlocal
for %%I in ("%~f0") do set "SCRIPT_DIR=%%~dpI"

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=Debug"
if not "%~1"=="" shift

where pwsh.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
	if "%~1"=="" (
		pwsh.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%"
	) else (
		pwsh.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -ExtraArgs %*
	)
	exit /b %ERRORLEVEL%
)

if "%~1"=="" (
	powershell.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%"
) else (
	powershell.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -ExtraArgs %*
)
exit /b %ERRORLEVEL%
