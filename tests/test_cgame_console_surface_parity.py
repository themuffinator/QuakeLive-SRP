"""Guard the retail-backed cgame console surface against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"


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


def test_local_console_surface_stays_narrower_like_retail() -> None:
	console_source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	menu_source = CG_NEWDRAW.read_text(encoding="utf-8")

	for unexpected in (
		"static void CG_SpectatorFollowNext_f",
		"static void CG_SpectatorFollowPrev_f",
		"static void CG_SpectatorStopFollow_f",
		"static void CG_SpectatorLockCamera_f",
		"static void CG_SpectatorUnlockCamera_f",
		'{ "spectatorFollowNext", CG_SpectatorFollowNext_f },',
		'{ "spectatorFollowPrev", CG_SpectatorFollowPrev_f },',
		'{ "spectatorFollowStop", CG_SpectatorStopFollow_f },',
		'{ "spectatorCameraLock", CG_SpectatorLockCamera_f },',
		'{ "spectatorCameraUnlock", CG_SpectatorUnlockCamera_f },',
	):
		assert unexpected not in console_source

	for expected in (
		'{ "nextTeamMember", CG_NextTeamMember_f },',
		'{ "prevTeamMember", CG_PrevTeamMember_f },',
		'spectatorFollowNext',
		'spectatorFollowPrev',
		'spectatorFollowStop',
		'spectatorCameraLock',
		'spectatorCameraUnlock',
	):
		assert expected in (menu_source if expected.startswith("spectator") else console_source)


def test_forwarded_server_command_registry_matches_retail_tail() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")

	for expected in (
		'trap_AddCommand ("abort");',
		'trap_AddCommand ("addadmin");',
		'trap_AddCommand ("addmod");',
		'trap_AddCommand ("addscore");',
		'trap_AddCommand ("addteamscore");',
		'trap_AddCommand ("allready");',
		'trap_AddCommand ("ban");',
		'trap_AddCommand ("demote");',
		'trap_AddCommand ("dropflag");',
		'trap_AddCommand ("droppowerup");',
		'trap_AddCommand ("droprune");',
		'trap_AddCommand ("dropweapon");',
		'trap_AddCommand ("forfeit");',
		'trap_AddCommand ("listaccess");',
		'trap_AddCommand ("lock");',
		'trap_AddCommand ("mute");',
		'trap_AddCommand ("opsay");',
		'trap_AddCommand ("pause");',
		'trap_AddCommand ("players");',
		'trap_AddCommand ("put");',
		'trap_AddCommand ("ragequit");',
		'trap_AddCommand ("rcon");',
		'trap_AddCommand ("reload_access");',
		'trap_AddCommand ("setmatchtime");',
		'trap_AddCommand ("spec");',
		'trap_AddCommand ("tempban");',
		'trap_AddCommand ("timein");',
		'trap_AddCommand ("timeout");',
		'trap_AddCommand ("unban");',
		'trap_AddCommand ("unlock");',
		'trap_AddCommand ("unmute");',
		'trap_AddCommand ("unpause");',
	):
		assert expected in source


def test_retail_local_drop_and_ragequit_wrappers_remain_in_console_surface() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")

	for expected in (
		'{ "dropflag", CG_DropFlag_f },',
		'{ "droppowerup", CG_DropPowerup_f },',
		'{ "droprune", CG_DropRune_f },',
		'{ "dropweapon", CG_DropWeapon_f },',
		'{ "forfeit", CG_Forfeit_f },',
		'{ "ragequit", CG_RageQuit_f },',
		'{ "kill", CG_Kill_f },',
		'trap_SendClientCommand( "dropflag" );',
		'trap_SendClientCommand( "droppowerup" );',
		'trap_SendClientCommand( "droprune" );',
		'trap_SendClientCommand( "dropweapon" );',
		'trap_SendClientCommand( "forfeit" );',
		'trap_SendClientCommand( "ragequit" );',
		'trap_SendClientCommand( "kill" );',
		'cg.rageQuitTime = 2;',
		'"DropFlag is not available in non-flag gametypes.\\n"',
		'"DropPowerup is not available in non-team gametypes.\\n"',
		'"DropPowerup is not available in %s.\\n"',
		'"DropPowerup is not available in InstaGib.\\n"',
		'"DropRune not available in %s.\\n"',
		'"DropWeapon is not available in non-team gametypes.\\n"',
		'"DropWeapon is not available in %s.\\n"',
		'"DropWeapon is not available in InstaGib.\\n"',
		'"Forfeit is not available in %s.\\n"',
		'"cmd vsay kill_gauntlet\\n"',
	):
		assert expected in source

	assert "kill_guantlet" not in source


def test_retail_local_kill_wrapper_remains_in_console_surface() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void CG_Kill_f")

	assert 'trap_SendClientCommand( "kill" );' in block


def test_retail_local_color_wrappers_remain_in_console_surface() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")

	for expected in (
		'{ "setteamcolor", CG_SetTeamColor_f },',
		'{ "setenemycolor", CG_SetEnemyColor_f },',
		'cg_retailCommandColorPalette[26]',
		'0x800000ffu',
		'0x404040ffu',
		'Current %s color: %s\\n',
		'trap_Cvar_Set( useTeam ? "cg_teamColors" : "cg_enemyColors", colorArg );',
		'trap_Cvar_Set( useTeam ? "cg_teamHeadColor" : "cg_enemyHeadColor", headColor );',
		'trap_Cvar_Set( useTeam ? "cg_teamUpperColor" : "cg_enemyUpperColor", upperColor );',
		'trap_Cvar_Set( useTeam ? "cg_teamLowerColor" : "cg_enemyLowerColor", lowerColor );',
	):
		assert expected in source


def test_retail_local_team_wrapper_remains_in_console_surface() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")

	for expected in (
		'{ "team", CG_Team_f },',
		'static void CG_Team_f( void ) {',
		'Com_sprintf( command, sizeof( command ), "team %s", teamArg );',
		'trap_SendClientCommand( command );',
		'CG_ClearRetailCommandCaptureState();',
		'static void CG_ClearRetailCommandCaptureState( void ) {',
		'cgs.eventHandling == CGAME_EVENT_TEAMMENU ||',
		'cgs.eventHandling == CGAME_EVENT_EDITHUD ) {',
		'CG_EventHandling( CGAME_EVENT_NONE );',
		'trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );',
	):
		assert expected in source


def test_retail_local_readyup_wrapper_remains_in_console_surface() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")

	for expected in (
		'{ "readyup", CG_ReadyUp_f },',
		'static qboolean CG_IsRetailReadyUpPregameBypassActive( void ) {',
		'Info_ValueForKey( info, "g_training" );',
		'CG_ConfigString( CS_TUTORIAL_NAME )',
		'CG_ConfigString( CS_TUTORIAL_TEXT )',
		'static void CG_ReadyUp_f( void ) {',
		'if ( !cg.snap ) {',
		'if ( cg.warmup == 0 && cgs.matchReadyUpDeadline <= 0 && !allowPregameBypass ) {',
		'cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR',
		'trap_SendClientCommand( "readyup" );',
	):
		assert expected in source


def test_browser_input_bridge_wraps_shared_display_dispatch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	cursor_block = _block_from_marker(source, "static int CG_BrowserDisplayCursorType")
	move_block = _block_from_marker(source, "static qboolean CG_BrowserDisplayMouseMove")
	key_block = _block_from_marker(source, "static void CG_BrowserDisplayHandleKey")
	capture_block = _block_from_marker(source, "static void *CG_BrowserDisplayCaptureItem")
	mouse_event_block = _block_from_marker(source, "void CG_MouseEvent")
	key_event_block = _block_from_marker(source, "void CG_KeyEvent")

	assert "return Display_CursorType( x, y );" in cursor_block
	assert "return Display_MouseMove( overlay, x, y );" in move_block
	assert "Display_HandleKey( key, down, x, y );" in key_block
	assert "return Display_CaptureItem( x, y );" in capture_block

	assert "n = CG_BrowserDisplayCursorType( cgs.cursorX, cgs.cursorY );" in mouse_event_block
	assert "CG_BrowserDisplayMouseMove( cgs.capturedItem, x, y );" in mouse_event_block
	assert "CG_BrowserDisplayMouseMove( NULL, cgs.cursorX, cgs.cursorY );" in mouse_event_block
	assert "Display_CursorType(" not in mouse_event_block
	assert "Display_MouseMove(" not in mouse_event_block

	assert "CG_BrowserDisplayHandleKey(key, down, cgs.cursorX, cgs.cursorY);" in key_event_block
	assert "cgs.capturedItem = CG_BrowserDisplayCaptureItem( cgs.cursorX, cgs.cursorY );" in key_event_block
	assert "Display_HandleKey(key, down, cgs.cursorX, cgs.cursorY);" not in key_event_block
	assert "Display_CaptureItem(" not in key_event_block
