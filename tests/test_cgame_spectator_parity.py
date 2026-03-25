"""Guard retail-backed cgame spectator/export behavior against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_shutdown_restores_ui_mainmenu() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_Shutdown")

	assert 'trap_Cvar_Set( "ui_mainmenu", "1" );' in block


def test_auto_follow_powerup_matches_retail_command_shape() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	should_follow = _block_from_marker(source, "static qboolean CG_ShouldAutoFollowTrack")
	try_follow = _block_from_marker(source, "static void CG_TryAutoFollowPowerup")
	track_event = _block_from_marker(source, "void CG_SpectatorTrackEvent")

	assert "CG_SPECTATOR_TRACK_FLAG || trackType == CG_SPECTATOR_TRACK_POWERUP" in should_follow
	assert "followMode > 1 && trackType != CG_SPECTATOR_TRACK_FLAG" not in should_follow

	assert 'suffix = " pw";' in try_follow
	assert "cg_followPowerup.integer == 2 && trackType == CG_SPECTATOR_TRACK_POWERUP" in try_follow
	assert 'trap_SendClientCommand( va( "follow %d%s", clientNum, suffix ) );' in try_follow

	assert "CG_TryAutoFollowPowerup( clientNum, trackType );" in track_event
	assert 'trap_SendClientCommand( va( "follow %d", clientNum ) );' not in track_event


def test_tracked_slot_notifiers_arm_retail_latches_and_replay_last_message() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	slot_block = _block_from_marker(main_source, "static void CG_ShowTrackedPlayerSlot")
	first_block = _block_from_marker(main_source, "static void CG_Show1stTrackedPlayer")
	second_block = _block_from_marker(main_source, "static void CG_Show2ndTrackedPlayer")
	tracked_block = _block_from_marker(newdraw_source, "static qboolean CG_SpectatorSlotTracked")

	assert "spectatorSlotTrackedTime[2];" in local_source
	assert "cg.spectatorSlotTrackedTime[slot] = cg.time + CG_SPECTATOR_SLOT_TRACK_HOLD;" in slot_block
	assert "CG_ReplayLastMessageFromCvar();" in slot_block
	assert "CG_ShowTrackedPlayerSlot( 0 );" in first_block
	assert "CG_ShowTrackedPlayerSlot( 1 );" in second_block
	assert "trackedTime = cg.spectatorSlotTrackedTime[0];" in tracked_block
	assert "trackedTime = cg.spectatorSlotTrackedTime[1];" in tracked_block
	assert "if ( trackedTime > cg.time ) {" in tracked_block


def test_key_event_intercepts_retail_hud_binding_commands() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	handler_block = _block_from_marker(source, "static qboolean CG_HandleHudBindingCommand")
	key_block = _block_from_marker(source, "void CG_KeyEvent")

	for expected in (
		'"messagemode"',
		'"screenshot"',
		'"screenshotJPEG"',
		'"+voice"',
		'"+scores"',
		'trap_Cmd_ExecuteText( EXEC_APPEND, va( "%s\\n", binding ) );',
		"CG_ShowResponseHead();",
		"CG_MenuScript_OpenScoreboard();",
	):
		assert expected in handler_block

	assert "trap_Key_GetBindingBuf( key, bindingBuf, sizeof( bindingBuf ) );" in key_block
	assert "if ( CG_HandleHudBindingCommand( bindingBuf ) ) {" in key_block
