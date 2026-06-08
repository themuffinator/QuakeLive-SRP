"""Guard retail-backed cgame sound command and announcer queue wiring."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
CGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "functions.csv"
)
CGAME_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
CGAME_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


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


def _function_rows() -> dict[str, dict[str, str]]:
	return {
		row["entry"].lower(): row
		for row in csv.DictReader(CGAME_FUNCTIONS.read_text(encoding="utf-8").splitlines())
	}


def _assert_order(block: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = block.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets() -> None:
	aliases = json.loads(_read(SYMBOL_ALIASES))["cgame"]
	rows = _function_rows()

	expected_aliases = {
		"FUN_1003ca30": "CG_CustomSound",
		"sub_1003ca30": "CG_CustomSound",
		"FUN_1004e050": "CG_PowerupTimerSounds",
		"sub_1004e050": "CG_PowerupTimerSounds",
		"FUN_1004e110": "CG_AddBufferedSound",
		"sub_1004e110": "CG_AddBufferedSound",
		"FUN_1004e180": "CG_ClearBufferedAnnouncements",
		"sub_1004e180": "CG_ClearBufferedAnnouncements",
		"FUN_1004e220": "CG_PlayBufferedSounds",
		"sub_1004e220": "CG_PlayBufferedSounds",
	}
	for symbol, expected_name in expected_aliases.items():
		assert aliases[symbol] == expected_name

	expected_rows = {
		"1003ca30": ("FUN_1003ca30", "156"),
		"1004e050": ("FUN_1004e050", "180"),
		"1004e110": ("FUN_1004e110", "109"),
		"1004e180": ("FUN_1004e180", "153"),
		"1004e220": ("FUN_1004e220", "182"),
	}
	for address, (name, size) in expected_rows.items():
		assert rows[address]["name"] == name
		assert rows[address]["size"] == size


def test_cgame_custom_sound_reconstructs_retail_lookup_and_diagnostics() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_PLAYERS)
	custom_sound_block = _block_from_marker(source, "sfxHandle_t\tCG_CustomSound")

	for expected in (
		"1003ca30    int32_t __convention(\"regparm\") sub_1003ca30",
		"1003ca4a      return (*(data_1074cccc + 0xb8))(ebx)",
		"1003caad          if (edi s< 0x20)",
		"1003cab5      sub_10020b50(\"Unknown custom sound: %s\")",
		"1003cacb  return *(arg1 * 0x738 + &data_10a41cf0 + (edi << 2) + 0x690)",
		'char const data_10071204[0x22] = "CG_CustomSound: invalid client %i", 0',
		'char const data_10071228[0x19] = "Unknown custom sound: %s", 0',
	):
		assert expected in hlil

	for expected in (
		"if ( soundName[0] != '*' ) {",
		"return trap_S_RegisterSound( soundName, qfalse );",
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		'CG_Error( "CG_CustomSound: invalid client %i", clientNum );',
		"for ( i = 0 ; i < MAX_CUSTOM_SOUNDS && cg_customSoundNames[i] ; i++ ) {",
		"if ( !strcmp( soundName, cg_customSoundNames[i] ) ) {",
		"return ci->sounds[i];",
		'CG_Error( "Unknown custom sound: %s", soundName );',
	):
		assert expected in custom_sound_block

	assert 'CG_Error( "CG_CustomSound: invalid client %d", clientNum );' not in custom_sound_block


def test_cgame_server_sound_commands_preserve_retail_import_slots_and_order() -> None:
	decompile = _read(CGAME_DECOMPILE)
	source = _read(CG_SERVERCMDS)
	server_command_block = _block_from_marker(source, "static void CG_ServerCommand")

	for expected in (
		'pcVar8 = "playSound";',
		"iVar5 = (**(code **)(iVar5 + 0xb8))(uVar4);",
		"(**(code **)(DAT_1074cccc + 0x9c))(iVar5,6);",
		'pcVar8 = "playMusic";',
		"(**(code **)(iVar5 + 0xbc))(uVar4);",
		'pcVar8 = "stopMusic";',
		"(**(code **)(DAT_1074cccc + 0xc0))();",
		'pcVar8 = "clearSounds";',
		"(**(code **)(DAT_1074cccc + 0xa8))();",
	):
		assert expected in decompile

	_assert_order(
		server_command_block,
		'if ( !strcmp( cmd, "playSound" ) ) {',
		"CG_ParsePlaySound();",
		'if ( !strcmp( cmd, "playMusic" ) ) {',
		"CG_ParsePlayMusic();",
		'if ( !strcmp( cmd, "stopMusic" ) ) {',
		"CG_ParseStopMusic();",
		'if ( !strcmp( cmd, "clearSounds" ) ) {',
		"CG_ParseClearSounds();",
		'if ( !strcmp( cmd, "tchat" ) ) {',
	)

	parse_sound_block = _block_from_marker(source, "static void CG_ParsePlaySound")
	parse_music_block = _block_from_marker(source, "static void CG_ParsePlayMusic")
	stop_music_block = _block_from_marker(source, "static void CG_ParseStopMusic")
	clear_sounds_block = _block_from_marker(source, "static void CG_ParseClearSounds")

	assert "trap_S_StartLocalSound( trap_S_RegisterSound( CG_Argv( 1 ), qfalse ), CHAN_LOCAL_SOUND );" in parse_sound_block
	assert "trap_S_StartBackgroundTrack( CG_Argv(1), CG_Argv(2) );" in parse_music_block
	assert "trap_S_StopBackgroundTrack();" in stop_music_block
	assert "trap_S_ClearLoopingSounds( qtrue );" in clear_sounds_block


def test_cgame_buffered_announcer_queue_matches_retail_ring_and_channel_wiring() -> None:
	hlil = _read(CGAME_HLIL)
	source = _read(CG_VIEW)
	powerup_block = _block_from_marker(source, "static void CG_PowerupTimerSounds")
	clear_buffered_block = _block_from_marker(source, "static void CG_ClearBufferedSounds")
	clear_announcements_block = _block_from_marker(source, "void CG_ClearBufferedAnnouncements")
	add_block = _block_from_marker(source, "void CG_AddBufferedSound")
	play_block = _block_from_marker(source, "static void CG_PlayBufferedSounds")

	for expected in (
		"1004e050    void sub_1004e050()",
		"(*(data_1074cccc + 0x94))(0, *(ebx_1 + 0xb4), 4, data_10a5f800)",
		"1004e110    void __convention(\"regparm\") sub_1004e110",
		"*((data_10ab8db4 << 2) + &data_10ab8e3c) = arg1",
		"*((data_10ab8db4 << 2) + &data_10ab8ebc) = 0x5dc",
		"1004e180    int32_t sub_1004e180()",
		"memset(&data_10ab8e3c, 0, 0x80)",
		"data_10ab8dbc = esi",
		"1004e220    int32_t sub_1004e220()",
		"(*(data_1074cccc + 0xa0))(result, 7",
	):
		assert expected in hlil

	for expected in (
		"for ( i = 0 ; i < MAX_POWERUPS ; i++ ) {",
		"if ( ( t - cg.time ) / POWERUP_BLINK_TIME != ( t - cg.oldTime ) / POWERUP_BLINK_TIME ) {",
		"trap_S_StartSound( NULL, cg.snap->ps.clientNum, CHAN_ITEM, cgs.media.wearOffSound );",
	):
		assert expected in powerup_block

	for expected in (
		"if ( cg_bufferedSoundTimes[cg_bufferedSoundTail] > cg.time ) {",
		"nextSoundTime = cg_bufferedSoundTimes[cg_bufferedSoundTail];",
		"memset( cg_bufferedSounds, 0, sizeof( cg_bufferedSounds ) );",
		"memset( cg_bufferedSoundTimes, 0, sizeof( cg_bufferedSoundTimes ) );",
		"memset( cg_bufferedSoundDelays, 0, sizeof( cg_bufferedSoundDelays ) );",
		"cg_bufferedSoundTimes[0] = nextSoundTime;",
	):
		assert expected in clear_buffered_block

	assert "CG_ClearRewardStack();" in clear_announcements_block
	assert "CG_ClearBufferedSounds();" in clear_announcements_block

	for expected in (
		"if ( !sfx ) {",
		"if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {",
		"cg_bufferedSounds[cg_bufferedSoundHead] = sfx;",
		"cg_bufferedSoundDelays[cg_bufferedSoundHead] = CG_BUFFERED_ANNOUNCER_DELAY;",
		"cg_bufferedSoundHead = ( cg_bufferedSoundHead + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;",
		"if ( cg_bufferedSoundHead == cg_bufferedSoundTail ) {",
		"cg_bufferedSoundTail = ( cg_bufferedSoundTail + 1 ) % CG_BUFFERED_ANNOUNCER_COUNT;",
	):
		assert expected in add_block

	for expected in (
		"if ( cgs.announcerProfile == ANNOUNCER_PROFILE_DISABLED ) {",
		"CG_ClearBufferedSounds();",
		"if ( cg_bufferedSoundTimes[cg_bufferedSoundTail] > cg.time ) {",
		"sfx = cg_bufferedSounds[cg_bufferedSoundTail];",
		"if ( !sfx || cg_bufferedSoundTail == cg_bufferedSoundHead ) {",
		"trap_S_StartLocalSound( sfx, CHAN_ANNOUNCER );",
		"cg_bufferedSoundTimes[nextIndex] = cg_bufferedSoundDelays[cg_bufferedSoundTail] + cg.time;",
		"cg_bufferedSoundTail = nextIndex;",
	):
		assert expected in play_block
