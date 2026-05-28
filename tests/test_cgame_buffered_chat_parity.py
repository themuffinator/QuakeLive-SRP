"""Guard the retail-backed cgame buffered chat path against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


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


def _text_between(source: str, start: str, end: str) -> str:
	start_index = source.index(start)
	end_index = source.index(end, start_index)
	return source[start_index:end_index]


def test_retail_hlil_exposes_new_chat_active_record_and_history_ring() -> None:
	source = CGAME_HLIL.read_text(encoding="utf-8")
	block = _text_between(
		source,
		"100068e0    int32_t sub_100068e0()",
		"10006be0    int32_t sub_10006be0()",
	)

	for expected in (
		"memset(0x10079950, 0, 0x1920)",
		"data_10079838 = 0x17",
		"temp1_1 * 0x10c + 0x10079950",
		"data_10079844 = eax_6 + arg3 + 0x7d0",
		"(sbb.d(ebx_2, ebx_2, ebx_1 != 0) & 0xb6) + 0x49",
		"if (data_10a9c214.d == 5)",
		"i_1 = 4",
		"else if (eax_6 != 0)",
		"i_1 = 2",
		"if (data_10a9c9b4 != 0 || eax_6 != 0)",
		"var_4 = fconvert.s(fconvert.t(var_4) - fconvert.t(13.0))",
	):
		assert expected in block


def test_buffered_chat_headers_expose_latch_and_writer() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "#define\tTEAMCHAT_HEIGHT\t\t24" in source
	assert "#define\tTEAMCHAT_TEXT_SIZE\t256" in source
	assert "qboolean\t\tchatHistoryVisible;" in source
	assert "teamChatMsgs[TEAMCHAT_HEIGHT][TEAMCHAT_TEXT_SIZE]" in source
	assert "teamChatMsgExpireTimes[TEAMCHAT_HEIGHT]" in source
	assert "teamChatMsgTypes[TEAMCHAT_HEIGHT]" in source
	assert "teamChatActiveMsg[TEAMCHAT_TEXT_SIZE]" in source
	assert "teamChatActiveExpireTime" in source
	assert "void CG_ArchiveNewChatLine( void );" in source
	assert "void CG_PushPrintString( const char *text, int type, int holdTime );" in source


def test_console_command_tail_exposes_retail_chat_handlers() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	chat_down = _block_from_marker(source, "static void CG_ChatDown_f")
	chat_up = _block_from_marker(source, "static void CG_ChatUp_f")
	toggle = _block_from_marker(source, "static void CG_ToggleChatHistory_f")
	print_block = _block_from_marker(source, "static void CG_Print_f")

	for expected in (
		'{ "+chat", CG_ChatDown_f },',
		'{ "-chat", CG_ChatUp_f },',
		'{ "togglechathistory", CG_ToggleChatHistory_f },',
		'{ "print", CG_Print_f },',
	):
		assert expected in source

	assert "cg.chatHistoryVisible = qtrue;" in chat_down
	assert "cg.chatHistoryVisible = qfalse;" in chat_up
	assert "cg.chatHistoryVisible = (qboolean)!cg.chatHistoryVisible;" in toggle
	assert "argc = trap_Argc();" in print_block
	assert 'Q_strcat( buffer, sizeof( buffer ), " " );' in print_block
	assert "CG_PushPrintString( buffer, SYSTEM_PRINT, 0 );" in print_block


def test_buffered_chat_writer_updates_ring_and_lastmsg() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	archive_block = _block_from_marker(source, "void CG_ArchiveNewChatLine( void )")
	block = _block_from_marker(source, "void CG_PushPrintString( const char *text, int type, int holdTime )")
	replay_block = _block_from_marker(source, "static void CG_ReplayLastMessageFromCvar")

	assert "index = cgs.teamChatPos % TEAMCHAT_HEIGHT;" in archive_block
	assert "Q_strncpyz( cgs.teamChatMsgs[index], cgs.teamChatActiveMsg, sizeof( cgs.teamChatMsgs[index] ) );" in archive_block
	assert "cgs.teamChatMsgTimes[index] = cgs.teamChatActiveTime;" in archive_block
	assert "cgs.teamChatMsgExpireTimes[index] = cgs.teamChatActiveExpireTime;" in archive_block
	assert "cgs.teamChatMsgTypes[index] = cgs.teamChatActiveType;" in archive_block
	assert "cgs.teamChatActiveMsg[0] = '\\0';" in archive_block
	assert "Q_strncpyz( cleanText, text, sizeof( cleanText ) );" in block
	assert "cleanText[len - 1] == '\\n'" in block
	assert "CG_SetPrintString( type, cleanText );" in block
	assert "CG_WriteLastMessageCvar( cg.time, cleanText );" in block
	assert "CG_ArchiveNewChatLine();" in block
	assert "maxLength = cg.intermissionStarted ? 73 : (int)sizeof( cgs.teamChatActiveMsg );" in block
	assert "Q_strncpyz( cgs.teamChatActiveMsg, cleanText, maxLength );" in block
	assert "cgs.teamChatActiveTime = cg.time;" in block
	assert "cgs.teamChatActiveExpireTime = cg.time + holdTime + 2000;" in block
	assert "cgs.teamChatActiveType = type;" in block
	assert "CG_PushPrintString( message, SYSTEM_PRINT, 0 );" in replay_block


def test_cgame_printf_does_not_play_chat_sound() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void QDECL CG_Printf")

	assert "trap_Print( text );" in block
	assert "trap_S_StartLocalSound" not in block
	assert "cg_chatbeep" not in block


def test_new_chat_area_obeys_history_latch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	init_block = _block_from_marker(source, "void CG_InitTeamChat()")
	draw_block = _block_from_marker(source, "static void CG_DrawNewChatArea")
	visible_block = _block_from_marker(source, "static qboolean CG_OwnerDrawPrimaryFlagVisible")

	assert "memset( cgs.teamChatMsgs, 0, sizeof( cgs.teamChatMsgs ) );" in init_block
	assert "memset( cgs.teamChatMsgTimes, 0, sizeof( cgs.teamChatMsgTimes ) );" in init_block
	assert "memset( cgs.teamChatMsgExpireTimes, 0, sizeof( cgs.teamChatMsgExpireTimes ) );" in init_block
	assert "memset( cgs.teamChatMsgTypes, 0, sizeof( cgs.teamChatMsgTypes ) );" in init_block
	assert "memset( cgs.teamChatActiveMsg, 0, sizeof( cgs.teamChatActiveMsg ) );" in init_block
	assert "cgs.teamChatActiveExpireTime = 0;" in init_block
	assert "cgs.teamChatPos = 0;" in init_block
	assert "cgs.teamLastChatPos = 0;" in init_block
	assert "cg.chatHistoryVisible = qfalse;" in init_block

	assert "if ( scale <= 0.0f || scale < 0.1f ) {" in draw_block
	assert "scale = 0.1f;" in draw_block
	assert "else if ( scale > 0.22f ) {" in draw_block
	assert "scale = 0.22f;" in draw_block
	assert "cg.time <= cgs.teamChatActiveExpireTime" in draw_block
	assert "CG_ArchiveNewChatLine();" in draw_block
	assert "maxLines = chatHeight;" in draw_block
	assert "maxLines = 4;" in draw_block
	assert "maxLines = 2;" in draw_block
	assert "if ( !( cg.chatHistoryVisible || cg.scoreBoardShowing ) ) {" in draw_block
	assert "index = pos % TEAMCHAT_HEIGHT;" in draw_block
	assert "y -= 13.0f;" in draw_block
	assert "cg_teamChatTime.integer" not in draw_block
	assert "lineColor[3]" not in draw_block
	assert "cg.chatHistoryVisible || cg.scoreBoardShowing" in visible_block


def test_server_command_path_uses_shared_buffered_writer() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	add_block = _block_from_marker(source, "static void CG_AddToTeamChat( const char *str )")
	buffered_block = _block_from_marker(source, "static void CG_ParseBufferedChat( void )")
	clear_block = _block_from_marker(source, "static void CG_ParseClearChat( void )")
	ui_priv_block = _block_from_marker(source, "static void CG_ParseUiPriv( void )")
	stoprecord_block = _block_from_marker(source, "static void CG_ParseStopRecord( void )")
	server_command = _block_from_marker(source, "static void CG_ServerCommand( void )")

	assert "CG_PushPrintString( str, TEAMCHAT_PRINT, 0 );" in add_block
	assert "trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );" in buffered_block
	assert "CG_RemoveChatEscapeChar( text );" in buffered_block
	assert 'CG_Printf( "%s\\n", text );' in buffered_block
	assert "holdTime = atoi( CG_Argv( 2 ) ) * 1000;" in buffered_block
	assert "CG_PushPrintString( text, SYSTEM_PRINT, holdTime );" in buffered_block
	assert "CG_InitTeamChat();" in clear_block
	assert 'trap_Cvar_Set( "ui_priv", CG_Argv( 1 ) );' in ui_priv_block
	assert 'trap_SendConsoleCommand( "stoprecord; wait\\n" );' in stoprecord_block
	assert 'CG_PushPrintString( CG_Argv(1), SYSTEM_PRINT, 0 );' in server_command
	assert "CG_PushPrintString( text, CHAT_PRINT, 0 );" in server_command
	assert "CG_PushPrintString( text, TEAMCHAT_PRINT, 0 );" in server_command
	assert 'if ( !strcmp( cmd, "bchat" ) ) {' in server_command
	assert "CG_ParseBufferedChat();" in server_command
	assert 'if ( !strcmp( cmd, "clearChat" ) ) {' in server_command
	assert "CG_ParseClearChat();" in server_command
	assert 'if ( !strcmp( cmd, "ui_priv" ) ) {' in server_command
	assert "CG_ParseUiPriv();" in server_command
