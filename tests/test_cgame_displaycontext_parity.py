"""Guard retail-backed cgame display-context bridge behavior against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_DRAWTOOLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_drawtools.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
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


def test_register_cvars_publishes_retail_version_and_vote_reset() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	block = _block_from_marker(source, "void CG_RegisterCvars")
	load_hud_block = _block_from_marker(source, "void CG_LoadHudMenu()")

	assert 'trap_Cvar_Register(NULL, "cg_version", Q3_VERSION, CVAR_ROM );' in block
	assert 'trap_Cvar_Set( "ui_voteactive", "0" );' in block
	assert "cgs.newHud = cg.competitiveHudLoaded;" in load_hud_block


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
