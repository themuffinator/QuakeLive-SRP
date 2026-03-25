from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_define(text: str, name: str) -> str:
    pattern = rf"#define\s+{re.escape(name)}\s+\"([^\"]+)\""
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"define for {name} not found")
    return match.group(1)


def _extract_vcxproj_group(text: str, condition: str) -> str:
    pattern = (
        r"<ItemDefinitionGroup Condition=\""
        + re.escape(condition)
        + r"\">(.*?)</ItemDefinitionGroup>"
    )
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise AssertionError(f"ItemDefinitionGroup for {condition} not found")
    return match.group(1)


def _extract_vcxproj_compile_item(text: str, include: str) -> str:
    pattern = r"<ClCompile Include=\"" + re.escape(include) + r"\">(.*?)</ClCompile>"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise AssertionError(f"ClCompile for {include} not found")
    return match.group(1)


def _extract_function_block(text: str, signature: str) -> str:
    start = text.find(signature)
    if start == -1:
        raise AssertionError(f"function signature not found: {signature}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise AssertionError(f"opening brace not found for: {signature}")

    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise AssertionError(f"unterminated function block for: {signature}")


def test_ui_menu_defaults_use_existing_assets() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert '"ui_menuFiles", UI_MENU_FILE_QUAKELIVE' in ui_main
    assert '"ui_menuFlow", "1"' in ui_main

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    legacy_menu = _extract_define(ui_local, "UI_MENU_FILE_LEGACY")
    legacy_ingame = _extract_define(ui_local, "UI_INGAME_FILE_LEGACY")

    for menu_file in (legacy_menu, legacy_ingame):
        assert (REPO_ROOT / "src" / menu_file).exists(), menu_file


def test_ui_extended_native_exports_match_retail_bridge_surface() -> None:
    ui_public = (REPO_ROOT / "src/code/ui/ui_public.h").read_text(encoding="utf-8")
    assert "#define UI_QL_API_VERSION\t8" in ui_public
    assert "UI_REFRESH_DISPLAY_CONTEXT" in ui_public
    assert "UI_MENUS_ANY_VISIBLE" in ui_public
    assert "UI_FOR_EACH_ARENA_NAME" in ui_public
    assert "UI_DRAW_ADVERTISEMENT_WAIT_SCREEN" in ui_public

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "return UI_QL_API_VERSION;" in ui_main
    assert "UI_RefreshDisplayContextScale" in ui_main
    assert "UI_DrawAdvertisementWaitScreen" in ui_main
    assert "Waiting on Advertisement" in ui_main
    assert "Press ESC to cancel" in ui_main
    assert "Waiting for new key... Press ESC..." in ui_main

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "qboolean Menus_AnyVisible()" in ui_shared

    vm_text = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")
    assert "case UI_REFRESH_DISPLAY_CONTEXT:" in vm_text
    assert "case UI_MENUS_ANY_VISIBLE:" in vm_text
    assert "case UI_FOR_EACH_ARENA_NAME:" in vm_text
    assert "case UI_DRAW_ADVERTISEMENT_WAIT_SCREEN:" in vm_text

    ui_vcxproj = (REPO_ROOT / "src/code/ui/ui.vcxproj").read_text(encoding="utf-8")
    debug_group = _extract_vcxproj_group(ui_vcxproj, "'$(Configuration)|$(Platform)'=='Debug|Win32'")
    release_group = _extract_vcxproj_group(ui_vcxproj, "'$(Configuration)|$(Platform)'=='Release|Win32'")
    assert "<ModuleDefinitionFile>.\\ui.def</ModuleDefinitionFile>" in debug_group
    assert "<ModuleDefinitionFile>.\\ui.def</ModuleDefinitionFile>" in release_group

    debug_exclusion = "<ExcludedFromBuild Condition=\"'$(Configuration)|$(Platform)'=='Debug|Win32'\">true</ExcludedFromBuild>"
    release_exclusion = "<ExcludedFromBuild Condition=\"'$(Configuration)|$(Platform)'=='Release|Win32'\">true</ExcludedFromBuild>"
    for include in (
        "..\\game\\bg_lib.c",
        "..\\game\\bg_misc.c",
        "..\\game\\q_math.c",
        "..\\game\\q_shared.c",
        "ui_atoms.c",
        "ui_cdkey.c",
        "ui_quakelive_bridge.c",
        "ui_gameinfo.c",
        "ui_main.c",
        "ui_players.c",
        "ui_shared.c",
        "ui_util.c",
    ):
        compile_item = _extract_vcxproj_compile_item(ui_vcxproj, include)
        assert debug_exclusion not in compile_item
        assert release_exclusion not in compile_item


def test_ui_cdkey_runtime_wrapper_restored() -> None:
    ui_cdkey = (REPO_ROOT / "src/code/ui/ui_cdkey.c").read_text(encoding="utf-8")
    assert "UI_CDKeyMenu_OpenBridge" in ui_cdkey
    assert 'Menus_ActivateByName( "ql_bridge_credentials" );' in ui_cdkey
    assert "UI_PushMenu( &cdkeyMenuInfo.menu );" in ui_cdkey

    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    assert "UI_CDKeyMenu_Cache();" in ui_atoms
    assert "UI_CDKeyMenu_f();" in ui_atoms

    q3asm = (REPO_ROOT / "src/code/ui/ui.q3asm").read_text(encoding="utf-8")
    assert "ui_cdkey" in q3asm

    ui_vcxproj = (REPO_ROOT / "src/code/ui/ui.vcxproj").read_text(encoding="utf-8")
    assert '<ClCompile Include="ui_cdkey.c">' in ui_vcxproj


def test_ui_retail_console_command_wrappers_restored() -> None:
    ui_atoms = (REPO_ROOT / "src/code/ui/ui_atoms.c").read_text(encoding="utf-8")
    assert 'Q_stricmp (cmd, "listPlayerModels")' in ui_atoms
    assert "UI_ListPlayerModels();" in ui_atoms
    assert 'Q_stricmp (cmd, "menu_close")' in ui_atoms
    assert "UI_ConsoleCommand_MenuClose();" in ui_atoms
    assert "Menus_CloseByName( menuName );" in ui_atoms
    assert 'Q_stricmp (cmd, "menu_open")' in ui_atoms
    assert "UI_ConsoleCommand_MenuOpen();" in ui_atoms
    assert "Menus_OpenByName( menuName );" in ui_atoms

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    assert "void UI_ListPlayerModels( void );" in ui_local

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "void UI_ListPlayerModels( void ) {" in ui_main
    assert 'Com_Printf( "Player Models\\n" );' in ui_main
    assert 'Com_Printf( "%s\\n", uiInfo.q3HeadNames[i] );' in ui_main


def test_ui_retail_ownerdraw_extensions_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "#define UI_CROSSHAIR_COLOR_COUNT\t27" in ui_main
    assert "static void UI_DrawCrosshairColor( rectDef_t *rect )" in ui_main
    assert 'trap_Cvar_VariableValue( "cg_crosshairColor" )' in ui_main
    assert "case UI_CROSSHAIR_COLOR:" in ui_main
    assert "return UI_CrosshairColor_HandleKey(flags, special, key);" in ui_main
    assert "case UI_VOTESTRING:" in ui_main
    assert "UI_DrawVoteString(&rect, scale, color, textStyle);" in ui_main
    assert 'UI_Cvar_VariableString("ui_votestring")' in ui_main


def test_ui_retail_starting_weapons_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "#define UI_STARTING_WEAPON_ICON_COUNT\t14" in ui_main
    assert "static int UI_StartingWeaponIndexFromToken( const char *value )" in ui_main
    assert 'trap_GetConfigString( CS_LOADOUT_MASK, loadoutMaskText, sizeof( loadoutMaskText ) );' in ui_main
    assert 'UI_Cvar_VariableString( "cg_weaponPrimaryQueued" )' in ui_main
    assert "case UI_STARTING_WEAPONS:" in ui_main
    assert "UI_DrawStartingWeapons(&rect, scale, color, textStyle);" in ui_main


def test_ui_retail_advert_runtime_seam_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "int cellId;" in ui_shared_h
    assert "const char *defaultContent;" in ui_shared_h
    assert "setupAdvertCellShader" in ui_shared_h
    assert "refreshAdvertCellShader" in ui_shared_h
    assert "activateAdvert" in ui_shared_h
    assert "initAdvertisementBridge" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static void Menu_SetupAdvertCellShaders(menuDef_t *menu)" in ui_shared
    assert "static void Menu_RefreshAdvertCellShaders(menuDef_t *menu)" in ui_shared
    assert "static qhandle_t Item_UpdateAdvertShader(itemDef_t *item, qboolean refresh)" in ui_shared
    assert 'if (item->window.ownerDraw == UI_ADVERT)' in ui_shared
    assert "static void Script_ActivateAdvert(itemDef_t *item, char **args)" in ui_shared
    assert '{"activateAdvert", &Script_ActivateAdvert}' in ui_shared
    assert '{"cellId", ItemParse_cellId, NULL}' in ui_shared
    assert '{"defaultContent", ItemParse_defaultContent, NULL}' in ui_shared

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static qhandle_t UI_SetupAdvertCellShader" in ui_main
    assert "static qhandle_t UI_RefreshAdvertCellShader" in ui_main
    assert "static void UI_ActivateAdvert(int cellId)" in ui_main
    assert "static void UI_InitAdvertisementBridge(void)" in ui_main
    assert "static void UI_DrawAdvert(rectDef_t *rect, vec4_t color, qhandle_t shader)" in ui_main
    assert "case UI_ADVERT:" in ui_main
    assert "uiInfo.uiDC.setupAdvertCellShader = &UI_SetupAdvertCellShader;" in ui_main
    assert "uiInfo.uiDC.refreshAdvertCellShader = &UI_RefreshAdvertCellShader;" in ui_main
    assert "uiInfo.uiDC.activateAdvert = &UI_ActivateAdvert;" in ui_main


def test_ui_retail_toggle_script_command_restored() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static void Script_Toggle(itemDef_t *item, char **args)" in ui_shared
    assert "menu = Menus_FindByName(name);" in ui_shared
    assert "if (menu->window.flags & WINDOW_VISIBLE)" in ui_shared
    assert "Menus_CloseByName(name);" in ui_shared
    assert "Menus_ActivateByName(name);" in ui_shared
    assert '{"toggle", &Script_Toggle}' in ui_shared
    assert 'DC->setCVar("model", name);' in ui_shared
    assert 'DC->setCVar("headmodel", name);' in ui_shared


def test_ui_display_mousemove_matches_retail_routing_only() -> None:
    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    block = _extract_function_block(ui_shared, "qboolean Display_MouseMove(void *p, int x, int y)")
    assert "menu = Menu_GetFocused();" in block
    assert "if (menu && (menu->window.flags & WINDOW_POPUP))" in block
    assert "Menu_HandleMouseMove(menu, x, y);" in block
    assert "Menu_HandleMouseMove(&Menus[i], x, y);" in block
    assert "menu->window.rectClient.x += x;" not in block
    assert "menu->window.rectClient.y += y;" not in block
    assert "Menu_UpdatePosition(menu);" not in block


def test_ui_retail_item_font_runtime_compatibility_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "#define ITEM_FONT_INHERIT -1" in ui_shared_h
    assert "int fontIndex;                 // retail item font bucket" in ui_shared_h
    assert "drawTextExt" in ui_shared_h
    assert "textWidthExt" in ui_shared_h
    assert "textHeightExt" in ui_shared_h
    assert "drawTextWithCursorExt" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "qboolean ItemParse_font( itemDef_t *item, int handle )" in ui_shared
    assert '{"font", ItemParse_font, NULL}' in ui_shared
    assert "item->fontIndex = ITEM_FONT_INHERIT;" in ui_shared
    assert "Item_DrawText(item, item->textRect.x, item->textRect.y, color, textPtr, 0, 0);" in ui_shared
    assert "Item_DrawTextWithCursor(item, item->textRect.x + item->textRect.w + offset, item->textRect.y, newColor, buff + editPtr->paintOffset, item->cursorPos - editPtr->paintOffset , cursor, editPtr->maxPaintChars);" in ui_shared

    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static fontInfo_t *UI_SelectTextFont(float scale, int fontIndex)" in ui_main
    assert "return Text_WidthExt(text, scale, limit, ITEM_FONT_INHERIT);" in ui_main
    assert "return Text_HeightExt(text, scale, limit, ITEM_FONT_INHERIT);" in ui_main
    assert "Text_PaintExt(x, y, scale, color, text, adjust, limit, style, ITEM_FONT_INHERIT);" in ui_main
    assert "Text_PaintWithCursorExt(x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT);" in ui_main
    assert "uiInfo.uiDC.drawTextExt = &Text_PaintExt;" in ui_main
    assert "uiInfo.uiDC.textWidthExt = &Text_WidthExt;" in ui_main
    assert "uiInfo.uiDC.textHeightExt = &Text_HeightExt;" in ui_main
    assert "uiInfo.uiDC.drawTextWithCursorExt = &Text_PaintWithCursorExt;" in ui_main


def test_ui_retail_preset_and_precision_runtime_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "int precision;" in ui_shared_h
    assert "qboolean integer;" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static void Menu_UpdatePresetLists(menuDef_t *menu)" in ui_shared
    assert "static const char *Item_GetTextSource(itemDef_t *item, char *buffer, int bufferSize)" in ui_shared
    assert "static void UI_SetItemCvarValue(itemDef_t *item, float value)" in ui_shared
    assert "qboolean ItemParse_precision( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvara( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarInt( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarPreset( itemDef_t *item, int handle )" in ui_shared
    assert '{"precision", ItemParse_precision, NULL}' in ui_shared
    assert '{"cvara", ItemParse_cvara, NULL}' in ui_shared
    assert '{"cvarInt", ItemParse_cvarInt, NULL}' in ui_shared
    assert '{"cvarPreset", ItemParse_cvarPreset, NULL}' in ui_shared
    assert '{"cvarPresetList", ItemParse_cvarStrList, NULL}' in ui_shared
    assert "const char *Item_PresetList_Setting(itemDef_t *item)" in ui_shared
    assert "int Item_PresetList_FindCvarByValue(itemDef_t *item)" in ui_shared
    assert "qboolean Item_PresetList_HandleKey(itemDef_t *item, int key)" in ui_shared
    assert "void Item_PresetList_Paint(itemDef_t *item)" in ui_shared
    assert "void Item_SliderColor_Paint(itemDef_t *item)" in ui_shared
    assert "case ITEM_TYPE_PRESETLIST:" in ui_shared
    assert "case ITEM_TYPE_SLIDER_COLOR:" in ui_shared
    assert "Menu_UpdatePresetLists(menu);" in ui_shared
    assert 'DC->setCVar(item->cvar, "Custom");' in ui_shared

    basic_menu = (REPO_ROOT / "src/ui/ingame_options_basic.menu").read_text(encoding="utf-8")
    assert 'type ITEM_TYPE_PRESETLIST' in basic_menu
    assert 'cvara "ui_globalpreset"' in basic_menu
    assert 'cvarPresetList { "Default", "globalpreset_default"' in basic_menu

    advanced_menu = (REPO_ROOT / "src/ui/ingame_options_advanced.menu").read_text(encoding="utf-8")
    assert 'type ITEM_TYPE_PRESET' in advanced_menu
    assert 'type ITEM_TYPE_SLIDER_COLOR' in advanced_menu
    assert 'cvarPreset { "cg_forceEnemySkin" bright }' in advanced_menu
    assert 'cvarInt "cg_crosshairColor" 25 1 26' in advanced_menu


def test_ui_retail_parser_gating_extensions_restored() -> None:
    ui_shared_h = (REPO_ROOT / "src/code/ui/ui_shared.h").read_text(encoding="utf-8")
    assert "#define MAX_MENUITEMS 1024" in ui_shared_h
    assert "#define ITEM_CVAR_SLOT_COUNT 4" in ui_shared_h
    assert "const char *cvarTest[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "const char *enableCvar[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "int cvarFlags[ITEM_CVAR_SLOT_COUNT];" in ui_shared_h
    assert "Rectangle backgroundRect;" in ui_shared_h
    assert "qboolean backgroundSizeSet;" in ui_shared_h

    ui_shared = (REPO_ROOT / "src/code/ui/ui_shared.c").read_text(encoding="utf-8")
    assert "static qboolean Item_HasCvarFlags( const itemDef_t *item, int mask )" in ui_shared
    assert "static qboolean Item_EnableShowViaCvarSlot( const itemDef_t *item, int slot, int flag )" in ui_shared
    assert "qboolean ItemParse_cvarTest2( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarTest3( itemDef_t *item, int handle )" in ui_shared
    assert "qboolean ItemParse_cvarTest4( itemDef_t *item, int handle )" in ui_shared
    assert "static qboolean Parse_showCvar2_or_hideCvar2( itemDef_t *item, int handle, int flag )" in ui_shared
    assert "static qboolean Parse_showCvar3_or_hideCvar3( itemDef_t *item, int handle, int flag )" in ui_shared
    assert "static qboolean Parse_showCvar4_or_hideCvar4( itemDef_t *item, int handle, int flag )" in ui_shared
    assert '{"cvarTest2", ItemParse_cvarTest2, NULL}' in ui_shared
    assert '{"cvarTest3", ItemParse_cvarTest3, NULL}' in ui_shared
    assert '{"cvarTest4", ItemParse_cvarTest4, NULL}' in ui_shared
    assert '{"showCvar2", ItemParse_showCvar2, NULL}' in ui_shared
    assert '{"showCvar3", ItemParse_showCvar3, NULL}' in ui_shared
    assert '{"showCvar4", ItemParse_showCvar4, NULL}' in ui_shared
    assert '{"hideCvar2", ItemParse_hideCvar2, NULL}' in ui_shared
    assert '{"hideCvar3", ItemParse_hideCvar3, NULL}' in ui_shared
    assert '{"hideCvar4", ItemParse_hideCvar4, NULL}' in ui_shared
    assert "qboolean MenuParse_backgroundSize( itemDef_t *item, int handle )" in ui_shared
    assert 'menu->backgroundSizeSet = qtrue;' in ui_shared
    assert '{"backgroundSize", MenuParse_backgroundSize, NULL}' in ui_shared

    admin_menu = (REPO_ROOT / "src/ui/ingame_admin.menu").read_text(encoding="utf-8")
    assert 'cvarTest2 "cg_gametype"' in admin_menu
    assert 'hideCvar2 { "0" ; "1" ; "2" ; "12" }' in admin_menu

    callvote_menu = (REPO_ROOT / "src/ui/ingame_callvote.menu").read_text(encoding="utf-8")
    assert 'cvarTest2 "ui_gameTypeVotingDisabled"' in callvote_menu
    assert 'showCvar2 { "1" }' in callvote_menu

    main_menu = (REPO_ROOT / "src/ui/main.menu").read_text(encoding="utf-8")
    connect_menu = (REPO_ROOT / "src/ui/connect.menu").read_text(encoding="utf-8")
    assert "backgroundSize 0 0 1920 1080" in main_menu
    assert "backgroundSize 0 0 1920 1080" in connect_menu

    controls_menu = (REPO_ROOT / "src/ui/ingame_controls.menu").read_text(encoding="utf-8")
    advanced_menu = (REPO_ROOT / "src/ui/ingame_options_advanced.menu").read_text(encoding="utf-8")
    assert controls_menu.lower().count("itemdef") > 96
    assert advanced_menu.lower().count("itemdef") > 96


def test_ui_retail_server_settings_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "static void UI_DrawServerSettings( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in ui_main
    assert 'UI_QLGametypeName( gametype )' in ui_main
    assert 'trap_GetConfigString( CS_PMOVE_SETTINGS, pmoveSettings, sizeof( pmoveSettings ) );' in ui_main
    assert 'UI_GetPmoveSettingFloat( pmoveSettings, "airControl", &airControl )' in ui_main
    assert 'UI_GetPmoveSettingBool( pmoveSettings, "rampJump", &hasRampJump )' in ui_main
    assert '"MODIFIED WEAPONS:"' in ui_main
    assert '"Default Settings"' in ui_main
    assert "case UI_SERVER_SETTINGS:" in ui_main
    assert "UI_DrawServerSettings(&rect, scale, color, textStyle);" in ui_main


def test_ui_retail_nextmap_ownerdraw_restored() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert "#define UI_NEXTMAP_CONFIGSTRING\t0x29A" in ui_main
    assert "static const char *UI_GetNextMapText( void )" in ui_main
    assert "trap_GetConfigString( UI_NEXTMAP_CONFIGSTRING, nextMapText, sizeof( nextMapText ) );" in ui_main
    assert "trap_GetConfigString( CS_ROTATION_TITLES, rotationTitles, sizeof( rotationTitles ) );" in ui_main
    assert 'Info_ValueForKey( rotationTitles, "title_0" )' in ui_main
    assert 'Info_ValueForKey( rotationTitles, "map_0" )' in ui_main
    assert "UI_MapRotationEntryForIndex( 0 )" in ui_main
    assert "static void UI_DrawNextMap( rectDef_t *rect, float scale, vec4_t color, int textStyle )" in ui_main
    assert "Text_Paint( rect->x, rect->y, scale, color, nextMapText, 0, 0, textStyle );" in ui_main
    assert "case UI_NEXTMAP:" in ui_main
    assert "UI_DrawNextMap(&rect, scale, color, textStyle);" in ui_main
