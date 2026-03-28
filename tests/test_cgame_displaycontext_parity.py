"""Guard retail-backed cgame display-context bridge behavior against source drift."""

from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_EFFECTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_effects.c"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_DRAWTOOLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_drawtools.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_VIEW = REPO_ROOT / "src" / "code" / "cgame" / "cg_view.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_LOCALENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_localents.c"
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
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
	assert "CG_SetBrowserFeederSelection(menu, feeder, i);" in score_block
	assert "CG_SetBrowserFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore);" in score_block
	assert "Menu_SetFeederSelection(menu, feeder, i, NULL);" not in score_block
	assert "Menu_SetFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore, NULL);" not in score_block

	assert "CG_InitBrowserRuntime();" in load_hud_cmd_block
	assert "String_Init();" not in load_hud_cmd_block
	assert "Menu_Reset();" not in load_hud_cmd_block
	assert "menuScoreboard = NULL;" not in load_hud_cmd_block

	assert "CG_InitBrowserRuntime();" in cgame_init_block


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
	overtime_block = _block_from_marker(event_source, "static int CG_GetOvertimeCount")
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
