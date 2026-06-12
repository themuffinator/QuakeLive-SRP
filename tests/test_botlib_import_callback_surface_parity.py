from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
SERVER_SV_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"

EXPECTED_IMPORT_CALLBACK_ROWS = {
	"4DCF90": ("BotImport_Print", 90),
	"4DD0B0": ("BotImport_Trace", 173),
	"4DD160": ("BotImport_EntityTrace", 173),
	"4DD210": ("BotImport_PointContents", 19),
	"4DD230": ("BotImport_inPVS", 9),
	"4DD240": ("BotImport_BSPEntityData", None),
	"4DD250": ("BotImport_BSPModelMinsMaxsOrigin", 246),
	"4DD640": ("BotClientCommand", 35),
	"4DD350": ("BotImport_GetMemory", 19),
	"4DD370": ("BotImport_FreeMemory", 9),
	"4DD380": ("BotImport_HunkAlloc", 43),
	"4DD450": ("BotImport_DebugLineCreate", 46),
	"4DD430": ("BotImport_DebugPolygonDelete", 30),
	"4DD480": ("BotImport_DebugLineShow", 448),
	"4DD3B0": ("BotImport_DebugPolygonCreate", 125),
	"4DD940": ("SV_BotInitBotLib", 263),
}

EXPECTED_SOURCE_IMPORT_ORDER = (
	("Print", "BotImport_Print"),
	("Trace", "BotImport_Trace"),
	("EntityTrace", "BotImport_EntityTrace"),
	("PointContents", "BotImport_PointContents"),
	("inPVS", "BotImport_inPVS"),
	("BSPEntityData", "BotImport_BSPEntityData"),
	("BSPModelMinsMaxsOrigin", "BotImport_BSPModelMinsMaxsOrigin"),
	("BotClientCommand", "BotClientCommand"),
	("GetMemory", "BotImport_GetMemory"),
	("FreeMemory", "BotImport_FreeMemory"),
	("AvailableMemory", "Z_AvailableMemory"),
	("HunkAlloc", "BotImport_HunkAlloc"),
	("FS_FOpenFile", "FS_FOpenFileByMode"),
	("FS_Read", "FS_Read2"),
	("FS_Write", "FS_Write"),
	("FS_FCloseFile", "FS_FCloseFile"),
	("FS_Seek", "FS_Seek"),
	("DebugLineCreate", "BotImport_DebugLineCreate"),
	("DebugLineDelete", "BotImport_DebugPolygonDelete"),
	("DebugLineShow", "BotImport_DebugLineShow"),
	("DebugPolygonCreate", "BotImport_DebugPolygonCreate"),
	("DebugPolygonDelete", "BotImport_DebugPolygonDelete"),
)

EXPECTED_IMPORT_COPY_SLAB = (
	("Print", "BotImport_Print", "var_5c", "sub_4dcf90"),
	("Trace", "BotImport_Trace", "var_58", "sub_4dd0b0"),
	("EntityTrace", "BotImport_EntityTrace", "var_54", "sub_4dd160"),
	("PointContents", "BotImport_PointContents", "var_50", "sub_4dd210"),
	("inPVS", "BotImport_inPVS", "var_4c", "sub_4dd230"),
	("BSPEntityData", "BotImport_BSPEntityData", "var_48", "j_sub_4c0250"),
	("BSPModelMinsMaxsOrigin", "BotImport_BSPModelMinsMaxsOrigin", "var_44", "sub_4dd250"),
	("BotClientCommand", "BotClientCommand", "var_40", "sub_4dd640"),
	("GetMemory", "BotImport_GetMemory", "var_3c", "sub_4dd350"),
	("FreeMemory", "BotImport_FreeMemory", "var_38", "sub_4dd370"),
	("AvailableMemory", "Z_AvailableMemory", "var_34", "sub_4c9220"),
	("HunkAlloc", "BotImport_HunkAlloc", "var_30", "sub_4dd380"),
	("FS_FOpenFile", "FS_FOpenFileByMode", "var_2c", "sub_4d22c0"),
	("FS_Read", "FS_Read2", "var_28", "sub_4d2a80"),
	("FS_Write", "FS_Write", "var_24", "sub_4d00f0"),
	("FS_FCloseFile", "FS_FCloseFile", "var_20", "sub_4cf320"),
	("FS_Seek", "FS_Seek", "var_1c", "sub_4d0240"),
	("DebugLineCreate", "BotImport_DebugLineCreate", "var_18", "sub_4dd450"),
	("DebugLineDelete", "BotImport_DebugPolygonDelete", "var_14", "sub_4dd430"),
	("DebugLineShow", "BotImport_DebugLineShow", "var_10", "sub_4dd480"),
	("DebugPolygonCreate", "BotImport_DebugPolygonCreate", "var_c", "sub_4dd3b0"),
	("DebugPolygonDelete", "BotImport_DebugPolygonDelete", "var_8", "sub_4dd430"),
)

EXPECTED_RETAIL_IMPORT_LOCALS = (
	"004dd99c  int32_t (* var_5c)(int32_t arg1, int32_t arg2) = sub_4dcf90",
	"004dd9a3  int32_t (* var_58)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
	"004dd9aa  int32_t (* var_54)(int32_t* arg1, float* arg2, int32_t* arg3, int32_t* arg4, float* arg5,",
	"004dd9b1  int32_t (* var_50)(float* arg1) = sub_4dd210",
	"004dd9b8  int32_t (* var_4c)() = sub_4dd230",
	"004dd9bf  int32_t (* var_48)() = j_sub_4c0250",
	"004dd9c6  float* (* var_44)(int32_t arg1, float* arg2, float* arg3, float* arg4, float* arg5) =",
	"004dd9cd  void* (* var_40)(int32_t arg1, char* arg2) = sub_4dd640",
	"004dd9d4  void* (* var_3c)(int32_t arg1) = sub_4dd350",
	"004dd9db  int32_t (* var_38)() = sub_4dd370",
	"004dd9e2  int32_t (* var_34)() = sub_4c9220",
	"004dd9e9  char* (* var_30)(int32_t arg1) = sub_4dd380",
	"004dd9f0  int32_t (* var_2c)(int32_t arg1, int32_t* arg2, int32_t arg3) = sub_4d22c0",
	"004dd9f7  void* (* var_28)(int32_t arg1, int32_t arg2, int32_t arg3) = sub_4d2a80",
	"004dd9fe  int32_t (* var_24)(int32_t arg1, int32_t arg2, int32_t arg3) = sub_4d00f0",
	"004dda05  int32_t (* var_20)(int32_t arg1) = sub_4cf320",
	"004dda0c  int32_t (* var_1c)(int32_t arg1 @ edi, int32_t arg2, int32_t arg3, int32_t arg4) =",
	"004dda13  int32_t (* var_18)() = sub_4dd450",
	"004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430",
	"004dda21  int32_t (* var_10)(int32_t arg1, float* arg2, float* arg3, int32_t arg4) = sub_4dd480",
	"004dda28  int32_t (* var_c)(int32_t arg1, int32_t arg2, int32_t* arg3) = sub_4dd3b0",
	"004dda2f  int32_t (* var_8)(int32_t arg1) = sub_4dd430",
	"004dda36  int32_t result = sub_4a83c0(2, &var_5c)",
	"004dda3e  data_13e1844 = result",
)

EXPECTED_IMPORT_WRAPPER_HLIL_BLOCKS = (
	(
		"BotImport_Print",
		"004dcf90    int32_t sub_4dcf90(int32_t arg1, int32_t arg2)",
		"004dd0b0    int32_t sub_4dd0b0",
		(
			"004dcfb2  vsprintf(&var_808, arg2, &arg_c)",
			'004dd00a          sub_525f8e(eax_1 ^ &__saved_ebp)',
			'004dd041          int32_t eax_7 = sub_4c9860(esi, "^1Fatal: %s")',
			'004dd065          sub_4c9b60(1, "^1Exit: %s")',
			'004dd080      int32_t eax_8 = sub_4c9860(esi, "unknown print type\\n")',
		),
	),
	(
		"BotImport_Trace",
		"004dd0b0    int32_t sub_4dd0b0",
		"004dd160    int32_t sub_4dd160",
		(
			"004dd0e4  sub_4e6930(&var_40, arg2, arg3, arg4, arg5, arg6, arg7, 0)",
			"004dd0ec  float var_38",
			"004dd10d  *arg1 = ecx_1",
			"004dd12a  int32_t var_c",
			"004dd147  arg1[0xb] = fconvert.s(float.t(0))",
			"004dd14a  arg1[0xc] = 0",
			"004dd14d  arg1[0x13] = 0",
		),
	),
	(
		"BotImport_EntityTrace",
		"004dd160    int32_t sub_4dd160",
		"004dd210    int32_t sub_4dd210",
		(
			"004dd194  sub_4e6690(&var_40, arg2, arg3, arg4, arg5, arg6, arg7, 0)",
			"004dd19c  float var_38",
			"004dd1bd  *arg1 = ecx_1",
			"004dd1da  int32_t var_c",
			"004dd1f7  arg1[0xb] = fconvert.s(float.t(0))",
			"004dd1fa  arg1[0xc] = 0",
			"004dd1fd  arg1[0x13] = 0",
		),
	),
	(
		"BotImport_PointContents",
		"004dd210    int32_t sub_4dd210(float* arg1)",
		"004dd230    int32_t sub_4dd230()",
		("004dd222  return sub_4e6ac0(arg1, 0xffffffff)",),
	),
	(
		"BotImport_inPVS",
		"004dd230    int32_t sub_4dd230()",
		"004dd240    int32_t j_sub_4c0250()",
		("004dd234  return sub_4e1230() __tailcall",),
	),
	(
		"BotImport_BSPEntityData",
		"004dd240    int32_t j_sub_4c0250()",
		"004dd250    float* sub_4dd250",
		("004dd240  return sub_4c0250() __tailcall",),
	),
	(
		"BotImport_BSPModelMinsMaxsOrigin",
		"004dd250    float* sub_4dd250",
		"004dd350    void* sub_4dd350",
		(
			"004dd27e  sub_4c0540(sub_4c0210(arg1), &var_14, &var_20)",
			"004dd2c0      label_4dd2c0:",
			"004dd2c0      st0_1, result = sub_4d8000(&var_14, &var_20)",
			"004dd2f3      *arg3 = fconvert.s(fconvert.t(var_14))",
			"004dd308      *arg4 = fconvert.s(fconvert.t(var_20))",
			"004dd31a  arg5[2] = fconvert.s(x87_r7)",
			"004dd322  *arg5 = fconvert.s(x87_r7)",
		),
	),
	(
		"BotImport_GetMemory",
		"004dd350    void* sub_4dd350(int32_t arg1)",
		"004dd370    int32_t sub_4dd370()",
		("004dd362  return sub_4ca2c0(arg1, 2)",),
	),
	(
		"BotImport_FreeMemory",
		"004dd370    int32_t sub_4dd370()",
		"004dd380    char* sub_4dd380",
		("004dd374  return sub_4ca1d0() __tailcall",),
	),
	(
		"BotImport_HunkAlloc",
		"004dd380    char* sub_4dd380(int32_t arg1)",
		"004dd3b0    int32_t sub_4dd3b0",
		(
			"004dd38a  if (sub_4c9310() == 0)",
			'004dd393  sub_4c9b60(1, "SV_Bot_HunkAlloc: Alloc with mar…")',
			"004dd3aa      return sub_4ca980(arg1, 0)",
		),
	),
	(
		"BotImport_DebugPolygonCreate",
		"004dd3b0    int32_t sub_4dd3b0",
		"004dd430    int32_t sub_4dd430",
		(
			"004dd3b3  void* edx = data_12cdeb0",
			"004dd3c1  int32_t ecx = data_13e184c",
			"004dd3c8  int32_t result = 1",
			"004dd3e4          if (result s>= ecx)",
			"004dd3ff          void* eax_7 = result * 0x60c + edx",
			"004dd401          *(eax_7 + 4) = arg1",
			"004dd40c          *(eax_7 + 8) = arg2",
			"004dd415          *eax_7 = 1",
			"004dd420          sub_4cb7d0(eax_7 + 0xc, arg3, arg2 * 0xc)",
		),
	),
	(
		"BotImport_DebugPolygonDelete",
		"004dd430    int32_t sub_4dd430(int32_t arg1)",
		"004dd450    int32_t sub_4dd450()",
		(
			"004dd433  int32_t result = data_12cdeb0",
			"004dd43a  if (result != 0)",
			"004dd445      *(arg1 * 0x60c + result) = 0",
		),
	),
	(
		"BotImport_DebugLineCreate",
		"004dd450    int32_t sub_4dd450()",
		"004dd480    int32_t sub_4dd480",
		("004dd468  int32_t result = sub_4dd3b0(0, 0, &var_14)",),
	),
	(
		"BotImport_DebugLineShow",
		"004dd480    int32_t sub_4dd480",
		"004dd640    void* sub_4dd640",
		(
			"004dd4de  float var_50 = fconvert.s(fconvert.t(*arg3) - fconvert.t(*arg2))",
			"004dd4f7  sub_4d8190(&var_50)",
			"004dd524  long double temp1 = fconvert.t(0.98999999999999999)",
			"004dd568      var_14 = fconvert.s(float.t(1))",
			"004dd577  st0_1, result = sub_4d8190(&var_14)",
			"004dd587  long double x87_r6_3 = fconvert.t(2.0)",
			"004dd600  if (ecx_1 != 0)",
			"004dd615      *eax_6 = 1",
			"004dd61b      eax_6[1] = arg4",
			"004dd61e      eax_6[2] = 4",
			"004dd62a      result = sub_4cb7d0(&eax_6[3], &var_44, 0x30)",
		),
	),
	(
		"BotClientCommand",
		"004dd640    void* sub_4dd640(int32_t arg1, char* arg2)",
		"004dd670    int32_t sub_4dd670()",
		("004dd662  return sub_4e0090(arg1 * 0x25b68 + data_13337ac, arg2, 1)",),
	),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	aliases = json.loads(_read(SYMBOL_ALIASES))
	if "quakelive_steam_srp" in aliases:
		return aliases["quakelive_steam_srp"]
	return aliases["quakelive_steam"]


def _function_rows() -> dict[str, str]:
	rows: dict[str, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()[2:]] = (
				f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			)
	return rows


def _extract_function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	assert start != -1, signature
	brace = source.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(source)):
		if source[offset] == "{":
			depth += 1
		elif source[offset] == "}":
			depth -= 1
			if depth == 0:
				return source[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _extract_text_window(source: str, start_anchor: str, end_anchor: str) -> str:
	start = source.index(start_anchor)
	end = source.index(end_anchor, start + len(start_anchor))
	return source[start:end]


def test_botlib_import_callback_surface_aliases_rows_and_hlil_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()
	hlil = _read(QL_STEAM_HLIL_PART04)

	for address, (name, size) in EXPECTED_IMPORT_CALLBACK_ROWS.items():
		assert aliases[f"sub_{address}"] == name
		if size is None:
			assert address not in rows
		else:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	assert "4DD400" not in rows
	assert "BotImport_DebugPolygonShow" not in aliases.values()

	for anchor in EXPECTED_RETAIL_IMPORT_LOCALS:
		assert anchor in hlil

	assert hlil.index("004dda13  int32_t (* var_18)() = sub_4dd450") < hlil.index(
		"004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430"
	)
	assert hlil.index("004dda1a  int32_t (* var_14)(int32_t arg1) = sub_4dd430") < hlil.index(
		"004dda21  int32_t (* var_10)(int32_t arg1, float* arg2, float* arg3, int32_t arg4) = sub_4dd480"
	)
	assert hlil.index("004dda28  int32_t (* var_c)(int32_t arg1, int32_t arg2, int32_t* arg3) = sub_4dd3b0") < hlil.index(
		"004dda2f  int32_t (* var_8)(int32_t arg1) = sub_4dd430"
	)


def test_botlib_import_callback_surface_source_layout_matches_retail_order() -> None:
	botlib_h = _read(BOTLIB_H)
	sv_bot = _read(SERVER_SV_BOT)
	import_decl = _extract_function_block(botlib_h, "typedef struct botlib_import_s")
	init_botlib = _extract_function_block(sv_bot, "void SV_BotInitBotLib")
	debug_line_delete = _extract_function_block(sv_bot, "void BotImport_DebugLineDelete")

	last_field_pos = -1
	last_init_pos = -1
	for field, target in EXPECTED_SOURCE_IMPORT_ORDER:
		field_anchor = f"(*{field})"
		if field == "Print":
			field_anchor = "(QDECL *Print)"
		assert field_anchor in import_decl
		field_pos = import_decl.index(field_anchor)
		assert field_pos > last_field_pos
		last_field_pos = field_pos

		init_anchor = f"botlib_import.{field} = {target};"
		assert init_anchor in init_botlib
		init_pos = init_botlib.index(init_anchor)
		assert init_pos > last_init_pos
		last_init_pos = init_pos

	assert "botlib_import.DebugLineDelete = BotImport_DebugLineDelete;" not in init_botlib
	assert "BotImport_DebugPolygonDelete(line);" in debug_line_delete
	assert "botlib_export = (botlib_export_t *)GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );" in init_botlib
	assert "assert(botlib_export);" in init_botlib


def test_botlib_import_callback_copy_slab_matches_retail_getapi_abi() -> None:
	botlib_h = _read(BOTLIB_H)
	be_interface = _read(BOTLIB_INTERFACE)
	sv_bot = _read(SERVER_SV_BOT)
	hlil_getapi = _read(QL_STEAM_HLIL_PART03)
	hlil_init = _read(QL_STEAM_HLIL_PART04)

	import_decl = _extract_function_block(botlib_h, "typedef struct botlib_import_s")
	get_api = _extract_function_block(be_interface, "botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)")
	init_botlib = _extract_function_block(sv_bot, "void SV_BotInitBotLib")
	init_hlil_start = hlil_init.index("004dd940    int32_t sub_4dd940()")
	init_hlil_end = hlil_init.index("004dda50    int32_t sub_4dda50", init_hlil_start)
	init_hlil = hlil_init[init_hlil_start:init_hlil_end]

	assert len(EXPECTED_IMPORT_COPY_SLAB) == len(EXPECTED_SOURCE_IMPORT_ORDER) == 0x58 // 4
	assert "004a83de  __builtin_memcpy(dest: &data_16dd800, src: arg2, n: 0x58)" in hlil_getapi
	assert "004dda36  int32_t result = sub_4a83c0(2, &var_5c)" in init_hlil
	assert "004dda3e  data_13e1844 = result" in init_hlil
	assert "botlib_import_t\tbotlib_import;" in init_botlib
	assert "botimport = *import;" in get_api
	assert "assert(botimport.Print);" in get_api
	assert "Com_Memset( &be_botlib_export, 0, sizeof( be_botlib_export ) );" in get_api

	previous_field_pos = -1
	previous_init_pos = -1
	previous_stack_pos = -1
	for field, source_target, stack_local, retail_target in EXPECTED_IMPORT_COPY_SLAB:
		field_anchor = "(QDECL *Print)" if field == "Print" else f"(*{field})"
		field_pos = import_decl.index(field_anchor)
		assert previous_field_pos < field_pos
		previous_field_pos = field_pos

		init_anchor = f"botlib_import.{field} = {source_target};"
		init_pos = init_botlib.index(init_anchor)
		assert previous_init_pos < init_pos
		previous_init_pos = init_pos

		stack_pos = init_hlil.index(f" {stack_local}")
		assert previous_stack_pos < stack_pos
		previous_stack_pos = stack_pos
		assert init_hlil.index(retail_target, stack_pos) > stack_pos

	assert previous_init_pos < init_botlib.index(
		"botlib_export = (botlib_export_t *)GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );"
	)


def test_botlib_import_callback_wrapper_hlil_bodies_match_source_contracts() -> None:
	hlil = _read(QL_STEAM_HLIL_PART04)

	for name, start_anchor, end_anchor, anchors in EXPECTED_IMPORT_WRAPPER_HLIL_BLOCKS:
		block = _extract_text_window(hlil, start_anchor, end_anchor)
		for anchor in anchors:
			assert anchor in block, f"{name}: {anchor}"

	debug_line_show = _extract_text_window(
		hlil,
		"004dd480    int32_t sub_4dd480",
		"004dd640    void* sub_4dd640",
	)
	assert "sub_4dd3b0" not in debug_line_show
	assert "sub_4dd430" not in debug_line_show


def test_botlib_import_callback_surface_source_bodies_match_retail_contracts() -> None:
	sv_bot = _read(SERVER_SV_BOT)
	print_import = _extract_function_block(sv_bot, "void QDECL BotImport_Print")
	trace = _extract_function_block(
		sv_bot,
		"void BotImport_Trace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int passent, int contentmask)",
	)
	entity_trace = _extract_function_block(
		sv_bot,
		"void BotImport_EntityTrace(bsp_trace_t *bsptrace, vec3_t start, vec3_t mins, vec3_t maxs, vec3_t end, int entnum, int contentmask)",
	)
	bsp_entity_data = _extract_function_block(sv_bot, "char *BotImport_BSPEntityData")
	bsp_model_bounds = _extract_function_block(sv_bot, "void BotImport_BSPModelMinsMaxsOrigin")
	hunk_alloc = _extract_function_block(sv_bot, "void *BotImport_HunkAlloc")
	debug_polygon_create = _extract_function_block(sv_bot, "int BotImport_DebugPolygonCreate")
	debug_polygon_show = _extract_function_block(sv_bot, "void BotImport_DebugPolygonShow")
	debug_polygon_delete = _extract_function_block(sv_bot, "void BotImport_DebugPolygonDelete")
	debug_line_create = _extract_function_block(sv_bot, "int BotImport_DebugLineCreate")
	debug_line_show = _extract_function_block(sv_bot, "void BotImport_DebugLineShow")
	bot_client_command = _extract_function_block(sv_bot, "void BotClientCommand")

	for print_anchor in (
		"vsprintf(str, fmt, ap);",
		'Com_Printf("%s", str);',
		'Com_Printf(S_COLOR_YELLOW "Warning: %s", str);',
		'Com_Printf(S_COLOR_RED "Error: %s", str);',
		'Com_Printf(S_COLOR_RED "Fatal: %s", str);',
		'Com_Error(ERR_DROP, S_COLOR_RED "Exit: %s", str);',
		'Com_Printf("unknown print type\\n");',
	):
		assert print_anchor in print_import

	for trace_block, trace_call in (
		(trace, "SV_Trace(&trace, start, mins, maxs, end, passent, contentmask, qfalse);"),
		(entity_trace, "SV_ClipToEntity(&trace, start, mins, maxs, end, entnum, contentmask, qfalse);"),
	):
		assert trace_call in trace_block
		for copy_anchor in (
			"bsptrace->allsolid = trace.allsolid;",
			"bsptrace->startsolid = trace.startsolid;",
			"bsptrace->fraction = trace.fraction;",
			"VectorCopy(trace.endpos, bsptrace->endpos);",
			"bsptrace->plane.dist = trace.plane.dist;",
			"VectorCopy(trace.plane.normal, bsptrace->plane.normal);",
			"bsptrace->plane.signbits = trace.plane.signbits;",
			"bsptrace->plane.type = trace.plane.type;",
			"bsptrace->surface.value = trace.surfaceFlags;",
			"bsptrace->ent = trace.entityNum;",
			"bsptrace->exp_dist = 0;",
			"bsptrace->sidenum = 0;",
			"bsptrace->contents = 0;",
		):
			assert copy_anchor in trace_block

	assert "return CM_EntityString();" in bsp_entity_data
	for bounds_anchor in (
		"h = CM_InlineModel(modelnum);",
		"CM_ModelBounds(h, mins, maxs);",
		"if ((angles[0] || angles[1] || angles[2])) {",
		"max = RadiusFromBounds(mins, maxs);",
		"if (outmins) VectorCopy(mins, outmins);",
		"if (outmaxs) VectorCopy(maxs, outmaxs);",
		"if (origin) VectorClear(origin);",
	):
		assert bounds_anchor in bsp_model_bounds

	assert 'Com_Error( ERR_DROP, "SV_Bot_HunkAlloc: Alloc with marks already set\\n" );' in hunk_alloc
	assert "return Hunk_Alloc( size, h_high );" in hunk_alloc

	for polygon_anchor in (
		"if (!debugpolygons)",
		"for (i = 1; i < bot_maxdebugpolys; i++)",
		"if (i >= bot_maxdebugpolys)",
		"poly->inuse = qtrue;",
		"poly->color = color;",
		"poly->numPoints = numPoints;",
		"Com_Memcpy(poly->points, points, numPoints * sizeof(vec3_t));",
	):
		assert polygon_anchor in debug_polygon_create

	for polygon_show_anchor in (
		"if (!debugpolygons) return;",
		"poly = &debugpolygons[id];",
		"poly->inuse = qtrue;",
		"poly->color = color;",
		"poly->numPoints = numPoints;",
		"Com_Memcpy(poly->points, points, numPoints * sizeof(vec3_t));",
	):
		assert polygon_show_anchor in debug_polygon_show
	assert "debugpolygons[id].inuse = qfalse;" in debug_polygon_delete

	assert "return BotImport_DebugPolygonCreate(0, 0, points);" in debug_line_create
	for line_show_anchor in (
		"VectorSubtract(end, start, dir);",
		"VectorNormalize(dir);",
		"dot = DotProduct(dir, up);",
		"if (dot > 0.99 || dot < -0.99) VectorSet(cross, 1, 0, 0);",
		"else CrossProduct(dir, up, cross);",
		"VectorMA(points[0], 2, cross, points[0]);",
		"VectorMA(points[1], -2, cross, points[1]);",
		"VectorMA(points[2], -2, cross, points[2]);",
		"VectorMA(points[3], 2, cross, points[3]);",
		"BotImport_DebugPolygonShow(line, color, 4, points);",
	):
		assert line_show_anchor in debug_line_show

	assert "SV_ExecuteClientCommand( &svs.clients[client], command, qtrue );" in bot_client_command
