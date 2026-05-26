"""Guard the retail-backed cgame console surface against source drift."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
CG_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "cgamex86.dll" / "cgamex86.dll_hlil.txt"


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
	):
		assert expected in console_source


def test_retail_target_and_team_order_command_batch_is_hlil_anchored() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("tcmd", "CG_TargetCommand_f", "0x10006be0", "sub_10006be0"),
		("tell_target", "CG_TellTarget_f", "0x10006f50", "sub_10006f50"),
		("tell_attacker", "CG_TellAttacker_f", "0x10006ff0", "sub_10006ff0"),
		("vtell_target", "CG_VoiceTellTarget_f", "0x10007090", "sub_10007090"),
		("vtell_attacker", "CG_VoiceTellAttacker_f", "0x10007120", "sub_10007120"),
		("nextTeamMember", "CG_NextTeamMember_f", "0x100071c0", "sub_100071c0"),
		("prevTeamMember", "CG_PrevTeamMember_f", "0x100071f0", "sub_100071f0"),
		("taskOffense", "CG_TaskOffense_f", "0x10007380", "sub_10007380"),
		("taskCamp", "CG_TaskCamp_f", "0x10007470", "sub_10007470"),
		("taskRetrieve", "CG_TaskRetrieve_f", "0x100074f0", "sub_100074f0"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }},' in source
		assert functions[function]["address"].lower() == address
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	init_block = _block_from_marker(source, "void CG_InitConsoleCommands")
	assert "for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {" in init_block
	assert "trap_AddCommand( commands[i].cmd );" in init_block

	target_block = _block_from_marker(source, "void CG_TargetCommand_f")
	assert "targetNum = CG_CrosshairPlayer();" in target_block
	assert "trap_Argv( 1, test, 4 );" in target_block
	assert 'trap_SendConsoleCommand( va( "gc %i %i", targetNum, atoi( test ) ) );' in target_block

	tell_target_block = _block_from_marker(source, "static void CG_TellTarget_f")
	tell_attacker_block = _block_from_marker(source, "static void CG_TellAttacker_f")
	vtell_target_block = _block_from_marker(source, "static void CG_VoiceTellTarget_f")
	vtell_attacker_block = _block_from_marker(source, "static void CG_VoiceTellAttacker_f")
	for block, target_helper, command_format in (
		(tell_target_block, "CG_CrosshairPlayer", '"tell %i %s"'),
		(tell_attacker_block, "CG_LastAttacker", '"tell %i %s"'),
		(vtell_target_block, "CG_CrosshairPlayer", '"vtell %i %s"'),
		(vtell_attacker_block, "CG_LastAttacker", '"vtell %i %s"'),
	):
		assert f"clientNum = {target_helper}();" in block
		assert "if ( clientNum == -1 ) {" in block
		assert "trap_Args( message, 128 );" in block
		assert command_format in block
		assert "trap_SendClientCommand( command );" in block

	next_block = _block_from_marker(source, "static void CG_NextTeamMember_f")
	prev_block = _block_from_marker(source, "static void CG_PrevTeamMember_f")
	assert "CG_SelectNextPlayer();" in next_block
	assert "CG_SelectPrevPlayer();" in prev_block
	assert "CG_SpectatorFollowCycle" not in next_block
	assert "CG_SpectatorFollowCycle" not in prev_block

	task_offense_block = _block_from_marker(source, "static void CG_TaskOffense_f")
	task_camp_block = _block_from_marker(source, "static void CG_TaskCamp_f")
	task_retrieve_block = _block_from_marker(source, "static void CG_TaskRetrieve_f")
	assert "cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF" in task_offense_block
	assert "VOICECHAT_ONGETFLAG" in task_offense_block
	assert "VOICECHAT_ONOFFENSE" in task_offense_block
	assert "TEAMTASK_OFFENSE" in task_offense_block
	assert "VOICECHAT_ONCAMPING" in task_camp_block
	assert "TEAMTASK_CAMP" in task_camp_block
	assert "VOICECHAT_ONRETURNFLAG" in task_retrieve_block
	assert "TEAMTASK_RETRIEVE" in task_retrieve_block


def test_retail_score_stats_and_hud_command_batch_is_hlil_anchored() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("viewpos", "CG_Viewpos_f", "0x10006cb0", "sub_10006cb0"),
		("+scores", "CG_ScoresDown_f", "0x10006cf0", "sub_10006cf0"),
		("-scores", "CG_ScoresUp_f", "0x10006d40", "sub_10006d40"),
		("+acc", "CG_AccDown_f", "0x10006d60", "sub_10006d60"),
		("-acc", "CG_AccUp_f", "0x10006db0", "sub_10006db0"),
		("+pstats", "CG_PStatsDown_f", "0x10006dd0", "sub_10006dd0"),
		("-pstats", "CG_PStatsUp_f", "0x10006e20", "sub_10006e20"),
		("loadhud", "CG_LoadHud_f", "0x10006e40", "sub_10006e40"),
		("sizeup", "CG_SizeUp_f", "0x10006c50", "sub_10006c50"),
		("sizedown", "CG_SizeDown_f", "0x10006c80", "sub_10006c80"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }},' in source
		assert functions[function]["address"].lower() == address
		assert functions[function]["raw_name"] == raw_name
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	init_block = _block_from_marker(source, "void CG_InitConsoleCommands")
	assert "for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {" in init_block
	assert "trap_AddCommand( commands[i].cmd );" in init_block

	sizeup_block = _block_from_marker(source, "static void CG_SizeUp_f")
	sizedown_block = _block_from_marker(source, "static void CG_SizeDown_f")
	viewpos_block = _block_from_marker(source, "static void CG_Viewpos_f")
	assert 'trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer+10)));' in sizeup_block
	assert 'trap_Cvar_Set("cg_viewsize", va("%i",(int)(cg_viewsize.integer-10)));' in sizedown_block
	assert 'CG_Printf ("(%i %i %i) : %i\\n"' in viewpos_block
	assert "cg.refdef.vieworg[0]" in viewpos_block
	assert "cg.refdefViewAngles[YAW]" in viewpos_block

	score_down_block = _block_from_marker(source, "void CG_ScoresDown_f")
	score_up_block = _block_from_marker(source, "static void CG_ScoresUp_f")
	assert "CG_BuildSpectatorString();" in score_down_block
	assert "cg.scoresRequestTime + 2000 < cg.time" in score_down_block
	assert 'trap_SendClientCommand( "score" );' in score_down_block
	assert score_down_block.count("cg.showScores = qtrue;") == 1
	assert "cg.numScores = 0;" not in score_down_block
	assert "if ( cg.showScores ) {" in score_up_block
	assert "cg.showScores = qfalse;" in score_up_block
	assert "cg.scoreFadeTime = cg.time;" in score_up_block

	acc_down_block = _block_from_marker(source, "static void CG_AccDown_f")
	acc_up_block = _block_from_marker(source, "static void CG_AccUp_f")
	pstats_down_block = _block_from_marker(source, "static void CG_PStatsDown_f")
	pstats_up_block = _block_from_marker(source, "static void CG_PStatsUp_f")
	for block, latch, command in (
		(acc_down_block, "cg.accRequestActive", "acc"),
		(pstats_down_block, "cg_pstatsRequestActive", "pstats"),
	):
		assert "cg.snap->ps.pm_type == PM_SPECTATOR" in block
		assert "!( cg.snap->ps.pm_flags & PMF_FOLLOW )" in block
		assert "cg.accRequestTime + 1000 < cg.time" in block
		assert "cg.accRequestTime = cg.time;" in block
		assert f'trap_SendClientCommand( "{command}" );' in block
		assert f"{latch} = qtrue;" in block
	assert "cg.accRequestActive = qfalse;" in acc_up_block
	assert "cg_pstatsRequestActive = qfalse;" in pstats_up_block

	load_hud_block = _block_from_marker(source, "static void CG_LoadHud_f")
	assert "CG_InitBrowserRuntime();" in load_hud_block
	assert "CG_LoadHudMenu();" in load_hud_block
	assert load_hud_block.index("CG_InitBrowserRuntime();") < load_hud_block.index("CG_LoadHudMenu();")
	assert "Menu_Reset();" not in load_hud_block
	assert "String_Init();" not in load_hud_block


def test_retail_zoom_weapon_and_order_command_batch_is_hlil_anchored() -> None:
	console_source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	view_source = CG_VIEW.read_text(encoding="utf-8")
	weapons_source = CG_WEAPONS.read_text(encoding="utf-8")
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("+zoom", "CG_ZoomDown_f", "0x1004d5b0", "sub_1004d5b0"),
		("-zoom", "CG_ZoomUp_f", "0x1004d610", "sub_1004d610"),
		("weapnext", "CG_NextWeapon_f", "0x10053c40", "sub_10053c40"),
		("weapprev", "CG_PrevWeapon_f", "0x10053c50", "sub_10053c50"),
		("weapon", "CG_Weapon_f", "0x10053c60", "sub_10053c60"),
		("nextOrder", "CG_NextOrder_f", "0x10007220", "sub_10007220"),
		("confirmOrder", "CG_ConfirmOrder_f", "0x100072c0", "sub_100072c0"),
		("denyOrder", "CG_DenyOrder_f", "0x10007330", "sub_10007330"),
		("taskDefense", "CG_TaskDefense_f", "0x100073f0", "sub_100073f0"),
		("taskPatrol", "CG_TaskPatrol_f", "0x10007430", "sub_10007430"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }},' in console_source
		assert functions[function]["address"].lower() == address
		assert functions[function]["raw_name"] == raw_name
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	init_block = _block_from_marker(console_source, "void CG_InitConsoleCommands")
	assert "for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {" in init_block
	assert "trap_AddCommand( commands[i].cmd );" in init_block
	for expected in (
		"void CG_ZoomDown_f( void );",
		"void CG_ZoomUp_f( void );",
		"void CG_NextWeapon_f( void );",
		"void CG_PrevWeapon_f( void );",
		"void CG_Weapon_f( void );",
	):
		assert expected in local_source

	zoom_down_block = _block_from_marker(view_source, "void CG_ZoomDown_f")
	zoom_up_block = _block_from_marker(view_source, "void CG_ZoomUp_f")
	assert "pmType == PM_DEAD || pmType == PM_FREEZE" in zoom_down_block
	assert "if ( cg.zoomToggle ) {" in zoom_down_block
	assert "CG_SetZoomState( cg.zoomed ? qfalse : qtrue );" in zoom_down_block
	assert "CG_SetZoomState( qtrue );" in zoom_down_block
	assert "if ( cg.zoomToggle ) {" in zoom_up_block
	assert "return;" in zoom_up_block
	assert "CG_SetZoomState( qfalse );" in zoom_up_block

	cycle_block = _block_from_marker(weapons_source, "static void CG_CycleWeaponSelection")
	next_weapon_block = _block_from_marker(weapons_source, "void CG_NextWeapon_f")
	prev_weapon_block = _block_from_marker(weapons_source, "void CG_PrevWeapon_f")
	weapon_command_block = _block_from_marker(weapons_source, "void CG_Weapon_f")
	assert "CG_CycleWeaponSelection( qtrue );" in next_weapon_block
	assert "CG_CycleWeaponSelection( qfalse );" in prev_weapon_block
	for expected in (
		"if ( !cg.snap ) {",
		"if ( cg.snap->ps.pm_flags & PMF_FOLLOW ) {",
		"cg.weaponSelectTime = cg.time;",
		"selected = cg.weaponSelect;",
		"if ( selected == MAX_WEAPONS ) {",
		"selected = 0;",
		"if ( selected < 0 ) {",
		"selected = WP_NUM_WEAPONS;",
		"if ( selected == WP_GAUNTLET || selected == WP_NUM_WEAPONS ) {",
		"if ( CG_WeaponSelectable( selected ) ) {",
		"CG_SetWeaponSelect( selected );",
	):
		assert expected in cycle_block
	for expected in (
		'if ( !Q_stricmp( arg, "toggle" ) ) {',
		"num = cg_weaponTogglePrevious;",
		"if ( !CG_WeaponSelectable( num ) && !cg_switchToEmpty.integer ) {",
		"primaryWeapon = cg_weaponPrimary.integer;",
		"num = cg_weaponToggleFallback;",
		"num = atoi( arg );",
		"if ( num < 1 || num > 15 ) {",
		"if ( ! ( cg.snap->ps.stats[STAT_WEAPONS] & ( 1 << num ) ) ) {",
		"if ( !CG_WeaponSelectable( num ) ) {",
		"CG_SetWeaponSelect( num );",
	):
		assert expected in weapon_command_block

	next_order_block = _block_from_marker(console_source, "static void CG_NextOrder_f")
	confirm_order_block = _block_from_marker(console_source, "static void CG_ConfirmOrder_f")
	deny_order_block = _block_from_marker(console_source, "static void CG_DenyOrder_f")
	defense_block = _block_from_marker(console_source, "static void CG_TaskDefense_f")
	patrol_block = _block_from_marker(console_source, "static void CG_TaskPatrol_f")
	assert "CG_IsSpectatorInput" not in console_source
	for block in (next_order_block, confirm_order_block, deny_order_block):
		assert "PM_SPECTATOR" not in block
		assert "PERS_TEAM" not in block
		assert "PMF_FOLLOW" not in block
	for expected in (
		"clientInfo_t *ci = cgs.clientinfo + cg.snap->ps.clientNum;",
		"!ci->teamLeader && sortedTeamPlayers[cg_currentSelectedPlayer.integer] != cg.snap->ps.clientNum",
		"if (cgs.currentOrder < TEAMTASK_CAMP) {",
		"cgs.currentOrder++;",
		"if (cgs.currentOrder == TEAMTASK_RETRIEVE) {",
		"if (!CG_OtherTeamHasFlag()) {",
		"if (cgs.currentOrder == TEAMTASK_ESCORT) {",
		"if (!CG_YourTeamHasFlag()) {",
		"cgs.currentOrder = TEAMTASK_OFFENSE;",
		"cgs.orderPending = qtrue;",
		"cgs.orderTime = cg.time + 3000;",
	):
		assert expected in next_order_block
	for expected in (
		'trap_SendConsoleCommand( va( "cmd vtell %d %s\\n", cgs.acceptLeader, VOICECHAT_YES ) );',
		'trap_SendConsoleCommand("+button5; wait; -button5");',
		"if (cg.time < cgs.acceptOrderTime) {",
		'trap_SendClientCommand( va( "teamtask %d\\n", cgs.acceptTask ) );',
		"cgs.acceptOrderTime = 0;",
	):
		assert expected in confirm_order_block
	for expected in (
		'trap_SendConsoleCommand( va( "cmd vtell %d %s\\n", cgs.acceptLeader, VOICECHAT_NO ) );',
		'trap_SendConsoleCommand("+button6; wait; -button6");',
		"if (cg.time < cgs.acceptOrderTime) {",
		"cgs.acceptOrderTime = 0;",
	):
		assert expected in deny_order_block
	assert "VOICECHAT_ONDEFENSE" in defense_block
	assert "TEAMTASK_DEFENSE" in defense_block
	assert "VOICECHAT_ONPATROL" in patrol_block
	assert "TEAMTASK_PATROL" in patrol_block


def test_retail_task_taunt_and_orbit_command_batch_is_hlil_anchored() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("taskFollow", "CG_TaskFollow_f", "0x100074b0", "sub_100074b0"),
		("taskEscort", "CG_TaskEscort_f", "0x10007530", "sub_10007530"),
		("taskOwnFlag", "CG_TaskOwnFlag_f", "0x10007570", "sub_10007570"),
		("taskSuicide", "CG_TaskSuicide_f", "0x10007640", "sub_10007640"),
		("tauntKillInsult", "CG_TauntKillInsult_f", "0x100075a0", "sub_100075a0"),
		("tauntPraise", "CG_TauntPraise_f", "0x100075c0", "sub_100075c0"),
		("tauntTaunt", "CG_TauntTaunt_f", "0x100075e0", "sub_100075e0"),
		("tauntDeathInsult", "CG_TauntDeathInsult_f", "0x10007600", "sub_10007600"),
		("tauntGauntlet", "CG_TauntGauntlet_f", "0x10007620", "sub_10007620"),
		("startOrbit", "CG_StartOrbit_f", "0x10007bc0", "sub_10007bc0"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }},' in source
		assert functions[function]["address"].lower() == address
		assert functions[function]["raw_name"] == raw_name
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	init_block = _block_from_marker(source, "void CG_InitConsoleCommands")
	assert "for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {" in init_block
	assert "trap_AddCommand( commands[i].cmd );" in init_block

	task_follow_block = _block_from_marker(source, "static void CG_TaskFollow_f")
	task_escort_block = _block_from_marker(source, "static void CG_TaskEscort_f")
	task_own_flag_block = _block_from_marker(source, "static void CG_TaskOwnFlag_f")
	task_suicide_block = _block_from_marker(source, "static void CG_TaskSuicide_f")
	for block, voice, task in (
		(task_follow_block, "VOICECHAT_ONFOLLOW", "TEAMTASK_FOLLOW"),
		(task_escort_block, "VOICECHAT_ONFOLLOWCARRIER", "TEAMTASK_ESCORT"),
	):
		assert f"trap_SendConsoleCommand(va(\"cmd vsay_team %s\\n\", {voice}));" in block
		assert f"trap_SendClientCommand(va(\"teamtask %d\\n\", {task}));" in block
	assert 'trap_SendConsoleCommand(va("cmd vsay_team %s\\n", VOICECHAT_IHAVEFLAG));' in task_own_flag_block
	assert "trap_SendClientCommand" not in task_own_flag_block
	assert "clientNum = CG_CrosshairPlayer();" in task_suicide_block
	assert "if ( clientNum == -1 ) {" in task_suicide_block
	assert 'Com_sprintf( command, 128, "tell %i suicide", clientNum );' in task_suicide_block
	assert "trap_SendClientCommand( command );" in task_suicide_block

	taunt_expectations = (
		("static void CG_TauntKillInsult_f", 'trap_SendConsoleCommand("cmd vsay kill_insult\\n");'),
		("static void CG_TauntPraise_f", 'trap_SendConsoleCommand("cmd vsay praise\\n");'),
		("static void CG_TauntTaunt_f", 'trap_SendConsoleCommand("cmd vtaunt\\n");'),
		("static void CG_TauntDeathInsult_f", 'trap_SendConsoleCommand("cmd vsay death_insult\\n");'),
		("static void CG_TauntGauntlet_f", 'trap_SendConsoleCommand("cmd vsay kill_gauntlet\\n");'),
	)
	for marker, expected in taunt_expectations:
		assert expected in _block_from_marker(source, marker)

	start_orbit_block = _block_from_marker(source, "static void CG_StartOrbit_f")
	assert 'trap_Cvar_VariableStringBuffer( "developer", var, sizeof( var ) );' in start_orbit_block
	assert "if ( !atoi(var) ) {" in start_orbit_block
	assert "if (cg_cameraOrbit.value != 0) {" in start_orbit_block
	for expected in (
		'trap_Cvar_Set ("cg_cameraOrbit", "0");',
		'trap_Cvar_Set("cg_thirdPerson", "0");',
		'trap_Cvar_Set("cg_cameraOrbit", "5");',
		'trap_Cvar_Set("cg_thirdPerson", "1");',
		'trap_Cvar_Set("cg_thirdPersonAngle", "0");',
		'trap_Cvar_Set("cg_thirdPersonRange", "100");',
	):
		assert expected in start_orbit_block


def test_retail_deferred_drop_chat_ready_and_team_command_batch_is_hlil_anchored() -> None:
	console_source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	players_source = CG_PLAYERS.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("loaddeferred", "CG_LoadDeferredPlayers", "0x1003edd0", "sub_1003edd0"),
		("dropflag", "CG_DropFlag_f", "0x100076b0", "sub_100076b0"),
		("droppowerup", "CG_DropPowerup_f", "0x100076f0", "sub_100076f0"),
		("droprune", "CG_DropRune_f", "0x10007780", "sub_10007780"),
		("dropweapon", "CG_DropWeapon_f", "0x100077b0", "sub_100077b0"),
		("+chat", "CG_ChatDown_f", "0x10007cd0", "sub_10007cd0"),
		("-chat", "CG_ChatUp_f", "0x10007cf0", "sub_10007cf0"),
		("readyup", "CG_ReadyUp_f", "0x10007840", "sub_10007840"),
		("team", "CG_Team_f", "0x10007880", "sub_10007880"),
		("togglechathistory", "CG_ToggleChatHistory_f", "0x10007d10", "sub_10007d10"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }},' in console_source
		assert functions[function]["address"].lower() == address
		assert functions[function]["raw_name"] == raw_name
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	init_block = _block_from_marker(console_source, "void CG_InitConsoleCommands")
	assert "for ( i = 0 ; i < ARRAY_LEN( commands ) ; i++ ) {" in init_block
	assert "trap_AddCommand( commands[i].cmd );" in init_block

	load_deferred_block = _block_from_marker(players_source, "void CG_LoadDeferredPlayers")
	for expected in (
		"for ( i = 0, ci = cgs.clientinfo ; i < cgs.maxclients ; i++, ci++ ) {",
		"if ( ci->infoValid && ci->deferred ) {",
		"if ( trap_MemoryRemaining() < 4000000 ) {",
		'CG_Printf( "Memory is low.  Using deferred model.\\n" );',
		"ci->deferred = qfalse;",
		"CG_LoadClientInfo( ci );",
	):
		assert expected in load_deferred_block

	drop_flag_block = _block_from_marker(console_source, "static void CG_DropFlag_f")
	drop_powerup_block = _block_from_marker(console_source, "static void CG_DropPowerup_f")
	drop_rune_block = _block_from_marker(console_source, "static void CG_DropRune_f")
	drop_weapon_block = _block_from_marker(console_source, "static void CG_DropWeapon_f")
	assert "cgs.gametype != GT_CTF && cgs.gametype != GT_1FCTF" in drop_flag_block
	assert "cgs.gametype != GT_ATTACK_DEFEND" in drop_flag_block
	assert 'trap_SendClientCommand( "dropflag" );' in drop_flag_block
	for block, command in (
		(drop_powerup_block, "droppowerup"),
		(drop_weapon_block, "dropweapon"),
	):
		assert "if ( cgs.gametype < GT_TEAM ) {" in block
		assert "cgs.gametype == GT_CLAN_ARENA" in block
		assert "cgs.gametype == GT_DOMINATION" in block
		assert "cgs.gametype == GT_ATTACK_DEFEND" in block
		assert "cgs.gametype == GT_RED_ROVER" in block
		assert "if ( CG_IsInstaGibMode() ) {" in block
		assert f'trap_SendClientCommand( "{command}" );' in block
	assert "if ( cgs.gametype == GT_RACE ) {" in drop_rune_block
	assert 'trap_SendClientCommand( "droprune" );' in drop_rune_block

	chat_down_block = _block_from_marker(console_source, "static void CG_ChatDown_f")
	chat_up_block = _block_from_marker(console_source, "static void CG_ChatUp_f")
	toggle_chat_block = _block_from_marker(console_source, "static void CG_ToggleChatHistory_f")
	assert "cg.chatHistoryVisible = qtrue;" in chat_down_block
	assert "cg.chatHistoryVisible = qfalse;" in chat_up_block
	assert "cg.chatHistoryVisible = (qboolean)!cg.chatHistoryVisible;" in toggle_chat_block

	ready_block = _block_from_marker(console_source, "static void CG_ReadyUp_f")
	assert "allowIntermissionBypass = CG_IsRetailReadyUpIntermissionBypassActive();" in ready_block
	assert "if ( cg.warmup == 0 && !allowIntermissionBypass ) {" in ready_block
	assert "cgs.matchReadyUpDeadline" not in ready_block
	assert "ps->persistant[PERS_TEAM] == TEAM_SPECTATOR && !allowIntermissionBypass" in ready_block
	assert 'trap_SendClientCommand( "readyup" );' in ready_block

	team_block = _block_from_marker(console_source, "static void CG_Team_f")
	clear_capture_block = _block_from_marker(console_source, "static void CG_ClearRetailCommandCaptureState")
	assert "trap_Argv( 1, teamArg, sizeof( teamArg ) );" in team_block
	assert 'Com_sprintf( command, sizeof( command ), "team %s", teamArg );' in team_block
	assert "trap_SendClientCommand( command );" in team_block
	assert "CG_ClearRetailCommandCaptureState();" in team_block
	assert "cgs.eventHandling == CGAME_EVENT_TEAMMENU" in clear_capture_block
	assert "cgs.eventHandling == CGAME_EVENT_EDITHUD" in clear_capture_block
	assert "CG_EventHandling( CGAME_EVENT_NONE );" in clear_capture_block
	assert "trap_Key_SetCatcher( catcher & ~KEYCATCH_CGAME );" in clear_capture_block


def test_retail_final_command_tail_completes_main_table_coverage() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	symbol_map = json.loads(CG_SYMBOL_MAP.read_text(encoding="utf-8"))
	hlil = CG_HLIL.read_text(encoding="utf-8")
	functions = {entry["normalized_name"]: entry for entry in symbol_map["functions"]}
	command_batch = (
		("forfeit", "CG_Forfeit_f", "0x10007900", "sub_10007900"),
		("ragequit", "CG_RageQuit_f", "0x10007960", "sub_10007960"),
		("setteamcolor", "CG_SetTeamColor_f", "0x10007ba0", "sub_10007ba0"),
		("setenemycolor", "CG_SetEnemyColor_f", "0x10007bb0", "sub_10007bb0"),
		("print", "CG_Print_f", "0x10007d30", "sub_10007d30"),
		("kill", "CG_Kill_f", "0x10007e70", "sub_10007e70"),
		("clientmute", "CG_ClientMute_f", "0x10007e90", "sub_10007e90"),
	)

	for command, function, address, raw_name in command_batch:
		assert f'{{ "{command}", {function} }}' in source
		assert functions[function]["address"].lower() == address
		assert functions[function]["raw_name"] == raw_name
		assert functions[function]["status"] == "matched"
		assert f'{{"{command}"}}' in hlil
		assert f"= {raw_name}" in hlil

	table_block = source[
		source.index("static consoleCommand_t\tcommands[]"):
		source.index("static consoleCommand_t compatCommands[]")
	]
	registered_commands = {
		command for command, _function in re.findall(
			r'\{\s*"([^"]+)"\s*,\s*([A-Za-z0-9_]+)\s*\}', table_block
		)
	}
	covered_commands = {
		"viewpos", "+scores", "-scores", "+acc", "-acc", "+pstats", "-pstats",
		"+zoom", "-zoom", "sizeup", "sizedown", "weapnext", "weapprev", "weapon",
		"tell_target", "tell_attacker", "vtell_target", "vtell_attacker", "tcmd",
		"loadhud", "nextTeamMember", "prevTeamMember", "nextOrder", "confirmOrder",
		"denyOrder", "taskOffense", "taskDefense", "taskPatrol", "taskCamp",
		"taskFollow", "taskRetrieve", "taskEscort", "taskSuicide", "taskOwnFlag",
		"tauntKillInsult", "tauntPraise", "tauntTaunt", "tauntDeathInsult",
		"tauntGauntlet", "startOrbit", "loaddeferred", "dropflag", "droppowerup",
		"droprune", "dropweapon", "+chat", "-chat", "readyup", "team",
		"togglechathistory", "forfeit", "ragequit", "setteamcolor", "setenemycolor",
		"print", "kill", "clientmute",
	}
	assert len(registered_commands) == 57
	assert registered_commands == covered_commands

	forfeit_block = _block_from_marker(source, "static void CG_Forfeit_f")
	ragequit_block = _block_from_marker(source, "static void CG_RageQuit_f")
	set_color_block = _block_from_marker(source, "static void CG_SetColorCommand_f")
	set_team_block = _block_from_marker(source, "static void CG_SetTeamColor_f")
	set_enemy_block = _block_from_marker(source, "static void CG_SetEnemyColor_f")
	print_block = _block_from_marker(source, "static void CG_Print_f")
	kill_block = _block_from_marker(source, "static void CG_Kill_f")
	clientmute_block = _block_from_marker(source, "static void CG_ClientMute_f")

	assert "cgs.gametype == GT_FFA || cgs.gametype == GT_RACE" in forfeit_block
	assert "cgs.gametype == GT_RED_ROVER" in forfeit_block
	assert 'Com_Printf( "Forfeit is not available in %s.\\n", CG_GameTypeString() );' in forfeit_block
	assert 'trap_SendClientCommand( "forfeit" );' in forfeit_block
	assert 'trap_SendClientCommand( "ragequit" );' in ragequit_block
	assert "cg.rageQuitTime = 2;" in ragequit_block

	for expected in (
		"trap_Argv( 1, colorArg, sizeof( colorArg ) );",
		"if ( len > 3 ) {",
		"colorArg[3] = '\\0';",
		"CG_ApplyCommandColorString( useTeam, colorArg );",
	):
		assert expected in set_color_block
	assert "cg_teamColors" not in set_color_block
	assert "cg_enemyColors" not in set_color_block
	assert "CG_SetColorCommand_f( qtrue );" in set_team_block
	assert "CG_SetColorCommand_f( qfalse );" in set_enemy_block

	for expected in (
		"argc = trap_Argc();",
		"for ( i = 1; i < argc; i++ ) {",
		"trap_Argv( i, arg, sizeof( arg ) );",
		'Q_strcat( buffer, sizeof( buffer ), " " );',
		"Q_strcat( buffer, sizeof( buffer ), arg );",
		"CG_PushPrintString( buffer, SYSTEM_PRINT, 0 );",
	):
		assert expected in print_block
	assert "cg.killRespawnHintSuppressed = qtrue;" in kill_block
	assert 'trap_SendClientCommand( "kill" );' in kill_block

	for expected in (
		"if ( trap_Argc() < 2 ) {",
		"trap_Argv( 1, arg, sizeof( arg ) );",
		"clientNum = atoi( arg );",
		"if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {",
		"ci = &cgs.clientinfo[clientNum];",
		"if ( ( ci->identityLow | ci->identityHigh ) == 0 ) {",
		"trap_QL_ToggleClientMute( ci->identityLow, ci->identityHigh );",
	):
		assert expected in clientmute_block


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
		'trap_Cvar_Set( useTeam ? "cg_teamHeadColor" : "cg_enemyHeadColor", headColor );',
		'trap_Cvar_Set( useTeam ? "cg_teamUpperColor" : "cg_enemyUpperColor", upperColor );',
		'trap_Cvar_Set( useTeam ? "cg_teamLowerColor" : "cg_enemyLowerColor", lowerColor );',
	):
		assert expected in source
	assert "cg_teamColors" not in source
	assert "cg_enemyColors" not in source


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
		'static pmtype_t CG_GetRetailReadyUpPmType( void ) {',
		'return (pmtype_t)cg.snap->ps.pm_type;',
		'return (pmtype_t)cg.predictedPlayerState.pm_type;',
		'static qboolean CG_IsRetailReadyUpIntermissionBypassActive( void ) {',
		'CG_GetRetailReadyUpPmType() == PM_INTERMISSION',
		'static void CG_ReadyUp_f( void ) {',
		'allowIntermissionBypass = CG_IsRetailReadyUpIntermissionBypassActive();',
		'if ( cg.warmup == 0 && !allowIntermissionBypass ) {',
		'if ( !ps ) {',
		'ps->persistant[PERS_TEAM] == TEAM_SPECTATOR',
		'trap_SendClientCommand( "readyup" );',
	):
		assert expected in source

	for unexpected in (
		'static qboolean CG_IsRetailReadyUpPregameBypassActive( void ) {',
		'Info_ValueForKey( info, "g_training" );',
		'CG_ConfigString( CS_TUTORIAL_NAME )',
		'CG_ConfigString( CS_TUTORIAL_TEXT )',
		'cgs.matchReadyUpDeadline <= 0',
	):
		assert unexpected not in source


def test_browser_input_bridge_wraps_shared_display_dispatch() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	cursor_block = _block_from_marker(source, "static int CG_BrowserDisplayCursorType")
	move_block = _block_from_marker(source, "static qboolean CG_BrowserDisplayMouseMove")
	convert_x_block = _block_from_marker(source, "static int CG_ConvertScreenCursorXToVirtual")
	convert_y_block = _block_from_marker(source, "static int CG_ConvertScreenCursorYToVirtual")
	text_rect_block = _block_from_marker(source, "static rectDef_t *CG_BrowserCorrectedTextRect")
	active_block = _block_from_marker(source, "static qboolean CG_BrowserOverActiveItem")
	focused_block = _block_from_marker(source, "static void *CG_GetFocusedBrowserOverlay")
	handle_block = _block_from_marker(source, "static void CG_BrowserHandleKey")
	key_block = _block_from_marker(source, "static void CG_BrowserDisplayHandleKey")
	mouse_event_block = _block_from_marker(source, "void CG_MouseEvent")
	key_event_block = _block_from_marker(source, "void CG_KeyEvent")

	assert "return Display_CursorType( x, y );" in cursor_block
	assert "return Display_MouseMove( overlay, x, y );" in move_block
	assert "rect = item->textRect;" in text_rect_block
	assert "rect.y -= rect.h;" in text_rect_block
	assert "Rect_ContainsPoint( &menu->window.rect, x, y )" in active_block
	assert "item->window.flags & WINDOW_DECORATION" in active_block
	assert "Rect_ContainsPoint( CG_BrowserCorrectedTextRect( item ), x, y )" in active_block
	assert "return Menu_GetFocused();" in focused_block
	assert "Menus_HandleOOBClick( menu, key, down );" in handle_block
	assert "if ( down && key == K_F11 ) {" in handle_block
	assert 'trap_SendConsoleCommand( "screenshotJPEG\\n" );' in handle_block
	assert "Menu_HandleKey( menu, key, down );" in handle_block
	assert "cgDC.cursorx = x;" in key_block
	assert "cgDC.cursory = y;" in key_block
	assert "overlay = CG_GetFocusedBrowserOverlay();" in key_block
	assert "CG_BrowserHandleKey( overlay, key, down, 0 );" in key_block
	assert "( (float)x - cgs.screenXBias ) / cgs.screenXScale" in convert_x_block
	assert "(float)x * ( (float)SCREEN_WIDTH / (float)cgs.glconfig.vidWidth )" in convert_x_block
	assert "(float)y * ( (float)SCREEN_HEIGHT / (float)cgs.glconfig.vidHeight )" in convert_y_block

	assert "cgDC.cursorx = cgs.cursorX;" in mouse_event_block
	assert "cgDC.cursory = cgs.cursorY;" in mouse_event_block
	assert "cgs.cursorX = CG_ConvertScreenCursorXToVirtual( x );" in mouse_event_block
	assert "cgs.cursorY = CG_ConvertScreenCursorYToVirtual( y );" in mouse_event_block
	assert "cgs.cursorX = SCREEN_WIDTH;" in mouse_event_block
	assert "cgs.cursorY = SCREEN_HEIGHT;" in mouse_event_block
	assert "cgs.cursorX += x;" not in mouse_event_block
	assert "cgs.cursorY += y;" not in mouse_event_block
	assert "n = CG_BrowserDisplayCursorType( cgs.cursorX, cgs.cursorY );" in mouse_event_block
	assert "CG_BrowserDisplayMouseMove( NULL, cgs.cursorX, cgs.cursorY );" in mouse_event_block
	assert "cgs.capturedItem" not in mouse_event_block
	assert "Display_CursorType(" not in mouse_event_block
	assert "Display_MouseMove(" not in mouse_event_block

	assert "CG_BrowserDisplayHandleKey( key, down, cgs.cursorX, cgs.cursorY );" in key_event_block
	assert "Display_HandleKey(" not in key_event_block
	assert "Display_CaptureItem(" not in key_event_block
	assert "cgs.capturedItem =" not in key_event_block


def test_cgame_menu_script_stays_fullscreen_only_like_retail() -> None:
	source = CG_NEWDRAW.read_text(encoding="utf-8")
	run_block = _block_from_marker(source, "void CG_RunMenuScript")
	assert "CG_MenuScript_OpenScoreboard" not in source
	assert "CG_RequestScoreboard" not in source

	for expected in (
		'"setFullScreen"',
		'"setWindowed"',
		'"toggleFullscreen"',
		'trap_Cvar_Set( "r_fullScreen", "1" );',
		'trap_Cvar_Set( "r_fullScreen", "0" );',
		'fullscreen = ( trap_Cvar_VariableValue( "r_fullScreen" ) != 0.0f ) ? qtrue : qfalse;',
		'trap_SendConsoleCommand( "vid_restart fast\\n" );',
	):
		assert expected in run_block

	for unexpected in (
		"openScoreboard",
		"closeScoreboard",
		"spectatorFollow",
		"spectatorCamera",
		"hud_editToggle",
		"stopRefresh",
		"web_",
		"Unknown cgame menu script",
	):
		assert unexpected not in run_block


def test_voice_menu_timer_uses_retail_separate_latch() -> None:
	local_source = CG_LOCAL.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	draw_block = _block_from_marker(draw_source, "void CG_DrawTimedMenus")
	play_block = _block_from_marker(servercmds_source, "void CG_PlayVoiceChat")

	assert "int\t\t\tvoiceMenuTime;" in local_source
	assert "CG_ShowResponseHead" not in newdraw_source
	assert "if ( cg.voiceMenuTime ) {" in draw_block
	assert "int t = cg.time - cg.voiceMenuTime;" in draw_block
	assert 'Menus_CloseByName( "voiceMenu" );' in draw_block
	assert "cg.voiceMenuTime = 0;" in draw_block
	assert "cl_conXOffset" not in draw_block
	assert 'Menus_OpenByName( "voiceMenu" );' in play_block
	assert "cg.voiceMenuTime = cg.time;" in play_block
