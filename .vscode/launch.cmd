@echo off
setlocal
for %%I in ("%~f0") do set "SCRIPT_DIR=%%~dpI"

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=Debug"
if not "%~1"=="" shift

set "BASEPATH="
set "ENABLE_AWESOMIUM="

:parse_opts
if /I "%~1"=="-BasePath" (
	if "%~2"=="" (
		echo launch.cmd: -BasePath requires a value.
		exit /b 1
	)
	set "BASEPATH=%~2"
	shift
	shift
	goto parse_opts
)
if /I "%~1"=="-Awesomium" (
	set "ENABLE_AWESOMIUM=1"
	shift
	goto parse_opts
)

set "EXTRA_ARGS="
:collect_args
if "%~1"=="" goto args_ready
set "EXTRA_ARGS=%EXTRA_ARGS% \"%~1\""
shift
goto collect_args

:args_ready
set "AWESOMIUM_ARG="
if defined ENABLE_AWESOMIUM set "AWESOMIUM_ARG=-EnableAwesomium"

where pwsh.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
	if not defined EXTRA_ARGS (
		pwsh.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG%
	) else (
		pwsh.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG% -ExtraArgs %EXTRA_ARGS%
	)
	exit /b %ERRORLEVEL%
)

if not defined EXTRA_ARGS (
	powershell.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG%
) else (
	powershell.exe -NoExit -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG% -ExtraArgs %EXTRA_ARGS%
)
exit /b %ERRORLEVEL%
