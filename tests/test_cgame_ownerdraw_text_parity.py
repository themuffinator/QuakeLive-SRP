"""Guard retail-backed cgame ownerdraw text against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
UI_SHARED = REPO_ROOT / "src" / "code" / "ui" / "ui_shared.c"
MENUDEF_H = REPO_ROOT / "src" / "ui" / "menudef.h"
INTRO_MENU = REPO_ROOT / "src" / "ui" / "intro.menu"
ENDSCORETEAM_MENU = REPO_ROOT / "src" / "ui" / "endscoreteam.menu"
SPECTATOR_MENU = REPO_ROOT / "src" / "ui" / "spectator.menu"
SPECTATOR_FOLLOW_MENU = REPO_ROOT / "src" / "ui" / "spectator_follow.menu"
CGAME_HLIL = (
    REPO_ROOT
    / "references"
    / "hlil"
    / "quakelive"
    / "cgamex86.dll"
    / "cgamex86.dll_hlil.txt"
)
CGAME_GHIDRA = (
    REPO_ROOT
    / "references"
    / "reverse-engineering"
    / "ghidra"
    / "cgamex86"
    / "decompile_top_functions.c"
)


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


def _text_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def test_vertical_accuracy_overlay_keeps_retail_payload_and_row_wiring() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    stats_menu = (REPO_ROOT / "src" / "ui" / "ingamestats.menu").read_text(encoding="utf-8")
    order_block = _text_between(
        servercmds_source,
        "static const weapon_t cg_retailAccuracyCommandOrder[] = {",
        "static const cgRetailMapAlias_t",
    )
    vertical_order_block = _text_between(
        newdraw_source,
        "static const weapon_t cgVerticalAccWeaponOrder[] = {",
        "/*\n=============\nCG_ShouldDrawAccVertical",
    )
    parse_block = _block_from_marker(servercmds_source, "static void CG_ParseRetailAccuracyCommand")
    draw_weapons_block = _block_from_marker(newdraw_source, "static void CG_DrawWeaponVertical")
    draw_acc_block = _block_from_marker(newdraw_source, "static void CG_DrawAccVertical")
    ownerdraw_block = _block_from_marker(newdraw_source, "void CG_OwnerDraw(")

    for expected in (
        "WP_NONE",
        "WP_GAUNTLET",
        "WP_GRAPPLING_HOOK",
        "WP_HEAVY_MACHINEGUN",
    ):
        assert expected in order_block

    for expected in (
        "WP_GAUNTLET",
        "WP_MACHINEGUN",
        "WP_SHOTGUN",
        "WP_GRENADE_LAUNCHER",
        "WP_ROCKET_LAUNCHER",
        "WP_LIGHTNING",
        "WP_RAILGUN",
        "WP_PLASMAGUN",
        "WP_BFG",
        "WP_CHAINGUN",
        "WP_NAILGUN",
        "WP_PROX_LAUNCHER",
        "WP_HEAVY_MACHINEGUN",
    ):
        assert expected in vertical_order_block

    assert "WP_NONE" not in vertical_order_block
    assert "WP_GRAPPLING_HOOK" not in vertical_order_block
    assert "memset( cg.weaponAccuracies, 0, sizeof( cg.weaponAccuracies ) );" in parse_block
    assert "value = atoi( CG_Argv( i + 1 ) );" in parse_block
    assert "cg.weaponAccuracies[weapon] = value;" in parse_block
    assert "value < 0" not in parse_block
    assert "value > 100" not in parse_block
    assert "CG_DrawPic( rect->x, rect->y + rect->h * i, rect->w, rect->w, icon );" in draw_weapons_block
    assert "Com_sprintf( buffer, sizeof( buffer ), \"%i%%\", cg.weaponAccuracies[weapon] );" in draw_acc_block
    assert "CG_Text_Paint( rect->x, rect->y + rect->h * i, scale, color, buffer, 0, 0, textStyle );" in draw_acc_block
    assert "rect->h * ( i + 1 )" not in draw_acc_block

    assert "#define\tCG_WP_VERTICAL\t\t\t\t\t\t97" in menudef_source
    assert "#define\tCG_ACC_VERTICAL\t\t\t\t\t\t98" in menudef_source
    assert "ownerdraw CG_WP_VERTICAL" in stats_menu
    assert "ownerdraw CG_ACC_VERTICAL" in stats_menu
    assert "case CG_WP_VERTICAL:" in ownerdraw_block
    assert "CG_DrawWeaponVertical( &rect, color );" in ownerdraw_block
    assert "case CG_ACC_VERTICAL:" in ownerdraw_block
    assert "CG_DrawAccVertical( &rect, scale, color, textStyle );" in ownerdraw_block


def test_game_limit_uses_retail_limit_strings() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
    ui_shared_source = UI_SHARED.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    endscoreteam_menu = ENDSCORETEAM_MENU.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawGameLimit")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    parse_serverinfo_block = _block_from_marker(servercmds_source, "void CG_ParseServerinfo")
    item_ownerdraw_parse_block = _block_from_marker(ui_shared_source, "qboolean ItemParse_ownerdraw( itemDef_t")
    retail_block = _text_between(
        hlil_source,
        '10033800    int32_t __convention("regparm") sub_10033800',
        "10033910",
    )
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0(")

    for expected in (
        '"Cap Limit: %d"',
        '"Frag Limit: %d"',
        '"Round Limit: %d"',
        '"Score Limit: %d"',
        "data_10a3ff38",
        "data_10a3ff48",
        "data_10a3ff54",
        "data_10a3ff34",
        "if (arg8 == 1)",
        "sub_100082b0(0, 0, result, &var_4, nullptr, 0, fconvert.s(fconvert.t(arg5)))",
        "var_4 = fconvert.s(x87_r7_5 - float.t(var_4))",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_block

    assert "arg4[3]" not in retail_block

    for expected in (
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_OBELISK:",
        "case GT_HARVESTER:",
        'Com_sprintf( buffer, sizeof( buffer ), "Cap Limit: %d", cgs.capturelimit );',
        "case GT_CLAN_ARENA:",
        "case GT_FREEZE:",
        "case GT_RED_ROVER:",
        'Com_sprintf( buffer, sizeof( buffer ), "Round Limit: %d", cgs.roundlimit );',
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        'Com_sprintf( buffer, sizeof( buffer ), "Score Limit: %d", cgs.scorelimit );',
        'Com_sprintf( buffer, sizeof( buffer ), "Frag Limit: %d", cgs.fraglimit );',
        "if ( align == ITEM_ALIGN_CENTER ) {",
        "x -= CG_Text_Width( buffer, scale, 0 ) * 0.5f;",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in block

    for stale in (
        "Time %i",
        "Captures %i",
        "Score %i",
        "Frags %i",
        "Mercy %i",
        "CG_GetServerInfoValue",
        "CG_HasObjectiveCountStat",
        "limitValue > 0",
        "CG_GetTextPosition",
        "ITEM_ALIGN_RIGHT",
        "rect->y + rect->h",
    ):
        assert stale not in block

    start = ownerdraw_block.index("case CG_GAME_LIMIT:")
    end = ownerdraw_block.index("break;", start)
    game_limit_case = ownerdraw_block[start:end]
    assert "CG_DrawGameLimit( &rect, scale, color, textStyle, align );" in game_limit_case
    assert "FUN_10033800(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

    for expected in (
		"cgs.fraglimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_FRAGLIMIT ) );",
		"cgs.capturelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_CAPTURELIMIT ) );",
		"cgs.scorelimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_SCORELIMIT ) );",
		"cgs.roundlimit = atoi( Info_ValueForKey( info, SERVERINFO_KEY_ROUNDLIMIT ) );",
    ):
        assert expected in parse_serverinfo_block

    assert any(line.split() == ["#define", "CG_GAME_LIMIT", "3"] for line in menudef_source.splitlines())
    assert '#include "ui/menudef.h"' in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in intro_menu
    assert '#include "ui/menudef.h"' in endscoreteam_menu
    assert "ownerdraw CG_GAME_LIMIT" in endscoreteam_menu
    assert "PC_Int_Parse(handle, &item->window.ownerDraw)" in item_ownerdraw_parse_block
    assert "item->type = ITEM_TYPE_OWNERDRAW;" in item_ownerdraw_parse_block
    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "CG_GAME_LIMIT" not in width_block


def test_match_end_condition_uses_retail_condition_strings() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    end_condition_menu_hits = [
        path
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
        if "ownerdraw CG_MATCH_END_CONDITION" in path.read_text(encoding="utf-8")
    ]
    block = _block_from_marker(source, "static void CG_DrawMatchEndCondition")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_block = _text_between(
        hlil_source,
        '10034280    int32_t __convention("regparm") sub_10034280',
        "10034360",
    )
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")

    for expected in (
        '"Fastest race time within the time limit"',
        '"Most flag captures within the time limit"',
        '"Most rounds won within the time limit"',
        '"Highest score within the time limit"',
        '"First to reach the capture limit"',
        '"First to reach the mercy limit"',
        '"First to reach the round limit"',
        '"First to reach the score limit"',
        '"Highest score at the end of the game"',
    ):
        assert expected in hlil_source

    for expected in (
        "data_10a3ff14",
        "data_10a3ff44",
        "data_10a3ff38",
        "data_10a403ec",
        "data_10a403f0",
    ):
        assert expected in retail_block

    for expected in (
        "if ( cgs.gametype == GT_RACE ) {",
        'reason = "Fastest race time within the time limit";',
        "timeLimitExpired = ( cgs.timelimit > 0",
        "&& cg.time - cgs.levelStartTime >= cgs.timelimit * 60000 ) ? qtrue : qfalse;",
        'reason = "Most flag captures within the time limit";',
        'reason = "Most rounds won within the time limit";',
        'reason = "Highest score within the time limit";',
        "if ( cgs.capturelimit == 0 || ( cgs.scores1 < cgs.capturelimit && cgs.scores2 < cgs.capturelimit ) ) {",
        'reason = "First to reach the mercy limit";',
        'reason = "First to reach the capture limit";',
        'reason = "First to reach the round limit";',
        'reason = "First to reach the score limit";',
        'reason = "Highest score at the end of the game";',
        "CG_Text_Paint( rect->x, rect->y, scale, color, reason, 0, 0, textStyle );",
    ):
        assert expected in block

    assert any(line.split()[:3] == ["#define", "CG_MATCH_END_CONDITION", "9"] for line in menudef_source.splitlines())
    assert len(end_condition_menu_hits) >= 10
    assert "case 9:" in retail_ownerdraw_block
    assert "FUN_10034280(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "case CG_MATCH_END_CONDITION:" in ownerdraw_block
    assert "CG_DrawMatchEndCondition( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawMatchEndCondition(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block

    for stale in (
        "Match complete",
        "Time limit hit",
        "Capture limit hit",
        "Score limit hit",
        "Frag limit hit",
        "Mercy rule",
        "Sudden death",
        "CG_TimeLimitHit",
        "CG_FragLimitHit",
        "CG_CaptureLimitHit",
        "CG_ScoreLimitHit",
        "CG_MercyLimitHit",
        "CG_GetTextPosition",
    ):
        assert stale not in block


def test_local_time_uses_retail_date_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawLocalTime")

    assert "static const char *cgMonthAbbrev[12]" in source
    assert '%02d:%02d (%s %02d, %d)' in block
    assert "x = rect->x;" in block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in block
    assert "CG_GetTextPosition" not in block
    assert '%02i:%02i' not in block


def test_spectator_messages_use_retail_copy_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    spectator_menu = SPECTATOR_MENU.read_text(encoding="utf-8")
    spectator_follow_menu = SPECTATOR_FOLLOW_MENU.read_text(encoding="utf-8")
    block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_block = _text_between(
        hlil_source,
        "10034d70    int32_t __fastcall sub_10034d70",
        "100350c0",
    )
    retail_decompile = _text_between(
        ghidra_source,
        "/* FUN_10034d70 @ 10034d70",
        "/* FUN_10005e60",
    )
    retail_switch = _text_between(ghidra_source, "case 0x23:", "case 0x24:")

    for expected in (
        "vec4_t spectatorHintColor = { 0.73f, 0.73f, 0.73f, 0.7f };",
        "(void)scale;",
        "(void)color;",
        "(void)textStyle;",
        "if ( !rect || !cg.snap || !cg_drawSpecMessages.integer ) {",
        "cgs.gametype == GT_CLAN_ARENA || cgs.gametype == GT_RED_ROVER",
        "cg.snap->ps.pm_type == PM_SPECTATOR",
        "cg.snap->ps.persistant[PERS_TEAM] != TEAM_SPECTATOR",
        "Round In Progress",
        "x = 320.0f - (float)CG_Text_Width( message, 0.35f, 0 ) * 0.5f;",
        "CG_Text_Paint( x, 60.0f, 0.35f, colorWhite, message, 0, 0, 3 );",
        'CG_Text_Paint( rect->x, rect->y, 0.22f, colorWhite, "SPECTATOR MODE", 0, 0, 0 );',
        "SPECTATOR MODE",
        'CG_Text_Paint( rect->x, rect->y + 12.0f, 0.18f, spectatorHintColor, "Press mouse button 1 to cycle through players", 0, 0, 0 );',
        "Press mouse button 1 to cycle through players",
        'trap_Key_GetBindingBuf( trap_Key_GetKey( "+moveup" ), bindingBuf, sizeof( bindingBuf ) );',
        'CG_FindBrowserOverlayByName( "comp_specfollowhud_menu" )',
        "!cgs.clientinfo[cg.clientNum].spectateOnly",
        'CG_Text_Paint( 20.0f, 461.0f, 0.28f, colorWhite, "waiting to play", 0, 0, 3 );',
        "waiting to play",
        'CG_Text_Paint( 20.0f, 453.0f, 0.28f, colorWhite, "press ESC and use the JOIN buttons", 0, 0, 3 );',
        "press ESC and use the JOIN buttons",
        'CG_Text_Paint( 20.0f, 470.0f, 0.28f, colorWhite, "to enter the game", 0, 0, 3 );',
        "to enter the game",
    ):
        assert expected in block

    for expected in (
        "eax_2 == 4 || eax_2 == 0xb",
        "*(ecx + 0x30) == 2",
        "*(ecx + 0x138) != 3",
        "data_10aa6934 == 0",
        'sub_100575e0("SPECTATOR MODE")',
        '(*(data_1074cccc + 0x184))("+moveup")',
        "data_10ab9688 == 0 ||",
        "data_10a42404 == 0",
    ):
        assert expected in retail_block

    for expected in (
        '"Press mouse button 1 to cycle through players"',
        '"press ESC and use the JOIN buttons"',
        '"to enter the game"',
    ):
        assert expected in hlil_source
    assert '"Press mouse button 1 to cycle through players"' in retail_decompile

    assert "FUN_10034d70();" in retail_switch
    assert "case CG_SPEC_MESSAGES:" in ownerdraw_block
    assert "CG_DrawSpectatorMessages( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "#define\tCG_SPEC_MESSAGES" in menudef_source
    assert spectator_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2
    assert spectator_follow_menu.count("ownerdraw CG_SPEC_MESSAGES") == 2

    for stale in (
        "FOLLOWING %s",
        "FREE SPECTATE",
        "Press FIRE to cycle, JUMP for free camera",
        "Press FIRE to follow a player",
        "press ESC and use the JOIN menu to play",
        "CG_DrawPregameCoach(rect",
        "case GT_FREEZE:",
        "case GT_ATTACK_DEFEND:",
        "cgs.matchRoundState",
        "scale * 0.8f",
    ):
        assert stale not in block


def test_level_timer_uses_retail_clock_format() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    draw_source = CG_DRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    helper_block = _block_from_marker(source, "static qboolean CG_BuildLevelTimerMilliseconds")
    block = _block_from_marker(source, "static void CG_DrawLevelTimer")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    classic_timer_block = _block_from_marker(draw_source, "static float CG_DrawTimer")
    retail_timer_block = _text_between(
        hlil_source,
        "10030c00    void sub_10030c00",
        "10030d20",
    )
    retail_clock_block = _text_between(
        hlil_source,
        "10029770    int32_t sub_10029770()",
        "10029820",
    )

    for expected in (
        "sub_10029770() == 1",
        'sub_100575e0("%i:%i%i")',
        "if (eax_9 == 1)",
        "else if (eax_9 != 2)",
        "fconvert.t(eax_12[1])",
    ):
        assert expected in retail_timer_block

    for expected in (
        "int32_t edx = data_10a403e0",
        "if (edx == 0)",
        "edx = data_10a9c1ec",
        "if (data_10ab8f4c != 0)",
        "data_10ab8f58 == 0",
        "int32_t ecx_1 = esi * 0xea60",
        "int32_t eax_7 = ecx_1 - edx + edi",
        "*ebx = edx - ecx_1 - edi",
        "if (data_10a6e6ac != 1)",
        "eax_7 = edx - edi",
    ):
        assert expected in retail_clock_block

    for expected in (
        "timeoutStart = CG_GetMatchTimeoutStartTime();",
        "currentTime = timeoutStart;",
        "if ( currentTime == 0 ) {",
        "currentTime = cg.time;",
        "if ( cg.warmup != 0 ) {",
        "if ( !CG_ShowPlayersRemaining() || cgs.matchRoundNumber <= 0 ) {",
        "return qfalse;",
        "limitMilliseconds = cgs.timelimit * 60000;",
        "milliseconds = limitMilliseconds - currentTime + cgs.levelStartTime;",
        "milliseconds = currentTime - limitMilliseconds - cgs.levelStartTime;",
        "else if ( cg_levelTimerDirection.integer != 1 ) {",
        "milliseconds = currentTime - cgs.levelStartTime;",
        "*millisecondsOut = milliseconds;",
        "return qtrue;",
    ):
        assert expected in helper_block

    for expected in (
        "CG_BuildLevelTimerMilliseconds( &milliseconds );",
        "seconds = milliseconds / 1000;",
        'Q_strncpyz( buffer, CG_FormatMinutesSeconds( seconds ), sizeof( buffer ) );',
        "x = rect->x;",
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in block

    assert "CG_DrawLevelTimer(&rect, scale, color, textStyle, align);" in ownerdraw_block
    assert '{ &cg_levelTimerDirection, "cg_levelTimerDirection", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },' in main_source
    assert "cg_levelTimerDirection.integer == 1" in classic_timer_block

    for stale in (
        "CG_GetScoreboardTimerSeconds",
        "rect->y + rect->h",
        "( elapsed + 500 ) / 1000",
        "( milliseconds + 500 ) / 1000",
        '%02i:%02i',
        '"up"',
        '"down"',
    ):
        assert stale not in block


def test_intro_panel_draws_use_retail_map_panel_shapes() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    match_details_menu_hits = [
        path
        for path in (REPO_ROOT / "src" / "ui").glob("*.menu")
        if "ownerdraw CG_MATCH_DETAILS" in path.read_text(encoding="utf-8")
    ]
    game_type_map = _block_from_marker(source, "static void CG_DrawGameTypeMap")
    match_details = _block_from_marker(source, "static void CG_DrawMatchDetails")
    phase_label = _block_from_marker(source, "static const char *CG_GetMatchPhaseText")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    retail_match_details = _text_between(
        hlil_source,
        '10034420    int32_t __convention("regparm") sub_10034420',
        "100344b0",
    )
    retail_game_type_map = _text_between(
        hlil_source,
        "100344b0    void sub_100344b0",
        "10034590",
    )

    assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in game_type_map
    assert '%s - %s", CG_GameTypeString(), detailBuffer' in game_type_map
    assert "x = rect->x;" in game_type_map
    assert "CG_AlignTextX( &x, buffer, scale, align );" in game_type_map
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in game_type_map
    assert 'CG_GetMapDisplayName( mapName, sizeof( mapName ) );' not in game_type_map
    assert '%s - %s - %s' not in game_type_map
    assert "CG_GetTextPosition" not in game_type_map

    for expected in (
        "eax_2, ecx_1 = sub_100575e0(\"%s - %s\")",
        "if (arg5 == 1)",
        "*ebp = fconvert.s(fconvert.t(*ebp) - float.t(arg1) * fconvert.t(0.5))",
        "else if (arg5 == 2)",
        "*ebp = fconvert.s(fconvert.t(*ebp) - float.t(arg1))",
    ):
        assert expected in retail_game_type_map

    assert "CG_BuildIntroPanelDetailString( detailBuffer, sizeof( detailBuffer ) );" in match_details
    assert 'CG_GetMatchPhaseText()' in match_details
    assert 'CG_GameTypeShortString(), detailBuffer );' in match_details
    assert '%s - %s - %s' in match_details
    assert "CG_Text_PaintExt( rect->x, rect->y, scale, color, buffer, 0, 0, ITEM_TEXTSTYLE_NORMAL, FONT_DEFAULT );" in match_details
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" not in match_details
    assert '%s - %s - %s - %s' not in match_details
    assert 'CG_GetMapDisplayName( mapName, sizeof( mapName ) );' not in match_details
    assert "CG_GetTextPosition" not in match_details
    assert 'sub_100575e0("%s - %s - %s")' in retail_match_details
    assert "sub_10008440(fconvert.s(fconvert.t(var_4)), fconvert.s(fconvert.t(var_8)), 0," in retail_match_details
    assert "fconvert.s(float.t(0)), 0)" in retail_match_details

    for expected in (
        'MATCH WARMUP',
        'MATCH IN PROGRESS',
        'MATCH SUMMARY',
    ):
        assert expected in phase_label

    assert "CG_GetMatchDetailsPhaseLabel" not in source
    assert any(line.split()[:3] == ["#define", "CG_MATCH_DETAILS", "8"] for line in menudef_source.splitlines())
    assert len(match_details_menu_hits) >= 10
    assert "case 8:" in retail_ownerdraw_block
    assert "FUN_10034420(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "CG_DrawGameTypeMap( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "case CG_MATCH_DETAILS:" in ownerdraw_block
    assert "CG_DrawMatchDetails( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawGameTypeMap(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block
    assert "CG_DrawMatchDetails(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block


def test_intro_panel_gametype_tables_match_retail_labels() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    short_labels = _block_from_marker(source, "static const char *CG_GameTypeShortString")
    full_labels = _block_from_marker(source, "const char *CG_GameTypeString()")

    for expected in (
        'return "DUEL";',
        'return "RACE";',
        'return "1F";',
        'return "OB";',
        'return "HAR";',
        'return "FT";',
        'return "DOM";',
        'return "AD";',
        'return "RR";',
        'return "Unknown Gametype";',
    ):
        assert expected in short_labels

    assert 'return "Attack and Defend";' in full_labels
    assert 'Attack & Defend' not in source


def test_plain_gametype_and_match_state_draws_use_retail_origin_alignment() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    game_type = _block_from_marker(source, "static void CG_DrawGameType( rectDef_t")
    match_state = _block_from_marker(source, "static void CG_DrawMatchState")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_game_type = _text_between(
        hlil_source,
        "10034c20    int32_t sub_10034c20",
        "10034cc0",
    )
    retail_match_state = _text_between(
        hlil_source,
        "10034360    int32_t sub_10034360",
        "100343d0",
    )

    for expected in (
        "if (arg5 == 1)",
        "sub_100082b0(0, 0, ebx, &arg1, nullptr, 0, fconvert.s(fconvert.t(arg2)))",
        "float var_28 = fconvert.s(fconvert.t(*(ebp + 4)))",
        "return sub_10008440(fconvert.s(fconvert.t(arg1)), var_28, 0,",
    ):
        assert expected in retail_game_type
    assert "else if (arg5 == 2)" not in retail_game_type

    for expected in (
        "gameType = CG_GameTypeString();",
        "x = rect->x;",
        "if ( align == ITEM_ALIGN_CENTER ) {",
        "x -= CG_Text_Width( gameType, scale, 0 ) * 0.5f;",
        "CG_Text_Paint( x, rect->y, scale, color, gameType, 0, 0, textStyle );",
    ):
        assert expected in game_type
    assert "ITEM_ALIGN_RIGHT" not in game_type
    assert "rect->y + rect->h" not in game_type
    assert "qhandle_t shader" not in game_type
    assert "CG_DrawGameType( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "CG_DrawGameType(&rect, scale, color, shader, textStyle);" not in ownerdraw_block

    assert "fconvert.s(fconvert.t(arg1[1]))" in retail_match_state
    assert "arg1[3]" not in retail_match_state
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_GetMatchPhaseText(), 0, 0, textStyle );" in match_state
    assert "rect->y + rect->h" not in match_state


def test_match_status_uses_retail_status_text_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    status_text = _block_from_marker(source, "const char *CG_GetGameStatusText")
    status_helper = _block_from_marker(source, "const char *CG_GetMatchStatusText")
    draw_match_status = _block_from_marker(source, "static void CG_DrawMatchStatus")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_draw_match_status = _text_between(
        hlil_source,
        "10034cc0    void sub_10034cc0",
        "10034d70",
    )
    retail_status_helper = _text_between(
        hlil_source,
        "10034a00    char const* const sub_10034a00()",
        "10034b30",
    )

    assert "case GT_SINGLE_PLAYER:" in status_text
    assert "case GT_RED_ROVER:" in status_text
    assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in status_text
    assert '"Teams are tied at %i"' in status_text
    assert '"^1Red^7 leads ^4Blue^7, %i to %i"' in status_text
    assert '"^4Blue^7 leads ^1Red^7, %i to %i"' in status_text
    assert '"Red leads Blue, %i to %i"' not in status_text
    assert '"Blue leads Red, %i to %i"' not in status_text
    assert "cgs.gametype < GT_TEAM" not in status_text

    assert "phase = CG_GetMatchPhaseText();" in status_helper
    assert 'phase = "MATCH SUMMARY";' not in status_helper
    assert 'phase = "MATCH WARMUP";' not in status_helper
    assert 'phase = "MATCH IN PROGRESS";' not in status_helper
    assert "if ( cgs.scores1 == SCORE_NOT_PRESENT && cgs.scores2 == SCORE_NOT_PRESENT &&" in status_helper
    assert "( cgs.gametype < GT_TEAM || cgs.gametype == GT_RED_ROVER )" in status_helper
    assert "if ( cgs.gametype == GT_RACE ) {" in status_helper
    assert "CG_FormatSignedMilliseconds( cgs.scores1 )" in status_helper
    assert '"%s - %s^7 leads with a score of %s"' in status_helper
    assert "if ( cgs.gametype >= GT_TEAM && cgs.gametype != GT_RED_ROVER ) {" in status_helper
    assert '"%s - Teams are tied at %i"' in status_helper
    assert '"%s - ^1Red^7 leads ^4Blue^7, %i to %i"' in status_helper
    assert '"%s - ^4Blue^7 leads ^1Red^7, %i to %i"' in status_helper
    assert "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR" in status_helper
    assert "if ( cgs.scores1 != CG_SCORE_FORFEIT ) {" in status_helper
    assert "if ( cgs.scores1 != SCORE_NOT_PRESENT ) {" not in status_helper
    assert "leaderName = cgs.firstPlaceName;" in status_helper
    assert "leaderName = cgs.secondPlaceName;" in status_helper
    assert '"%s - %s leads with %i"' in status_helper
    assert '"%s - %s place with %i"' in status_helper
    assert "CG_GetGameStatusText()" not in status_helper
    assert "if ( !status || !status[0] )" not in status_helper

    assert "statusText = CG_GetMatchStatusText();" in draw_match_status
    assert "x = rect->x;" in draw_match_status
    assert "CG_AlignTextX( &x, statusText, scale, align );" in draw_match_status
    assert "CG_Text_Paint( x, rect->y, scale, color, statusText, 0, 0, textStyle );" in draw_match_status
    assert 'Com_sprintf( buffer, sizeof( buffer ), "%s - %s", CG_GetMatchStateLabel(), CG_GetGameStatusText() );' not in draw_match_status
    assert "if ( !cg.snap ) {" not in draw_match_status
    assert "CG_GetTextPosition" not in draw_match_status
    assert any(line.split()[:3] == ["#define", "CG_MATCH_STATUS", "10"] for line in menudef_source.splitlines())
    assert "ownerdraw CG_MATCH_STATUS" in intro_menu
    assert "case CG_MATCH_STATUS:" in ownerdraw_block
    assert "CG_DrawMatchStatus( &rect, scale, color, textStyle, align );" in ownerdraw_block
    assert "CG_DrawMatchStatus(&rect, text_x, text_y, scale, color, textStyle);" not in ownerdraw_block

    for expected in (
        "if (esi == edx && esi == 0xffffd8f1 && (eax s< 3 || eax == 0xc))",
        "if (eax == 2)",
        'var_18 = " - %s^7 leads with a score of %s"',
        "else if (eax s>= 3 && eax != 0xc)",
        'var_18 = " - ^4Blue^7 leads ^1Red^7, %i to',
        'var_18 = " - ^1Red^7 leads ^4Blue^7, %i to',
        "if (*(edi + 0x138) == 3)",
        "if (esi != 0xfffffc19)",
        'var_18 = " - %s leads with %i"',
        'var_18 = " - %s place with %i"',
    ):
        assert expected in retail_status_helper

    for expected in (
        "char* eax = sub_10034a00()",
        "int32_t eax_1 = sub_100575e0(&data_10068de8)",
        "if (edx == 1)",
        "*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10) * fconvert.t(0.5))",
        "else if (edx == 2)",
        "*ebx = fconvert.s(fconvert.t(*ebx) - float.t(arg_10))",
    ):
        assert expected in retail_draw_match_status


def test_game_status_ownerdraw_matches_retail_text_and_wiring() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    local_source = CG_LOCAL.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")

    status_text = _block_from_marker(source, "const char *CG_GetGameStatusText")
    draw_game_status = _block_from_marker(source, "static void CG_DrawGameStatus")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    retail_status_text = _text_between(
        hlil_source,
        "10034b30    void* const sub_10034b30()",
        "10034bc7",
    )
    retail_draw_call = _text_between(
        ghidra_source,
        "  case 7:\n    FUN_10034bd0(param_13,param_14,param_16);",
        "  case 8:",
    )

    assert "#define\tCG_GAME_STATUS\t\t\t\t\t\t7" in menudef_source
    assert "case 7:\n    FUN_10034bd0(param_13,param_14,param_16);" in retail_draw_call
    assert "const char *CG_GetGameStatusText( void );" in local_source

    for menu_name in (
        "ingamescoreteam.menu",
        "ingamescorenoteam.menu",
        "ingame_scoreboard_1fctf.menu",
        "ingame_scoreboard_ad.menu",
        "ingame_scoreboard_ca.menu",
        "ingame_scoreboard_ctf.menu",
        "ingame_scoreboard_dom.menu",
        "ingame_scoreboard_duel.menu",
        "ingame_scoreboard_ffa.menu",
        "ingame_scoreboard_ft.menu",
        "ingame_scoreboard_har.menu",
        "ingame_scoreboard_race.menu",
        "ingame_scoreboard_rr.menu",
        "ingame_scoreboard_tdm.menu",
    ):
        menu_source = (REPO_ROOT / "src" / "ui" / menu_name).read_text(encoding="utf-8")
        assert "ownerdraw CG_GAME_STATUS" in menu_source

    for expected in (
        "case GT_SINGLE_PLAYER:",
        "case GT_FFA:",
        "case GT_TOURNAMENT:",
        "case GT_RED_ROVER:",
        "cg.snap->ps.persistant[PERS_TEAM] == TEAM_SPECTATOR",
        '"%s place with %i"',
        "if ( cg.teamScores[0] == cg.teamScores[1] ) {",
        '"Teams are tied at %i"',
        "if ( cg.teamScores[0] > cg.teamScores[1] ) {",
        '"^1Red^7 leads ^4Blue^7, %i to %i"',
        '"^4Blue^7 leads ^1Red^7, %i to %i"',
    ):
        assert expected in status_text

    for stale in (
        "cgs.scores1",
        "cgs.scores2",
        "CG_GetMatchStatusText",
        "CG_GetMatchStateLabel",
        '" - Teams are tied at %i"',
        '"Red leads Blue, %i to %i"',
        '"Blue leads Red, %i to %i"',
    ):
        assert stale not in status_text

    for expected in (
        "if (esi == 2)",
        "if (esi s< 3 || esi == 0xc)",
        "if (*(edx + 0x138) == 3)",
        'return sub_100575e0("%s place with %i")',
        "int32_t eax_1 = data_10a9cdc8",
        "int32_t ecx_2 = data_10a9cdcc",
        'return sub_100575e0("Teams are tied at %i")',
        'return sub_100575e0("^4Blue^7 leads ^1Red^7, %i to %i")',
        'return sub_100575e0("^1Red^7 leads ^4Blue^7, %i to %i")',
    ):
        assert expected in retail_status_text

    assert "static void CG_DrawGameStatus( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in draw_game_status
    assert "qhandle_t shader" not in draw_game_status
    assert "CG_Text_Paint(rect->x, rect->y + rect->h, scale, color, CG_GetGameStatusText(), 0, 0, textStyle);" in draw_game_status
    assert "CG_DrawGameStatus( &rect, scale, color, textStyle );" in ownerdraw_block
    assert "CG_DrawGameStatus(&rect, scale, color, shader, textStyle);" not in ownerdraw_block
    assert "return CG_Text_Width( CG_GetGameStatusText(), scale, 0 );" in width_block


def test_player_model_helper_restores_retail_3d_preview_scene() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    shared_block = _block_from_marker(source, "static void CG_DrawProfileModel")
    preview_block = _block_from_marker(source, "static void CG_DrawClientModelPreview")
    first_place_block = _block_from_marker(source, "static void CG_DrawFirstPlaceModel")
    player_block = _block_from_marker(source, "static void CG_DrawPlayerModel")

    assert "shader = ci->modelIcon;" in shared_block
    assert "shader = CG_GetProfileFallbackShader();" in shared_block
    assert "Vector4Set( modulate, 1.0f, 1.0f, 1.0f, active ? 1.0f : 0.8f );" in shared_block

    for expected in (
        "heightScale = ( ci->headOffset[0] > 0.0f ) ? ci->headOffset[0] : 1.0f;",
        "previewHeight = 32.0f / ( heightScale * 0.85f );",
        "refdef.rdflags = RDF_NOWORLDMODEL;",
        "CG_InitClientPreviewEntity( &legs, origin, renderfx );",
        'CG_PositionRotatedEntityOnTag( &torso, &legs, ci->legsModel, "tag_torso" );',
        'CG_PositionRotatedEntityOnTag( &head, &torso, ci->torsoModel, "tag_head" );',
        'CG_PositionEntityOnTag( &gun, &torso, ci->torsoModel, "tag_weapon" );',
        "trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 1.0f, 1.0f );",
        "trap_R_AddLightToScene( lightOrigin, 500.0f, 1.0f, 0.0f, 0.0f );",
        "trap_R_RenderScene( &refdef );",
        "CG_DrawProfileModel( rect, clientNum, active );",
    ):
        assert expected in preview_block

    for expected in (
        "weaponNum = score->bestWeapon;",
        "weaponNum = CG_ClientPreviewWeapon( score->client );",
        "VectorSet( previewAngles, 5.0f, 160.0f, 0.0f );",
        "CG_DrawClientModelPreview( rect, score->client, weaponNum, previewAngles, active );",
    ):
        assert expected in first_place_block

    assert "clientNum = cg.spectatorTrackedClient;" in player_block
    assert "clientNum = cg.snap->ps.clientNum;" in player_block
    assert "weaponNum = CG_ClientPreviewWeapon( clientNum );" in player_block
    assert "VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );" in player_block
    assert "CG_DrawClientModelPreview( rect, clientNum, weaponNum, previewAngles, qtrue );" in player_block


def test_endgame_summary_uses_retail_message_family() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    summary_block = _block_from_marker(source, "static const char *CG_GetEndGameScoreText")
    winner_block = _block_from_marker(source, "static const char *CG_GetMatchWinnerText")

    assert "#define CG_SCORE_FORFEIT -999" in source
    assert "static const char *CG_PluralSuffix( int count )" in source

    for expected in (
        "PERS_DEFEND_COUNT",
        "PERS_ASSIST_COUNT",
        "PERS_CAPTURES",
        '"You forfeited the match."',
        '"You finished with a score of %d."',
        '"You finished %s with a score of %d"',
        '"You had %d assist%s."',
        '"You had %d defend%s."',
        '"You had %d flag capture%s."',
        '"You captured %d skull%s."',
        "cgs.gametype == GT_HARVESTER",
        "cgs.gametype == GT_RED_ROVER",
        "score == CG_SCORE_FORFEIT",
    ):
        assert expected in summary_block

    for stale in (
        '"Your score: %i"',
        '"Score: %i"',
        '"Top score: %i"',
        '"%s %i - %i %s"',
    ):
        assert stale not in summary_block

    assert '"^%c%s^7 WINS by forfeit"' in winner_block
    assert '"%s^7 WINS by forfeit"' in winner_block
    assert "winner->score == CG_SCORE_FORFEIT" in winner_block
    assert "byForfeit = qtrue;" in winner_block


def test_starting_weapons_uses_retail_icon_preview_path() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    token_table = _block_from_marker(main_source, "static const cgRetailWeaponToken_t cgRetailWeaponTokens")
    token_helper = _block_from_marker(main_source, "int CG_StartingWeaponIndexFromToken")
    preview_mask = _block_from_marker(source, "static unsigned int CG_GetStartingWeaponPreviewMask")
    block = _block_from_marker(source, "static void CG_DrawStartingWeapons")
    retail_block = _text_between(
        hlil_source,
        "10033910    int32_t sub_10033910",
        "10033b10",
    )

    assert "static const cgStartingWeaponInfo_t cgStartingWeaponIcons" in source
    assert "CG_ConfigString( CS_LOADOUT_MASK )" in preview_mask
    assert '"g_startingWeapons"' not in preview_mask
    for expected in (
        "if ((data_10a601dc & result) != 0)",
        "if (data_10a249cc != 0)",
        "int32_t esi_1 = data_10a9c7a4",
        "esi_1 = 0xe",
    ):
        assert expected in retail_block

    assert "primaryIndex = cg.weaponPrimary;" in block
    assert "primaryIndex = CG_STARTING_WEAPON_ICON_COUNT;" in block
    assert "CG_GetStartingWeaponIconHandle( cgStartingWeaponIcons[primaryIndex - 1].weapon )" in block
    assert 'CG_Text_Paint( plusX, plusY, scale, color, "+", 0, 0, textStyle );' in block
    assert "CG_DrawPic( rect->x + xOffset, rect->y, rect->w, rect->h, shader );" in block
    assert "CG_DrawPic( rect->x + xOffset + rect->w, rect->y, rect->w, rect->h, shader );" in block

    for expected in (
        '{ "g", WP_GAUNTLET, 1 }',
        '{ "mg", WP_MACHINEGUN, 2 }',
        '{ "sg", WP_SHOTGUN, 3 }',
        '{ "cg", WP_CHAINGUN, 13 }',
        '{ "hmg", WP_HEAVY_MACHINEGUN, 14 }',
    ):
        assert expected in token_table

    for expected in (
        "token = COM_ParseExt( &cursor, qtrue );",
        "weaponToken = CG_RetailWeaponTokenForToken( token );",
        "return weaponToken->index;",
    ):
        assert expected in token_helper

    for stale in (
        "Factory loadouts active",
        "Default loadout",
        "Q_strcat( buffer",
        "CG_ResolveWeaponName( weapon )",
        "CG_StartingWeaponFromToken",
        "cg_weaponPrimary.integer",
    ):
        assert stale not in block


def test_front_panel_ownerdraw_trio_matches_retail_dispatch_and_callback_surface() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    menudef_source = MENUDEF_H.read_text(encoding="utf-8")
    intro_menu = INTRO_MENU.read_text(encoding="utf-8")
    endscoreteam_menu = ENDSCORETEAM_MENU.read_text(encoding="utf-8")
    ghidra_source = CGAME_GHIDRA.read_text(encoding="utf-8")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_ownerdraw_block = _block_from_marker(ghidra_source, "void FUN_1003b0f0")
    value_block = _block_from_marker(source, "float CG_GetValue")
    width_block = _block_from_marker(main_source, "static int CG_OwnerDrawWidth")
    key_block = _block_from_marker(main_source, "static qboolean CG_OwnerDrawHandleKey")
    display_context_block = _block_from_marker(main_source, "static void CG_InitDisplayContext")
    server_case = _text_between(ownerdraw_block, "case CG_SERVER_SETTINGS:", "case CG_STARTING_WEAPONS:")
    starting_case = _text_between(ownerdraw_block, "case CG_STARTING_WEAPONS:", "case CG_GAME_LIMIT:")
    limit_case = _text_between(ownerdraw_block, "case CG_GAME_LIMIT:", "case CG_GAME_TYPE_ICON:")

    assert any(line.split() == ["#define", "CG_SERVER_SETTINGS", "1"] for line in menudef_source.splitlines())
    assert any(line.split() == ["#define", "CG_STARTING_WEAPONS", "2"] for line in menudef_source.splitlines())
    assert any(line.split() == ["#define", "CG_GAME_LIMIT", "3"] for line in menudef_source.splitlines())

    assert "CG_DrawServerSettings(&rect, text_x, text_y, scale, color, textStyle);" in server_case
    assert "CG_DrawStartingWeapons(&rect, text_x, text_y, scale, color, textStyle);" in starting_case
    assert "CG_DrawGameLimit( &rect, scale, color, textStyle, align );" in limit_case

    assert "case 1:" in retail_ownerdraw_block
    assert "FUN_1003a1c0(param_13,param_14);" in retail_ownerdraw_block
    assert "case 2:" in retail_ownerdraw_block
    assert "FUN_10033910(param_13,param_14,param_16);" in retail_ownerdraw_block
    assert "case 3:" in retail_ownerdraw_block
    assert "FUN_10033800(&local_18,param_13,param_14,param_16,param_10);" in retail_ownerdraw_block

    for ownerdraw in ("CG_SERVER_SETTINGS", "CG_STARTING_WEAPONS", "CG_GAME_LIMIT"):
        assert ownerdraw not in value_block
        assert ownerdraw not in width_block
        assert ownerdraw not in key_block

    assert "cgDC.ownerDrawItem = &CG_OwnerDraw;" in display_context_block
    assert "cgDC.getValue = &CG_GetValue;" in display_context_block
    assert "cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;" in display_context_block
    assert "cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;" in display_context_block

    assert "ownerdraw CG_STARTING_WEAPONS" in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in intro_menu
    assert "ownerdraw CG_GAME_LIMIT" in endscoreteam_menu


def test_gametype_icons_use_retail_tga_registration_path() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    main_source = CG_MAIN.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    register_block = _block_from_marker(newdraw_source, "void CG_RegisterGameTypeIcons")
    icon_block = _block_from_marker(newdraw_source, "static qhandle_t CG_GameTypeIconShader")
    retail_icon_block = _text_between(
        hlil_source,
        "10034840    int32_t __fastcall sub_10034840",
        "10034900",
    )

    assert "static qhandle_t cgGameTypeIconShaders[GT_MAX_GAME_TYPE];" in newdraw_source
    assert 'memset( cgGameTypeIconShaders, 0, sizeof( cgGameTypeIconShaders ) );' in register_block

    for expected in (
        '"ui/assets/hud/ffa.tga"',
        '"ui/assets/hud/duel.tga"',
        '"ui/assets/hud/race.tga"',
        '"ui/assets/hud/tdm.tga"',
        '"ui/assets/hud/ca.tga"',
        '"ui/assets/hud/ctf.tga"',
        '"ui/assets/hud/1f.tga"',
        '"ui/assets/hud/har.tga"',
        '"ui/assets/hud/ft.tga"',
        '"ui/assets/hud/dom.tga"',
        '"ui/assets/hud/ad.tga"',
        '"ui/assets/hud/rr.tga"',
    ):
        assert expected in register_block

    for expected in (
        "else if (eax_2 != 0xb)",
        "if (eax_2 != 0xc)",
        "eax = data_10a5f328",
    ):
        assert expected in retail_icon_block

    assert "cgGameTypeIconShaders[GT_OBELISK] = cgGameTypeIconShaders[GT_FFA];" in register_block

    for stale in (
        ".png",
        '"ui/assets/hud/flag.png"',
        'cgGameTypeIconShaders[GT_OBELISK] = trap_R_RegisterShaderNoMip( "ui/assets/hud/dom.tga" );',
    ):
        assert stale not in newdraw_source

    assert "return cgGameTypeIconShaders[gametype];" in icon_block
    assert "CG_RegisterGameTypeIcons();" in main_source


def test_first_twenty_limit_count_map_and_vote_draws_match_retail_origins() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    capfrag_block = _block_from_marker(source, "static void CG_DrawCapFragLimit")
    race_limit_block = _block_from_marker(source, "static int CG_GetRaceCapFragLimitValue")
    count_block = _block_from_marker(source, "static int CG_CountActivePlayers")
    player_counts_block = _block_from_marker(source, "static void CG_DrawPlayerCounts")
    map_text_block = _block_from_marker(source, "static const char *CG_MapNameText")
    map_name_block = _block_from_marker(source, "static void CG_DrawMapName")
    map_display_block = _block_from_marker(source, "static void CG_GetMapDisplayName")
    detail_block = _block_from_marker(source, "static void CG_BuildIntroPanelDetailString")
    vote_gametype_block = _block_from_marker(source, "static void CG_DrawVoteGametype")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_capfrag = _text_between(
        hlil_source,
        "10032260    void sub_10032260",
        "100323d0",
    )
    retail_player_counts = _text_between(
        hlil_source,
        "10032f30    void sub_10032f30",
        "10033040",
    )
    retail_map_name = _text_between(
        hlil_source,
        "100343d0    int32_t sub_100343d0",
        "10034420",
    )
    retail_vote_gametype = _text_between(
        hlil_source,
        '100356f0    void* __convention("regparm") sub_100356f0',
        "10035790",
    )

    for expected in (
        "data_10a3ff38",
        "data_10a3ff48",
        "data_10a3ff54",
        "data_10a3ff34",
        "atoi(data_10a38f38 + 0x10a39420) - data_10abaad4",
        "if (arg5 == 1)",
        "else if (arg5 == 2)",
        "var_8 = fconvert.s(fconvert.t(arg1[1]))",
    ):
        assert expected in retail_capfrag

    for expected in (
        "case GT_RACE:",
        "limit = CG_GetRaceCapFragLimitValue();",
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_OBELISK:",
        "case GT_HARVESTER:",
        "limit = cgs.capturelimit;",
        "case GT_CLAN_ARENA:",
        "case GT_FREEZE:",
        "case GT_RED_ROVER:",
        "limit = cgs.roundlimit;",
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        "limit = cgs.scorelimit;",
        "limit = cgs.fraglimit;",
        'Com_sprintf( buffer, sizeof( buffer ), "%2i", limit );',
        "CG_AlignTextX( &x, buffer, scale, align );",
        "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );",
    ):
        assert expected in capfrag_block

    assert "remaining = cgs.racePointCount - ( progress->currentCheckpoint + 1 );" in race_limit_block
    assert "CG_HasObjectiveCountStat" not in capfrag_block
    assert "qhandle_t shader" not in capfrag_block
    assert "rect->y + rect->h" not in capfrag_block
    assert "CG_DrawCapFragLimit( &rect, scale, color, textStyle, align );" in ownerdraw_block

    for expected in (
        "if (*eax_1 != 0)",
        'eax_2, ecx = sub_100575e0("%d/%d Players")',
        "if (arg6 == 1)",
        "else if (arg6 == 2)",
        "fconvert.t(*(ebp + 4))",
    ):
        assert expected in retail_player_counts

    assert "for ( i = 0; i < cgs.maxclients && i < MAX_CLIENTS; i++ )" in count_block
    assert "cgs.clientinfo[i].infoValid" in count_block
    assert "cg.numScores" not in count_block
    assert "TEAM_SPECTATOR" not in count_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in player_counts_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in player_counts_block
    assert "rect->y + rect->h" not in player_counts_block
    assert "CG_DrawPlayerCounts(&rect, scale, color, textStyle, align);" in ownerdraw_block

    for expected in (
        "int32_t var_10 = data_10a3842c + 0x10a39420",
        "eax_1, ecx_1 = sub_100575e0(&data_10068de8)",
        "return sub_10008440(fconvert.s(fconvert.t(*arg1))",
        "fconvert.s(fconvert.t(arg1[1]))",
    ):
        assert expected in retail_map_name

    for expected in (
        "info = CG_ConfigString( CS_SERVERINFO );",
        "mapName = info ? Info_ValueForKey( info, SERVERINFO_KEY_MAPNAME ) : \"\";",
        "return mapName ? mapName : \"\";",
    ):
        assert expected in map_text_block
    assert "cgs.mapname" not in map_text_block

    assert "CG_Text_Paint( rect->x, rect->y, scale, color, CG_MapNameText(), 0, 0, textStyle );" in map_name_block
    assert "rect->y + rect->h" not in map_name_block
    assert "Q_strncpyz( buffer, CG_MapNameText(), bufferSize );" in map_display_block
    assert "CG_GetMapDisplayName( buffer, bufferSize );" in detail_block
    assert "CG_GetServerLocation" not in source
    assert "CG_BuildMapDisplayName" not in source
    assert "ARENA_INFO_KEY_LONGNAME" not in source
    assert 'CG_FindArenaLongNameInFile( "scripts/arenas.txt", mapName, buffer, bufferSize )' not in source
    assert "CG_DrawMapName( &rect, scale, color, textStyle );" in ownerdraw_block

    assert "if (arg1 == 0x13 || arg1 == 0x14 || arg1 == 0x15)" in retail_vote_gametype
    assert "arg2[1]) - fconvert.t(8.0)" in retail_vote_gametype
    assert 'CG_GetVoteSlotString( slot, "Gametype", buffer, sizeof( buffer ) );' in vote_gametype_block
    assert "CG_Text_Paint( rect->x, rect->y - 8.0f, scale, color, buffer, 0, 0, textStyle );" in vote_gametype_block
    assert "CG_GetTextPosition" not in vote_gametype_block
    assert "case CG_VOTEGAMETYPE1:" in ownerdraw_block
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 1);" in ownerdraw_block
    assert "case CG_VOTEGAMETYPE2:" in ownerdraw_block
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 2);" in ownerdraw_block


def test_second_twenty_vote_and_local_player_ownerdraws_match_retail_wiring() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
    vote_gametype_block = _block_from_marker(source, "static void CG_DrawVoteGametype")
    vote_map_block = _block_from_marker(source, "static void CG_DrawVoteMapSlot")
    vote_name_block = _block_from_marker(source, "static void CG_DrawVoteName")
    vote_shot_block = _block_from_marker(source, "static void CG_DrawVoteShot")
    vote_count_block = _block_from_marker(source, "static void CG_DrawVoteCount")
    vote_timer_block = _block_from_marker(source, "static void CG_DrawVoteTimer")
    spectator_block = _block_from_marker(source, "static void CG_DrawSpectatorMessages")
    armor_icon_block = _block_from_marker(source, "static void CG_DrawPlayerArmorIcon")
    armor_value_block = _block_from_marker(source, "static void CG_DrawPlayerArmorValue")
    player_head_block = _block_from_marker(source, "static void CG_DrawPlayerHead")
    player_model_block = _block_from_marker(source, "static void CG_DrawPlayerModel")
    ownerdraw_block = _block_from_marker(source, "void CG_OwnerDraw(")
    retail_vote_map = _text_between(
        hlil_source,
        '100355d0    void* __convention("regparm") sub_100355d0',
        "10035660",
    )
    retail_vote_name = _text_between(
        hlil_source,
        '10035660    void* __convention("regparm") sub_10035660',
        "100356f0",
    )
    retail_vote_shot = _text_between(
        hlil_source,
        "10035790    int32_t __convention",
        "10035820",
    )
    retail_vote_count = _text_between(
        hlil_source,
        "10035820    void __convention",
        "10035920",
    )
    retail_vote_timer = _text_between(
        hlil_source,
        "10035920    void sub_10035920",
        "10035a10",
    )
    retail_armor_value = _text_between(
        hlil_source,
        "1002e500    void __convention",
        "1002e660",
    )
    retail_armor_icon = _text_between(
        hlil_source,
        "1002e3f0    void __convention",
        "1002e500",
    )
    retail_player_head = _text_between(
        hlil_source,
        "1002f950    int80_t sub_1002f950",
        "1002fc70",
    )
    retail_player_model = _text_between(
        hlil_source,
        "10034980    int32_t __convention",
        "10034a00",
    )
    retail_spectator = _text_between(
        hlil_source,
        "10034d70    int32_t __fastcall sub_10034d70",
        "100350c0",
    )

    assert "if (arg1 == 0x13 || arg1 == 0x14 || arg1 == 0x15)" in hlil_source
    assert "CG_DrawVoteGametype(&rect, scale, color, textStyle, 3);" in ownerdraw_block
    assert "CG_GetTextPosition" not in vote_gametype_block

    for expected in (
        "if (arg1 == 0x16 || arg1 == 0x17 || arg1 == 0x18)",
        "fconvert.s(fconvert.t(*arg2))",
        "fconvert.s(fconvert.t(arg2[1]))",
    ):
        assert expected in retail_vote_map
    assert 'CG_GetVoteSlotString( slot, "Map", buffer, sizeof( buffer ) );' in vote_map_block
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_map_block
    assert "CG_GetTextPosition" not in vote_map_block

    assert "if (arg1 == 0x1c || arg1 == 0x1d || arg1 == 0x1e)" in retail_vote_name
    assert 'CG_GetVoteSlotString( slot, "Name", buffer, sizeof( buffer ) );' in vote_name_block
    assert "CG_Text_Paint( rect->x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_name_block
    assert "CG_GetTextPosition" not in vote_name_block

    for expected in (
        "if (arg1 == 0x19 || arg1 == 0x1a || arg1 == 0x1b)",
        'eax_2 = "default"',
        'sub_100575e0("levelshots/preview/%s")',
    ):
        assert expected in retail_vote_shot
    assert 'Q_strncpyz( previewToken, "default", sizeof( previewToken ) );' in vote_shot_block
    assert 'Com_sprintf( path, sizeof( path ), "levelshots/preview/%s", previewToken );' in vote_shot_block

    for expected in (
        "if (arg3 == 0x1f || arg3 == 0x20 || arg3 == 0x21)",
        'eax_1, ecx_5 = sub_100575e0("Votes: %s")',
        "if (arg9 == 1)",
        "else if (arg9 == 2)",
        "fconvert.s(fconvert.t(arg4[1]))",
    ):
        assert expected in retail_vote_count
    assert 'Com_sprintf( buffer, sizeof( buffer ), "Votes: %s", countText );' in vote_count_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_count_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_count_block
    assert "CG_GetTextPosition" not in vote_count_block

    for expected in (
        "data_10a3ffc4 - data_10a9c1ec + 0x4e20",
        '"Voting has ended."',
        '"Voting ends in %i second."',
        '"Voting ends in %i seconds."',
        "if (eax_5 == 1)",
        "else if (eax_5 == 2)",
    ):
        assert expected in retail_vote_timer
    assert "remaining = ( cgs.voteTime - cg.time + 20000 ) / 1000;" in vote_timer_block
    assert "CG_AlignTextX( &x, buffer, scale, align );" in vote_timer_block
    assert "CG_Text_Paint( x, rect->y, scale, color, buffer, 0, 0, textStyle );" in vote_timer_block
    assert "CG_GetTextPosition" not in vote_timer_block

    for expected in (
        "case CG_VOTEMAP1:",
        "CG_DrawVoteMapSlot(&rect, scale, color, textStyle, 1);",
        "case CG_VOTESHOT1:",
        "CG_DrawVoteShot(&rect, 1);",
        "case CG_VOTENAME1:",
        "CG_DrawVoteName(&rect, scale, color, textStyle, 1);",
        "case CG_VOTECOUNT1:",
        "CG_DrawVoteCount(&rect, scale, color, textStyle, 1, align);",
        "case CG_VOTETIMER:",
        "CG_DrawVoteTimer(&rect, scale, color, textStyle, align);",
    ):
        assert expected in ownerdraw_block

    assert "Round In Progress" in retail_spectator
    assert "SPECTATOR MODE" in spectator_block
    assert "CG_DrawSpectatorMessages( &rect, scale, color, textStyle );" in ownerdraw_block

    assert "data_10a5f418" in retail_armor_icon
    assert "data_10a5f414" in retail_armor_icon
    assert "CG_DrawPlayerArmorIcon( &rect, ownerDrawFlags & CG_SHOW_2DONLY );" in ownerdraw_block
    assert "CG_DrawPlayerArmorIcon( &rect, qtrue );" in ownerdraw_block
    assert "cgs.media.armorIcon" in armor_icon_block
    assert "cgs.media.armorModel" in armor_icon_block

    for expected in (
        "if (arg1 != 0)",
        "if (arg8 == 1)",
        "else if (arg8 == 2)",
        "fconvert.t(ebx[1]) + float.t(var_4)",
    ):
        assert expected in retail_armor_value
    assert "value = ps->stats[STAT_ARMOR];" in armor_value_block
    assert "CG_AlignTextX( &x, num, scale, align );" in armor_value_block
    assert "y = rect->y + CG_Text_Height( num, scale, 0 );" in armor_value_block
    assert "CG_DrawPlayerArmorValue( &rect, scale, color, shader, textStyle, align );" in ownerdraw_block

    assert "CG_DrawHead( x, rect->y, rect->w, rect->h, cg.snap->ps.clientNum, angles );" in player_head_block
    assert "return sub_10009490" in retail_player_head
    assert "CG_DrawPlayerHead( &rect, ownerDrawFlags & CG_SHOW_2DONLY );" in ownerdraw_block

    assert "VectorSet( previewAngles, 5.0f, 210.0f, 0.0f );" in player_model_block
    assert "0x43520000" in retail_player_model
    assert "CG_DrawPlayerModel( &rect );" in ownerdraw_block


def test_team_pickup_ownerdraws_use_team_scorestats_payload() -> None:
    newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
    local_source = CG_LOCAL.read_text(encoding="utf-8")
    block = _block_from_marker(newdraw_source, "static qboolean CG_BuildTeamPickupText")

    assert "int\t\tfieldCount;" in local_source or "int\t\t\tfieldCount;" in local_source
    assert "cg.teamScoreStats.valid" in block
    assert "cg.teamScoreStats.fieldCount <= 0" in block
    assert "statIndex >= cg.teamScoreStats.fieldCount" in block
    assert "cg.teamScoreStats.values[teamIndex][statIndex]" in block

    for stale in (
        "CG_TeamMapPickupProxyTotal",
        "legacy map-pickup proxy",
        "currently available proxy data",
    ):
        assert stale not in newdraw_source


def test_placement_frags_use_retail_team_family_kill_rows() -> None:
    source = CG_NEWDRAW.read_text(encoding="utf-8")
    helper_block = _block_from_marker(source, "static int CG_GetPlacementFragCount")
    placement_block = _block_from_marker(source, "static qboolean CG_BuildPlacementMetricText")

    for expected in (
        "case GT_TEAM:",
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_HARVESTER:",
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
        "case GT_FREEZE:",
        "return score->kills;",
        "return score->score;",
    ):
        assert expected in helper_block

    assert "case CG_1ST_PLYR_FRAGS:" in placement_block
    assert 'Com_sprintf( buffer, bufferSize, "%i", CG_GetPlacementFragCount( score ) );' in placement_block
