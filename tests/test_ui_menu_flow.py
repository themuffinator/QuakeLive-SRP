from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

_MENU_FLOW_HARNESS = r"""#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "ui_menu_flow.h"

vmCvar_t ui_new = {0};
vmCvar_t ui_debug = {0};
vmCvar_t ui_initialized = {0};
vmCvar_t ui_teamArenaFirstRun = {0};
vmCvar_t ui_menuFlow = {0};
vmCvar_t ui_browserAwesomium = {0};

static int cmd_count = 0;
static char last_cmd[64];

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
trap_Cmd_ExecuteText

Capture outgoing overlay activation commands.
=============
*/
void trap_Cmd_ExecuteText( int exec_when, const char *text ) {
	(void)exec_when;
	cmd_count++;
	strncpy( last_cmd, text, sizeof( last_cmd ) - 1 );
	last_cmd[sizeof( last_cmd ) - 1] = '\0';
	size_t len = strlen( last_cmd );
	if ( len > 0 && last_cmd[len - 1] == '\n' ) {
		last_cmd[len - 1] = '\0';
	}
}

/*
=============
trap_Cvar_SetValue

Mirror menu flow cvar updates into harness storage.
=============
*/
void trap_Cvar_SetValue( const char *var_name, float value ) {
	if ( strcmp( var_name, "ui_menuFlow" ) == 0 ) {
		ui_menuFlow.integer = (int)value;
		ui_menuFlow.value = value;
	}
}

/*
=============
UI_Load

Placeholder to satisfy link requirements for UI_ApplyMenuFlowChange.
=============
*/
void UI_Load( void ) {
	return;
}

/*
=============
main

Exercise menu flow resolution toggling.
=============
*/
int main( void ) {
	ui_menuFlow.integer = 0;
	ui_browserAwesomium.integer = 0;
	ui_new.integer = 0;
	UI_UpdateActiveMenuFlow();
	printf( "legacy:%d ui_new:%d cmds:%d\n", UI_UsingLegacyMenuFlow(), ui_new.integer, cmd_count );

	ui_browserAwesomium.integer = 1;
	UI_ApplyMenuFlowChange( UI_MENU_FLOW_QUAKELIVE, qfalse );
	printf( "quakelive:%d ui_new:%d cmds:%d last:%s\n", UI_UsingLegacyMenuFlow(), ui_new.integer, cmd_count, last_cmd );
	return 0;
}
"""


def test_menu_flow_switching(tmp_path: Path) -> None:
	workdir = tmp_path / "menu_flow"
	workdir.mkdir(parents=True, exist_ok=True)
	harness_path = workdir / "menu_flow_harness.c"
	harness_path.write_text(_MENU_FLOW_HARNESS, encoding="utf-8")
	exe_path = workdir / "menu_flow_harness"
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
	"-o",
	str(exe_path),
	]
	subprocess.run(compile_cmd, check=True, capture_output=True, text=True, cwd=REPO_ROOT)
	run_result = subprocess.run([str(exe_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)
	lines = [line.strip() for line in run_result.stdout.splitlines() if line.strip()]
	assert lines == [
	"legacy:1 ui_new:0 cmds:1",
	"quakelive:0 ui_new:1 cmds:2 last:web_browserActive 1",
	]

