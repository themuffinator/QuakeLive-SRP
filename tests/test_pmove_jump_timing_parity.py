from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"
BG_PMOVE_JUMP_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove_jump.h"
Q_SHARED_PATH = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
MSG_PATH = REPO_ROOT / "src" / "code" / "qcommon" / "msg.c"


def _function_body(path: Path, pattern: str) -> str:
	source = path.read_text(encoding="utf-8")
	match = re.search(
		pattern,
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, f"Function definition missing in {path.name}"
	return match.group("body")


def test_playerstate_uses_retail_jump_time_and_double_jump_latch() -> None:
	source = Q_SHARED_PATH.read_text(encoding="utf-8")

	assert "int\t\t\tjumpTime;" in source
	assert "int\t\t\tdoubleJumped;" in source
	assert "doubleJumpTime" not in source
	assert "doubleJumpEntNum" not in source
	assert "doubleJumpNormal" not in source


def test_playerstate_delta_replication_matches_retail_jump_fields() -> None:
	source = MSG_PATH.read_text(encoding="utf-8")

	assert "{ PSF(jumpTime), 32 }" in source
	assert "{ PSF(doubleJumped), 1 }" in source
	assert "PSF(doubleJumpTime)" not in source
	assert "PSF(doubleJumpEntNum)" not in source
	assert "PSF(doubleJumpNormal[0])" not in source


def test_jump_velocity_scaling_uses_previous_jump_time() -> None:
	source = BG_PMOVE_JUMP_PATH.read_text(encoding="utf-8")

	assert "ps->jumpTime > 0" in source
	assert "commandTime >= ps->jumpTime" in source
	assert "timeDelta = commandTime - ps->jumpTime;" in source
	assert "groundTraceHistoryCount" not in source
	assert "groundTraceTimes" not in source


def test_air_move_probes_retail_double_jump_path() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_AirMove\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "settings = PM_GetActiveSettings();" in body
	assert "if ( settings && settings->doubleJump ) {" in body
	assert "PM_CheckJump( qtrue );" in body


def test_checkjump_uses_jump_time_gate_and_retail_double_jump_latch() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static qboolean PM_CheckJump\( qboolean allowAirDoubleJump \)\s*\{(?P<body>.*?)^\}",
	)

	assert "timeDelta < settings->jumpTimeDeltaMin" in body
	assert "pm->cmd.upmove = 0;" in body
	assert "pm->ps->jumpTime = pm->cmd.serverTime;" in body
	assert "pm->ps->doubleJumped = qtrue;" in body
	assert "PM_CanTriggerDoubleJump" not in body
	assert "PM_ResetDoubleJumpSupport" not in body


def test_ground_trace_clears_double_jump_latch_on_ground_contact() -> None:
	body = _function_body(
		BG_PMOVE_PATH,
		r"static void PM_GroundTrace\( void \)\s*\{(?P<body>.*?)^\}",
	)

	assert "pm->ps->doubleJumped = qfalse;" in body
	assert "PMF_DOUBLE_JUMP" not in body
