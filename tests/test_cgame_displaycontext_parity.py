"""Guard retail-backed cgame display-context bridge behavior against source drift."""

from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_EFFECTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_effects.c"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SCOREBOARD = REPO_ROOT / "src" / "code" / "cgame" / "cg_scoreboard.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_DRAWTOOLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_drawtools.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_MARKS = REPO_ROOT / "src" / "code" / "cgame" / "cg_marks.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_LOCALENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_localents.c"
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
G_CLIENT = REPO_ROOT / "src" / "code" / "game" / "g_client.c"
QL_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
UI_MAIN = REPO_ROOT / "src" / "code" / "ui" / "ui_main.c"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
UI_SHARED_H = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.h"


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


def test_cgame_display_context_wires_binding_and_execute_hooks() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")

	for expected in (
		"cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;",
		"cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;",
		"cgDC.setBinding = &trap_Key_SetBinding;",
		"cgDC.getBindingBuf = &trap_Key_GetBindingBuf;",
		"cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;",
		"cgDC.executeText = &trap_Cmd_ExecuteText;",
	):
		assert expected in source

	for stale in (
		"//cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;",
		"//cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;",
		"//cgDC.setBinding = &trap_Key_SetBinding;",
		"//cgDC.getBindingBuf = &trap_Key_GetBindingBuf;",
		"//cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;",
		"//cgDC.executeText = &trap_Cmd_ExecuteText;",
	):
		assert stale not in source


def test_cgame_weapon_reload_configstring_bridge_restored() -> None:
	servercmds = CG_SERVERCMDS.read_text(encoding="utf-8")
	weapons = CG_WEAPONS.read_text(encoding="utf-8")

	for expected in (
		"static const weapon_t cg_retailWeaponReloadOrder[] = {",
		"WP_GAUNTLET,",
		"WP_BFG,",
		"WP_HEAVY_MACHINEGUN",
		"static void CG_ParseWeaponReloadConfigString( void ) {",
		"payload = CG_ConfigString( CS_WEAPON_RELOAD_TIMES );",
		"token = COM_ParseExt( &cursor, qfalse );",
		"cg_pmoveSettings.weaponReloadTimes[cg_retailWeaponReloadOrder[i]] = parsed[i];",
		"CG_ParseWeaponReloadConfigString();",
		"} else if ( num == CS_WEAPON_RELOAD_TIMES ) {",
	):
		assert expected in servercmds

	assert "static int CG_GetWeaponReloadTime( weapon_t weapon ) {" in weapons
	assert "railReloadTime = CG_GetWeaponReloadTime( WP_RAILGUN );" in weapons
	assert "f = (float)cg.predictedPlayerState.weaponTime / (float)railReloadTime;" in weapons
	assert "f = (float)cg.predictedPlayerState.weaponTime / 1500;" not in weapons


def test_cgame_weapon_helper_split_restores_retail_view_weapon_and_selection_seam() -> None:
	weapons_source = CG_WEAPONS.read_text(encoding="utf-8")
	rail_block = _block_from_marker(weapons_source, "static void CG_SpawnRailTrail")
	powerup_block = _block_from_marker(weapons_source, "static void CG_AddWeaponWithPowerups")
	cycle_block = _block_from_marker(weapons_source, "static void CG_CycleWeaponSelection")
	highest_block = _block_from_marker(weapons_source, "static void CG_SelectHighestWeapon")
	next_block = _block_from_marker(weapons_source, "void CG_NextWeapon_f( void )")
	prev_block = _block_from_marker(weapons_source, "void CG_PrevWeapon_f( void )")
	out_of_ammo_block = _block_from_marker(weapons_source, "void CG_OutOfAmmoChange( void )")

	assert "static void CG_SpawnRailTrail( centity_t *cent, vec3_t origin ) {" in weapons_source
	for expected in (
		"if ( cent->currentState.weapon != WP_RAILGUN ) {",
		"if ( !cent->pe.railgunFlash ) {",
		"cent->pe.railgunFlash = qfalse;",
		"VectorCopy( origin, start );",
		"VectorCopy( cent->pe.railgunImpact, end );",
		"CG_RailTrail( ci, start, end );",
	):
		assert expected in rail_block
	assert "forcePredicted" not in rail_block
	assert "CG_GetStoredPredictedBeam" not in rail_block

	assert "static void CG_AddWeaponWithPowerups( const centity_t *cent, refEntity_t *gun ) {" in weapons_source
	for expected in (
		"int\t\tpowerups;",
		"powerups = cent->currentState.powerups;",
		"CG_AddWeaponWithPowerups( cent, &gun );",
		"CG_AddWeaponWithPowerups( cent, &barrel );",
		"CG_AddWeaponWithPowerups( cent, &ammo );",
		"CG_SpawnRailTrail( cent, flash.origin );",
	):
		assert expected in weapons_source or expected in powerup_block

	for expected in (
		"if ( !cg.snap ) {",
		"if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {",
		"cg.weaponSelectTime = cg.time;",
		"selected = cg.weaponSelect;",
		"if ( next ) {",
		"selected++;",
		"selected--;",
		"if ( selected == MAX_WEAPONS ) {",
		"selected = WP_NUM_WEAPONS;",
		"if ( selected == WP_GAUNTLET || selected == WP_NUM_WEAPONS ) {",
		"CG_SetWeaponSelect( selected );",
	):
		assert expected in cycle_block

	for expected in (
		"cg.weaponSelectTime = cg.time;",
		"for ( i = MAX_WEAPONS - 1 ; i > 0 ; i-- ) {",
		"if ( i == WP_NUM_WEAPONS ) {",
		"CG_SetWeaponSelect( i );",
	):
		assert expected in highest_block

	assert "CG_CycleWeaponSelection( qtrue );" in next_block
	assert "CG_CycleWeaponSelection( qfalse );" in prev_block
	assert "CG_SelectHighestWeapon();" in out_of_ammo_block


def test_cgame_mark_axis_helper_restores_retail_impact_mark_math_split() -> None:
	marks_source = CG_MARKS.read_text(encoding="utf-8")
	axis_block = _block_from_marker(marks_source, "static void CG_BuildMarkAxis")
	impact_block = _block_from_marker(marks_source, "void CG_ImpactMark")

	for expected in (
		"static void CG_BuildMarkAxis( const vec3_t dir, float orientation, vec3_t axis[3] ) {",
		"VectorNormalize2( dir, axis[0] );",
		"PerpendicularVector( axis[1], axis[0] );",
		"RotatePointAroundVector( axis[2], axis[0], axis[1], orientation );",
		"CrossProduct( axis[0], axis[2], axis[1] );",
	):
		assert expected in axis_block

	assert "CG_BuildMarkAxis( dir, orientation, axis );" in impact_block

	for unexpected in (
		"VectorNormalize2( dir, axis[0] );",
		"PerpendicularVector( axis[1], axis[0] );",
		"RotatePointAroundVector( axis[2], axis[0], axis[1], orientation );",
		"CrossProduct( axis[0], axis[2], axis[1] );",
	):
		assert unexpected not in impact_block


def test_cgame_match_state_auxiliary_configstrings_drive_live_timeout_and_team_count_state() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	reset_block = _block_from_marker(servercmds_source, "static void CG_ResetMatchStateFields( void )")
	parse_timeout_block = _block_from_marker(servercmds_source, "static void CG_ParseTimeoutConfigStrings( void )")
	parse_team_block = _block_from_marker(servercmds_source, "static void CG_ParseTeamCountConfigStrings( void )")
	parse_match_block = _block_from_marker(servercmds_source, "static void CG_ParseMatchState( void )")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues( void )")
	get_timeout_start_block = _block_from_marker(servercmds_source, "int CG_GetMatchTimeoutStartTime( void )")
	match_clock_block = _block_from_marker(event_source, "static int CG_MatchClockMilliseconds( void )")
	match_label_block = _block_from_marker(newdraw_source, "static void CG_BuildMatchStateLabel")

	assert "static int cg_matchTimeoutStartTime;" in servercmds_source
	assert "cg_matchTimeoutStartTime = 0;" in reset_block
	assert "int CG_GetMatchTimeoutStartTime( void );" in local_source
	assert "return cg_matchTimeoutStartTime;" in get_timeout_start_block

	for expected in (
		"info = CG_ConfigString( CS_TIMEOUT_START_TIME );",
		"cg_matchTimeoutStartTime = value;",
		"info = CG_ConfigString( CS_TIMEOUT_EXPIRE_TIME );",
		"cgs.matchTimeoutExpireTime = value;",
		"info = CG_ConfigString( CS_TIMEOUT_COUNT_RED );",
		"info = CG_ConfigString( CS_TIMEOUT_COUNT_BLUE );",
		"value = cgs.matchTimeoutCountPerTeam;",
		"cgs.matchTimeoutRemaining[TEAM_RED] = value;",
		"cgs.matchTimeoutRemaining[TEAM_BLUE] = value;",
	):
		assert expected in parse_timeout_block

	for expected in (
		"info = CG_ConfigString( CS_TEAM_COUNT_RED );",
		"cgs.matchTeamCount[TEAM_RED] = value;",
		"info = CG_ConfigString( CS_TEAM_COUNT_BLUE );",
		"cgs.matchTeamCount[TEAM_BLUE] = value;",
	):
		assert expected in parse_team_block

	assert "CG_ParseMatchFactoryConfig( info );" in parse_match_block
	assert "CG_ParseTimeoutConfigStrings();" in parse_match_block
	assert "CG_ParseTeamCountConfigStrings();" in parse_match_block
	assert "CG_ParseTimeoutConfigStrings();" in set_config_values_block
	assert "CG_ParseTeamCountConfigStrings();" in set_config_values_block
	assert "num == CS_TEAM_COUNT_RED || num == CS_TEAM_COUNT_BLUE" in servercmds_source
	assert "num == CS_TIMEOUT_START_TIME || num == CS_TIMEOUT_EXPIRE_TIME ||" in servercmds_source
	assert "num == CS_TIMEOUT_COUNT_RED || num == CS_TIMEOUT_COUNT_BLUE" in servercmds_source

	assert "timeoutStart = CG_GetMatchTimeoutStartTime();" in match_clock_block
	assert "} else if ( timeoutStart > 0 ) {" in match_clock_block
	assert "timeoutStartTime = CG_GetMatchTimeoutStartTime();" in match_label_block
	assert 'Com_sprintf( buffer, bufferSize, "Timeout %s", CG_GetTeamLabel( cgs.matchTimeoutTeam ) );' in match_label_block


def test_cgame_overtime_ownerdraw_reconstruction_matches_retail_label_family() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	event_source = CG_EVENT.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	scoreboard_source = CG_SCOREBOARD.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
	draw_block = _block_from_marker(newdraw_source, "static void CG_DrawOvertime")
	scoreboard_block = _block_from_marker(scoreboard_source, "static void CG_UpdateHudScoreboardBanners( void )")

	assert "int CG_GetOvertimeCount( void );" in local_source
	assert "int CG_GetOvertimeCount( void ) {" in event_source

	for expected in (
		"overtimeCount = CG_GetOvertimeCount();",
		'Com_sprintf( buffer, sizeof( buffer ), "Overtime x%i", overtimeCount );',
		'Q_strncpyz( buffer, "Overtime", sizeof( buffer ) );',
	):
		assert expected in draw_block
		assert expected in width_block

	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, buffer, 0, 0, textStyle);' in draw_block
	assert "return CG_Text_Width( buffer, scale, 0 );" in width_block
	assert "if ( cgHudScoreboard.overtimeCount > 1 ) {" in scoreboard_block


def test_scoreboard_and_race_server_command_wrappers_match_retail_dispatch() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	compact_block = _block_from_marker(servercmds_source, "static void CG_ParseCompactScores( void )")
	race_info_block = _block_from_marker(servercmds_source, "static void CG_ParseRaceInfo( void )")

	assert 'if ( !strcmp( cmd, "scores" ) ) {' in servercmds_source
	assert "\t\tCG_ParseScores();" in servercmds_source
	assert 'if ( !strcmp( cmd, "smscores" ) ) {' in servercmds_source
	assert "\t\tCG_ParseCompactScores();" in servercmds_source
	assert 'if ( !strcmp( cmd, "tinfo" ) ) {' in servercmds_source
	assert "\t\tCG_ParseTeamInfo();" in servercmds_source
	assert 'if ( !strcmp( cmd, "race_info" ) ) {' in servercmds_source
	assert "\t\tCG_ParseRaceInfo();" in servercmds_source
	assert "CG_ParseRaceInfoCommand" not in servercmds_source

	assert "cg.scores[i].scoreFlags = 0;" in compact_block
	assert "cg.scores[i].activePlayer = atoi( CG_Argv( i * 8 + 9 ) ) ? qtrue : qfalse;" in compact_block
	assert "CG_FinalizeParsedScoreRow( &cg.scores[i], powerups );" in compact_block
	assert "cg.scores[i].scoreFlags = atoi( CG_Argv( i * 8 + 9 ) );" not in compact_block

	for expected in (
		"argc = trap_Argc();",
		"count = atoi( CG_Argv( 1 ) );",
		"cgs.raceLeaderSplitCount = 0;",
		"cgs.raceLeaderSplits[i] = atoi( CG_Argv( i + 2 ) );",
	):
		assert expected in race_info_block


def test_cgame_acc_vertical_overlay_reconstruction_uses_retail_acc_parser_and_sender() -> None:
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	console_source = (REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c").read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	game_source = (REPO_ROOT / "src" / "code" / "game" / "g_cmds.c").read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	parse_block = _block_from_marker(servercmds_source, "static void CG_ParseAcc( void )")
	acc_down_block = _block_from_marker(console_source, "static void CG_AccDown_f( void )")
	acc_up_block = _block_from_marker(console_source, "static void CG_AccUp_f( void )")
	draw_gate_block = _block_from_marker(newdraw_source, "static qboolean CG_ShouldDrawAccVertical( void )")
	draw_weapon_block = _block_from_marker(newdraw_source, "static void CG_DrawWeaponVertical( rectDef_t *rect, vec4_t color )")
	draw_acc_block = _block_from_marker(newdraw_source, "static void CG_DrawAccVertical( rectDef_t *rect, float scale, vec4_t color, int textStyle )")
	source_client_block = _block_from_marker(game_source, "static gclient_t *G_RetailAccuracySourceClient( gentity_t *ent )")
	sender_block = _block_from_marker(game_source, "static void G_SendRetailAccuracyCommand( gentity_t *ent )")
	cmd_acc_block = _block_from_marker(game_source, "void Cmd_Acc_f( gentity_t *ent )")

	for expected in (
		"int\t\t\tweaponAccuracies[WP_NUM_WEAPONS];",
		"qboolean\taccRequestActive;",
		"int\t\t\taccRequestTime;",
	):
		assert expected in local_source

	for expected in (
		"static const weapon_t cg_retailAccuracyCommandOrder[] = {",
		"WP_NONE,",
		"WP_GAUNTLET,",
		"WP_HEAVY_MACHINEGUN",
		"memset( cg.weaponAccuracies, 0, sizeof( cg.weaponAccuracies ) );",
		"weapon = cg_retailAccuracyCommandOrder[i];",
		"value = atoi( CG_Argv( i + 1 ) );",
		"cg.weaponAccuracies[weapon] = value;",
	):
		assert expected in servercmds_source

	assert 'if ( !strcmp( cmd, "acc" ) ) {' in servercmds_source
	assert "\t\tCG_ParseAcc();" in servercmds_source

	assert '"+acc"' in console_source
	assert '"-acc"' in console_source
	assert 'trap_AddCommand ("acc");' in console_source
	assert "cg.accRequestActive = qtrue;" in acc_down_block
	assert "cg.accRequestTime = 0;" in acc_down_block
	assert 'trap_SendClientCommand( "acc" );' in acc_down_block
	assert "cg.accRequestActive = qfalse;" in acc_up_block

	for expected in (
		"static const weapon_t cgVerticalAccWeaponOrder[] = {",
		"WP_MACHINEGUN,",
		"WP_BFG,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in newdraw_source

	assert "if ( !cg.accRequestActive || !cg.snap ) {" in draw_gate_block
	assert "cg.snap->ps.pm_type == PM_SPECTATOR" in draw_gate_block
	assert "cg.snap->ps.pm_flags & PMF_FOLLOW" in draw_gate_block
	assert 'trap_SendClientCommand( "acc" );' in draw_gate_block

	assert "icon = CG_GetStartingWeaponIconHandle( cgVerticalAccWeaponOrder[i] );" in draw_weapon_block
	assert "CG_DrawPic( rect->x, rect->y + rect->h * i, rect->w, rect->w, icon );" in draw_weapon_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i%%", cg.weaponAccuracies[weapon] );' in draw_acc_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h * ( i + 1 ), scale, color, buffer, 0, 0, textStyle );" in draw_acc_block

	assert "case CG_WP_VERTICAL:" in newdraw_source
	assert "CG_DrawWeaponVertical( &rect, color );" in newdraw_source
	assert "case CG_ACC_VERTICAL:" in newdraw_source
	assert "CG_DrawAccVertical( &rect, scale, color, textStyle );" in newdraw_source

	for expected in (
		"static const weapon_t retailAccuracyCommandOrder[] = {",
		"WP_NONE,",
		"WP_GAUNTLET,",
		"WP_HEAVY_MACHINEGUN",
	):
		assert expected in game_source

	assert "ent->client->sess.sessionTeam == TEAM_SPECTATOR" in source_client_block
	assert "ent->client->sess.spectatorState == SPECTATOR_FOLLOW" in source_client_block
	assert "ent->client->sess.spectatorClient" in source_client_block
	assert "level.clients[clientNum].pers.connected == CON_CONNECTED" in source_client_block

	assert "client = G_RetailAccuracySourceClient( ent );" in sender_block
	assert "client->pers.accuracy_hits[weapon]" in sender_block
	assert "client->pers.accuracy_shots[weapon]" in sender_block
	assert 'trap_SendServerCommand( ent-g_entities, va( "acc %s", payload ) );' in sender_block
	assert "G_SendRetailAccuracyCommand( ent );" in cmd_acc_block


def test_cgame_placement_scorebox_widgets_match_retail_split_ownerdraws() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	slot_block = _block_from_marker(source, "static int CG_GetSpectatorOwnerDrawSlot")
	flag_shader_block = _block_from_marker(source, "static qhandle_t CG_GetPlacementFlagShader")
	flag_block = _block_from_marker(source, "static void CG_DrawPlacementFlagOwnerDraw")
	avatar_block = _block_from_marker(source, "static void CG_DrawPlacementAvatarOwnerDraw")
	frags_block = _block_from_marker(source, "static qboolean CG_DrawPlacementFragsOwnerDraw")
	deaths_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDeathsOwnerDraw")
	damage_block = _block_from_marker(source, "static qboolean CG_DrawPlacementDamageOwnerDraw")
	wins_block = _block_from_marker(source, "static qboolean CG_DrawPlacementWinsOwnerDraw")
	build_metric_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")
	draw_metric_block = _block_from_marker(source, "static qboolean CG_DrawPlacementMetricOwnerDraw")

	for expected in (
		"case CG_1ST_PLYR_HEALTH_ARMOR:",
		"case CG_2ND_PLYR_HEALTH_ARMOR:",
		"case CG_SPEC_COMPARE_PRIMARY:",
		"case CG_SPEC_COMPARE_SECONDARY:",
	):
		assert expected in slot_block

	assert "ci->countryFlagShader ? ci->countryFlagShader : CG_RegisterCountryFlag( ci->country );" in flag_shader_block
	assert "PW_REDFLAG" not in flag_shader_block
	assert "PW_BLUEFLAG" not in flag_shader_block
	assert "PW_NEUTRALFLAG" not in flag_shader_block

	assert "CG_GetPlacementFlagShader( slot );" in flag_block
	assert "CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );" in flag_block
	assert "CG_DrawSpectatorProfileImage( rect, slot );" in avatar_block

	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", CG_GetPlacementFragCount( score ) );' in frags_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", score->deaths );' in deaths_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", score->damage );' in damage_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%i", ci->wins );' in wins_block

	assert "case CG_1ST_PLYR_FLAG:" in build_metric_block
	assert 'Q_strncpyz( buffer, hasFlag ? "Yes" : "-", bufferSize );' not in source

	for expected in (
		"case CG_1ST_PLYR_FRAGS:",
		"return CG_DrawPlacementFragsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_DEATHS:",
		"return CG_DrawPlacementDeathsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_DMG:",
		"return CG_DrawPlacementDamageOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_WINS:",
		"return CG_DrawPlacementWinsOwnerDraw( rect, scale, color, textStyle, slot );",
		"case CG_1ST_PLYR_FLAG:",
		"CG_DrawPlacementFlagOwnerDraw( rect, slot );",
	):
		assert expected in draw_metric_block

	assert "case CG_1ST_PLYR_HEALTH_ARMOR:" in source
	assert "CG_DrawSpectatorComparison( &rect, scale, color, textStyle, ownerDraw );" in source
	assert "case CG_1ST_PLYR_AVATAR:" in source
	assert "CG_DrawPlacementAvatarOwnerDraw( &rect, 0 );" in source
	assert "case CG_2ND_PLYR_AVATAR:" in source
	assert "CG_DrawPlacementAvatarOwnerDraw( &rect, 1 );" in source


def test_cgame_country_flag_cache_restores_retail_player_configstring_transport() -> None:
	cg_main = CG_MAIN.read_text(encoding="utf-8")
	cg_players = CG_PLAYERS.read_text(encoding="utf-8")
	cg_local = CG_LOCAL.read_text(encoding="utf-8")
	g_client = G_CLIENT.read_text(encoding="utf-8")
	init_block = _block_from_marker(cg_main, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	cache_block = _block_from_marker(cg_main, "static void CG_CacheCountryFlags( void )")
	register_block = _block_from_marker(cg_main, "qhandle_t CG_RegisterCountryFlag( const char *countryCode )")
	new_client_block = _block_from_marker(cg_players, "void CG_NewClientInfo( int clientNum )")

	assert "country[MAX_COUNTRY_CODE]" in cg_local
	assert "countryFlagShader;" in cg_local

	for expected in (
		"ui/assets/flags/none.tga",
		"ui/country.txt",
		"ERROR: CG_CacheCountryFlags: %s too small\\n",
		"ERROR: CG_CacheCountryFlags: %s too large. Size is %d, limit is %d\\n",
		"trap_FS_FOpenFile( filename, &f, FS_READ );",
		"trap_FS_Read( buffer, len, f );",
		"token = COM_Parse( &text_p );",
		"CG_RegisterCountryFlag( token );",
	):
		assert expected in cache_block

	for expected in (
		'Com_sprintf( filename, sizeof( filename ), "ui/assets/flags/%s.tga", normalized );',
		'trap_R_RegisterShaderNoMip( "ui/assets/flags/none.tga" );',
		"Q_strlwr( normalized );",
	):
		assert expected in register_block

	assert init_block.index("CG_ParseServerinfo();") < init_block.index("CG_CacheCountryFlags();") < init_block.index("CG_InitDisplayContext();")
	assert 'Info_ValueForKey( configstring, "country" );' in new_client_block
	assert "newInfo.countryFlagShader = CG_RegisterCountryFlag( newInfo.country );" in new_client_block
	assert 'Info_ValueForKey( userinfo, "country" )' in g_client
	assert g_client.count(r"\\country\\%s") >= 2


def test_cgame_live_placement_and_follow_ownerdraws_follow_retail_helper_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	first_place_block = _block_from_marker(source, "static void CG_Draw1stPlace(")
	second_place_block = _block_from_marker(source, "static void CG_Draw2ndPlace(")
	value_block = _block_from_marker(source, "static qboolean CG_BuildPlacementScoreValue")
	line_block = _block_from_marker(source, "static void CG_DrawPlacementScoreLine")
	first_score_block = _block_from_marker(source, "static void CG_Draw1stPlaceScore")
	second_score_block = _block_from_marker(source, "static void CG_Draw2ndPlaceScore")
	follow_block = _block_from_marker(source, "static void CG_DrawFollowPlayerNameEx")

	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores1),0, 0, textStyle);' in first_place_block
	assert 'CG_Text_Paint(rect->x, rect->y, scale, color, va("%2i", cgs.scores2),0, 0, textStyle);' in second_place_block

	for expected in (
		"if ( cgs.gametype == GT_RACE ) {",
		"CG_RaceFormatMilliseconds( value, buffer, bufferSize );",
		'Q_strncpyz( buffer, "-", bufferSize );',
		'Com_sprintf( buffer, bufferSize, "%d", value );',
	):
		assert expected in value_block

	for expected in (
		"CG_Text_Paint_Limit( &maxX, x, rect->y, scale, color, nameText, 0, 0 );",
		'CG_Text_Paint( ellipsisX, rect->y, scale, color, "...", 0, 0, textStyle );',
		"CG_Text_Paint( valueX, rect->y, scale, color, valueText, 0, 0, textStyle );",
	):
		assert expected in line_block

	for expected in (
		"CG_GetActiveScoreByIndex( 0 );",
		'CG_DrawPlacementScoreLine( rect, scale, color, textStyle, "1. ", nameBuffer, valueBuffer );',
		"CG_GetTeamName( leaderTeam )",
	):
		assert expected in first_score_block

	for expected in (
		"score = CG_GetScoreForClientNum( cg.snap->ps.clientNum );",
		"score = CG_GetActiveScoreByIndex( 1 );",
		'Com_sprintf( rankBuffer, sizeof( rankBuffer ), "%d. ", localRank );',
		"CG_DrawPlacementScoreLine( rect, scale, color, textStyle, rankBuffer, nameBuffer, valueBuffer );",
	):
		assert expected in second_score_block

	for expected in (
		"if ( ownerDraw == CG_FOLLOW_PLAYER_NAME ) {",
		'"Following - %s"',
		"Q_strncpyz( buffer, ci->name, sizeof( buffer ) );",
		"Vector4Copy( CG_TeamColor( ci->team ), drawColor );",
		"if ( align == ITEM_ALIGN_CENTER ) {",
		"} else if ( align == ITEM_ALIGN_RIGHT ) {",
	):
		assert expected in follow_block

	assert "case CG_1ST_PLACE_SCORE:" in source
	assert "CG_Draw1stPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_2ND_PLACE_SCORE:" in source
	assert "CG_Draw2ndPlaceScore(&rect, scale, color, textStyle);" in source
	assert "case CG_FOLLOW_PLAYER_NAME:" in source
	assert "CG_DrawFollowPlayerNameEx(&rect, scale, color, textStyle, ownerDraw, align);" in source
	assert "case CG_FOLLOW_PLAYER_NAME_EX:" in source


def test_cgame_objective_ownerdraws_restore_retail_flag_key_and_powerup_seam() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	harvester_block = _block_from_marker(source, "static void CG_HarvesterSkulls")
	oneflag_block = _block_from_marker(source, "static void CG_OneFlagStatus")
	powerup_block = _block_from_marker(source, "static void CG_DrawCTFPowerUp")
	key_block = _block_from_marker(source, "static void CG_DrawPlayerHasKey")
	flag_block = _block_from_marker(source, "static void CG_DrawPlayerHasFlag")

	assert "int value = cg.snap->ps.generic1;" in harvester_block
	assert "value = cg.snap->ps.stats[STAT_PERSISTANT_POWERUP];" in powerup_block
	assert "x += rect->w * 0.5f;" in key_block
	assert "x += rect->w * 0.65f;" not in key_block

	for expected in (
		"shaderIndex = 0;",
		"case FLAG_TAKEN_RED:",
		"shaderIndex = 1;",
		"case FLAG_TAKEN_BLUE:",
		"shaderIndex = 2;",
		"case FLAG_DROPPED:",
		"shaderIndex = 3;",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, cgs.media.flagShader[shaderIndex] );",
	):
		assert expected in oneflag_block

	assert "cgs.media.flagShaders[index]" not in oneflag_block

	for expected in (
		"inset = force2D ? 0.0f : 4.0f;",
		'key = trap_Key_GetKey( "dropflag" );',
		'trap_Key_KeynumToStringBuf( key, keyName, sizeof( keyName ) );',
		'Q_strupr( keyName );',
		'Com_sprintf( prompt, sizeof( prompt ), "Press %s to throw.", keyName );',
		'CG_Text_Paint( promptX, rect->y + rect->h, promptScale, promptColor, prompt, 0, 0, 3 );',
	):
		assert expected in flag_block

	for expected in (
		"case CG_ONEFLAG_STATUS:",
		"CG_OneFlagStatus(&rect);",
		"case CG_CTF_POWERUP:",
		"CG_DrawCTFPowerUp(&rect);",
		"case CG_PLAYER_HASFLAG:",
		"CG_DrawPlayerHasFlag(&rect, qfalse);",
		"case CG_PLAYER_HASFLAG2D:",
		"CG_DrawPlayerHasFlag(&rect, qtrue);",
		"case CG_PLAYER_HASKEY:",
		"CG_DrawPlayerHasKey( &rect );",
	):
		assert expected in source


def test_cgame_classic_player_status_ownerdraws_follow_retail_leaf_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	health_range_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBarRange")
	health_100_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar100")
	health_200_block = _block_from_marker(source, "static void CG_DrawPlayerHealthBar200")
	armor_range_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBarRange")
	armor_100_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar100")
	armor_200_block = _block_from_marker(source, "static void CG_DrawPlayerArmorBar200")
	armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
	armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
	ammo_icon_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoIcon")
	ammo_value_block = _block_from_marker(source, "static void CG_DrawPlayerAmmoValue")
	head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
	tiered_block = _block_from_marker(source, "static void CG_DrawArmorTieredColorized")

	for expected in (
		"ratio = use200Range ? CG_NormalizedTo200( health ) : CG_NormalizedTo100( health );",
		"shader = use200Range ? cgs.media.healthBar200 : cgs.media.healthBar100;",
		"CG_DrawBarFill( rect, shader, ratio, barColor );",
	):
		assert expected in health_range_block

	assert "CG_DrawPlayerHealthBarRange( rect, shader, qfalse );" in health_100_block
	assert "CG_DrawPlayerHealthBarRange( rect, shader, qtrue );" in health_200_block

	for expected in (
		"CG_GetArmorTierColor( armor, barColor );",
		"ratio = use200Range ? CG_NormalizedTo200( armor ) : CG_NormalizedTo100( armor );",
		"shader = use200Range ? cgs.media.armorBar200 : cgs.media.armorBar100;",
	):
		assert expected in armor_range_block

	assert "CG_DrawPlayerArmorBarRange( rect, shader, qfalse );" in armor_100_block
	assert "CG_DrawPlayerArmorBarRange( rect, shader, qtrue );" in armor_200_block

	for expected in (
		"cgs.media.armorIcon",
		"cgs.media.armorModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cgs.media.armorModel, 0, origin, angles );",
	):
		assert expected in armor_icon_block

	assert "value = ps->stats[STAT_ARMOR];" in armor_value_block

	for expected in (
		"cg_weapons[ cg.predictedPlayerState.weapon ].ammoIcon",
		"cg_weapons[ cent->currentState.weapon ].ammoModel",
		"CG_Draw3DModel( rect->x, rect->y, rect->w, rect->h, cg_weapons[ cent->currentState.weapon ].ammoModel, 0, origin, angles );",
	):
		assert expected in ammo_icon_block

	assert "value = ps->ammo[cent->currentState.weapon];" in ammo_value_block
	assert "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );" in head_block

	for expected in (
		"CG_GetArmorTierColor( cg.snap->ps.stats[STAT_ARMOR], color );",
		"color[3] = 0.5f;",
		"CG_FillRect( rect->x, rect->y, rect->w, rect->h, color );",
	):
		assert expected in tiered_block

	for expected in (
		"case CG_PLAYER_ARMOR_BAR_100:",
		"CG_DrawPlayerArmorBar100( &rect, shader );",
		"case CG_PLAYER_ARMOR_BAR_200:",
		"CG_DrawPlayerArmorBar200( &rect, shader );",
		"case CG_PLAYER_HEALTH_BAR_100:",
		"CG_DrawPlayerHealthBar100( &rect, shader );",
		"case CG_PLAYER_HEALTH_BAR_200:",
		"CG_DrawPlayerHealthBar200( &rect, shader );",
		"case CG_PLAYER_ARMOR_ICON:",
		"CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_ARMOR_VALUE:",
		"CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle );",
		"case CG_PLAYER_AMMO_ICON:",
		"CG_DrawPlayerAmmoIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_AMMO_VALUE:",
		"CG_DrawPlayerAmmoValue( &rect, scale, color, shader, textStyle );",
		"case CG_PLAYER_HEAD:",
		"CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );",
		"case CG_PLAYER_HEALTH:",
		"CG_DrawPlayerHealth( &rect, scale, color, shader, textStyle );",
	):
		assert expected in source


def test_cgame_team_score_name_playercount_and_match_phase_ownerdraws_follow_retail_shared_leaves() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	align_block = _block_from_marker(source, "static float CG_AlignTextInRectX")
	score_text_block = _block_from_marker(source, "static qboolean CG_BuildTeamScoreText")
	score_block = _block_from_marker(source, "static void CG_DrawTeamScore")
	name_block = _block_from_marker(source, "static void CG_DrawTeamName")
	player_count_block = _block_from_marker(source, "static void CG_DrawTeamPlayerCount")
	match_phase_block = _block_from_marker(source, "static const char *CG_GetMatchPhaseText")
	match_status_block = _block_from_marker(source, "static const char *CG_GetMatchStatusText")
	match_state_block = _block_from_marker(source, "static void CG_DrawMatchState")

	for expected in (
		"if ( align == ITEM_ALIGN_CENTER ) {",
		"if ( align == ITEM_ALIGN_RIGHT ) {",
		"return rect->x;",
	):
		assert expected in align_block

	for expected in (
		"score = ( team == TEAM_RED ) ? cgs.scores1 : cgs.scores2;",
		"if ( score == SCORE_NOT_PRESENT || score == CG_SCORE_FORFEIT ) {",
		'Q_strncpyz( buffer, "-", bufferSize );',
		'Com_sprintf( buffer, bufferSize, "%i", score );',
	):
		assert expected in score_text_block

	for expected in (
		"CG_TranslateHudRectForWidescreen( rect, &widescreenRect );",
		"x = CG_AlignTextInRectX( &widescreenRect, scale, buffer, align );",
		"CG_Text_Paint( x, widescreenRect.y + widescreenRect.h, scale, color, buffer, 0, 0, textStyle );",
	):
		assert expected in score_block

	for expected in (
		"teamName = CG_GetTeamName( team );",
		"x = CG_AlignTextInRectX( &widescreenRect, scale, teamName, align );",
	):
		assert expected in name_block

	for expected in (
		"teamLimit = cgs.playerCountTeamSize;",
		"case GT_TEAM:",
		'Com_sprintf( buffer, sizeof( buffer ), "(%d/%d)", count, teamLimit );',
		'Com_sprintf( buffer, sizeof( buffer ), "(%d)", count );',
		"if ( teamLimit > 0 && teamLimit * 2 <= cgs.maxclients ) {",
		'Com_sprintf( buffer, sizeof( buffer ), "%d/%d Players", count, teamLimit );',
		'Com_sprintf( buffer, sizeof( buffer ), "%d Player%s", count, ( count == 1 ) ? "" : "s" );',
		"x = CG_AlignTextInRectX( rect, scale, buffer, align );",
	):
		assert expected in player_count_block

	for expected in (
		'return "MATCH SUMMARY";',
		'return "MATCH WARMUP";',
		'return "MATCH IN PROGRESS";',
	):
		assert expected in match_phase_block

	assert "phase = CG_GetMatchPhaseText();" in match_status_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state_block

	for expected in (
		"case CG_RED_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_BLUE_SCORE:",
		"CG_DrawTeamScore( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_RED_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_RED, align);",
		"case CG_BLUE_PLAYER_COUNT:",
		"CG_DrawTeamPlayerCount(&rect, scale, color, textStyle, TEAM_BLUE, align);",
		"case CG_RED_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_RED, align );",
		"case CG_BLUE_NAME:",
		"CG_DrawTeamName( &rect, scale, color, textStyle, TEAM_BLUE, align );",
		"case CG_MATCH_STATE:",
		"CG_DrawMatchState(&rect, scale, color, textStyle);",
	):
		assert expected in source

	assert "static void CG_DrawRedScore" not in source
	assert "static void CG_DrawBlueScore" not in source
	assert "static void CG_DrawRedName" not in source
	assert "static void CG_DrawBlueName" not in source


def test_cgame_intro_panel_and_player_count_widgets_restore_retail_detail_and_cap_rules() -> None:
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	player_limit_block = _block_from_marker(newdraw_source, "static int CG_GetConfiguredPlayerCountLimit")
	player_counts_block = _block_from_marker(newdraw_source, "static void CG_DrawPlayerCounts")
	location_block = _block_from_marker(newdraw_source, "static void CG_GetServerLocation")
	detail_block = _block_from_marker(newdraw_source, "static void CG_BuildIntroPanelDetailString")
	game_type_map_block = _block_from_marker(newdraw_source, "static void CG_DrawGameTypeMap")
	match_details_block = _block_from_marker(newdraw_source, "static void CG_DrawMatchDetails")
	parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")

	assert "playerCountTeamSize;" in local_source

	for expected in (
		"playerLimit = cgs.maxclients;",
		"if ( cgs.gametype == GT_FFA || cgs.playerCountTeamSize <= 0 ) {",
		"playerLimit = cgs.playerCountTeamSize * 2;",
		"if ( playerLimit > cgs.maxclients ) {",
		"return cgs.playerCountTeamSize;",
	):
		assert expected in player_limit_block

	for expected in (
		"active = CG_CountActivePlayers();",
		"playerLimit = CG_GetConfiguredPlayerCountLimit();",
		"if ( playerLimit <= 0 ) {",
		'Com_sprintf( buffer, sizeof( buffer ), "%i/%i Players", active, playerLimit );',
	):
		assert expected in player_counts_block

	for expected in (
		'CG_GetServerInfoValue( info, "location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "sv_location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "server_location", buffer, bufferSize );',
		'CG_GetServerInfoValue( info, "sv_hostname", buffer, bufferSize );',
	):
		assert expected in location_block

	for expected in (
		"CG_GetMapDisplayName( mapName, sizeof( mapName ) );",
		"CG_GetServerLocation( location, sizeof( location ) );",
		'Com_sprintf( buffer, bufferSize, "%s - %s", location, mapName );',
		'Q_strncpyz( buffer, mapName, bufferSize );',
	):
		assert expected in detail_block

	assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in game_type_map_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GameTypeString(), detailBuffer );' in game_type_map_block
	assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in match_details_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s - %s",' in match_details_block

	for expected in (
		'playerCountTeamSizeValue = Info_ValueForKey( info, "teamsize" );',
		'playerCountTeamSizeValue = Info_ValueForKey( info, "g_teamSizeMin" );',
		"cgs.playerCountTeamSize = playerCountTeamSizeValue[0] ? atoi( playerCountTeamSizeValue ) : 0;",
		"if ( cgs.playerCountTeamSize < 0 ) {",
	):
		assert expected in parse_serverinfo_block


def test_cgame_hud_ownerdraw_reconstruction_keeps_retail_medal_spectator_advert_and_team_pickup_seam() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	syscalls_source = CG_SYSCALLS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	client_source = CL_CGAME.read_text(encoding="utf-8")
	build_spectator_block = _block_from_marker(main_source, "void CG_BuildSpectatorString()")
	speedometer_block = _block_from_marker(newdraw_source, "static void CG_DrawSpeedometerOwnerDraw")
	spectator_block = _block_from_marker(newdraw_source, "void CG_DrawTeamSpectators")
	advert_block = _block_from_marker(newdraw_source, "static void CG_DrawAdvert")
	medal_block = _block_from_marker(newdraw_source, "void CG_DrawMedal")
	team_pickup_block = _block_from_marker(newdraw_source, "static void CG_DrawTeamPickupOwnerDraw")
	syscall_block = _block_from_marker(syscalls_source, "void trap_QL_UpdateAdvert")
	client_block = _block_from_marker(client_source, "static void QDECL QL_CG_trap_UpdateAdvert")

	for expected in (
		"cg.spectatorOffset = 0;",
		"cg.spectatorPaintX = 0;",
		"cg.spectatorPaintX2 = 0;",
		"cg.spectatorPaintLen = 0;",
		"cg.spectatorTime = 0;",
	):
		assert expected in build_spectator_block

	assert "CG_DrawSpeedometer( rect, scale, color, textStyle );" in speedometer_block

	for expected in (
		"cg.spectatorOffset < 0 || cg.spectatorOffset >= cg.spectatorEntryCount",
		"entry = cg.spectatorEntries[i];",
		"pendingWidth += 10;",
		"CG_Text_Paint( x, y, scale, color, entry, 0, 0, 0 );",
		"cg.spectatorTime = cg.time + 4000;",
		"cg.spectatorOffset = startIndex + displayedCount;",
	):
		assert expected in spectator_block
	assert "CG_UpdateSpectatorTargets();" not in spectator_block

	for expected in (
		"trap_R_SetColor( color );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
		"pixelArea = (int)( rect->w * rect->h );",
		"trap_QL_UpdateAdvert( shader, pixelArea );",
		"trap_R_SetColor( NULL );",
	):
		assert expected in advert_block

	for expected in (
		"case CG_ACCURACY:",
		'text = va("%i%%", (int)value);',
		'text = "Wow";',
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, shader );",
	):
		assert expected in medal_block

	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );" in team_pickup_block

	assert "case CG_SPECTATORS:" in newdraw_source
	assert "CG_DrawTeamSpectators(&rect, scale, color, shader);" in newdraw_source
	assert "case UI_ADVERT:" in newdraw_source
	assert "CG_DrawAdvert( &rect, color, shader );" in newdraw_source
	assert "case CG_SPEEDOMETER:" in newdraw_source
	assert "CG_DrawSpeedometerOwnerDraw( &rect, scale, color, textStyle );" in newdraw_source

	assert "CG_QL_IMPORT_UPDATE_ADVERT = 58," in public_source
	assert "void\t\ttrap_QL_UpdateAdvert( int handleOrToken, int area );" in local_source
	assert "cg_imports[CG_QL_IMPORT_UPDATE_ADVERT]" in syscall_block
	assert "(void)handleOrToken;" in client_block
	assert "(void)area;" in client_block
	assert "ql_cgame_imports[CG_QL_IMPORT_UPDATE_ADVERT] = (ql_import_f)QL_CG_trap_UpdateAdvert;" in client_source


def test_cgame_spectator_cache_restores_retail_queue_metadata_and_cached_strip() -> None:
	players_source = CG_PLAYERS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	parse_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")
	compare_block = _block_from_marker(main_source, "static int QDECL CG_CompareSpectatorClients")
	build_block = _block_from_marker(main_source, "void CG_BuildSpectatorString()")
	draw_block = _block_from_marker(newdraw_source, "void CG_DrawTeamSpectators")

	for expected in (
		"qboolean\t\tspectateOnly;",
		"int\t\t\t\tspectatorQueuePosition;",
		"char\t\t\tspectatorEntries[MAX_CLIENTS][64];",
		"int\t\t\t\tspectatorEntryCount;",
	):
		assert expected in local_source

	for expected in (
		'v = Info_ValueForKey( configstring, "so" );',
		"newInfo.spectateOnly = atoi( v );",
		'v = Info_ValueForKey( configstring, "pq" );',
		"newInfo.spectatorQueuePosition = atoi( v );",
	):
		assert expected in parse_block

	for expected in (
		"clientA->spectateOnly > clientB->spectateOnly",
		"clientA->spectatorQueuePosition > clientB->spectatorQueuePosition",
		"return clientNumA - clientNumB;",
	):
		assert expected in compare_block

	for expected in (
		"qsort( spectatorClients, newEntryCount, sizeof( spectatorClients[0] ), CG_CompareSpectatorClients );",
		"Q_CleanStr( cleanName );",
		'Com_sprintf( entry, sizeof( entry ), "^7(^5s^7) %s", cleanName );',
		'Com_sprintf( entry, sizeof( entry ), "(%d) %s", ci->spectatorQueuePosition, cleanName );',
		"memcpy( cg.spectatorEntries, newSpectatorEntries, sizeof( cg.spectatorEntries ) );",
		"cg.spectatorEntryCount = newEntryCount;",
	):
		assert expected in build_block

	for expected in (
		"cg.spectatorEntryCount <= 0",
		"entry = cg.spectatorEntries[i];",
		"entry = cg.spectatorEntries[startIndex + i];",
		"cg.spectatorEntryCount > displayedCount",
	):
		assert expected in draw_block

	assert "CG_UpdateSpectatorTargets();" not in draw_block


def test_cgame_team_scoreboard_and_award_ownerdraws_follow_retail_helper_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	average_ping_block = _block_from_marker(source, "static void CG_DrawTeamAveragePing")
	timeheld_build_block = _block_from_marker(source, "static qboolean CG_BuildTeamTimeHeldText")
	timeheld_block = _block_from_marker(source, "static void CG_DrawTeamTimeHeldOwnerDraw")
	award_client_block = _block_from_marker(source, "static int CG_GetAwardClientNum")
	award_player_block = _block_from_marker(source, "static qboolean CG_DrawAwardPlayer")

	assert 'Com_sprintf( buffer, sizeof( buffer ), "Avg ping %i", average );' in average_ping_block
	assert "if ( !CG_IsTeamTimeHeldOwnerDraw( ownerDraw ) ) {" in timeheld_build_block
	assert 'Com_sprintf( buffer, bufferSize, "%i:%i%i", value / 60, ( value % 60 ) / 10, value % 10 );' in timeheld_build_block
	assert "CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );" in timeheld_block

	assert "score = CG_FindAwardScore( ownerDraw );" in award_client_block
	assert "if ( !CG_IsAwardOwnerDraw( ownerDraw ) ) {" in award_player_block
	assert "clientNum = CG_GetAwardClientNum( ownerDraw );" in award_player_block
	assert "CG_DrawProfileModel( rect, clientNum, qtrue );" in award_player_block

	assert "if ( CG_DrawAwardPlayer( &rect, ownerDraw ) ) {" in source
	assert "case CG_RED_AVG_PING:" in source
	assert "CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_RED);" in source
	assert "case CG_BLUE_AVG_PING:" in source
	assert "CG_DrawTeamAveragePing(&rect, scale, color, textStyle, TEAM_BLUE);" in source
	assert "case CG_RED_TEAM_TIMEHELD_QUAD:" in source
	assert "case CG_BLUE_TEAM_TIMEHELD_INVIS:" in source
	assert "CG_DrawTeamTimeHeldOwnerDraw( &rect, scale, color, textStyle, ownerDraw );" in source


def test_register_cvars_publishes_retail_version_and_vote_reset() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_RegisterCvars")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")

	assert 'trap_Cvar_Register(NULL, "cg_version", Q3_VERSION, CVAR_ROM );' in block
	assert 'trap_Cvar_Set( "ui_voteactive", "0" );' in block
	assert "cgs.newHud = cg.competitiveHudLoaded;" in load_hud_block


def test_register_sounds_prefers_retail_announcer_folders_before_fallbacks() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	folder_block = _block_from_marker(source, "static const char *CG_RetailAnnouncerFolderForProfile")
	retail_clip_block = _block_from_marker(source, "static sfxHandle_t CG_RegisterRetailAnnouncerClip")
	voice_set_block = _block_from_marker(source, "static void CG_RegisterAnnouncerVoiceSet")
	argv_block = _block_from_marker(source, "const char *CG_Argv")
	error_block = _block_from_marker(source, "void QDECL CG_Error")

	assert 'return "vo";' in folder_block
	assert 'return "vo_evil";' in folder_block
	assert 'return "vo_female";' in folder_block
	assert 'Com_sprintf( path, sizeof( path ), "sound/%s/%s%s", folder, sample, exts[i] );' in retail_clip_block
	assert "#define CG_REGISTER_ANNOUNCER_SAMPLE(field, sample)" in voice_set_block
	assert "set->field = CG_RegisterRetailAnnouncerClip( profile, sample );" in voice_set_block
	assert "set->field = CG_RegisterAnnouncerClip( folder, sample );" in voice_set_block
	assert 'CG_REGISTER_ANNOUNCER_SAMPLE( oneMinuteSound, "1_minute" );' in voice_set_block
	assert 'CG_REGISTER_ANNOUNCER_SAMPLE( threeFragSound, "3_frags" );' in voice_set_block
	assert "trap_Argv( arg, buffer, sizeof( buffer ) );" in argv_block
	assert "trap_Error( text );" in error_block


def test_display_context_print_and_error_bridges_use_retail_direct_trap_wrappers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	com_error_block = _block_from_marker(source, "void QDECL Com_Error")
	com_printf_block = _block_from_marker(source, "void QDECL Com_Printf")

	assert "(void)level;" in com_error_block
	assert "trap_Error( text );" in com_error_block
	assert "CG_Error( \"%s\", text);" not in com_error_block

	assert "trap_Print( text );" in com_printf_block
	assert "CG_Printf (\"%s\", text);" not in com_printf_block


def test_cgame_browser_runtime_wrappers_drive_hud_reload_and_score_feeders() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	console_source = (REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c").read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	init_block = _block_from_marker(main_source, "void CG_InitBrowserRuntime")
	reset_block = _block_from_marker(main_source, "void CG_ResetBrowserOverlayState")
	feeder_block = _block_from_marker(main_source, "void CG_SetBrowserFeederSelection")
	load_menus_block = _block_from_marker(main_source, "void CG_LoadMenus")
	score_block = _block_from_marker(main_source, "void CG_SetScoreSelection")
	load_hud_cmd_block = _block_from_marker(console_source, "static void CG_LoadHud_f")
	cgame_init_block = _block_from_marker(main_source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")

	assert "void CG_InitBrowserRuntime( void );" in local_source
	assert "void CG_ResetBrowserOverlayState( void );" in local_source
	assert "void CG_SetBrowserFeederSelection( void *overlay, int feeder, int index );" in local_source

	assert "String_Init();" in init_block
	assert "Menu_Reset();" in reset_block
	assert "menuScoreboard = NULL;" in reset_block
	assert "Menu_SetFeederSelection( (menuDef_t *)overlay, feeder, index, NULL );" in feeder_block

	assert "CG_ResetBrowserOverlayState();" in load_menus_block
	assert "Menu_Reset();" not in load_menus_block
	assert "CG_SetBrowserFeederSelection( menu, feeder, cg.selectedScore );" in score_block
	assert "CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );" in score_block
	assert "Menu_SetFeederSelection(menu, feeder, i, NULL);" not in score_block
	assert "Menu_SetFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore, NULL);" not in score_block

	assert "CG_InitBrowserRuntime();" in load_hud_cmd_block
	assert "String_Init();" not in load_hud_cmd_block
	assert "Menu_Reset();" not in load_hud_cmd_block
	assert "menuScoreboard = NULL;" not in load_hud_cmd_block

	assert "CG_InitBrowserRuntime();" in cgame_init_block


def test_cgame_menu_parser_and_score_selection_restore_retail_parser_and_cursor_seam() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	score_block = _block_from_marker(source, "void CG_SetScoreSelection")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")

	for expected in (
		'handle = trap_PC_LoadSource("ui/testhud.menu");',
		'if (Q_stricmp(token.string, "assetGlobalDef") == 0) {',
		"if (CG_Asset_Parse(handle)) {",
		'if (Q_stricmp(token.string, "menudef") == 0) {',
		"Menu_New(handle);",
	):
		assert expected in source

	for expected in (
		"token = COM_ParseExt(p, qtrue);",
		"if (token[0] != '{') {",
		'if (Q_stricmp(token, "}") == 0) {',
		"CG_ParseMenu(token);",
	):
		assert expected in source

	for expected in (
		"if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores ) {",
		"CG_SetBrowserFeederSelection( menu, feeder, cg.selectedScore );",
		"CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );",
	):
		assert expected in score_block

	for expected in (
		"if ( index == -1 ) {",
		"if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {",
		"selectedClient = cg.scores[cg.selectedScore].client;",
		"if ( cg.scores[i].client == selectedClient ) {",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block


def test_cgame_serverinfo_restores_retail_map_alias_normalizer() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	normalize_block = _block_from_marker(source, "static const char *CG_NormalizeMapFilename")
	parse_block = _block_from_marker(source, "void CG_ParseServerinfo")

	for expected in (
		'{ "qzca1", "asylum" },',
		'{ "qzdm6", "campgrounds" },',
		'{ "qztourney7", "furiousheights" },',
		'{ "ztntourney1", "bloodrun" }',
	):
		assert expected in source

	for expected in (
		'if ( !Q_stricmp( mapname, cg_retailMapAliases[i].legacyName ) ) {',
		"return cg_retailMapAliases[i].retailName;",
	):
		assert expected in normalize_block

	assert 'mapname = CG_NormalizeMapFilename( Info_ValueForKey( info, "mapname" ) );' in parse_block
	assert 'Com_sprintf( cgs.mapname, sizeof( cgs.mapname ), "maps/%s.bsp", mapname );' in parse_block


def test_cgame_scoreboard_feeder_stats_restore_retail_leaf_split() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	count_block = _block_from_marker(source, "static int CG_FeederCount")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")
	scoreboard_block = _block_from_marker(source, "static const char *CG_FeederItemTextScoreboard")
	race_block = _block_from_marker(source, "static const char *CG_FeederItemTextRaceScoreboard")
	tdm_block = _block_from_marker(source, "static const char *CG_FeederItemTextTDMFreezeStats")
	ca_block = _block_from_marker(source, "static const char *CG_FeederItemTextClanArenaStats")
	ctf_block = _block_from_marker(source, "static const char *CG_FeederItemTextCTFFamilyStats")

	for expected in (
		"feederID == FEEDER_REDTEAM_STATS",
		"feederID == FEEDER_BLUETEAM_STATS",
		"CG_IsScoreboardFeeder( feederID )",
	):
		assert expected in count_block

	for expected in (
		"(void)feederID;",
		"(void)index;",
		"return 0;",
	):
		assert expected in image_block

	for expected in (
		"if ( CG_IsTeamStatsFeeder( feederID ) ) {",
		"return CG_FeederItemTextTDMFreezeStats( team, index, column, handle );",
		"return CG_FeederItemTextClanArenaStats( team, index, column, handle );",
		"return CG_FeederItemTextCTFFamilyStats( team, index, column, handle );",
		"return CG_FeederItemTextRaceScoreboard( index, column, handle );",
		"return CG_FeederItemTextScoreboard( index, column, handle );",
	):
		assert expected in text_block

	assert "return CG_FeederItemTextBaseColumns( &row, column, handle );" in scoreboard_block
	assert "return CG_FeederItemTextScoreboard( index, column, handle );" in race_block

	for expected in (
		"stats = &cg.tdmStats[row.scoreIndex];",
		"net = kills + stats->values[8] - stats->values[9] - stats->values[10];",
		'return va( "%i%%", row.scoreRow->accuracy );',
		'return va( "%i", stats->values[5] );',
		'return va( "%i", stats->values[0] );',
	):
		assert expected in tdm_block

	for expected in (
		"stats = &cg.clanArenaStats[row.scoreIndex];",
		'return va( "%i", stats->damageGiven );',
		'return va( "%i", stats->damageReceived );',
		'"^3%i ^7%i%%"',
		"stats->weaponFrags[WP_HEAVY_MACHINEGUN]",
	):
		assert expected in ca_block

	for expected in (
		"stats = &cg.ctfStats[row.scoreIndex];",
		"net = row.scoreRow->kills - row.scoreRow->deaths - stats->values[11];",
		'return va( "%i", stats->values[10] );',
		'return va( "%i", stats->values[8] );',
		'return va( "%i", stats->values[0] );',
	):
		assert expected in ctf_block


def test_cgame_team_list_feeders_restore_retail_family_split() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	lead_block = _block_from_marker(source, "static const char *CG_FeederItemTextTeamListLeadColumns")
	fallback_block = _block_from_marker(source, "static const char *CG_FeederItemTextFallbackTeamList")
	tdm_block = _block_from_marker(source, "static const char *CG_FeederItemTextTDMFreezeTeamList")
	ca_block = _block_from_marker(source, "static const char *CG_FeederItemTextClanArenaTeamList")
	ctf_block = _block_from_marker(source, "static const char *CG_FeederItemTextCTFFamilyTeamList")

	for expected in (
		"return CG_FeederItemTextTDMFreezeTeamList( team, index, column, handle );",
		"return CG_FeederItemTextClanArenaTeamList( team, index, column, handle );",
		"return CG_FeederItemTextCTFFamilyTeamList( team, index, column, handle );",
		"return CG_FeederItemTextFallbackTeamList( team, index, column, handle );",
	):
		assert expected in text_block

	for expected in (
		"row->scoreRow->bestWeapon > WP_NONE",
		"cg_weapons[ row->scoreRow->bestWeapon ].weaponIcon",
		"row->scoreRow->activePlayer ) {",
		'return "*";',
		"return row->info->name;",
	):
		assert expected in lead_block

	for expected in (
		"return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );",
		'return va( "%i", row.scoreRow->score );',
		'if ( row.scoreRow->ping == -1 ) {',
		'return va( "%4i", row.scoreRow->ping );',
	):
		assert expected in fallback_block

	for expected in (
		"stats = &cg.tdmStats[row.scoreIndex];",
		"if ( cgs.gametype == GT_FREEZE ) {",
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->damage );',
		'return va( "%i%%", row.scoreRow->accuracy );',
	):
		assert expected in tdm_block

	for expected in (
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->damage );',
		"cg_weapons[ row.scoreRow->bestWeapon ].weaponIcon",
		'return va( "%i%%", row.scoreRow->accuracy );',
	):
		assert expected in ca_block

	for expected in (
		'return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );',
		'return va( "%i", row.scoreRow->captures );',
		'return va( "%i", row.scoreRow->assistCount );',
		'return va( "%i", row.scoreRow->defendCount );',
	):
		assert expected in ctf_block


def test_cgame_scoreboard_selection_callbacks_restore_cached_team_list_menu_seam() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	menu_name_block = _block_from_marker(source, "static const char *CG_GetScoreboardSelectionMenuName")
	cache_block = _block_from_marker(source, "static void CG_CacheScoreboardSelectionMenus")
	sync_block = _block_from_marker(source, "static void CG_SyncScoreboardTeamListSelection")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")
	selection_block = _block_from_marker(source, "static void CG_FeederSelection")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")

	for expected in (
		'return "score_menu_ffa";',
		'return "endscore_menu_ffa";',
		'return "teamscore_menu_tdm";',
		'return "endteamscore_menu_tdm";',
		'return "teamscore_menu_har";',
		'return "endteamscore_menu_har";',
		'return "endscoreteam";',
		'return "endscorenoteam";',
	):
		assert expected in menu_name_block

	for expected in (
		"cgScoreboardSelectionMenus[0] = Menus_FindByName( liveMenuName );",
		"cgScoreboardSelectionMenus[1] = Menus_FindByName( endMenuName );",
	):
		assert expected in cache_block

	for expected in (
		'selectedItemName = ( team == TEAM_RED ) ? "playerlistRED" : "playerlistBLUE";',
		'clearedItemName = ( team == TEAM_RED ) ? "playerlistBLUE" : "playerlistRED";',
		"CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], selectedItemName, index );",
		"CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], clearedItemName, -1 );",
	):
		assert expected in sync_block

	for expected in (
		"(void)feederID;",
		"(void)index;",
		"return 0;",
	):
		assert expected in image_block

	for expected in (
		"selectedIndex = index;",
		"CG_CacheScoreboardSelectionMenus();",
		"CG_SyncScoreboardTeamListSelection( team, selectedIndex );",
	):
		assert expected in selection_block

	assert "CG_CacheScoreboardSelectionMenus();" in load_hud_block


def test_cgame_gameinfo_cvars_restore_retail_training_and_gametype_text() -> None:
	source = CG_SERVERCMDS.read_text(encoding="utf-8")
	game_info_block = _block_from_marker(source, "static void CG_SetGameInfoCvars")
	parse_block = _block_from_marker(source, "void CG_ParseServerinfo( void )")

	for expected in (
		"static const char *const cg_retailBlankGameInfoLines[6] = {",
		"static const char *const cg_retailTrainingGameInfoLines[6] = {",
		'"Welcome to QUAKE LIVE training"',
		'"A trainer named \'Crash\' is waiting to give you a quick introduction"',
		'"to the game. Follow \'Crash\' through a tour of the warm-up arena, then"',
		'"compete against her in a free-for-all deathmatch game."',
		'"Click \'Start Training\' to begin."',
		"static const char *const cg_retailGameInfoLines[GT_MAX_GAME_TYPE][6] = {",
		'"This is a 1 vs 1 Duel game"',
		'"If the time limit is hit and there is a tie, the match extends"',
		'"into overtime."',
		'"This is a Team Deathmatch game"',
		'"This is an Attack and Defend game"',
		'"Frag enemies and they will respawn onto your team."',
	):
		assert expected in source

	for expected in (
		'info = CG_ConfigString( CS_SERVERINFO );',
		'trainingValue = Info_ValueForKey( info, "g_training" );',
		"gameInfo = cg_retailBlankGameInfoLines;",
		"gameInfo = cg_retailTrainingGameInfoLines;",
		"gameInfo = cg_retailGameInfoLines[cgs.gametype];",
		'trap_Cvar_Set( "cg_gameInfo1", gameInfo[0] );',
		'trap_Cvar_Set( "cg_gameInfo2", gameInfo[1] );',
		'trap_Cvar_Set( "cg_gameInfo3", gameInfo[2] );',
		'trap_Cvar_Set( "cg_gameInfo4", gameInfo[3] );',
		'trap_Cvar_Set( "cg_gameInfo5", gameInfo[4] );',
		'trap_Cvar_Set( "cg_gameInfo6", gameInfo[5] );',
	):
		assert expected in game_info_block

	assert "CG_SetGameInfoCvars();" in parse_block
	assert parse_block.index("CG_SetGameInfoCvars();") > parse_block.index('cgs.timelimit = atoi( Info_ValueForKey( info, "timelimit" ) );')
	assert parse_block.index("CG_SetGameInfoCvars();") < parse_block.index('voteFlagsValue = Info_ValueForKey( info, "g_voteFlags" );')


def test_display_context_uses_named_cvar_string_and_native_chat_helpers() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	cvar_string_block = _block_from_marker(source, "void CG_Cvar_GetString")
	compact_hud_block = _block_from_marker(source, "static qboolean CG_IsCompactChatHudActive")
	physics_block = _block_from_marker(source, "static int CG_GetPhysicsTime")
	chat_y_block = _block_from_marker(source, "static float CG_GetChatFieldY")
	chat_width_block = _block_from_marker(source, "static float CG_GetChatFieldPixelWidth")
	chat_chars_block = _block_from_marker(source, "static int CG_GetChatFieldWidthInChars")

	assert "cgDC.getCVarString = &CG_Cvar_GetString;" in display_block
	assert "trap_Cvar_VariableStringBuffer( cvar, buffer, bufsize );" in cvar_string_block
	assert "return (qboolean)( cgs.newHud && !cg_useLegacyHud.integer );" in compact_hud_block
	assert "return cg.physicsTime;" in physics_block
	assert "return CG_IsCompactChatHudActive() ? 413.0f : 455.0f;" in chat_y_block
	assert "return CG_IsCompactChatHudActive() ? 300.0f : 640.0f;" in chat_width_block
	assert "return CG_IsCompactChatHudActive() ? 30 : 73;" in chat_chars_block


def test_cgame_init_splits_display_context_bootstrap_before_collision_map() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	display_block = _block_from_marker(source, "static void CG_InitDisplayContext")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")
	asset_block = _block_from_marker(source, "void CG_AssetCache()")
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")

	for expected in (
		"cgDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;",
		"cgDC.setColor = &trap_R_SetColor;",
		"cgDC.drawHandlePic = &CG_DrawPic;",
		"cgDC.fillRect = &CG_FillRect;",
		"cgDC.drawRect = &CG_DrawRect;",
		"cgDC.drawSides = &CG_DrawSides;",
		"cgDC.drawTopBottom = &CG_DrawTopBottom;",
		"cgDC.registerModel = &trap_R_RegisterModel;",
		"cgDC.modelBounds = &trap_R_ModelBounds;",
		"cgDC.clearScene = &trap_R_ClearScene;",
		"cgDC.addRefEntityToScene = &trap_R_AddRefEntityToScene;",
		"cgDC.renderScene = &trap_R_RenderScene;",
		"cgDC.registerFont = &trap_R_RegisterFont;",
		"cgDC.registerSound = &trap_S_RegisterSound;",
		"cgDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;",
		"cgDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;",
		"cgDC.adjustFrom640 = &CG_AdjustFrom640;",
		"cgDC.setAdjustFrom640Mode = &CG_SetAdjustFrom640Mode;",
		"cgDC.bias = cgs.screenXBias;",
		"Init_Display( &cgDC );",
	):
		assert expected in display_block

	assert "Init_Display(" not in load_hud_block
	assert "CG_RegisterHudFonts();" in asset_block

	collision_index = init_block.index('CG_LoadingString( "collision map" );')
	assert init_block.index("CG_InitDisplayContext();") < collision_index
	assert init_block.index("CG_RegisterHudFonts();") < collision_index

	for expected in (
		"cgs.screenXScale = cgs.glconfig.vidWidth / 640.0;",
		"cgs.screenYScale = cgs.glconfig.vidHeight / 480.0;",
		"cgs.screenXBias = 0.5f * ( (float)cgs.glconfig.vidWidth - ( (float)cgs.glconfig.vidHeight * ( (float)SCREEN_WIDTH / (float)SCREEN_HEIGHT ) ) );",
		"cgs.screenXBias = 0.0f;",
	):
		assert expected in init_block


def test_cgame_advert_bridge_lifecycle_matches_retail_init_and_shutdown_order() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	init_block = _block_from_marker(source, "void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum )")
	shutdown_block = _block_from_marker(source, "void CG_Shutdown( void )")

	assert "trap_AdvertisementBridge_InitCGame();" in init_block
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") > init_block.index("CG_ShaderStateChanged();")
	assert init_block.index("trap_AdvertisementBridge_InitCGame();") < init_block.index("trap_S_ClearLoopingSounds( qtrue );")

	assert "trap_AdvertisementBridge_ShutdownCGame();" in shutdown_block
	assert shutdown_block.index("trap_AdvertisementBridge_ShutdownCGame();") < shutdown_block.index('trap_Cvar_Set( "ui_mainmenu", "1" );')


def test_cgame_drawtools_keep_retail_widescreen_bias_consumers() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	adjust_block = _block_from_marker(source, "void CG_AdjustFrom640")

	for expected in (
		"static int cgAdjustFrom640Mode = -1;",
		"static void CG_GetAdjustedXScale( float *xScale, float *xBias ) {",
		"centered = ( trap_Key_GetCatcher() & KEYCATCH_CGAME ) != 0;",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_STRETCH && !centered ) {",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_RIGHT ) {",
		"if ( cgAdjustFrom640Mode == WIDESCREEN_CENTER || centered ) {",
		"CG_GetAdjustedXScale( &xScale, &xBias );",
		"if ( x ) {",
		"if ( y ) {",
		"if ( w ) {",
		"if ( h ) {",
		"*x = (*x * xScale) + xBias;",
		"ax = x * xScale + xBias;",
		"ay = y * cgs.screenYScale;",
		"aw = (float)propMapB[ch][2] * xScale;",
		"ah = (float)PROPB_HEIGHT * cgs.screenYScale;",
		"aw = (float)propMap[ch][2] * xScale * sizeScale;",
		"ah = (float)PROP_HEIGHT * cgs.screenYScale * sizeScale;",
		"void CG_SetAdjustFrom640Mode( int widescreen ) {",
	):
		assert expected in source

	assert "if ( x ) {" in adjust_block
	assert "ax = x * cgs.screenXScale + cgs.screenXBias;" not in source
	assert "ay = y * cgs.screenXScale;" not in source


def test_cgame_drawtools_big_string_wrappers_use_retail_text_paint_path() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	big_block = _block_from_marker(source, "void CG_DrawBigString")
	big_color_block = _block_from_marker(source, "void CG_DrawBigStringColor")

	assert "CG_Text_Paint( (float)x, (float)( y + BIGCHAR_HEIGHT ), 0.25f, color, s, 0, 0, 0 );" in big_block
	assert "CG_DrawStringExt(" not in big_block

	assert "CG_Text_Paint( (float)x, (float)( y + BIGCHAR_HEIGHT ), 0.25f, color, s, 0, 0, 0 );" in big_color_block
	assert "CG_DrawStringExt(" not in big_color_block


def test_cgame_effect_event_bridge_keeps_retail_teleport_and_impact_callbacks() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	obelisk_block = _block_from_marker(effects_source, "void CG_ObeliskPain")

	for expected in (
		"CG_SpawnEffect( position);",
		"CG_SpawnEffect(  position);",
		"CG_KamikazeEffect( cent->lerpOrigin );",
		"CG_ObeliskExplode( cent->lerpOrigin, es->eventParm );",
		"CG_ObeliskPain( cent->lerpOrigin );",
		"CG_InvulnerabilityImpact( cent->lerpOrigin, cent->currentState.angles );",
		"CG_LightningBoltBeam(es->origin2, es->pos.trBase);",
	):
		assert expected in event_source

	assert re.search(r"\bint\s+r;", obelisk_block)
	assert "float r;" not in obelisk_block
	assert "r = rand() & 3;" in obelisk_block


def test_cgame_effects_keep_retail_lightning_discharge_sprite_producer() -> None:
	source = CG_EFFECTS.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_LightningDischargeEffect")

	assert 'trap_R_RegisterShader( "models/weaphits/electric.tga" );' in block
	assert "radius = (float)( ( magnitude * 10 + 48 ) >> 4 );" in block
	assert "duration = magnitude + 300;" in block
	assert "le = CG_SmokePuff( origin, vec3_origin, radius," in block
	assert "le->leType = LE_SCALE_FADE;" in block


def test_cgame_race_reset_state_keeps_retail_raceinit_command() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_RaceResetState")

	assert "memset( cgs.raceLeaderSplits, 0, sizeof( cgs.raceLeaderSplits ) );" in block
	assert "if ( cgs.gametype == GT_RACE ) {" in block
	assert 'trap_SendClientCommand( "raceinit" );' in block


def test_cgame_event_reconstruction_keeps_retail_overtime_gameover_and_race_handlers() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	view_source = CG_VIEW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	winner_block = _block_from_marker(event_source, "static qboolean CG_IsLocalPlayerWinner")
	overtime_block = _block_from_marker(event_source, "int CG_GetOvertimeCount( void )")
	local_client_block = _block_from_marker(event_source, "static qboolean CG_IsRetailLocalEventClient")
	event_block = _block_from_marker(event_source, "void CG_EntityEvent")
	view_block = _block_from_marker(view_source, "void CG_ClearBufferedAnnouncements")

	for expected in (
		"QL_EV_OVERTIME = 0x54",
		"QL_EV_GAMEOVER = 0x55",
		"QL_EV_LIGHTNING_DISCHARGE = 0x5c",
		"QL_EV_RACE_START = 0x5d",
		"QL_EV_RACE_CHECKPOINT = 0x5e",
		"QL_EV_RACE_FINISH = 0x5f",
	):
		assert expected in event_source

	assert "void CG_ClearBufferedAnnouncements( void );" in local_source
	assert "CG_ClearBufferedSounds();" in view_block

	assert "if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {" in local_client_block
	assert "return ( qboolean )( clientNum == cg.spectatorFollowClient );" in local_client_block
	assert "return ( qboolean )( clientNum == cg.clientNum );" in local_client_block

	assert "rank = cg.snap->ps.persistant[PERS_RANK];" in winner_block
	assert "if ( rank & RANK_TIED_FLAG ) {" in winner_block
	assert "if ( cg.teamScores[0] == cg.teamScores[1] ) {" in winner_block
	assert "return ( qboolean )( cg.teamScores[0] > cg.teamScores[1] );" in winner_block
	assert "return ( qboolean )( cg.teamScores[1] > cg.teamScores[0] );" in winner_block

	assert "if ( cgs.matchOvertimeCount > 0 ) {" in overtime_block
	assert "regulationEnd = cgs.levelStartTime + ( cgs.timelimit * 60000 );" in overtime_block
	assert "elapsed = anchor - regulationEnd;" in overtime_block
	assert "return elapsed / overtimeWindow;" in overtime_block

	for expected in (
		"case QL_EV_OVERTIME:",
		'trap_S_RegisterSound( "sound/world/klaxon2.ogg", qfalse )',
		'CG_CenterPrint( va( "Overtime! %d seconds added", secondsAdded ), 90, BIGCHAR_WIDTH );',
		"CG_AddBufferedSound( cgs.media.overtimeSound );",
		"case QL_EV_GAMEOVER:",
		"CG_ClearBufferedAnnouncements();",
		'trap_S_StartLocalSound( trap_S_RegisterSound( "sound/world/buzzer.ogg", qfalse ), CHAN_LOCAL_SOUND );',
		'trap_S_StartBackgroundTrack( "music/win", "" );',
		'trap_S_StartBackgroundTrack( "music/loss", "" );',
		"case QL_EV_LIGHTNING_DISCHARGE:",
		"CG_LightningDischargeEffect( cent->lerpOrigin, es->eventParm );",
		"case QL_EV_RACE_START:",
		"CG_RacePlayCue( CG_RACE_CUE_START );",
		"case QL_EV_RACE_CHECKPOINT:",
		"CG_RacePlayCue( CG_RACE_CUE_CHECKPOINT );",
		"case QL_EV_RACE_FINISH:",
		"CG_RaceResetState();",
		"CG_RacePlayCue( CG_RACE_CUE_FINISH );",
	):
		assert expected in event_block


def test_cgame_event_reconstruction_keeps_retail_award_and_local_reward_handlers() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	main_source = CG_MAIN.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	award_block = _block_from_marker(event_source, "static void CG_HandleRetailAwardEvent")

	for expected in (
		"QL_EV_AWARD = 0x61",
		"QL_EV_INFECTED = 0x62",
		"QL_EV_NEW_HIGH_SCORE = 99",
		"static int CG_GetRetailEventClientNum( const entityState_t *es )",
		"static int CG_GetRetailAwardType( const entityState_t *es )",
		"static int CG_GetRetailAwardCount( const entityState_t *es )",
	):
		assert expected in event_source

	for expected in (
		"qhandle_t\tmedalAccuracy;",
		"qhandle_t\tmedalComboKill;",
		"sfxHandle_t comboKillSound;",
		"sfxHandle_t comboKillSound2;",
		"sfxHandle_t comboKillSound3;",
		"sfxHandle_t accuracySound;",
		"sfxHandle_t rampageSound2;",
		"sfxHandle_t rampageSound3;",
		"sfxHandle_t revengeSound2;",
		"sfxHandle_t revengeSound3;",
		"sfxHandle_t infectedSound;",
		"sfxHandle_t newHighScoreSound;",
		"void pushReward( sfxHandle_t sfx, qhandle_t shader, int rewardCount );",
	):
		assert expected in local_source

	for expected in (
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound, \"combokill1\", \"combokill1\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound2, \"combokill2\", \"combokill2\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound3, \"combokill3\", \"combokill3\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( accuracySound, \"accuracy\", \"accuracy\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( infectedSound, \"infected\", \"infected\" );",
		"CG_REGISTER_RETAIL_REWARD_SAMPLE( newHighScoreSound, \"new_high_score\", \"new_high_score\" );",
		'cgs.media.medalAccuracy = trap_R_RegisterShaderNoMip( "medal_accuracy" );',
		'cgs.media.medalComboKill = trap_R_RegisterShaderNoMip( "medal_combokill" );',
	):
		assert expected in main_source

	for expected in (
		"rewardCount = CG_GetRetailAwardCount( es );",
		"variant = rand() % 3;",
		"shader = cgs.media.medalComboKill;",
		"shader = cgs.media.medalAccuracy;",
		"shader = cgs.media.medalFirstFrag;",
		"rewardCount = 1;",
		"pushReward( sfx, shader, rewardCount );",
		"case QL_EV_AWARD:",
		"CG_HandleRetailAwardEvent( es );",
		"case QL_EV_INFECTED:",
		"CG_AddBufferedSound( cgs.media.infectedSound );",
		"case QL_EV_NEW_HIGH_SCORE:",
		"CG_AddBufferedSound( cgs.media.newHighScoreSound );",
	):
		assert expected in event_source

	assert "CG_IsRetailLocalEventClient( clientNum )" in award_block
	assert "CG_GetRetailEventClientNum( es )" in event_source


def test_cgame_event_reconstruction_keeps_retail_damage_plum_bridge() -> None:
	event_source = CG_EVENT.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	localents_source = CG_LOCALENTS.read_text(encoding="utf-8")
	damage_plum_block = _block_from_marker(event_source, "static void CG_DamagePlum")

	for expected in (
		"static int CG_GetRetailDamagePlumDamage( const entityState_t *es )",
		"static weapon_t CG_GetRetailDamagePlumWeapon( const entityState_t *es )",
		"static void CG_GetDamagePlumColor( int damage, weapon_t weapon, vec4_t color )",
		"static void CG_DamagePlum( vec3_t org, int damage, weapon_t weapon )",
		"case EV_DAMAGEPLUM:",
		"CG_DamagePlum( cent->lerpOrigin, CG_GetRetailDamagePlumDamage( es ), CG_GetRetailDamagePlumWeapon( es ) );",
	):
		assert expected in event_source

	for expected in (
		"if ( damage <= 0 || !CG_DamagePlumsEnabled() ) {",
		"if ( !CG_ShouldRenderDamagePlumForWeapon( weapon ) ) {",
		"CG_GetDamagePlumColor( damage, weapon, color );",
		"le->leFlags = LEF_SCOREPLUM_CUSTOMCOLOR;",
		"le->leType = LE_SCOREPLUM;",
	):
		assert expected in damage_plum_block

	assert "CG_IsRetailLocalEventClient( CG_GetRetailEventClientNum( es ) )" in event_source
	assert "return es->eventParm;" in event_source
	assert "return WP_NONE;" in event_source
	assert "LEF_SCOREPLUM_CUSTOMCOLOR = 0x0010" in local_source
	assert "if ( le->leFlags & LEF_SCOREPLUM_CUSTOMCOLOR ) {" in localents_source
	assert "re->shaderRGBA[0] = (byte)( 0xff * Com_Clamp( 0.0f, 1.0f, le->color[0] ) );" in localents_source


def test_cgame_server_settings_panel_reconstruction_uses_retail_custom_setting_configstrings() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	parse_custom_block = _block_from_marker(servercmds_source, "static void CG_ParseCustomSettingsConfigString")
	parse_info_block = _block_from_marker(servercmds_source, "static void CG_ParseServerSettingsInfoConfigStrings")
	draw_block = _block_from_marker(newdraw_source, "static void CG_DrawServerSettings")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")

	for expected in (
		"unsigned long long\tcustomSettingsMask;",
		"qboolean\tserverSettingsArmorTiered;",
		"int\t\tserverSettingsQuadFactor;",
		"int\t\tserverSettingsGravity;",
	):
		assert expected in local_source

	assert "info = CG_ConfigString( CS_CUSTOM_SETTINGS );" in parse_custom_block
	assert "value = strtoull( info, &end, 0 );" in parse_custom_block
	assert "cgs.customSettingsMask = value;" in parse_custom_block

	for expected in (
		'info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_A );',
		'Info_ValueForKey( info, "armor_tiered" )',
		'info = CG_ConfigString( CS_SERVER_SETTINGS_INFO_B );',
		'Info_ValueForKey( info, "g_quadDamageFactor" )',
		'Info_ValueForKey( info, "g_gravity" )',
		"cgs.serverSettingsArmorTiered = (qboolean)( value[0] && atoi( value ) != 0 );",
		"cgs.serverSettingsQuadFactor = value[0] ? atoi( value ) : 3;",
		"cgs.serverSettingsGravity = value[0] ? atoi( value ) : 800;",
	):
		assert expected in parse_info_block

	assert "CG_ParseCustomSettingsConfigString();" in set_config_values_block
	assert "CG_ParseServerSettingsInfoConfigStrings();" in set_config_values_block
	assert "num == CS_CUSTOM_SETTINGS" in servercmds_source
	assert "num == CS_SERVER_SETTINGS_INFO_A || num == CS_SERVER_SETTINGS_INFO_B" in servercmds_source

	for expected in (
		'"AIR CONTROL"',
		'"RAMP JUMPING"',
		'"TIERED ARMOR"',
		'"MODIFIED WEAPON SWITCH"',
		'"%ix QUAD"',
		'"MODIFIED PHYSICS"',
		'"GRAVITY %i"',
		'"INSTAGIB"',
		'"QUAD HOG"',
		'"REGEN HEALTH"',
		'"DROP DAMAGED HEALTH"',
		'"VAMPIRIC DAMAGE"',
		'"MODIFIED ITEM SPAWNING"',
		'"HEADSHOTS ENABLED"',
		'"RAIL JUMPING"',
		'"MODIFIED WEAPONS"',
		"weaponMask = (unsigned int)( cgs.customSettingsMask & CUSTOM_SETTING_WEAPON_MASK );",
		"cgs.serverSettingsQuadFactor != 3",
		"cgs.serverSettingsGravity != 800",
		"cgs.serverSettingsArmorTiered",
		"if ( activeCount < 15 ) {",
		"CG_DrawPic( iconX, iconY, iconSize, iconSize, icon );",
	):
		assert expected in draw_block


def test_cgame_player_appearance_configstring_reconstruction_uses_retail_parser_and_head_gate() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	draw_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c" ).read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayerAppearanceConfigString")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")
	new_client_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")
	draw_head_block = _block_from_marker(draw_source, "void CG_DrawHead( float x, float y, float w, float h, int clientNum, vec3_t headAngles )")

	for expected in (
		"qboolean\t\tallowCustomHeadmodels;",
		"float\t\t\tplayerHeadScale;",
		"float\t\t\tplayerHeadScaleOffset;",
		"float\t\t\tplayerModelScale;",
	):
		assert expected in local_source

	for expected in (
		"info = CG_ConfigString( CS_PLAYER_APPEARANCE );",
		'Info_ValueForKey( info, "g_playermodelOverride" )',
		'Info_ValueForKey( info, "g_playerheadmodelOverride" )',
		'Info_ValueForKey( info, "g_allowCustomHeadmodels" )',
		'Info_ValueForKey( info, "g_playerheadScale" )',
		'Info_ValueForKey( info, "g_playerheadScaleOffset" )',
		'Info_ValueForKey( info, "g_playerModelScale" )',
		"CG_ResetPlayerAppearanceState();",
		"cgs.allowCustomHeadmodels = (qboolean)( atoi( value ) != 0 );",
		"cgs.playerHeadScale = (float)atof( value );",
		"cgs.playerHeadScaleOffset = (float)atof( value );",
		"cgs.playerModelScale = (float)atof( value );",
		"CG_ApplyModelOverrides();",
	):
		assert expected in parse_block

	assert "CG_ParsePlayerAppearanceConfigString();" in set_config_values_block
	assert "num == CS_PLAYER_APPEARANCE" in servercmds_source

	for expected in (
		"if ( !cgs.allowCustomHeadmodels ) {",
		"Q_strncpyz( newInfo.headModelName, newInfo.modelName, sizeof( newInfo.headModelName ) );",
		"Q_strncpyz( newInfo.headSkinName, newInfo.skinName, sizeof( newInfo.headSkinName ) );",
	):
		assert expected in new_client_block

	assert "len *= cgs.playerModelScale;" in draw_head_block


def test_cgame_head_offset_refresh_restores_retail_model_scale_seam() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	parse_block = _block_from_marker(servercmds_source, "static void CG_ParsePlayerAppearanceConfigString")
	update_block = _block_from_marker(players_source, "static qboolean CG_UpdateClientHeadOffset")
	refresh_block = _block_from_marker(players_source, "void CG_RefreshClientHeadOffsets( void )")
	register_block = _block_from_marker(players_source, "static qboolean CG_RegisterClientModelname")

	assert "void CG_RefreshClientHeadOffsets( void );" in local_source

	for expected in (
		'!Q_stricmp( ci->modelName, "orbb" )',
		"ci->headOffset[0] = 1.0f;",
		"trap_R_ModelBounds( ci->headModel, mins, maxs );",
		'"tag_torso"',
		'"tag_head"',
		"cgs.playerModelScale",
		"ci->headOffset[0] = ( 56.0f / totalHeight ) * cgs.playerModelScale;",
	):
		assert expected in update_block

	for expected in (
		"oldPlayerModelScale = cgs.playerModelScale;",
		"oldPlayerModelScale != cgs.playerModelScale",
		"CG_RefreshClientHeadOffsets();",
	):
		assert expected in parse_block

	assert "CG_UpdateClientHeadOffset( ci );" in register_block
	assert "CG_UpdateClientHeadOffset( ci );" in refresh_block


def test_cgame_player_color_helper_restores_retail_shared_color_scale_seam() -> None:
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	scale_block = _block_from_marker(players_source, "static int CG_GetPlayerColorScale")
	tint_block = _block_from_marker(players_source, "static void CG_ApplyDeadBodyTint")
	set_color_block = _block_from_marker(players_source, "static void CG_SetRefEntityColor")
	apply_block = _block_from_marker(players_source, "static void CG_ApplyPlayerColors")
	player_block = _block_from_marker(players_source, "void CG_Player( centity_t *cent )")

	for expected in (
		'trap_Cvar_VariableStringBuffer( "r_colorCorrectActive", value, sizeof( value ) );',
		"return atof( value ) > 0.0f ? 1 : 2;",
	):
		assert expected in scale_block

	for expected in (
		"CG_SetScaledShaderRGBA( re->shaderRGBA, cg.deadBodyColor, colorScale );",
		"shaderColor[3] = 1.0f;",
		"CG_SetScaledShaderRGBA( ent->shaderRGBA, shaderColor, colorScale );",
	):
		assert expected in tint_block + set_color_block

	for expected in (
		"colorScale = CG_GetPlayerColorScale();",
		"CG_ShouldTintDeadBody( cent, ci )",
		"legs->shaderRGBA[0] = 255;",
		"CG_ApplyDeadBodyTint( legs, colorScale );",
		"CG_SetRefEntityColor( torso, ci->upperColor, colorScale );",
		"CG_SetRefEntityColor( head, ci->headColor, colorScale );",
	):
		assert expected in apply_block

	assert "CG_ApplyPlayerColors( cent, ci, &legs, &torso, &head );" in player_block
	assert "tintCorpse = CG_ShouldTintDeadBody" not in player_block


def test_cgame_client_skin_normalizers_restore_retail_team_default_and_sport_split() -> None:
	players_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c" ).read_text(encoding="utf-8")
	default_skin_block = _block_from_marker(players_source, "static const char *CG_DefaultTeamSkinName")
	skin_block = _block_from_marker(players_source, "static void CG_NormalizeClientSkinName")
	head_skin_block = _block_from_marker(players_source, "static void CG_NormalizeClientHeadSkinName")
	new_client_block = _block_from_marker(players_source, "void CG_NewClientInfo( int clientNum )")

	for expected in (
		'return "red";',
		'return "blue";',
		'return "default";',
	):
		assert expected in default_skin_block

	for expected in (
		'Q_strncpyz( modelToken, ci->modelName, sizeof( modelToken ) );',
		"skinToken = strchr( modelToken, '/' );",
		"Q_strncpyz( ci->skinName, skinToken, sizeof( ci->skinName ) );",
		"CG_DefaultTeamSkinName( ci->team )",
		'!Q_stricmp( ci->skinName, "sport" )',
		'Q_strncpyz( ci->skinName, "sport_red", sizeof( ci->skinName ) );',
		'Q_strncpyz( ci->skinName, "sport_blue", sizeof( ci->skinName ) );',
	):
		assert expected in skin_block

	for expected in (
		'Q_strncpyz( headModelToken, ci->headModelName, sizeof( headModelToken ) );',
		"skinToken = strchr( headModelToken, '/' );",
		"Q_strncpyz( ci->headSkinName, skinToken, sizeof( ci->headSkinName ) );",
		"CG_DefaultTeamSkinName( ci->team )",
		'!Q_stricmp( ci->headSkinName, "sport" )',
		'Q_strncpyz( ci->headSkinName, "sport_red", sizeof( ci->headSkinName ) );',
		'Q_strncpyz( ci->headSkinName, "sport_blue", sizeof( ci->headSkinName ) );',
	):
		assert expected in head_skin_block

	for expected in (
		"CG_NormalizeClientSkinName( &newInfo );",
		"CG_NormalizeClientHeadSkinName( &newInfo );",
	):
		assert expected in new_client_block

	assert 'Q_strncpyz( newInfo.skinName, slash + 1, sizeof( newInfo.skinName ) );' not in new_client_block
	assert 'Q_strncpyz( newInfo.headSkinName, slash + 1, sizeof( newInfo.headSkinName ) );' not in new_client_block


def test_cgame_respawn_weapon_select_restores_retail_primary_preference_seam() -> None:
	playerstate_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_playerstate.c" ).read_text(encoding="utf-8")
	token_block = _block_from_marker(playerstate_source, "static weapon_t CG_RespawnWeaponFromToken")
	select_block = _block_from_marker(playerstate_source, "static void CG_SelectRespawnWeapon")
	respawn_block = _block_from_marker(playerstate_source, "void CG_Respawn( void )")

	for expected in (
		'"gauntlet"',
		'"rocket_launcher"',
		'"grappling_hook"',
		'"heavy_machinegun"',
		"return (weapon_t)atoi( token );",
	):
		assert expected in token_block

	for expected in (
		'trap_Cvar_VariableStringBuffer( "cg_weaponPrimary", buffer, sizeof( buffer ) );',
		"token = COM_ParseExt( &cursor, qtrue );",
		"weapon = CG_RespawnWeaponFromToken( token );",
		"cg.snap->ps.stats[STAT_WEAPONS] & ( 1 << weapon )",
		"CG_SetWeaponSelect( weapon );",
		"CG_SetWeaponSelect( cg.snap->ps.weapon );",
	):
		assert expected in select_block

	assert "CG_SelectRespawnWeapon();" in respawn_block
	assert "CG_SetWeaponSelect( cg.snap->ps.weapon );" not in respawn_block


def test_cgame_trace_capsule_helper_restores_retail_trace_split() -> None:
	predict_source = CG_PREDICT.read_text(encoding="utf-8")
	clip_block = _block_from_marker(predict_source, "static void CG_ClipMoveToEntities")
	capsule_block = _block_from_marker(predict_source, "static void CG_TraceCapsule")
	trace_block = _block_from_marker(predict_source, "void\tCG_Trace")

	for expected in (
		"int skipNumber, int mask, qboolean useCapsule, trace_t *tr )",
		"if ( useCapsule ) {",
		"cmodel = trap_CM_TempCapsuleModel( bmins, bmaxs );",
		"trap_CM_TransformedCapsuleTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
		"cmodel = trap_CM_TempBoxModel( bmins, bmaxs );",
		"trap_CM_TransformedBoxTrace( &trace, start, end, mins, maxs, cmodel, mask, origin, angles );",
	):
		assert expected in clip_block

	for expected in (
		"trap_CM_CapsuleTrace( &t, start, end, mins, maxs, 0, mask );",
		"CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qtrue, &t );",
	):
		assert expected in capsule_block

	for expected in (
		"if ( CG_UseCapsuleTrace() ) {",
		"CG_TraceCapsule( result, start, mins, maxs, end, skipNumber, mask );",
		"trap_CM_BoxTrace( &t, start, end, mins, maxs, 0, mask );",
		"CG_ClipMoveToEntities( start, mins, maxs, end, skipNumber, mask, qfalse, &t );",
	):
		assert expected in trace_block


def test_cgame_local_entity_dispatch_restores_retail_fragment_and_effect_split() -> None:
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	effects_source = CG_EFFECTS.read_text(encoding="utf-8")
	localents_source = CG_LOCALENTS.read_text(encoding="utf-8")
	fragment_block = _block_from_marker(localents_source, "void CG_AddFragment( localEntity_t *le )")
	tracer_block = _block_from_marker(localents_source, "static void CG_AddBigExplodeTracer")
	death_block = _block_from_marker(localents_source, "static void CG_AddDeathEffect")
	dispatch_block = _block_from_marker(localents_source, "void CG_AddLocalEntities( void )")

	for expected in (
		"LE_BIGEXPLODE_TRACER = 0x05,",
		"LE_05 = LE_BIGEXPLODE_TRACER,",
		"LE_DEATH_EFFECT = 0x0F,",
		"LE_0F = LE_DEATH_EFFECT,",
		"LE_SCALE_FADE_OUT = LE_DEATH_EFFECT,",
	):
		assert expected in local_source

	for expected in (
		"le->leType = LE_BIGEXPLODE_TRACER;",
		"le->leType = LE_DEATH_EFFECT;",
	):
		assert expected in effects_source

	for expected in (
		"(void)CG_AddFragmentImpl( le );",
		"if ( le->leType == LE_FRAGMENT_14 ) {",
		"CG_AddFragmentTrail( le, cgs.media.tracerShader );",
	):
		assert expected in fragment_block

	assert "(void)CG_AddSpriteEffectCommon( le );" in tracer_block
	assert "if ( CG_AddSpriteEffectCommon( le ) && le->light ) {" in death_block

	for expected in (
		"case LE_BIGEXPLODE_TRACER:",
		"CG_AddBigExplodeTracer( le );",
		"case LE_FRAGMENT_14:",
		"case LE_FRAGMENT_16:",
		"CG_AddFragment( le );",
		"case LE_DEATH_EFFECT:",
		"CG_AddDeathEffect( le );",
	):
		assert expected in dispatch_block

	for unexpected in (
		"CG_AddFragment14",
		"CG_AddFragment16",
		"CG_AddType05",
		"CG_AddType0F",
	):
		assert unexpected not in localents_source


def test_cgame_vote_widget_reconstruction_uses_retail_vote_cvar_and_text_paths() -> None:
	servercmds_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c" ).read_text(encoding="utf-8")
	main_source = ( REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c" ).read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	vote_timer_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteTimer")
	vote_count_block = _block_from_marker(newdraw_source, "static void CG_DrawVoteCount")
	set_config_values_block = _block_from_marker(servercmds_source, "void CG_SetConfigValues")

	for expected in (
		'cgs.voteTime = atoi( CG_ConfigString( CS_VOTE_TIME ) );',
		'cgs.voteYes = atoi( CG_ConfigString( CS_VOTE_YES ) );',
		'cgs.voteNo = atoi( CG_ConfigString( CS_VOTE_NO ) );',
		'Q_strncpyz( cgs.voteString, CG_ConfigString( CS_VOTE_STRING ), sizeof( cgs.voteString ) );',
		'trap_Cvar_Set( "ui_voteactive", cgs.voteTime ? "1" : "0" );',
		'trap_Cvar_Set( "ui_votestring", cgs.voteString );',
	):
		assert expected in set_config_values_block

	for expected in (
		'trap_Cvar_Set( "ui_votestring", "" );',
		'trap_Cvar_Set( "ui_votestring", cgs.voteString );',
		'cgs.voteString[0] = \'\\0\';',
	):
		assert expected in servercmds_source or expected in main_source

	for expected in (
		'"Voting has ended."',
		'"Voting ends in %i second."',
		'"Voting ends in %i seconds."',
	):
		assert expected in vote_timer_block

	assert '"Vote %is"' not in vote_timer_block
	assert 'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );' in vote_count_block


def test_display_context_core_layout_matches_retail_widescreen_tail() -> None:
	source = UI_SHARED_H.read_text(encoding="utf-8")

	assert source.index("void (*drawText) (float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style );") < source.index("int (*textWidth) (const char *text, float scale, int limit);")
	assert source.index("int (*textWidth) (const char *text, float scale, int limit);") < source.index("int (*textHeight) (const char *text, float scale, int limit);")
	assert source.index("void (*drawTextWithCursor)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style);") < source.index("void (*setOverstrikeMode)(qboolean b);")
	assert source.index("qhandle_t (*playLauncherCinematic)(const char *name, qboolean loop, int width, int height);") < source.index("void (*stopCinematic)(int handle);")
	assert source.index("void (*activateAdvert)(int cellId);") < source.index("void (*adjustFrom640)(float *x, float *y, float *w, float *h);")
	assert source.index("void (*adjustFrom640)(float *x, float *y, float *w, float *h);") < source.index("void (*setAdjustFrom640Mode)(int widescreen);")
	assert source.index("void (*setAdjustFrom640Mode)(int widescreen);") < source.index("yscale;")
	assert source.index("float FPS;") < source.index("void (*drawTextExt)(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex);")
	assert source.index("void (*drawTextExt)(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style, int fontIndex);") < source.index("int (*textWidthExt)(const char *text, float scale, int limit, int fontIndex);")
	assert source.index("int (*textHeightExt)(const char *text, float scale, int limit, int fontIndex);") < source.index("void (*drawTextWithCursorExt)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex);")
	assert source.index("void (*drawTextWithCursorExt)(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex);") < source.index("void (*initAdvertisementBridge)(void);")


def test_shared_ui_widescreen_flow_uses_retail_adjust_callbacks() -> None:
	shared_source = UI_SHARED.read_text(encoding="utf-8")
	ui_main_source = UI_MAIN.read_text(encoding="utf-8")

	for expected in (
		"if (DC && DC->setAdjustFrom640Mode) {",
		"if (DC && DC->adjustFrom640) {",
		"if (DC->setAdjustFrom640Mode && item->widescreenSet) {",
		"DC->setAdjustFrom640Mode(item->widescreen);",
		"DC->setAdjustFrom640Mode(parent ? parent->widescreen : WIDESCREEN_STRETCH);",
		"DC->setAdjustFrom640Mode(menu->widescreen);",
		"DC->setAdjustFrom640Mode(WIDESCREEN_STRETCH);",
	):
		assert expected in shared_source

	for expected in (
		"uiInfo.uiDC.adjustFrom640 = &UI_AdjustFrom640;",
		"uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;",
		"uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;",
		"uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;",
		"uiInfo.uiDC.initAdvertisementBridge = &UI_InitAdvertisementBridge;",
	):
		assert expected in ui_main_source


def test_cgame_public_and_local_headers_expose_bridge_imports() -> None:
	public_source = CG_PUBLIC.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")

	assert "#define CGAME_NATIVE_IMPORT_COUNT\t(CG_ADVERTISEMENTBRIDGE_SETFRAMETIME + 1)" in public_source

	for expected in (
		"CG_KEY_GETBINDINGBUF",
		"CG_KEY_SETBINDING",
		"CG_KEY_GETOVERSTRIKEMODE",
		"CG_KEY_SETOVERSTRIKEMODE",
		"CG_CMD_EXECUTETEXT",
		"CG_ADVERTISEMENTBRIDGE_INITCGAME",
		"CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME",
		"CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS",
		"CG_ADVERTISEMENTBRIDGE_SETFRAMETIME",
	):
		assert expected in public_source

	assert "CG_MEMSET = 100" in public_source

	for expected in (
		"void\t\ttrap_Key_GetBindingBuf( int keynum, char *buf, int buflen );",
		"void\t\ttrap_Key_SetBinding( int keynum, const char *binding );",
		"qboolean\ttrap_Key_GetOverstrikeMode( void );",
		"void\t\ttrap_Key_SetOverstrikeMode( qboolean state );",
		"void\t\ttrap_Cmd_ExecuteText( int exec_when, const char *text );",
		"void\t\ttrap_AdvertisementBridge_InitCGame( void );",
		"void\t\ttrap_AdvertisementBridge_ShutdownCGame( void );",
		"void\t\ttrap_AdvertisementBridge_UpdateLoadingViewParameters( void );",
		"void\t\ttrap_AdvertisementBridge_SetFrameTime( int frameTime );",
	):
		assert expected in local_source


def test_cgame_syscall_bridge_handles_binding_and_execute_ops() -> None:
	syscalls = CG_SYSCALLS.read_text(encoding="utf-8")
	client = CL_CGAME.read_text(encoding="utf-8")

	for expected in (
		"void trap_Cmd_ExecuteText( int exec_when, const char *text ) {",
		"syscall( CG_CMD_EXECUTETEXT, exec_when, text );",
		"void trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {",
		"syscall( CG_KEY_GETBINDINGBUF, keynum, buf, buflen );",
		"void trap_Key_SetBinding( int keynum, const char *binding ) {",
		"syscall( CG_KEY_SETBINDING, keynum, binding );",
		"qboolean trap_Key_GetOverstrikeMode( void ) {",
		"return syscall( CG_KEY_GETOVERSTRIKEMODE );",
		"void trap_Key_SetOverstrikeMode( qboolean state ) {",
		"syscall( CG_KEY_SETOVERSTRIKEMODE, state );",
		"void trap_AdvertisementBridge_InitCGame( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_INITCGAME );",
		"void trap_AdvertisementBridge_ShutdownCGame( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME );",
		"void trap_AdvertisementBridge_UpdateLoadingViewParameters( void ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS );",
		"void trap_AdvertisementBridge_SetFrameTime( int frameTime ) {",
		"syscall( CG_ADVERTISEMENTBRIDGE_SETFRAMETIME, frameTime );",
	):
		assert expected in syscalls

	switch_block = _block_from_marker(client, "int CL_CgameSystemCalls")
	for expected in (
		"case CG_CMD_EXECUTETEXT:",
		"Cbuf_ExecuteText( args[1], VMA(2) );",
		"case CG_KEY_GETBINDINGBUF:",
		'Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );',
		"case CG_KEY_SETBINDING:",
		"Key_SetBinding( args[1], VMA(2) );",
		"case CG_KEY_GETOVERSTRIKEMODE:",
		"return Key_GetOverstrikeMode();",
		"case CG_KEY_SETOVERSTRIKEMODE:",
		"Key_SetOverstrikeMode( args[1] );",
		"case CG_ADVERTISEMENTBRIDGE_INITCGAME:",
		"CL_AdvertisementBridge_InitCGame();",
		"case CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME:",
		"CL_AdvertisementBridge_ShutdownCGame();",
		"case CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS:",
		"CL_AdvertisementBridge_UpdateLoadingViewParameters();",
		"case CG_ADVERTISEMENTBRIDGE_SETFRAMETIME:",
		"CL_AdvertisementBridge_SetFrameTime( args[1] );",
	):
		assert expected in switch_block


def test_native_import_table_keeps_new_cgame_bridge_callbacks() -> None:
	imports_source = QL_CGAME_IMPORTS.read_text(encoding="utf-8")
	client_source = CL_CGAME.read_text(encoding="utf-8")

	for expected in (
		"static void QDECL QL_CG_trap_Cmd_ExecuteText( int exec_when, const char *text ) {",
		"CG_Import_Syscall( CG_CMD_EXECUTETEXT, exec_when, text );",
		"static void QDECL QL_CG_trap_Key_GetBindingBuf( int keynum, char *buf, int buflen ) {",
		"CG_Import_Syscall( CG_KEY_GETBINDINGBUF, keynum, buf, buflen );",
		"static void QDECL QL_CG_trap_Key_SetBinding( int keynum, const char *binding ) {",
		"CG_Import_Syscall( CG_KEY_SETBINDING, keynum, binding );",
		"static qboolean QDECL QL_CG_trap_Key_GetOverstrikeMode( void ) {",
		"return CG_Import_Syscall( CG_KEY_GETOVERSTRIKEMODE );",
		"static void QDECL QL_CG_trap_Key_SetOverstrikeMode( qboolean state ) {",
		"CG_Import_Syscall( CG_KEY_SETOVERSTRIKEMODE, state );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_InitCGame( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_INITCGAME );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_ShutdownCGame( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters( void ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS );",
		"static void QDECL QL_CG_trap_AdvertisementBridge_SetFrameTime( int frameTime ) {",
		"CG_Import_Syscall( CG_ADVERTISEMENTBRIDGE_SETFRAMETIME, frameTime );",
	):
		assert expected in imports_source

	for expected in (
		"static ql_import_f ql_cgame_imports[CGAME_NATIVE_IMPORT_COUNT] = {",
		"[CG_KEY_GETBINDINGBUF] = (ql_import_f)QL_CG_trap_Key_GetBindingBuf,",
		"[CG_KEY_SETBINDING] = (ql_import_f)QL_CG_trap_Key_SetBinding,",
		"[CG_KEY_GETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_GetOverstrikeMode,",
		"[CG_KEY_SETOVERSTRIKEMODE] = (ql_import_f)QL_CG_trap_Key_SetOverstrikeMode,",
		"[CG_CMD_EXECUTETEXT] = (ql_import_f)QL_CG_trap_Cmd_ExecuteText,",
		"[CG_ADVERTISEMENTBRIDGE_INITCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_InitCGame,",
		"[CG_ADVERTISEMENTBRIDGE_SHUTDOWNCGAME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_ShutdownCGame,",
		"[CG_ADVERTISEMENTBRIDGE_UPDATELOADINGVIEWPARAMETERS] = (ql_import_f)QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters,",
		"[CG_ADVERTISEMENTBRIDGE_SETFRAMETIME] = (ql_import_f)QL_CG_trap_AdvertisementBridge_SetFrameTime,",
	):
		assert expected in client_source


def test_cgame_round_race_and_flag_ownerdraws_follow_retail_leaf_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	race_block = _block_from_marker(source, "static void CG_DrawRaceStatusAndTimes")
	round_timer_block = _block_from_marker(source, "static void CG_DrawRoundTimer")
	blue_flag_block = _block_from_marker(source, "static qboolean CG_ShowBlueTeamHasRedFlag")
	red_flag_block = _block_from_marker(source, "static qboolean CG_ShowRedTeamHasBlueFlag")
	visible_block = _block_from_marker(source, "qboolean CG_OwnerDrawVisible")

	for expected in (
		"if ( ownerDraw == CG_RACE_STATUS ) {",
		"text = CG_GetRaceStatusText();",
		"if ( ownerDraw != CG_RACE_TIMES ) {",
		"CG_RaceBuildTimesStrings( primary, sizeof( primary ), secondary, sizeof( secondary ) )",
		"CG_Text_Paint( rect->x, rect->y + rect->h + lineHeight, scale, color, secondary, 0, 0, textStyle );",
	):
		assert expected in race_block

	for expected in (
		"if ( cgs.matchRoundState != ROUNDSTATE_ACTIVE ) {",
		"if ( cgs.matchTimeoutActive ) {",
		"seconds = CG_GetScoreboardTimerSeconds();",
		'Com_sprintf( buffer, sizeof( buffer ), "%i:%i%i", seconds / 60, ( seconds % 60 ) / 10, seconds % 10 );',
	):
		assert expected in round_timer_block

	assert "CG_DrawLevelTimer(" not in round_timer_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"return ( cgs.redflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_RED ) ? qtrue : qfalse;",
	):
		assert expected in blue_flag_block

	for expected in (
		"cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF && cgs.gametype != GT_ATTACK_DEFEND",
		"return ( cgs.blueflag == FLAG_TAKEN || cgs.flagStatus == FLAG_TAKEN_BLUE ) ? qtrue : qfalse;",
	):
		assert expected in red_flag_block

	for expected in (
		"if (flags & (CG_SHOW_BLUE_TEAM_HAS_REDFLAG | CG_SHOW_RED_TEAM_HAS_BLUEFLAG)) {",
		"if (flags & CG_SHOW_BLUE_TEAM_HAS_REDFLAG && CG_ShowBlueTeamHasRedFlag()) {",
		"} else if (flags & CG_SHOW_RED_TEAM_HAS_BLUEFLAG && CG_ShowRedTeamHasBlueFlag()) {",
	):
		assert expected in visible_block

	for expected in (
		"case CG_RACE_STATUS:",
		"case CG_RACE_TIMES:",
		"CG_DrawRaceStatusAndTimes( &rect, scale, color, textStyle, ownerDraw );",
	):
		assert expected in source

	assert "static void CG_DrawRaceStatus(" not in source
	assert "static void CG_DrawRaceTimes(" not in source


def test_cgame_objective_status_ownerdraws_use_shared_team_status_leaf() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	shader_block = _block_from_marker(source, "static qhandle_t CG_GetTeamFlagStatusShader")
	team_status_block = _block_from_marker(source, "static void CG_DrawTeamFlagOrBaseStatus")
	objective_label_block = _block_from_marker(source, "static qboolean CG_BuildObjectiveStatusLabel")
	objective_draw_block = _block_from_marker(source, "static void CG_DrawObjectiveStatus")

	for expected in (
		"if ( cgs.gametype == GT_HARVESTER && !baseStatus ) {",
		"return ( team == TEAM_RED ) ? cgs.media.redCubeIcon : cgs.media.blueCubeIcon;",
		"if ( cgs.gametype == GT_1FCTF ) {",
		"if ( team == TEAM_RED && cgs.flagStatus == FLAG_TAKEN_RED ) {",
		"return cgs.media.flagShader[3];",
		"if ( cgs.gametype != GT_CTF && cgs.gametype != GT_ATTACK_DEFEND && cgs.gametype != GT_OBELISK ) {",
		"status = ( team == TEAM_RED ) ? cgs.redflag : cgs.blueflag;",
		"if ( baseStatus && status != FLAG_ATBASE ) {",
		"return ( team == TEAM_RED ) ? cgs.media.redFlagShader[status] : cgs.media.blueFlagShader[status];",
	):
		assert expected in shader_block

	for expected in (
		"if ( shader && !baseStatus && cgs.gametype != GT_1FCTF ) {",
		"handle = CG_GetTeamFlagStatusShader( team, baseStatus );",
		"CG_DrawPic( rect->x, rect->y, rect->w, rect->h, handle );",
	):
		assert expected in team_status_block

	for expected in (
		"if ( cgs.gametype == GT_ATTACK_DEFEND ) {",
		'Com_sprintf( buffer, bufferSize, "%s %s  %s %s",',
		"CG_GetTeamName( TEAM_RED ), CG_FlagStatusText( redStatus ),",
		"CG_GetTeamName( TEAM_BLUE ), CG_FlagStatusText( blueStatus ) );",
	):
		assert expected in objective_label_block

	assert "CG_BuildObjectiveStatusLabel( buffer, sizeof( buffer ) )" in objective_draw_block
	assert 'CG_Text_Paint( rect->x, rect->y + rect->h, scale, color, buffer, 0, 0, textStyle );' in objective_draw_block

	for expected in (
		"case CG_BLUE_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qfalse, shader );",
		"case CG_RED_FLAGSTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qfalse, shader );",
		"case CG_FLAG_STATUS:",
		"CG_DrawObjectiveStatus( &rect, scale, color, textStyle );",
		"case CG_RED_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_RED, qtrue, shader );",
		"case CG_BLUE_BASESTATUS:",
		"CG_DrawTeamFlagOrBaseStatus( &rect, TEAM_BLUE, qtrue, shader );",
	):
		assert expected in source

	assert "static void CG_DrawFlagStatusText(" not in source
	assert "static qboolean CG_BuildFlagStatusLabel(" not in source


def test_cgame_selected_player_and_placement_weapon_helpers_restore_retail_split() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	order_block = _block_from_marker(source, "void CG_CheckOrderPending()")
	selected_block = _block_from_marker(source, "static void CG_SetSelectedPlayerName()")
	next_block = _block_from_marker(source, "void CG_SelectNextPlayer()")
	prev_block = _block_from_marker(source, "void CG_SelectPrevPlayer()")
	weapon_block = _block_from_marker(source, "static weapon_t CG_GetPlacementMetricWeapon( int ownerDraw )")
	build_block = _block_from_marker(source, "static qboolean CG_BuildPlacementWeaponMetricText")

	for expected in (
		"if (cgs.gametype < GT_CTF) {",
		'trap_SendConsoleCommand( va( "teamtask %i\\n", cgs.currentOrder ) );',
		'trap_SendConsoleCommand( va( "cmd vsay_team %s\\n", p1 ) );',
		'trap_SendConsoleCommand( va( "cmd vtell %d %s\\n", sortedTeamPlayers[cg_currentSelectedPlayer.integer], p2 ) );',
		'trap_SendConsoleCommand(b);',
		"cgs.orderPending = qfalse;",
	):
		assert expected in order_block

	for expected in (
		'trap_Cvar_Set("cg_selectedPlayerName", ci->name);',
		'trap_Cvar_Set("cg_selectedPlayer", va("%d", sortedTeamPlayers[cg_currentSelectedPlayer.integer]));',
		"cgs.currentOrder = ci->teamTask;",
		'trap_Cvar_Set("cg_selectedPlayerName", "Everyone");',
	):
		assert expected in selected_block

	for expected in (
		"CG_CheckOrderPending();",
		"cg_currentSelectedPlayer.integer++;",
		"CG_SetSelectedPlayerName();",
	):
		assert expected in next_block

	for expected in (
		"CG_CheckOrderPending();",
		"cg_currentSelectedPlayer.integer--;",
		"CG_SetSelectedPlayerName();",
	):
		assert expected in prev_block

	for expected in (
		"if ( ownerDraw >= CG_2ND_PLYR_FRAGS_G && ownerDraw <= CG_2ND_PLYR_ACC_HMG ) {",
		"normalized = ownerDraw - ( CG_2ND_PLYR - CG_1ST_PLYR );",
		"case CG_1ST_PLYR_FRAGS_MG:",
		"case CG_1ST_PLYR_ACC_MG:",
		"return WP_MACHINEGUN;",
		"case CG_1ST_PLYR_FRAGS_CG:",
		"return WP_CHAINGUN;",
		"case CG_1ST_PLYR_FRAGS_NG:",
		"return WP_NAILGUN;",
		"case CG_1ST_PLYR_FRAGS_PL:",
		"return WP_PROX_LAUNCHER;",
		"case CG_1ST_PLYR_FRAGS_HMG:",
		"return WP_HEAVY_MACHINEGUN;",
		"return WP_NONE;",
	):
		assert expected in weapon_block

	for expected in (
		"weapon = CG_GetPlacementMetricWeapon( ownerDraw );",
		"if ( weapon == WP_NONE ) {",
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponFrags[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponHits[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponShots[weapon] );',
		'Com_sprintf( buffer, bufferSize, "%i", stats->weaponDamage[weapon] );',
		'shots = stats->weaponShots[weapon];',
		'hits = stats->weaponHits[weapon];',
	):
		assert expected in build_block
