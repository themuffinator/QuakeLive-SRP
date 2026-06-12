from __future__ import annotations

import csv
import json
import re
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
QL_STEAM_HLIL_PART05 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part05.txt"
)
QL_STEAM_HLIL_PART07 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part07.txt"
)
SERVER_SV_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_SV_INIT = REPO_ROOT / "src" / "code" / "server" / "sv_init.c"
SERVER_SV_MAIN = REPO_ROOT / "src" / "code" / "server" / "sv_main.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"

SERVER_BOT_BRIDGE_START = 0x4DCD00
SERVER_BOT_BRIDGE_END = 0x4DDB00
GAME_BOT_IMPORT_START = 0x4E1600
GAME_BOT_IMPORT_END = 0x4E1820
BOT_BRIDGE_NAME_PATTERN = re.compile(
	r"(Bot|BotImport|BotLib|QL_G_trap_Bot|PC_AddGlobalDefine|SV_GetUsercmd|"
	r"SV_GetEntityToken|DebugPolygon)"
)

EXPECTED_SERVER_GAME_BRIDGE_ALIASES = {
	"4DCD30": ("SV_BotAllocateClient", None),
	"4DCDB0": ("SV_BotFreeClient", 82),
	"4DCE10": ("BotDrawDebugPolygons", 375),
	"4DCF90": ("BotImport_Print", 90),
	"4DD0B0": ("BotImport_Trace", 173),
	"4DD160": ("BotImport_EntityTrace", 173),
	"4DD210": ("BotImport_PointContents", 19),
	"4DD230": ("BotImport_inPVS", 9),
	"4DD240": ("BotImport_BSPEntityData", None),
	"4DD250": ("BotImport_BSPModelMinsMaxsOrigin", 246),
	"4DD350": ("BotImport_GetMemory", 19),
	"4DD370": ("BotImport_FreeMemory", 9),
	"4DD380": ("BotImport_HunkAlloc", 43),
	"4DD3B0": ("BotImport_DebugPolygonCreate", 125),
	"4DD430": ("BotImport_DebugPolygonDelete", 30),
	"4DD450": ("BotImport_DebugLineCreate", 46),
	"4DD480": ("BotImport_DebugLineShow", 448),
	"4DD640": ("BotClientCommand", 35),
	"4DD670": ("SV_BotFrame", 35),
	"4DD6A0": ("SV_BotLibSetup", None),
	"4DD6D0": ("SV_BotLibShutdown", None),
	"4DD6F0": ("SV_BotInitCvars", 579),
	"4DD940": ("SV_BotInitBotLib", 263),
	"4DDA50": ("SV_BotGetConsoleMessage", 102),
	"4DDAC0": ("SV_BotGetSnapshotEntity", 91),
	"4E1610": ("QL_G_trap_BotAllocateClient", None),
	"4E1620": ("QL_G_trap_BotFreeClient", 9),
	"4E1630": ("SV_GetUsercmd", 71),
	"4E1680": ("SV_GetEntityToken", 60),
	"4E16C0": ("QL_G_trap_DebugPolygonCreate", 9),
	"4E16D0": ("QL_G_trap_DebugPolygonDelete", 9),
	"4E16E0": ("QL_G_trap_BotLibSetup", None),
	"4E16F0": ("QL_G_trap_BotLibShutdown", None),
	"4E1700": ("QL_G_trap_BotLibVarSet", 18),
	"4E1720": ("QL_G_trap_BotLibVarGet", 17),
	"4E1740": ("PC_AddGlobalDefine", 18),
	"4E1760": ("QL_G_trap_BotLibStartFrame", 28),
	"4E1780": ("QL_G_trap_BotLibLoadMap", 18),
	"4E17A0": ("QL_G_trap_BotLibUpdateEntity", 18),
	"4E17C0": ("QL_G_trap_BotLibTest", 18),
	"4E17E0": ("QL_G_trap_BotGetSnapshotEntity", 9),
	"4E17F0": ("QL_G_trap_BotGetServerCommand", 9),
	"4E1800": ("QL_G_trap_BotUserCommand", 33),
}

EXPECTED_NATIVE_GAME_IMPORT_ASSIGNMENTS = (
	("G_QL_IMPORT_BOT_ALLOCATE_CLIENT", "QL_G_trap_BotAllocateClient"),
	("G_QL_IMPORT_BOT_FREE_CLIENT", "QL_G_trap_BotFreeClient"),
	("G_QL_IMPORT_GET_USERCMD", "QL_G_trap_GetUsercmd"),
	("G_QL_IMPORT_GET_ENTITY_TOKEN", "QL_G_trap_GetEntityToken"),
	("G_QL_IMPORT_DEBUG_POLYGON_CREATE", "QL_G_trap_DebugPolygonCreate"),
	("G_QL_IMPORT_DEBUG_POLYGON_DELETE", "QL_G_trap_DebugPolygonDelete"),
	("G_QL_IMPORT_BOTLIB_SETUP", "QL_G_trap_BotLibSetup"),
	("G_QL_IMPORT_BOTLIB_SHUTDOWN", "QL_G_trap_BotLibShutdown"),
	("G_QL_IMPORT_BOTLIB_LIBVAR_SET", "QL_G_trap_BotLibVarSet"),
	("G_QL_IMPORT_BOTLIB_LIBVAR_GET", "QL_G_trap_BotLibVarGet"),
	("G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE", "QL_G_trap_BotLibDefine"),
	("G_QL_IMPORT_BOTLIB_START_FRAME", "QL_G_trap_BotLibStartFrame"),
	("G_QL_IMPORT_BOTLIB_LOAD_MAP", "QL_G_trap_BotLibLoadMap"),
	("G_QL_IMPORT_BOTLIB_UPDATE_ENTITY", "QL_G_trap_BotLibUpdateEntity"),
	("G_QL_IMPORT_BOTLIB_TEST", "QL_G_trap_BotLibTest"),
	("G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY", "QL_G_trap_BotGetSnapshotEntity"),
	("G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE", "QL_G_trap_BotGetServerCommand"),
	("G_QL_IMPORT_BOTLIB_USER_COMMAND", "QL_G_trap_BotUserCommand"),
)

EXPECTED_BOT_FRAME_CALLSITE_OWNERS = (
	("4DD670", "SV_BotFrame", 35),
	("4DD6F0", "SV_BotInitCvars", 579),
	("4DD940", "SV_BotInitBotLib", 263),
	("4E2C10", "SV_InitGameProgs", 130),
	("4E31B0", "SV_CreateBaseline", 89),
	("4E3510", "SV_SpawnServer", 1468),
	("4E3AD0", "SV_Init", 1015),
	("4E49D0", "SV_Frame", 758),
)

EXPECTED_SERVER_BOT_CLIENT_HLIL_BLOCKS = (
	(
		"SV_BotAllocateClient",
		"004dcd30    int32_t sub_4dcd30()",
		"004dcdb0    void* sub_4dcdb0",
		(
			"004dcd35  int32_t eax = *(data_13e17ec + 0x30)",
			"004dcd39  int32_t* esi = data_13337ac",
			"004dcd44  if (eax s> 0)",
			"004dcd49      while (*esi != 0)",
			"004dcd58  if (result == eax)",
			"004dcd5f      return 0xffffffff",
			"004dcd61  int32_t* eax_2 = sub_4e10b0(result)",
			"004dcd66  esi[0x4210] = eax_2",
			"004dcd6c  *eax_2 = result",
			"004dcd6e  *esi = 4",
			"004dcd7d  esi[0x426f] = data_13337a4",
			"004dcd83  esi[0x56bb] = 0",
			"004dcd8d  esi[0x56b5] = 0x4000",
			"004dcd97  eax_3, edx = sub_465df0()",
			"004dcd9c  esi[0x96d8] = eax_3",
			"004dcda5  esi[0x96d9] = edx",
			"004dcdac  return result",
		),
	),
	(
		"SV_BotFreeClient",
		"004dcdb0    void* sub_4dcdb0(int32_t arg1)",
		"004dce10    void sub_4dce10",
		(
			"004dcdb9  if (arg1 s>= 0)",
			"004dcdc3      if (arg1 s< *(result + 0x30))",
			"004dcddb          int32_t* esi_2 = arg1 * 0x25b68 + data_13337ac",
			"004dcde1          *esi_2 = 0",
			"004dcde7          esi_2[0x4211].b = 0",
			"004dcdee          void* esi_3 = esi_2[0x4210]",
			"004dcdf8              *(esi_3 + 0x1e0) &= 0xfffffff7",
			'004dcdcd  sub_4c9b60(1, "SV_BotFreeClient: bad clientNum:',
		),
	),
	(
		"BotDrawDebugPolygons",
		"004dce10    void sub_4dce10(int32_t arg1)",
		"004dcf90    int32_t sub_4dcf90",
		(
			"004dce13  int32_t ecx = data_12cdeb0",
			"004dce1b  if (ecx != 0)",
			"004dce35          eax = sub_4ce0d0(x87_r0, \"bot_debug\", U\"0\", eax)",
			"004dce5a      if (data_13e1848 != 0 && eax[0xc] != 0)",
			"004dce7d              data_12cdea4 = sub_4ce0d0(\"bot_reachability\", U\"0\", nullptr)",
			"004dce9f              data_12cdea8 = sub_4ce0d0(\"bot_groundonly\", U\"1\", nullptr)",
			"004dceb8              eax_3 = sub_4ce0d0(\"bot_highlightarea\", U\"0\", eax_3)",
			"004dced4          if ((*(data_13337ac + 0x1042c) & 1) != 0)",
			"004dcee7              esi_1 |= 2",
			"004dcef6              esi_1 |= 4",
			"004dcf0d          (*(data_13e1844 + 0x1f8))(\"bot_highlightarea\", eax_3[1])",
			"004dcf37          (*(data_13e1844 + 0x220))(esi_1, 0, eax_5 + 0x220, eax_5 + 0x22c)",
			"004dcf4b      if (data_13e184c s> 0)",
			"004dcf57              if (*(esi_2 + ecx) != 0)",
			"004dcf68                  arg1(*(esi_2 + ecx + 4), *(esi_2 + ecx + 8), esi_2 + ecx + 0xc)",
		),
	),
)

EXPECTED_QAGAME_BOT_CLIENT_HLIL_BLOCKS = (
	(
		"QL_G_trap_BotAllocateClient",
		"004e1610    int32_t j_sub_4dcd30()",
		"004e1620    int32_t sub_4e1620()",
		("004e1610  return sub_4dcd30() __tailcall",),
	),
	(
		"QL_G_trap_BotFreeClient",
		"004e1620    int32_t sub_4e1620()",
		"004e1630    void* sub_4e1630",
		("004e1624  return sub_4dcdb0() __tailcall",),
	),
	(
		"SV_GetUsercmd",
		"004e1630    void* sub_4e1630(int32_t arg1, int32_t arg2)",
		"004e1680    int32_t sub_4e1680",
		(
			"004e163a  if (arg1 s>= 0)",
			"004e1644      if (arg1 s< *(result + 0x30))",
			"004e1671          __builtin_memcpy(dest: arg2, src: arg1 * 0x25b68 + data_13337ac + 0x1041c,",
			"004e1671              n: 0x1c)",
			'004e164e  sub_4c9b60(1, "SV_GetUsercmd: bad clientNum:%i")',
		),
	),
	(
		"SV_GetEntityToken",
		"004e1680    int32_t sub_4e1680(int32_t arg1, int32_t arg2)",
		"004e16c0    int32_t sub_4e16c0",
		(
			"004e1689  sub_4d9b00(&data_1333764)",
			"004e1699  sub_4d8f40(arg1, &data_124e6c0, arg2)",
			"004e16ad  if (data_1333764 == 0 && data_124e6c0 == 0)",
			"004e16b3      return 0",
			"004e16bb  return 1",
		),
	),
	(
		"QL_G_trap_DebugPolygonCreate",
		"004e16c0    int32_t sub_4e16c0()",
		"004e16d0    int32_t sub_4e16d0()",
		("004e16c4  return sub_4dd3b0() __tailcall",),
	),
	(
		"QL_G_trap_DebugPolygonDelete",
		"004e16d0    int32_t sub_4e16d0()",
		"004e16e0    int32_t j_sub_4dd6a0()",
		("004e16d4  return sub_4dd430() __tailcall",),
	),
)

EXPECTED_SERVER_BOTLIB_RUNTIME_HLIL_BLOCKS = (
	(
		"SV_BotLibSetup",
		"004dd6a0    int32_t sub_4dd6a0()",
		"004dd6d0    int32_t sub_4dd6d0()",
		(
			"004dd6a7  if (data_13e1848 == 0)",
			"004dd6ab      return 0",
			"004dd6ac  void* eax_1 = data_13e1844",
			"004dd6b3  if (eax_1 != 0)",
			"004dd6cc      jump(*(eax_1 + 0x1f0))",
			'004dd6ba  sub_4c9860(esi, "^1Error: SV_BotLibSetup without',
			"004dd6c5  return 0xffffffff",
		),
	),
	(
		"SV_BotLibShutdown",
		"004dd6d0    int32_t sub_4dd6d0()",
		"004dd6f0    void** sub_4dd6f0()",
		(
			"004dd6d0  void* eax_2 = data_13e1844",
			"004dd6d7  if (eax_2 != 0)",
			"004dd6e3      jump(*(eax_2 + 0x1f4))",
			"004dd6dc  return 0xffffffff",
		),
	),
	(
		"SV_BotGetConsoleMessage",
		"004dda50    int32_t sub_4dda50(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004ddac0    int32_t sub_4ddac0",
		(
			"004dda62  void* eax_2 = arg1 * 0x25b68 + data_13337ac",
			"004dda68  *(eax_2 + 0x109bc) = data_13337a4",
			"004dda6e  int32_t ecx_1 = *(eax_2 + 0x10408)",
			"004dda7a  if (ecx_1 != *(eax_2 + 0x10404))",
			"004dda81      *(eax_2 + 0x10408) = ecx_1 + 1",
			"004dda8a      int32_t ecx_4 = ((ecx_1 + 1) & 0x3f) << 0xa",
			"004dda9c      if (*(ecx_4 + eax_2 + 0x404) != 0)",
			"004ddaa7          sub_4d8f40(arg2, ecx_4 + eax_2 + 0x404, arg3)",
			"004ddab5          return 1",
			"004dda7f  return 0",
		),
	),
	(
		"SV_BotGetSnapshotEntity",
		"004ddac0    int32_t sub_4ddac0(int32_t arg1, int32_t arg2)",
		"004ddb20    int32_t* sub_4ddb20()",
		(
			"004ddacc  void* eax_2 = arg1 * 0x25b68 + data_13337ac",
			"004ddae1  void* eax_3 = (*(eax_2 + 0x15b08) & 0x1f) * 0x288 + eax_2 + 0x109d0",
			"004ddaf5  if (arg2 s< 0 || arg2 s>= *(eax_3 + 0x274))",
			"004ddb1a      return 0xffffffff",
			"004ddb15  return *(mods.dp.d(sx.q(*(eax_3 + 0x278) + arg2), data_13337b0) * 0xec + data_13337b8)",
		),
	),
)

EXPECTED_QAGAME_BOTLIB_RUNTIME_HLIL_BLOCKS = (
	(
		"QL_G_trap_BotLibSetup",
		"004e16e0    int32_t j_sub_4dd6a0()",
		"004e16f0    int32_t j_sub_4dd6d0()",
		("004e16e0  return sub_4dd6a0() __tailcall",),
	),
	(
		"QL_G_trap_BotLibShutdown",
		"004e16f0    int32_t j_sub_4dd6d0()",
		"004e1700    int32_t sub_4e1700()",
		("004e16f0  return sub_4dd6d0() __tailcall",),
	),
	(
		"QL_G_trap_BotLibVarSet",
		"004e1700    int32_t sub_4e1700()",
		"004e1720    int32_t sub_4e1720()",
		("004e1710  jump(*(data_13e1844 + 0x1f8))",),
	),
	(
		"QL_G_trap_BotLibVarGet",
		"004e1720    int32_t sub_4e1720()",
		"004e1740    int32_t sub_4e1740()",
		("004e172f  jump(*(data_13e1844 + 0x1fc))",),
	),
	(
		"QL_G_trap_BotLibDefine",
		"004e1740    int32_t sub_4e1740()",
		"004e1760    int32_t sub_4e1760",
		("004e1750  jump(*(data_13e1844 + 0x200))",),
	),
	(
		"QL_G_trap_BotLibStartFrame",
		"004e1760    int32_t sub_4e1760(float arg1)",
		"004e1780    int32_t sub_4e1780()",
		(
			"004e176b  int32_t ecx",
			"004e176b  int32_t var_8 = ecx",
			"004e177b  return (*(data_13e1844 + 0x214))(fconvert.s(fconvert.t(arg1)))",
		),
	),
	(
		"QL_G_trap_BotLibLoadMap",
		"004e1780    int32_t sub_4e1780()",
		"004e17a0    int32_t sub_4e17a0()",
		("004e1790  jump(*(data_13e1844 + 0x218))",),
	),
	(
		"QL_G_trap_BotLibUpdateEntity",
		"004e17a0    int32_t sub_4e17a0()",
		"004e17c0    int32_t sub_4e17c0()",
		("004e17b0  jump(*(data_13e1844 + 0x21c))",),
	),
	(
		"QL_G_trap_BotLibTest",
		"004e17c0    int32_t sub_4e17c0()",
		"004e17e0    int32_t sub_4e17e0()",
		("004e17d0  jump(*(data_13e1844 + 0x220))",),
	),
	(
		"QL_G_trap_BotGetSnapshotEntity",
		"004e17e0    int32_t sub_4e17e0()",
		"004e17f0    int32_t sub_4e17f0()",
		("004e17e4  return sub_4ddac0() __tailcall",),
	),
	(
		"QL_G_trap_BotGetServerCommand",
		"004e17f0    int32_t sub_4e17f0()",
		"004e1800    int32_t sub_4e1800",
		("004e17f4  return sub_4dda50() __tailcall",),
	),
	(
		"QL_G_trap_BotUserCommand",
		"004e1800    int32_t sub_4e1800(int32_t arg1, int32_t arg2)",
		"004e1830    int32_t sub_4e1830()",
		("004e1820  return sub_4e02d0(arg1 * 0x25b68 + data_13337ac, arg2)",),
	),
)


NATIVE_BOTLIB_BRIDGE_SLOT_PATTERN = re.compile(
	r"\b("
	r"G_QL_IMPORT_(?:"
	r"BOT_ALLOCATE_CLIENT|BOT_FREE_CLIENT|GET_USERCMD|GET_ENTITY_TOKEN|"
	r"DEBUG_POLYGON_CREATE|DEBUG_POLYGON_DELETE|BOTLIB_[A-Z0-9_]+"
	r")"
	r")\s*=\s*(\d+),"
)
NATIVE_BOTLIB_BRIDGE_TABLE_BASE = 0x56CF80
NATIVE_BOTLIB_BRIDGE_FIRST_SLOT = 43
NATIVE_BOTLIB_BRIDGE_LAST_SLOT = 184
NATIVE_BOTLIB_BRIDGE_EXPECTED_COUNT = (
	NATIVE_BOTLIB_BRIDGE_LAST_SLOT - NATIVE_BOTLIB_BRIDGE_FIRST_SLOT + 1
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


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


def _assert_anchors_in_order(source: str, anchors: tuple[str, ...]) -> None:
	last_offset = -1
	for anchor in anchors:
		offset = source.find(anchor)
		assert offset != -1, anchor
		assert offset > last_offset, anchor
		last_offset = offset


def _extract_text_window(source: str, start_anchor: str, end_anchor: str) -> str:
	start = source.index(start_anchor)
	end = source.index(end_anchor, start + len(start_anchor))
	return source[start:end]


def _native_botlib_bridge_slots(g_public: str) -> list[tuple[int, str]]:
	rows = [
		(int(slot), name)
		for name, slot in NATIVE_BOTLIB_BRIDGE_SLOT_PATTERN.findall(g_public)
		if NATIVE_BOTLIB_BRIDGE_FIRST_SLOT <= int(slot) <= NATIVE_BOTLIB_BRIDGE_LAST_SLOT
	]
	rows.sort()
	return rows


def test_server_game_botlib_bridge_aliases_and_rows_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()

	for address, (name, size) in EXPECTED_SERVER_GAME_BRIDGE_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		if size is not None:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	for alias_without_row in (
		"4DCD30",
		"4DD240",
		"4DD6A0",
		"4DD6D0",
		"4E1610",
		"4E16E0",
		"4E16F0",
	):
		assert alias_without_row not in rows


def test_server_bot_source_matches_retail_bridge_lifecycle_shape() -> None:
	sv_bot = _read(SERVER_SV_BOT)
	allocate = _extract_function_block(sv_bot, "int SV_BotAllocateClient")
	free = _extract_function_block(sv_bot, "void SV_BotFreeClient")
	debug_draw = _extract_function_block(sv_bot, "void BotDrawDebugPolygons")
	frame = _extract_function_block(sv_bot, "void SV_BotFrame")
	setup = _extract_function_block(sv_bot, "int SV_BotLibSetup")
	shutdown = _extract_function_block(sv_bot, "int SV_BotLibShutdown")
	cvars = _extract_function_block(sv_bot, "void SV_BotInitCvars")
	init = _extract_function_block(sv_bot, "void SV_BotInitBotLib")
	console = _extract_function_block(sv_bot, "int SV_BotGetConsoleMessage")
	snapshot = _extract_function_block(sv_bot, "int SV_BotGetSnapshotEntity")

	assert '#include "../../common/platform/platform_steamworks.h"' in sv_bot
	assert "static void SV_BotAssignSteamIdentity( client_t *cl )" in sv_bot
	assert "QL_Steamworks_ServerCreateUnauthenticatedUserConnection( &steamIdLow, &steamIdHigh )" in sv_bot
	assert 'Com_sprintf( cl->platformSteamId, sizeof( cl->platformSteamId ), "%llu", steamId );' in sv_bot

	for anchor in (
		"for ( i = 0, cl = svs.clients; i < sv_maxclients->integer; i++, cl++ )",
		"if ( i == sv_maxclients->integer )",
		"return -1;",
		"cl->gentity = SV_GentityNum( i );",
		"cl->gentity->s.number = i;",
		"cl->isBot = qtrue;",
		"cl->state = CS_ACTIVE;",
		"cl->lastPacketTime = svs.time;",
		"cl->lastConnectTime = svs.time;",
		"cl->netchan.remoteAddress.type = NA_BOT;",
		"cl->rate = 16384;",
		"SV_BotAssignSteamIdentity( cl );",
		"SV_BotRefreshEntityBotFlag( cl );",
		"return i;",
	):
		assert anchor in allocate

	for anchor in (
		"Com_Error( ERR_DROP, \"SV_BotFreeClient: bad clientNum: %i\", clientNum );",
		"cl->state = CS_FREE;",
		"cl->name[0] = 0;",
		"cl->isBot = qfalse;",
		"cl->netchan.remoteAddress.type = NA_BAD;",
		"SV_BotRefreshEntityBotFlag( cl );",
	):
		assert anchor in free

	for anchor in (
		"if (!debugpolygons)",
		'if (!bot_debug) bot_debug = Cvar_Get("bot_debug", "0", 0);',
		"if (bot_enable && bot_debug->integer) {",
		'if (!bot_reachability) bot_reachability = Cvar_Get("bot_reachability", "0", 0);',
		'if (!bot_groundonly) bot_groundonly = Cvar_Get("bot_groundonly", "1", 0);',
		'if (!bot_highlightarea) bot_highlightarea = Cvar_Get("bot_highlightarea", "0", 0);',
		"parm0 = 0;",
		"if (svs.clients[0].lastUsercmd.buttons & BUTTON_ATTACK) parm0 |= 1;",
		"if (bot_reachability->integer) parm0 |= 2;",
		"if (bot_groundonly->integer) parm0 |= 4;",
		'botlib_export->BotLibVarSet("bot_highlightarea", bot_highlightarea->string);',
		"botlib_export->Test(parm0, NULL, svs.clients[0].gentity->r.currentOrigin,",
		"for (i = 0; i < bot_maxdebugpolys; i++)",
		"if (!poly->inuse) continue;",
		"drawPoly(poly->color, poly->numPoints, (float *) poly->points);",
	):
		assert anchor in debug_draw

	for anchor in (
		"if (!bot_enable) return;",
		"if (!gvm) return;",
		"VM_Call( gvm, BOTAI_START_FRAME, time );",
	):
		assert anchor in frame

	for anchor in (
		"if (!bot_enable) {",
		"if ( !botlib_export ) {",
		"Com_Printf( S_COLOR_RED \"Error: SV_BotLibSetup without SV_BotInitBotLib\\n\" );",
		"return -1;",
		"return botlib_export->BotLibSetup();",
	):
		assert anchor in setup

	for anchor in (
		"if ( !botlib_export ) {",
		"return -1;",
		"return botlib_export->BotLibShutdown();",
	):
		assert anchor in shutdown

	retail_cvar_sequence = (
		'Cvar_Get("bot_enable", "1", CVAR_ROM);',
		'Cvar_Get("bot_developer", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_debug", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_maxdebugpolys", "2", 0);',
		'Cvar_Get("bot_groundonly", "1", 0);',
		'Cvar_Get("bot_reachability", "0", 0);',
		'Cvar_Get("bot_visualizejumppads", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_forceclustering", "0", 0);',
		'Cvar_Get("bot_forcereachability", "0", 0);',
		'Cvar_Get("bot_forcewrite", "0", 0);',
		'Cvar_Get("bot_aasoptimize", "0", 0);',
		'Cvar_Get("bot_saveroutingcache", "0", 0);',
		'Cvar_Get("bot_thinktime", "100", 0);',
		'Cvar_Get("bot_reloadcharacters", "0", 0);',
		'Cvar_Get("bot_testichat", "0", 0);',
		'Cvar_Get("bot_testrchat", "0", 0);',
		'Cvar_Get("bot_testsolid", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_testclusters", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_fastchat", "0", 0);',
		'Cvar_Get("bot_nochat", "0", 0);',
		'Cvar_Get("bot_pause", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_report", "0", CVAR_CHEAT);',
		'Cvar_Get("bot_grapple", "1", 0);',
		'Cvar_Get("bot_rocketjump", "1", 0);',
		'Cvar_Get("bot_challenge", "0", 0);',
		'Cvar_Get("bot_minplayers", "0", 0);',
		'Cvar_Get("bot_interbreedchar", "", CVAR_CHEAT);',
		'Cvar_Get("bot_interbreedbots", "10", CVAR_CHEAT);',
		'Cvar_Get("bot_interbreedcycle", "20", CVAR_CHEAT);',
		'Cvar_Get("bot_interbreedwrite", "", CVAR_CHEAT);',
		'Cvar_Get("bot_teamkill", "0", 0);',
	)
	last_offset = -1
	for anchor in retail_cvar_sequence:
		offset = cvars.find(anchor)
		assert offset != -1, anchor
		assert offset > last_offset, anchor
		last_offset = offset

	for anchor in (
		"botlib_import.Print = BotImport_Print;",
		"botlib_import.Trace = BotImport_Trace;",
		"botlib_import.EntityTrace = BotImport_EntityTrace;",
		"botlib_import.PointContents = BotImport_PointContents;",
		"botlib_import.inPVS = BotImport_inPVS;",
		"botlib_import.BSPEntityData = BotImport_BSPEntityData;",
		"botlib_import.BSPModelMinsMaxsOrigin = BotImport_BSPModelMinsMaxsOrigin;",
		"botlib_import.GetMemory = BotImport_GetMemory;",
		"botlib_import.FreeMemory = BotImport_FreeMemory;",
		"botlib_import.HunkAlloc = BotImport_HunkAlloc;",
		"botlib_import.DebugLineCreate = BotImport_DebugLineCreate;",
		"botlib_import.DebugLineDelete = BotImport_DebugPolygonDelete;",
		"botlib_import.DebugLineShow = BotImport_DebugLineShow;",
		"botlib_import.DebugPolygonCreate = BotImport_DebugPolygonCreate;",
		"botlib_import.DebugPolygonDelete = BotImport_DebugPolygonDelete;",
		"botlib_export = (botlib_export_t *)GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );",
		"assert(botlib_export);",
	):
		assert anchor in init

	for anchor in (
		"cl = &svs.clients[client];",
		"cl->lastPacketTime = svs.time;",
		"if ( cl->reliableAcknowledge == cl->reliableSequence )",
		"cl->reliableAcknowledge++;",
		"index = cl->reliableAcknowledge & ( MAX_RELIABLE_COMMANDS - 1 );",
		"if ( !cl->reliableCommands[index][0] )",
		"Q_strncpyz( buf, cl->reliableCommands[index], size );",
		"return qtrue;",
	):
		assert anchor in console

	for anchor in (
		"frame = &cl->frames[cl->netchan.outgoingSequence & PACKET_MASK];",
		"if (sequence < 0 || sequence >= frame->num_entities)",
		"return -1;",
		"return svs.snapshotEntities[(frame->first_entity + sequence) % svs.numSnapshotEntities].number;",
	):
		assert anchor in snapshot


def test_server_bot_frame_callsite_wiring_matches_retail_binary_ninja_refs() -> None:
	aliases = _aliases()
	rows = _function_rows()
	server_hlil = _read(QL_STEAM_HLIL_PART04)
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	sv_init = _read(SERVER_SV_INIT)
	sv_main = _read(SERVER_SV_MAIN)

	spawn_server = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
	server_init = _extract_function_block(sv_init, "void SV_Init (void)")
	server_frame = _extract_function_block(sv_main, "void SV_Frame( int msec )")

	for address, name, size in EXPECTED_BOT_FRAME_CALLSITE_OWNERS:
		assert aliases[f"sub_{address}"] == name
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	assert spawn_server.count("VM_Call( gvm, GAME_RUN_FRAME, svs.time );") == 2
	assert spawn_server.count("SV_BotFrame( svs.time );") == 2

	first_game_frame = spawn_server.index("VM_Call( gvm, GAME_RUN_FRAME, svs.time );")
	first_bot_frame = spawn_server.index("SV_BotFrame( svs.time );")
	first_time_advance = spawn_server.index("svs.time += 100;")
	baseline = spawn_server.index("SV_CreateBaseline ();")
	second_game_frame = spawn_server.rindex("VM_Call( gvm, GAME_RUN_FRAME, svs.time );")
	second_bot_frame = spawn_server.rindex("SV_BotFrame( svs.time );")
	second_time_advance = spawn_server.rindex("svs.time += 100;")

	assert spawn_server.index("SV_InitGameProgs();") < first_game_frame
	assert first_game_frame < first_bot_frame < first_time_advance < baseline
	assert baseline < second_game_frame < second_bot_frame < second_time_advance

	_assert_anchors_in_order(
		spawn_server,
		(
			"SV_InitGameProgs();",
			"for ( i = 0 ;i < 3 ; i++ ) {",
			"VM_Call( gvm, GAME_RUN_FRAME, svs.time );",
			"SV_BotFrame( svs.time );",
			"SV_CreateBaseline ();",
			"SV_GameClientConnect( i, qfalse, isBot );",
		),
	)

	assert server_frame.count("SV_BotFrame(") == 2
	_assert_anchors_in_order(
		server_frame,
		(
			"sv.timeResidual += msec;",
			"if (!com_dedicated->integer) SV_BotFrame( svs.time + sv.timeResidual );",
			"if ( com_dedicated->integer && sv.timeResidual < frameMsec )",
			"SV_CalcPings();",
			"if (com_dedicated->integer) SV_BotFrame( svs.time );",
			"while ( sv.timeResidual >= frameMsec )",
			"VM_Call( gvm, GAME_RUN_FRAME, svs.time );",
		),
	)

	_assert_anchors_in_order(
		server_init,
		(
			"SV_SteamServerInitCallbacks();",
			"Zmq_RegisterCvarsAndInitRcon();",
			"SV_BotInitCvars();",
			"SV_BotInitBotLib();",
		),
	)

	_assert_anchors_in_order(
		game_hlil,
		(
			"004e3510  int32_t __saved_ebp_2",
			"004e3746  eax_21, ecx_4, edx_2 = sub_4e2c10(ecx_3)",
			"004e377f      (*(data_13e180c + 4))(data_1333780)",
			"004e3787      sub_4dd670(data_1333780)",
			"004e3791      data_1333780 += 0x64",
			"004e37a3  sub_4e31b0()",
			"004e3897  int32_t eax_31 = *(data_13e180c + 4)",
			"004e38a4  sub_4dd670()",
			"004e38ae  data_1333780 += 0x64",
		),
	)

	_assert_anchors_in_order(
		game_hlil,
		(
			"004e49d0    int32_t* sub_4e49d0",
			"004e4a50          data_12e035c = eax_4",
			"004e4a59          if (*(ecx_3 + 0x30) == 0)",
			"004e4a64              sub_4dd670(data_1333780 + eax_4)",
			"004e4c45                      sub_4e46b0()",
			"004e4c54                      if (*(data_1205e28 + 0x30) != 0)",
			"004e4c5d                          sub_4dd670(data_1333780)",
			"004e4c6b                      while (data_12e035c s>= i)",
			"004e4c91                          (*(data_13e180c + 4))(eax_13)",
		),
	)

	_assert_anchors_in_order(
		game_hlil,
		(
			"004e3ad0    int32_t sub_4e3ad0()",
			"004e3eb8  sub_465e30()",
			"004e3ebd  sub_4dd6f0()",
			"004e3ec2  return sub_4dd940() __tailcall",
		),
	)

	assert "004dd670    int32_t sub_4dd670()" in server_hlil
	assert "004dd683  if (data_13e1848 != 0 && data_12ce2b8 != 0)" in server_hlil
	assert "004dd68f      jump(*(data_13e180c + 0x2c))" in server_hlil


def test_native_qagame_import_slots_bind_full_botlib_bridge_surface() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	legacy_table = _extract_function_block(sv_game, "static const ql_import_f ql_game_compat_imports")
	legacy_syscalls = _extract_function_block(sv_game, "static int SV_GameSystemCallsImpl")
	get_usercmd = _extract_function_block(sv_game, "void SV_GetUsercmd")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot_anchor in (
		"G_QL_IMPORT_BOT_ALLOCATE_CLIENT = 43,",
		"G_QL_IMPORT_BOT_FREE_CLIENT = 44,",
		"G_QL_IMPORT_GET_USERCMD = 45,",
		"G_QL_IMPORT_GET_ENTITY_TOKEN = 46,",
		"G_QL_IMPORT_DEBUG_POLYGON_CREATE = 47,",
		"G_QL_IMPORT_DEBUG_POLYGON_DELETE = 48,",
		"G_QL_IMPORT_BOTLIB_SETUP = 49,",
	):
		assert slot_anchor in g_public

	for legacy_import, native_slot in (
		("G_BOT_ALLOCATE_CLIENT", "G_QL_IMPORT_BOT_ALLOCATE_CLIENT"),
		("G_BOT_FREE_CLIENT", "G_QL_IMPORT_BOT_FREE_CLIENT"),
		("G_GET_USERCMD", "G_QL_IMPORT_GET_USERCMD"),
		("G_GET_ENTITY_TOKEN", "G_QL_IMPORT_GET_ENTITY_TOKEN"),
		("G_DEBUG_POLYGON_CREATE", "G_QL_IMPORT_DEBUG_POLYGON_CREATE"),
		("G_DEBUG_POLYGON_DELETE", "G_QL_IMPORT_DEBUG_POLYGON_DELETE"),
	):
		assert f"case {legacy_import}: return {native_slot};" in g_syscalls

	for legacy_slot, trap_name in (
		("G_BOT_ALLOCATE_CLIENT", "QL_G_trap_BotAllocateClient"),
		("G_BOT_FREE_CLIENT", "QL_G_trap_BotFreeClient"),
		("G_GET_USERCMD", "QL_G_trap_GetUsercmd"),
		("G_GET_ENTITY_TOKEN", "QL_G_trap_GetEntityToken"),
		("G_DEBUG_POLYGON_CREATE", "QL_G_trap_DebugPolygonCreate"),
		("G_DEBUG_POLYGON_DELETE", "QL_G_trap_DebugPolygonDelete"),
	):
		assert f"[{legacy_slot}] = (ql_import_f){trap_name}," in legacy_table

	for slot_name, trap_name in EXPECTED_NATIVE_GAME_IMPORT_ASSIGNMENTS:
		assert f"{slot_name}" in g_public
		assert f"ql_game_imports[{slot_name}] = (ql_import_f){trap_name};" in init_imports

	for wrapper_anchor in (
		"static int QDECL QL_G_trap_BotAllocateClient( void )",
		"return G_Import_Syscall( G_BOT_ALLOCATE_CLIENT );",
		"static void QDECL QL_G_trap_BotFreeClient( int clientNum )",
		"G_Import_Syscall( G_BOT_FREE_CLIENT, clientNum );",
		"static void QDECL QL_G_trap_GetUsercmd( int clientNum, usercmd_t *cmd )",
		"G_Import_Syscall( G_GET_USERCMD, clientNum, cmd );",
		"static qboolean QDECL QL_G_trap_GetEntityToken( char *buffer, int bufferSize )",
		"return G_Import_Syscall( G_GET_ENTITY_TOKEN, buffer, bufferSize );",
		"static int QDECL QL_G_trap_DebugPolygonCreate( int color, int numPoints, vec3_t *points )",
		"return G_Import_Syscall( G_DEBUG_POLYGON_CREATE, color, numPoints, points );",
		"static void QDECL QL_G_trap_DebugPolygonDelete( int id )",
		"G_Import_Syscall( G_DEBUG_POLYGON_DELETE, id );",
		"static int QDECL QL_G_trap_BotLibSetup( void )",
		"return G_Import_Syscall( BOTLIB_SETUP );",
		"static int QDECL QL_G_trap_BotLibShutdown( void )",
		"return G_Import_Syscall( BOTLIB_SHUTDOWN );",
		"static int QDECL QL_G_trap_BotLibVarSet( char *var_name, char *value )",
		"return G_Import_Syscall( BOTLIB_LIBVAR_SET, var_name, value );",
		"static int QDECL QL_G_trap_BotLibVarGet( char *var_name, char *value, int size )",
		"return G_Import_Syscall( BOTLIB_LIBVAR_GET, var_name, value, size );",
		"static int QDECL QL_G_trap_BotLibDefine( char *string )",
		"return G_Import_Syscall( BOTLIB_PC_ADD_GLOBAL_DEFINE, string );",
		"static int QDECL QL_G_trap_BotLibStartFrame( float time )",
		"return G_Import_Syscall( BOTLIB_START_FRAME, QL_G_PASSFLOAT( time ) );",
		"static int QDECL QL_G_trap_BotLibLoadMap( const char *mapname )",
		"return G_Import_Syscall( BOTLIB_LOAD_MAP, mapname );",
		"static int QDECL QL_G_trap_BotLibUpdateEntity( int ent, void /* struct bot_updateentity_s */ *bue )",
		"return G_Import_Syscall( BOTLIB_UPDATENTITY, ent, bue );",
		"static int QDECL QL_G_trap_BotLibTest( int parm0, char *parm1, vec3_t parm2, vec3_t parm3 )",
		"return G_Import_Syscall( BOTLIB_TEST, parm0, parm1, parm2, parm3 );",
		"static int QDECL QL_G_trap_BotGetSnapshotEntity( int clientNum, int sequence )",
		"return G_Import_Syscall( BOTLIB_GET_SNAPSHOT_ENTITY, clientNum, sequence );",
		"static int QDECL QL_G_trap_BotGetServerCommand( int clientNum, char *message, int size )",
		"return G_Import_Syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"static void QDECL QL_G_trap_BotUserCommand( int clientNum, usercmd_t *ucmd )",
		"G_Import_Syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
	):
		assert wrapper_anchor in ql_imports

	for anchor in (
		"if ( clientNum < 0 || clientNum >= sv_maxclients->integer )",
		'Com_Error( ERR_DROP, "SV_GetUsercmd: bad clientNum:%i", clientNum );',
		"*cmd = svs.clients[clientNum].lastUsercmd;",
	):
		assert anchor in get_usercmd

	for qagame_syscall_anchor in (
		"int trap_BotLibSetup( void )",
		"return syscall( BOTLIB_SETUP );",
		"int trap_BotLibShutdown( void )",
		"return syscall( BOTLIB_SHUTDOWN );",
		"int trap_BotLibStartFrame(float time)",
		"return syscall( BOTLIB_START_FRAME, PASSFLOAT( time ) );",
		"int trap_BotLibLoadMap(const char *mapname)",
		"return syscall( BOTLIB_LOAD_MAP, mapname );",
		"int trap_BotLibUpdateEntity(int ent, void /* struct bot_updateentity_s */ *bue)",
		"return syscall( BOTLIB_UPDATENTITY, ent, bue );",
		"int trap_BotLibTest(int parm0, char *parm1, vec3_t parm2, vec3_t parm3)",
		"return syscall( BOTLIB_TEST, parm0, parm1, parm2, parm3 );",
		"int trap_BotGetSnapshotEntity( int clientNum, int sequence )",
		"return syscall( BOTLIB_GET_SNAPSHOT_ENTITY, clientNum, sequence );",
		"int trap_BotGetServerCommand(int clientNum, char *message, int size)",
		"return syscall( BOTLIB_GET_CONSOLE_MESSAGE, clientNum, message, size );",
		"void trap_BotUserCommand(int clientNum, usercmd_t *ucmd)",
		"syscall( BOTLIB_USER_COMMAND, clientNum, ucmd );",
	):
		assert qagame_syscall_anchor in g_syscalls

	_assert_anchors_in_order(
		legacy_syscalls,
		(
			"case G_BOT_ALLOCATE_CLIENT:",
			"return SV_BotAllocateClient();",
			"case G_BOT_FREE_CLIENT:",
			"SV_BotFreeClient( args[1] );",
			"case G_GET_USERCMD:",
			"SV_GetUsercmd( args[1], VMA(2) );",
			"case G_GET_ENTITY_TOKEN:",
			"s = COM_Parse( &sv.entityParsePoint );",
			"Q_strncpyz( VMA(1), s, args[2] );",
			"return qfalse;",
			"return qtrue;",
			"case G_DEBUG_POLYGON_CREATE:",
			"return BotImport_DebugPolygonCreate( args[1], args[2], VMA(3) );",
			"case G_DEBUG_POLYGON_DELETE:",
			"BotImport_DebugPolygonDelete( args[1] );",
		),
	)

	_assert_anchors_in_order(
		legacy_syscalls,
		(
			"case BOTLIB_SETUP:",
			"return SV_BotLibSetup();",
			"case BOTLIB_SHUTDOWN:",
			"return SV_BotLibShutdown();",
			"case BOTLIB_LIBVAR_SET:",
			"return botlib_export->BotLibVarSet( VMA(1), VMA(2) );",
			"case BOTLIB_START_FRAME:",
			"return botlib_export->BotLibStartFrame( VMF(1) );",
			"case BOTLIB_LOAD_MAP:",
			"return botlib_export->BotLibLoadMap( VMA(1) );",
			"case BOTLIB_UPDATENTITY:",
			"return botlib_export->BotLibUpdateEntity( args[1], VMA(2) );",
			"case BOTLIB_TEST:",
			"return botlib_export->Test( args[1], VMA(2), VMA(3), VMA(4) );",
			"case BOTLIB_GET_SNAPSHOT_ENTITY:",
			"return SV_BotGetSnapshotEntity( args[1], args[2] );",
			"case BOTLIB_GET_CONSOLE_MESSAGE:",
			"return SV_BotGetConsoleMessage( args[1], VMA(2), args[3] );",
			"case BOTLIB_USER_COMMAND:",
			"SV_ClientThink( &svs.clients[args[1]], VMA(2) );",
		),
	)


def test_server_and_native_qagame_bot_client_wrapper_hlil_bodies_match_retail_refs() -> None:
	server_hlil = _read(QL_STEAM_HLIL_PART04)
	game_hlil = _read(QL_STEAM_HLIL_PART05)

	for name, start_anchor, end_anchor, anchors in EXPECTED_SERVER_BOT_CLIENT_HLIL_BLOCKS:
		block = _extract_text_window(server_hlil, start_anchor, end_anchor)
		for anchor in anchors:
			assert anchor in block, f"{name}: {anchor}"

	for name, start_anchor, end_anchor, anchors in EXPECTED_QAGAME_BOT_CLIENT_HLIL_BLOCKS:
		block = _extract_text_window(game_hlil, start_anchor, end_anchor)
		for anchor in anchors:
			assert anchor in block, f"{name}: {anchor}"

	_assert_anchors_in_order(
		server_hlil,
		(
			"004dcd30    int32_t sub_4dcd30()",
			"004dcd61  int32_t* eax_2 = sub_4e10b0(result)",
			"004dcd6e  *esi = 4",
			"004dcd8d  esi[0x56b5] = 0x4000",
			"004dcd97  eax_3, edx = sub_465df0()",
			"004dcdb0    void* sub_4dcdb0(int32_t arg1)",
			"004dcde1          *esi_2 = 0",
			"004dcdf8              *(esi_3 + 0x1e0) &= 0xfffffff7",
			"004dce10    void sub_4dce10(int32_t arg1)",
			"004dcf0d          (*(data_13e1844 + 0x1f8))(\"bot_highlightarea\", eax_3[1])",
			"004dcf37          (*(data_13e1844 + 0x220))(esi_1, 0, eax_5 + 0x220, eax_5 + 0x22c)",
			"004dcf68                  arg1(*(esi_2 + ecx + 4), *(esi_2 + ecx + 8), esi_2 + ecx + 0xc)",
		),
	)

	_assert_anchors_in_order(
		game_hlil,
		(
			"004e1610    int32_t j_sub_4dcd30()",
			"004e1620    int32_t sub_4e1620()",
			"004e1630    void* sub_4e1630(int32_t arg1, int32_t arg2)",
			"004e1680    int32_t sub_4e1680(int32_t arg1, int32_t arg2)",
			"004e16c0    int32_t sub_4e16c0()",
			"004e16d0    int32_t sub_4e16d0()",
		),
	)


def test_server_and_native_qagame_botlib_runtime_wrapper_hlil_bodies_match_retail_refs() -> None:
	server_hlil = _read(QL_STEAM_HLIL_PART04)
	game_hlil = _read(QL_STEAM_HLIL_PART05)

	for name, start_anchor, end_anchor, anchors in EXPECTED_SERVER_BOTLIB_RUNTIME_HLIL_BLOCKS:
		block = _extract_text_window(server_hlil, start_anchor, end_anchor)
		for anchor in anchors:
			assert anchor in block, f"{name}: {anchor}"

	for name, start_anchor, end_anchor, anchors in EXPECTED_QAGAME_BOTLIB_RUNTIME_HLIL_BLOCKS:
		block = _extract_text_window(game_hlil, start_anchor, end_anchor)
		for anchor in anchors:
			assert anchor in block, f"{name}: {anchor}"

	_assert_anchors_in_order(
		server_hlil,
		(
			"004dda50    int32_t sub_4dda50(int32_t arg1, int32_t arg2, int32_t arg3)",
			"004dda68  *(eax_2 + 0x109bc) = data_13337a4",
			"004dda81      *(eax_2 + 0x10408) = ecx_1 + 1",
			"004ddaa7          sub_4d8f40(arg2, ecx_4 + eax_2 + 0x404, arg3)",
			"004ddac0    int32_t sub_4ddac0(int32_t arg1, int32_t arg2)",
			"004ddae1  void* eax_3 = (*(eax_2 + 0x15b08) & 0x1f) * 0x288 + eax_2 + 0x109d0",
			"004ddb15  return *(mods.dp.d(sx.q(*(eax_3 + 0x278) + arg2), data_13337b0) * 0xec + data_13337b8)",
		),
	)

	_assert_anchors_in_order(
		game_hlil,
		(
			"004e16e0    int32_t j_sub_4dd6a0()",
			"004e16f0    int32_t j_sub_4dd6d0()",
			"004e1700    int32_t sub_4e1700()",
			"004e1760    int32_t sub_4e1760(float arg1)",
			"004e1780    int32_t sub_4e1780()",
			"004e17a0    int32_t sub_4e17a0()",
			"004e17c0    int32_t sub_4e17c0()",
			"004e17e0    int32_t sub_4e17e0()",
			"004e17f0    int32_t sub_4e17f0()",
			"004e1800    int32_t sub_4e1800(int32_t arg1, int32_t arg2)",
		),
	)


def test_native_qagame_botlib_import_table_is_complete_and_contiguous() -> None:
	g_public = _read(GAME_PUBLIC)
	sv_game = _read(SERVER_SV_GAME)
	table_hlil = _read(QL_STEAM_HLIL_PART07)
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")
	rows = _native_botlib_bridge_slots(g_public)

	assert len(rows) == NATIVE_BOTLIB_BRIDGE_EXPECTED_COUNT
	assert [slot for slot, _ in rows] == list(
		range(NATIVE_BOTLIB_BRIDGE_FIRST_SLOT, NATIVE_BOTLIB_BRIDGE_LAST_SLOT + 1)
	)

	for slot, name in rows:
		table_address = NATIVE_BOTLIB_BRIDGE_TABLE_BASE + slot * 4
		table_anchor = f"{table_address:08x}  void* data_{table_address:x} = "
		assert table_anchor in table_hlil, name
		assert f"ql_game_imports[{name}] = (ql_import_f)" in init_imports, name

	for slot, name, target in (
		(43, "G_QL_IMPORT_BOT_ALLOCATE_CLIENT", "j_sub_4dcd30"),
		(49, "G_QL_IMPORT_BOTLIB_SETUP", "j_sub_4dd6a0"),
		(56, "G_QL_IMPORT_BOTLIB_UPDATE_ENTITY", "sub_4e17a0"),
		(61, "G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS", "sub_4e18a0"),
		(83, "G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS", "sub_4e2680"),
		(85, "G_QL_IMPORT_BOTLIB_EA_SAY", "sub_4e19d0"),
		(110, "G_QL_IMPORT_BOTLIB_AI_LOAD_CHARACTER", "sub_4e1c80"),
		(137, "G_QL_IMPORT_BOTLIB_AI_RESET_GOAL_STATE", "sub_4e1ff0"),
		(166, "G_QL_IMPORT_BOTLIB_AI_RESET_MOVE_STATE", "sub_4e23b0"),
		(178, "G_QL_IMPORT_BOTLIB_AI_CHOOSE_BEST_FIGHT_WEAPON", "sub_4e2550"),
		(184, "G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION", "sub_4e2600"),
	):
		table_address = NATIVE_BOTLIB_BRIDGE_TABLE_BASE + slot * 4
		assert (slot, name) in rows
		assert f"{table_address:08x}  void* data_{table_address:x} = {target}" in table_hlil

	previous_offset = -1
	for _, name in rows:
		offset = init_imports.index(f"ql_game_imports[{name}] = (ql_import_f)")
		assert offset > previous_offset, name
		previous_offset = offset

	assert "0056d264  void* data_56d264 = sub_4e2620" in table_hlil
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AI_GENETIC_PARENTS_AND_CHILD_SELECTION") < init_imports.index(
		"G_QL_IMPORT_SUBMIT_MATCH_REPORT"
	)


def test_server_game_botlib_bridge_hlil_shapes_are_pinned() -> None:
	server_hlil = _read(QL_STEAM_HLIL_PART04)
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for hlil_anchor in (
		"004dcd30    int32_t sub_4dcd30()",
		"004dcd5f      return 0xffffffff",
		"004dcd61  int32_t* eax_2 = sub_4e10b0(result)",
		"004dcd6e  *esi = 4",
		"004dcd8d  esi[0x56b5] = 0x4000",
		"004dcd97  eax_3, edx = sub_465df0()",
		"004dcd9c  esi[0x96d8] = eax_3",
		"004dcda5  esi[0x96d9] = edx",
		"004dcdb0    void* sub_4dcdb0(int32_t arg1)",
		"004dcde1          *esi_2 = 0",
		"004dcdf8              *(esi_3 + 0x1e0) &= 0xfffffff7",
		"004dd670    int32_t sub_4dd670()",
		"004dd683  if (data_13e1848 != 0 && data_12ce2b8 != 0)",
		"004dd68f      jump(*(data_13e180c + 0x2c))",
		"004dd6a0    int32_t sub_4dd6a0()",
		"004dd6ab      return 0",
		"004dd6cc      jump(*(eax_1 + 0x1f0))",
		"004dd6d0    int32_t sub_4dd6d0()",
		"004dd6e3      jump(*(eax_2 + 0x1f4))",
		"004dd6f0    void** sub_4dd6f0()",
		'004dd6fc  sub_4ce0d0(x87_r0, "bot_enable", U"1", 0x40)',
		'004dd916  sub_4ce0d0(x87_r2, "bot_interbreedwrite", &data_54f9da, 0x200)',
		'004dd932  return sub_4ce0d0(x87_r4, "bot_teamkill", U"0", 0)',
		"004dda50    int32_t sub_4dda50(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004dda62  void* eax_2 = arg1 * 0x25b68 + data_13337ac",
		"004ddaa7          sub_4d8f40(arg2, ecx_4 + eax_2 + 0x404, arg3)",
		"004ddab5          return 1",
		"004ddac0    int32_t sub_4ddac0(int32_t arg1, int32_t arg2)",
		"004ddb1a      return 0xffffffff",
	):
		assert hlil_anchor in server_hlil

	for hlil_anchor in (
		"004e1610    int32_t j_sub_4dcd30()",
		"004e1610  return sub_4dcd30() __tailcall",
		"004e1620    int32_t sub_4e1620()",
		"004e1624  return sub_4dcdb0() __tailcall",
		"004e1630    void* sub_4e1630(int32_t arg1, int32_t arg2)",
		"004e1671          __builtin_memcpy(dest: arg2, src: arg1 * 0x25b68 + data_13337ac + 0x1041c,",
		"004e1680    int32_t sub_4e1680(int32_t arg1, int32_t arg2)",
		"004e1699  sub_4d8f40(arg1, &data_124e6c0, arg2)",
		"004e16c4  return sub_4dd3b0() __tailcall",
		"004e16d4  return sub_4dd430() __tailcall",
		"004e16e0    int32_t j_sub_4dd6a0()",
		"004e16e0  return sub_4dd6a0() __tailcall",
		"004e16f0    int32_t j_sub_4dd6d0()",
		"004e16f0  return sub_4dd6d0() __tailcall",
		"004e1710  jump(*(data_13e1844 + 0x1f8))",
		"004e172f  jump(*(data_13e1844 + 0x1fc))",
		"004e1750  jump(*(data_13e1844 + 0x200))",
		"004e177b  return (*(data_13e1844 + 0x214))(fconvert.s(fconvert.t(arg1)))",
		"004e1790  jump(*(data_13e1844 + 0x218))",
		"004e17b0  jump(*(data_13e1844 + 0x21c))",
		"004e17d0  jump(*(data_13e1844 + 0x220))",
		"004e17e4  return sub_4ddac0() __tailcall",
		"004e17f4  return sub_4dda50() __tailcall",
		"004e1820  return sub_4e02d0(arg1 * 0x25b68 + data_13337ac, arg2)",
	):
		assert hlil_anchor in game_hlil

	for table_anchor in (
		"0056d02c  void* data_56d02c = j_sub_4dcd30",
		"0056d030  void* data_56d030 = sub_4e1620",
		"0056d034  void* data_56d034 = sub_4e1630",
		"0056d038  void* data_56d038 = sub_4e1680",
		"0056d03c  void* data_56d03c = sub_4e16c0",
		"0056d040  void* data_56d040 = sub_4e16d0",
		"0056d044  void* data_56d044 = j_sub_4dd6a0",
		"0056d048  void* data_56d048 = j_sub_4dd6d0",
		"0056d04c  void* data_56d04c = sub_4e1700",
		"0056d050  void* data_56d050 = sub_4e1720",
		"0056d054  void* data_56d054 = sub_4e1740",
		"0056d058  void* data_56d058 = sub_4e1760",
		"0056d05c  void* data_56d05c = sub_4e1780",
		"0056d060  void* data_56d060 = sub_4e17a0",
		"0056d064  void* data_56d064 = sub_4e17c0",
		"0056d068  void* data_56d068 = sub_4e17e0",
		"0056d06c  void* data_56d06c = sub_4e17f0",
		"0056d070  void* data_56d070 = sub_4e1800",
	):
		assert table_anchor in table_hlil


def test_server_game_botlib_bridge_alias_scan_has_direct_botlib_test_mentions() -> None:
	aliases = _aliases()
	botlib_test_text = "\n".join(
		path.read_text(encoding="utf-8")
		for path in sorted((REPO_ROOT / "tests").glob("test_botlib_*.py"))
	)
	missing: list[str] = []

	for key, name in aliases.items():
		if not key.startswith("sub_"):
			continue
		try:
			address = int(key[4:], 16)
		except ValueError:
			continue
		if not (
			SERVER_BOT_BRIDGE_START <= address <= SERVER_BOT_BRIDGE_END
			or GAME_BOT_IMPORT_START <= address <= GAME_BOT_IMPORT_END
		):
			continue
		if not BOT_BRIDGE_NAME_PATTERN.search(name):
			continue

		address_text = key[4:]
		if not any(
			form in botlib_test_text
			for form in (key, address_text, address_text.lower(), address_text.upper(), name)
		):
			missing.append(f"0x{address:08X} {key} {name}")

	assert missing == []
