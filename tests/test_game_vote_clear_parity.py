from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


_VOTE_CLEAR_PROBE = textwrap.dedent(
	"""
	#include <stdio.h>
	#include <string.h>

	#define QAGAME 1
	#include "g_vote.c"

	level_locals_t level;
	gclient_t localClients[MAX_CLIENTS];

	void trap_SendServerCommand( int clientNum, const char *text ) {
		(void)clientNum;
		(void)text;
	}

	void trap_SendConsoleCommand( int exec_when, const char *text ) {
		(void)exec_when;
		(void)text;
	}

	void trap_SetConfigstring( int index, const char *value ) {
		printf("cs:%d:%s\\n", index, value ? value : "<null>");
	}

	void trap_Cvar_Set( const char *var_name, const char *value ) {
		(void)var_name;
		(void)value;
	}

	vmCvar_t g_itemHeight;

	team_t TeamCount( int ignoreClientNum, int team ) {
		(void)ignoreClientNum;
		(void)team;
		return TEAM_FREE;
	}

	void Cmd_ShuffleTeams_f( void ) {
	}

	void G_BroadcastItemTimerState( int enabled, int height ) {
		(void)enabled;
		(void)height;
	}

	int main(void) {
		memset(&level, 0, sizeof(level));
		memset(localClients, 0, sizeof(localClients));

		level.maxclients = 2;
		level.clients = localClients;
		level.voteTime = 111;
		level.voteExecuteTime = 222;
		level.voteEligibleTime = 333;
		level.voteYes = 4;
		level.voteNo = 2;
		strcpy(level.voteString, "map bloodrun");
		strcpy(level.voteDisplayString, "bloodrun");
		level.clients[0].ps.eFlags = EF_VOTED;
		level.clients[1].ps.eFlags = EF_VOTED | EF_TALK;

		G_ClearVoteState();

		printf(
			"state:%d:%d:%d:%d:%d:%d:%d:%s:%s\\n",
			level.voteTime,
			level.voteExecuteTime,
			level.voteEligibleTime,
			level.voteYes,
			level.voteNo,
			level.clients[0].ps.eFlags,
			level.clients[1].ps.eFlags,
			level.voteString[0] ? level.voteString : "<empty>",
			level.voteDisplayString[0] ? level.voteDisplayString : "<empty>"
		);

		return 0;
	}
	"""
)


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_g_clear_vote_state_clears_vote_configstrings_and_flags(tmp_path: Path) -> None:
	workdir = tmp_path / "vote_clear"
	workdir.mkdir(parents=True, exist_ok=True)

	c_path = workdir / "probe.c"
	c_path.write_text(_VOTE_CLEAR_PROBE, encoding="utf-8")
	exe_path = workdir / "probe"

	include_args = [
		f"-I{REPO_ROOT / 'src' / 'code' / 'game'}",
		f"-I{REPO_ROOT / 'src' / 'code'}",
		f"-I{REPO_ROOT / 'src'}",
	]
	compiler = shutil.which("gcc")
	if compiler is None:
		pytest.skip("gcc is not available for the standalone vote-clear probe")

	compile_cmd = [
		compiler,
		"-std=c99",
		"-Wall",
		"-Werror",
		*include_args,
		str(c_path),
		"-o",
		str(exe_path),
	]
	subprocess.run(compile_cmd, check=True, cwd=REPO_ROOT)

	result = subprocess.run([str(exe_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)
	lines = [line for line in result.stdout.splitlines() if line.strip()]

	assert lines == [
		"cs:8:",
		"cs:9:",
		"cs:10:0",
		"cs:11:0",
		"state:0:0:0:0:0:0:2:<empty>:<empty>",
	]


def test_intermission_and_vote_resolution_route_through_g_clear_vote_state() -> None:
	g_main = _read("src/code/game/g_main.c")
	g_cmds = _read("src/code/game/g_cmds.c")

	begin_intermission_start = g_main.index("void BeginIntermission( void ) {")
	begin_intermission_end = g_main.index("/*", begin_intermission_start + 1)
	begin_intermission = g_main[begin_intermission_start:begin_intermission_end]
	assert "G_ClearVoteState();" in begin_intermission

	check_vote_start = g_main.index("void CheckVote( void ) {")
	check_vote_end = g_main.index("/*", check_vote_start + 1)
	check_vote = g_main[check_vote_start:check_vote_end]
	assert "G_ClearVoteState();" in check_vote
	assert "trap_SetConfigstring( CS_VOTE_TIME, \"\" );" not in check_vote

	cancel_start = g_cmds.index('if ( !Q_stricmp( arg, "cancel" ) ) {')
	cancel_block = g_cmds[cancel_start:cancel_start + 400]
	assert "G_ClearVoteState();" in cancel_block
