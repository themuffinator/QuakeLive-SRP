from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

_SERVER_REFRESH_HARNESS = r"""
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <stdarg.h>
#include "ui_server_browser.h"

vmCvar_t ui_new = {0};
vmCvar_t ui_debug = {0};
vmCvar_t ui_initialized = {0};
vmCvar_t ui_teamArenaFirstRun = {0};
vmCvar_t ui_menuFlow = {0};
vmCvar_t ui_browserAwesomium = {0};
vmCvar_t ui_netSource = {0};
uiInfo_t uiInfo;

static int reset_pings = 0;
static int mark_visible = 0;
static char last_cmd[64];
static char last_cvar[64];
static char last_cvar_value[128];

/*
=============
Q_stricmp

Stubbed case-insensitive compare for test harnesses.
=============
*/
int Q_stricmp( const char *s1, const char *s2 ) {
	return strcasecmp( s1, s2 );
}

/*
=============
Q_stricmpn

Stubbed length-bound case-insensitive compare for test harnesses.
=============
*/
int Q_stricmpn( const char *s1, const char *s2, int n ) {
	return strncasecmp( s1, s2, n );
}

/*
=============
va

Minimal formatter stub for harness output.
=============
*/
char *va( char *format, ... ) {
	static char buffers[2][256];
	static int index = 0;
	va_list args;

	index ^= 1;
	va_start( args, format );
	vsnprintf( buffers[index], sizeof( buffers[index] ), format, args );
	va_end( args );
	return buffers[index];
}

/*
=============
trap_LAN_ResetPings

Record that the harness reset pending pings.
=============
*/
void trap_LAN_ResetPings( int source ) {
	reset_pings = source;
}

/*
=============
trap_LAN_MarkServerVisible

Record the current visibility flag applied during refresh.
=============
*/
void trap_LAN_MarkServerVisible( int source, int n, qboolean visible ) {
	(void)n;
	mark_visible = visible ? source : -source;
}

/*
=============
trap_Cmd_ExecuteText

Capture the last command dispatched by the refresh routine.
=============
*/
void trap_Cmd_ExecuteText( int when, const char *text ) {
	(void)when;
	strncpy( last_cmd, text, sizeof( last_cmd ) - 1 );
	last_cmd[sizeof( last_cmd ) - 1] = '\0';
	size_t len = strlen( last_cmd );
	if ( len > 0 && last_cmd[len - 1] == '\n' ) {
		last_cmd[len - 1] = '\0';
	}
}

/*
=============
trap_Cvar_Set

Capture the last cvar update applied during refresh.
=============
*/
void trap_Cvar_Set( const char *var_name, const char *value ) {
	strncpy( last_cvar, var_name, sizeof( last_cvar ) - 1 );
	last_cvar[sizeof( last_cvar ) - 1] = '\0';
	strncpy( last_cvar_value, value, sizeof( last_cvar_value ) - 1 );
	last_cvar_value[sizeof( last_cvar_value ) - 1] = '\0';
}

/*
=============
trap_Cvar_SetValue

Mirror float cvar updates into the string channel for verification.
=============
*/
void trap_Cvar_SetValue( const char *var_name, float value ) {
	char buffer[32];
	snprintf( buffer, sizeof( buffer ), "%g", value );
	trap_Cvar_Set( var_name, buffer );
}

/*
=============
trap_RealTime

Populate a deterministic qtime_t for timestamp formatting.
=============
*/
int trap_RealTime( qtime_t *qtime ) {
	memset( qtime, 0, sizeof( qtime_t ) );
	qtime->tm_mon = 0;
	qtime->tm_mday = 2;
	qtime->tm_year = 100;
	qtime->tm_hour = 3;
	qtime->tm_min = 4;
	return 0;
}

/*
=============
UI_Cvar_VariableString

Harness stub for debug_protocol lookups.
=============
*/
char *UI_Cvar_VariableString( const char *var_name ) {
	(void)var_name;
	static char empty[1] = { '\0' };
	return empty;
}

/*
=============
trap_Cvar_VariableValue

Provide a fixed protocol value for global server queries.
=============
*/
float trap_Cvar_VariableValue( const char *var_name ) {
	(void)var_name;
	return 73.0f;
}

/*
=============
UI_Load

Placeholder to satisfy link requirements.
=============
*/
void UI_Load( void ) {
	return;
}


/*
=============
main

Exercise the pending ping reset and full refresh path.
=============
*/
int main( void ) {
	memset( &uiInfo, 0, sizeof( uiInfo ) );
	ui_menuFlow.integer = 0;
	ui_browserAwesomium.integer = 0;
	ui_netSource.integer = AS_LOCAL;
	uiInfo.uiDC.realTime = 5000;
	UI_UpdateActiveMenuFlow();
	UI_UpdatePendingPings();
	printf( "pending:active:%d time:%d resets:%d\n", uiInfo.serverStatus.refreshActive, uiInfo.serverStatus.refreshtime, reset_pings );

	reset_pings = 0;
	mark_visible = 0;
	uiInfo.serverStatus.refreshActive = qfalse;
	uiInfo.serverStatus.refreshtime = 0;
	UI_StartServerRefresh( qtrue );
	printf( "start:active:%d next:%d time:%d cmd:%s cvar:%s=%s visible:%d\n", uiInfo.serverStatus.refreshActive, uiInfo.serverStatus.nextDisplayRefresh, uiInfo.serverStatus.refreshtime, last_cmd, last_cvar, last_cvar_value, mark_visible );
	return 0;
}"""


def test_server_refresh_paths(tmp_path: Path) -> None:
	workdir = tmp_path / "server_refresh"
	workdir.mkdir(parents=True, exist_ok=True)
	harness_path = workdir / "server_refresh_harness.c"
	harness_path.write_text(_SERVER_REFRESH_HARNESS, encoding="utf-8")
	exe_path = workdir / "server_refresh_harness"
	compile_cmd = [
		"gcc",
		"-std=c99",
		"-Wall",
		"-Wno-error",
		"-I",
		str(REPO_ROOT / "src" / "code" / "ui"),
		"-I",
		str(REPO_ROOT / "src" / "code"),
		"-I",
		str(REPO_ROOT / "src"),
		str(harness_path),
		str(REPO_ROOT / "src" / "code" / "ui" / "ui_menu_flow.c"),
		str(REPO_ROOT / "src" / "code" / "ui" / "ui_server_browser.c"),
		"-o",
		str(exe_path),
	]
	compile_result = subprocess.run(compile_cmd, check=True, capture_output=True, text=True, cwd=REPO_ROOT)
	run_result = subprocess.run([str(exe_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)
	lines = [line.strip() for line in run_result.stdout.splitlines() if line.strip()]
	assert lines == [
	"pending:active:1 time:6000 resets:0",
	"start:active:1 next:6000 time:6000 cmd:localservers cvar:ui_lastServerRefresh_0=Jan-2, 2000 at 3:4 visible:0",
	]

