from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
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
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
BOTLIB_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"

EXPECTED_AAS_NATIVE_SLOTS = (
	(61, "G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS", "BOTLIB_AAS_BBOX_AREAS", "QL_G_trap_AAS_BBoxAreas", "4E18A0", 15, "0056d074", "0x1c"),
	(62, "G_QL_IMPORT_BOTLIB_AAS_AREA_INFO", "BOTLIB_AAS_AREA_INFO", "QL_G_trap_AAS_AreaInfo", "4E18B0", 15, "0056d078", "0x20"),
	(63, "G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO", "BOTLIB_AAS_ENTITY_INFO", "QL_G_trap_AAS_EntityInfo", "4E1830", 14, "0056d07c", "0x00"),
	(64, "G_QL_IMPORT_BOTLIB_AAS_INITIALIZED", "BOTLIB_AAS_INITIALIZED", "QL_G_trap_AAS_Initialized", "4E1840", None, "0056d080", "0x04"),
	(65, "G_QL_IMPORT_BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX", "BOTLIB_AAS_PRESENCE_TYPE_BOUNDING_BOX", "QL_G_trap_AAS_PresenceTypeBoundingBox", "4E1850", 14, "0056d084", "0x08"),
	(66, "G_QL_IMPORT_BOTLIB_AAS_TIME", "BOTLIB_AAS_TIME", "QL_G_trap_AAS_Time", "4E1860", None, "0056d088", "0x0c"),
	(67, "G_QL_IMPORT_BOTLIB_AAS_POINT_AREA_NUM", "BOTLIB_AAS_POINT_AREA_NUM", "QL_G_trap_AAS_PointAreaNum", "4E1870", 15, "0056d08c", "0x10"),
	(68, "G_QL_IMPORT_BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX", "BOTLIB_AAS_POINT_REACHABILITY_AREA_INDEX", "QL_G_trap_AAS_PointReachabilityAreaIndex", "4E1880", 15, "0056d090", "0x14"),
	(69, "G_QL_IMPORT_BOTLIB_AAS_TRACE_AREAS", "BOTLIB_AAS_TRACE_AREAS", "QL_G_trap_AAS_TraceAreas", "4E1890", 15, "0056d094", "0x18"),
	(70, "G_QL_IMPORT_BOTLIB_AAS_POINT_CONTENTS", "BOTLIB_AAS_POINT_CONTENTS", "QL_G_trap_AAS_PointContents", "4E18C0", 15, "0056d098", "0x24"),
	(71, "G_QL_IMPORT_BOTLIB_AAS_NEXT_BSP_ENTITY", "BOTLIB_AAS_NEXT_BSP_ENTITY", "QL_G_trap_AAS_NextBSPEntity", "4E18D0", 15, "0056d09c", "0x28"),
	(72, "G_QL_IMPORT_BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY", "BOTLIB_AAS_VALUE_FOR_BSP_EPAIR_KEY", "QL_G_trap_AAS_ValueForBSPEpairKey", "4E18E0", 15, "0056d0a0", "0x2c"),
	(73, "G_QL_IMPORT_BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY", "BOTLIB_AAS_VECTOR_FOR_BSP_EPAIR_KEY", "QL_G_trap_AAS_VectorForBSPEpairKey", "4E18F0", 14, "0056d0a4", "0x30"),
	(74, "G_QL_IMPORT_BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY", "BOTLIB_AAS_FLOAT_FOR_BSP_EPAIR_KEY", "QL_G_trap_AAS_FloatForBSPEpairKey", "4E1900", 14, "0056d0a8", "0x34"),
	(75, "G_QL_IMPORT_BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY", "BOTLIB_AAS_INT_FOR_BSP_EPAIR_KEY", "QL_G_trap_AAS_IntForBSPEpairKey", "4E1910", 14, "0056d0ac", "0x38"),
	(76, "G_QL_IMPORT_BOTLIB_AAS_AREA_REACHABILITY", "BOTLIB_AAS_AREA_REACHABILITY", "QL_G_trap_AAS_AreaReachability", "4E1920", 15, "0056d0b0", "0x3c"),
	(77, "G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA", "BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA", "QL_G_trap_AAS_AreaTravelTimeToGoalArea", "4E1930", 15, "0056d0b4", "0x40"),
	(78, "G_QL_IMPORT_BOTLIB_AAS_ENABLE_ROUTING_AREA", "BOTLIB_AAS_ENABLE_ROUTING_AREA", "QL_G_trap_AAS_EnableRoutingArea", "4E1940", 15, "0056d0b8", "0x44"),
	(79, "G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE", "BOTLIB_AAS_PREDICT_ROUTE", "QL_G_trap_AAS_PredictRoute", "4E1950", 15, "0056d0bc", "0x48"),
	(80, "G_QL_IMPORT_BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL", "BOTLIB_AAS_ALTERNATIVE_ROUTE_GOAL", "QL_G_trap_AAS_AlternativeRouteGoals", "4E1960", 15, "0056d0c0", "0x4c"),
	(81, "G_QL_IMPORT_BOTLIB_AAS_SWIMMING", "BOTLIB_AAS_SWIMMING", "QL_G_trap_AAS_Swimming", "4E1970", 15, "0056d0c4", "0x50"),
	(82, "G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT", "BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT", "QL_G_trap_AAS_PredictClientMovement", "4E1980", 73, "0056d0c8", "0x54"),
)

EXPECTED_AAS_EXPORT_SLOTS = (
	("AAS_EntityInfo", "4851B0", "004a7fc0", "*arg1", 128),
	("AAS_Initialized", "486200", "004a7fc6", "arg1[1]", None),
	("AAS_PresenceTypeBoundingBox", "495270", "004a7fcd", "arg1[2]", 214),
	("AAS_Time", "486400", "004a7fd4", "arg1[3]", 7),
	("AAS_PointAreaNum", "4954B0", "004a7fdb", "arg1[4]", 136),
	("AAS_PointReachabilityAreaIndex", "495540", "004a7fe2", "arg1[5]", 296),
	("AAS_TraceAreas", "495F40", "004a7fe9", "arg1[6]", 940),
	("AAS_BBoxAreas", "4967E0", "004a7ff0", "arg1[7]", 72),
	("AAS_AreaInfo", "496830", "004a7ff7", "arg1[8]", 229),
	("AAS_PointContents", "4829F0", "004a7ffe", "arg1[9]", 10),
	("AAS_NextBSPEntity", "482AB0", "004a8005", "arg1[0xa]", 24),
	("AAS_ValueForBSPEpairKey", "482AD0", "004a800c", "arg1[0xb]", 159),
	("AAS_VectorForBSPEpairKey", "482B70", "004a8013", "arg1[0xc]", 188),
	("AAS_FloatForBSPEpairKey", "482C30", "004a801a", "arg1[0xd]", 112),
	("AAS_IntForBSPEpairKey", "482CA0", "004a8021", "arg1[0xe]", 114),
	("AAS_AreaReachability", "488B50", "004a8028", "arg1[0xf]", 57),
	("AAS_AreaTravelTimeToGoalArea", "494830", "004a802f", "arg1[0x10]", 49),
	("AAS_EnableRoutingArea", "492990", "004a8036", "arg1[0x11]", 133),
	("AAS_PredictRoute", "494870", "004a803d", "arg1[0x12]", 830),
	("AAS_AlternativeRouteGoals", "494DB0", "004a8044", "arg1[0x13]", 1036),
	("AAS_Swimming", "486CF0", "004a804b", "arg1[0x14]", 78),
	("AAS_PredictClientMovement", "488190", "004a8052", "arg1[0x15]", 81),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	aliases = json.loads(_read(SYMBOL_ALIASES))
	return aliases["quakelive_steam_srp"]


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


def test_aas_public_export_initializer_matches_retail_table_order() -> None:
	rows = _function_rows()
	aliases = _aliases()
	botlib_public = _read(BOTLIB_PUBLIC)
	interface_source = _read(BOTLIB_INTERFACE)
	hlil = _read(QL_STEAM_HLIL_PART03)

	aas_export = _extract_function_block(botlib_public, "typedef struct aas_export_s")
	init_aas = _extract_function_block(interface_source, "static void Init_AAS_Export( aas_export_t *aas )")
	init_hlil_start = hlil.index("004a7fc0    void __convention(\"regparm\") sub_4a7fc0")
	init_hlil_end = hlil.index("004a8060    void __convention(\"regparm\") sub_4a8060", init_hlil_start)
	init_hlil = hlil[init_hlil_start:init_hlil_end]

	assert aliases["sub_4A7FC0"] == "Init_AAS_Export"
	assert rows["4A7FC0"] == "FUN_004a7fc0,004a7fc0,154,0,unknown"
	assert len(EXPECTED_AAS_EXPORT_SLOTS) == 0x16
	assert "004a840e  sub_4a7fc0(&data_16dd860)" in hlil

	previous_field_pos = -1
	previous_source_pos = -1
	previous_hlil_pos = -1
	for field_name, address, hlil_address, hlil_slot, ghidra_size in EXPECTED_AAS_EXPORT_SLOTS:
		field_anchor = f"(*{field_name})"
		field_pos = aas_export.index(field_anchor)
		assert previous_field_pos < field_pos
		previous_field_pos = field_pos

		source_anchor = f"aas->{field_name} = {field_name};"
		source_pos = init_aas.index(source_anchor)
		assert previous_source_pos < source_pos
		previous_source_pos = source_pos

		hlil_anchor = f"{hlil_address}  {hlil_slot} = sub_{address.lower()}"
		hlil_pos = init_hlil.index(hlil_anchor)
		assert previous_hlil_pos < hlil_pos
		previous_hlil_pos = hlil_pos

		assert aliases[f"sub_{address}"] == field_name
		if ghidra_size is None:
			assert address not in rows
		else:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{ghidra_size},0,unknown"


def test_aas_native_wrapper_slab_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, _, address, size, table_address, export_offset in EXPECTED_AAS_NATIVE_SLOTS:
		table_target = f"sub_{address.lower()}" if size is not None else f"0x{address.lower()}"
		assert f"{table_address}  void* data_{table_address[2:]} = {table_target}" in table_hlil

		if size is None:
			offset_byte = export_offset[2:].rjust(2, "0")
			assert address not in rows
			assert f"00{address.lower()}  a1 44 18 3e 01 8b 48 {offset_byte}" in game_hlil
		else:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
			assert f"00{address.lower()}    int32_t sub_{address.lower()}" in game_hlil

		if size is None:
			continue
		if export_offset == "0x00":
			assert f"00{address.lower()[:-1]}c  jump(*data_13e1844)" in game_hlil
		else:
			display_offset = "8" if export_offset == "0x08" else export_offset
			assert f"*(data_13e1844 + {display_offset})" in game_hlil

	for table_anchor in (
		"0056d070  void* data_56d070 = sub_4e1800",
		"0056d074  void* data_56d074 = sub_4e18a0",
		"0056d078  void* data_56d078 = sub_4e18b0",
		"0056d07c  void* data_56d07c = sub_4e1830",
		"0056d080  void* data_56d080 = 0x4e1840",
		"0056d088  void* data_56d088 = 0x4e1860",
		"0056d0c8  void* data_56d0c8 = sub_4e1980",
		"0056d0cc  void* data_56d0cc = sub_4e2680",
	):
		assert table_anchor in table_hlil

	assert "004e1998  int32_t var_14 = arg12" in game_hlil
	assert "004e19c8      fconvert.s(fconvert.t(arg10)), arg11, arg12, arg13)" in game_hlil


def test_aas_native_wrapper_slab_source_wiring_matches_retail_order() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot, native_name, legacy_name, wrapper, _, _, _, _ in EXPECTED_AAS_NATIVE_SLOTS:
		assert f"{native_name} = {slot}," in g_public
		assert f"case {legacy_name}: return {native_name};" in syscall_map
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports
		assert f"[{legacy_name}] = (ql_import_f){wrapper}," in sv_game
		assert f"QDECL {wrapper}" in ql_imports

	assert init_imports.index("G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS") < init_imports.index("G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AAS_AREA_INFO") < init_imports.index("G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO")
	assert init_imports.index("G_QL_IMPORT_BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT") < init_imports.index("G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS")
	assert g_public.index("G_QL_IMPORT_BOTLIB_AAS_BBOX_AREAS = 61,") < g_public.index("G_QL_IMPORT_BOTLIB_AAS_ENTITY_INFO = 63,")

	for wrapper_anchor in (
		"static void QDECL QL_G_trap_AAS_EntityInfo( int entnum, void /* struct aas_entityinfo_s */ *info )",
		"G_Import_Syscall( BOTLIB_AAS_ENTITY_INFO, entnum, info );",
		"static float QDECL QL_G_trap_AAS_Time( void )",
		"temp = G_Import_Syscall( BOTLIB_AAS_TIME );",
		"return (*(float*)&temp);",
		"static int QDECL QL_G_trap_AAS_BBoxAreas( vec3_t absmins, vec3_t absmaxs, int *areas, int maxareas )",
		"return G_Import_Syscall( BOTLIB_AAS_BBOX_AREAS, absmins, absmaxs, areas, maxareas );",
		"static int QDECL QL_G_trap_AAS_PredictRoute( void /*struct aas_predictroute_s*/ *route, int areanum, vec3_t origin, int goalareanum, int travelflags, int maxareas, int maxtime, int stopevent, int stopcontents, int stoptfl, int stopareanum )",
		"return G_Import_Syscall( BOTLIB_AAS_PREDICT_ROUTE, route, areanum, origin, goalareanum, travelflags, maxareas, maxtime, stopevent, stopcontents, stoptfl, stopareanum );",
		"static int QDECL QL_G_trap_AAS_PredictClientMovement( void /* struct aas_clientmove_s */ *move, int entnum, vec3_t origin, int presencetype, int onground, vec3_t velocity, vec3_t cmdmove, int cmdframes, int maxframes, float frametime, int stopevent, int stopareanum, int visualize )",
		"return G_Import_Syscall( BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT, move, entnum, origin, presencetype, onground, velocity, cmdmove, cmdframes, maxframes, QL_G_PASSFLOAT(frametime), stopevent, stopareanum, visualize );",
	):
		assert wrapper_anchor in ql_imports
