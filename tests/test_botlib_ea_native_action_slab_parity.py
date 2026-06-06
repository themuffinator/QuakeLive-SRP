from __future__ import annotations

import csv
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
GAME_PUBLIC = REPO_ROOT / "src" / "code" / "game" / "g_public.h"
GAME_SYSCALLS = REPO_ROOT / "src" / "code" / "game" / "g_syscalls.c"
GAME_LOCAL = REPO_ROOT / "src" / "code" / "game" / "g_local.h"
BOTLIB_H = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
BOTLIB_EA = REPO_ROOT / "src" / "code" / "botlib" / "be_ea.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
SERVER_SV_GAME = REPO_ROOT / "src" / "code" / "server" / "sv_game.c"
SERVER_QL_GAME_IMPORTS = REPO_ROOT / "src" / "code" / "server" / "ql_game_imports.inc"

EXPECTED_EA_NATIVE_SLOTS = (
	(85, "G_QL_IMPORT_BOTLIB_EA_SAY", "BOTLIB_EA_SAY", "QL_G_trap_EA_Say", "4E19D0", 15, "0056d0d4", "0x5c"),
	(86, "G_QL_IMPORT_BOTLIB_EA_SAY_TEAM", "BOTLIB_EA_SAY_TEAM", "QL_G_trap_EA_SayTeam", "4E19E0", 15, "0056d0d8", "0x60"),
	(87, "G_QL_IMPORT_BOTLIB_EA_COMMAND", "BOTLIB_EA_COMMAND", "QL_G_trap_EA_Command", "4E19F0", 15, "0056d0dc", "0x58"),
	(88, "G_QL_IMPORT_BOTLIB_EA_ACTION", "BOTLIB_EA_ACTION", "QL_G_trap_EA_Action", "4E1A00", 15, "0056d0e0", "0x64"),
	(89, "G_QL_IMPORT_BOTLIB_EA_WALK", None, "QL_G_trap_EA_Walk", "4E1A10", 15, "0056d0e4", "0x68"),
	(90, "G_QL_IMPORT_BOTLIB_EA_GESTURE", "BOTLIB_EA_GESTURE", "QL_G_trap_EA_Gesture", "4E1A20", 15, "0056d0e8", "0x6c"),
	(91, "G_QL_IMPORT_BOTLIB_EA_TALK", "BOTLIB_EA_TALK", "QL_G_trap_EA_Talk", "4E1A30", 15, "0056d0ec", "0x70"),
	(92, "G_QL_IMPORT_BOTLIB_EA_ATTACK", "BOTLIB_EA_ATTACK", "QL_G_trap_EA_Attack", "4E1A40", 15, "0056d0f0", "0x74"),
	(93, "G_QL_IMPORT_BOTLIB_EA_USE", "BOTLIB_EA_USE", "QL_G_trap_EA_Use", "4E1A50", 15, "0056d0f4", "0x78"),
	(94, "G_QL_IMPORT_BOTLIB_EA_RESPAWN", "BOTLIB_EA_RESPAWN", "QL_G_trap_EA_Respawn", "4E1A60", 15, "0056d0f8", "0x7c"),
	(95, "G_QL_IMPORT_BOTLIB_EA_CROUCH", "BOTLIB_EA_CROUCH", "QL_G_trap_EA_Crouch", "4E1A70", 18, "0056d0fc", "0x98"),
	(96, "G_QL_IMPORT_BOTLIB_EA_MOVE_UP", "BOTLIB_EA_MOVE_UP", "QL_G_trap_EA_MoveUp", "4E1A90", 18, "0056d100", "0x80"),
	(97, "G_QL_IMPORT_BOTLIB_EA_MOVE_DOWN", "BOTLIB_EA_MOVE_DOWN", "QL_G_trap_EA_MoveDown", "4E1AB0", 18, "0056d104", "0x84"),
	(98, "G_QL_IMPORT_BOTLIB_EA_MOVE_FORWARD", "BOTLIB_EA_MOVE_FORWARD", "QL_G_trap_EA_MoveForward", "4E1AD0", 18, "0056d108", "0x88"),
	(99, "G_QL_IMPORT_BOTLIB_EA_MOVE_BACK", "BOTLIB_EA_MOVE_BACK", "QL_G_trap_EA_MoveBack", "4E1AF0", 18, "0056d10c", "0x8c"),
	(100, "G_QL_IMPORT_BOTLIB_EA_MOVE_LEFT", "BOTLIB_EA_MOVE_LEFT", "QL_G_trap_EA_MoveLeft", "4E1B10", 18, "0056d110", "0x90"),
	(101, "G_QL_IMPORT_BOTLIB_EA_MOVE_RIGHT", "BOTLIB_EA_MOVE_RIGHT", "QL_G_trap_EA_MoveRight", "4E1B30", 18, "0056d114", "0x94"),
	(102, "G_QL_IMPORT_BOTLIB_EA_SELECT_WEAPON", "BOTLIB_EA_SELECT_WEAPON", "QL_G_trap_EA_SelectWeapon", "4E1B50", 18, "0056d118", "0x9c"),
	(103, "G_QL_IMPORT_BOTLIB_EA_JUMP", "BOTLIB_EA_JUMP", "QL_G_trap_EA_Jump", "4E1B70", 18, "0056d11c", "0xa0"),
	(104, "G_QL_IMPORT_BOTLIB_EA_DELAYED_JUMP", "BOTLIB_EA_DELAYED_JUMP", "QL_G_trap_EA_DelayedJump", "4E1B90", 18, "0056d120", "0xa4"),
	(105, "G_QL_IMPORT_BOTLIB_EA_MOVE", "BOTLIB_EA_MOVE", "QL_G_trap_EA_Move", "4E1BB0", 37, "0056d124", "0xa8"),
	(106, "G_QL_IMPORT_BOTLIB_EA_VIEW", "BOTLIB_EA_VIEW", "QL_G_trap_EA_View", "4E1BE0", 18, "0056d128", "0xac"),
	(107, "G_QL_IMPORT_BOTLIB_EA_END_REGULAR", "BOTLIB_EA_END_REGULAR", "QL_G_trap_EA_EndRegular", "4E1C00", 33, "0056d12c", "0xb0"),
	(108, "G_QL_IMPORT_BOTLIB_EA_GET_INPUT", "BOTLIB_EA_GET_INPUT", "QL_G_trap_EA_GetInput", "4E1C30", 37, "0056d130", "0xb4"),
	(109, "G_QL_IMPORT_BOTLIB_EA_RESET_INPUT", "BOTLIB_EA_RESET_INPUT", "QL_G_trap_EA_ResetInput", "4E1C60", 18, "0056d134", "0xb8"),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


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


def test_ea_native_action_slab_rows_and_hlil_table_are_pinned() -> None:
	rows = _function_rows()
	game_hlil = _read(QL_STEAM_HLIL_PART05)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for _, _, _, _, address, size, table_address, export_offset in EXPECTED_EA_NATIVE_SLOTS:
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"
		assert f"{table_address}  void* data_{table_address[2:]} = " in table_hlil
		assert f"00{address.lower()}    int32_t sub_{address.lower()}" in game_hlil
		assert f"*(data_13e1844 + {export_offset})" in game_hlil

	for table_anchor in (
		"0056d0cc  void* data_56d0cc = sub_4e2680",
		"0056d0d0  void* data_56d0d0 = sub_4e26a0",
		"0056d0d4  void* data_56d0d4 = sub_4e19d0",
		"0056d0e4  void* data_56d0e4 = sub_4e1a10",
		"0056d134  void* data_56d134 = sub_4e1c60",
	):
		assert table_anchor in table_hlil


def test_ea_native_action_slab_source_wiring_preserves_direct_only_walk_slot() -> None:
	g_public = _read(GAME_PUBLIC)
	g_syscalls = _read(GAME_SYSCALLS)
	g_local = _read(GAME_LOCAL)
	sv_game = _read(SERVER_SV_GAME)
	ql_imports = _read(SERVER_QL_GAME_IMPORTS)
	botlib_h = _read(BOTLIB_H)
	be_ea = _read(BOTLIB_EA)
	be_interface = _read(BOTLIB_INTERFACE)
	syscall_map = _extract_function_block(g_syscalls, "static int G_MapNativeImport")
	legacy_ea_enum = g_public[g_public.index("BOTLIB_EA_SAY = 400") : g_public.index("BOTLIB_AI_LOAD_CHARACTER = 500")]
	init_imports = _extract_function_block(sv_game, "static void SV_InitGameImports")

	for slot, native_name, legacy_name, wrapper, _, _, _, _ in EXPECTED_EA_NATIVE_SLOTS:
		assert f"{native_name} = {slot}," in g_public
		assert f"ql_game_imports[{native_name}] = (ql_import_f){wrapper};" in init_imports
		assert f"static void QDECL {wrapper}" in ql_imports

		if legacy_name is None:
			assert "BOTLIB_EA_WALK" not in legacy_ea_enum
			assert "BOTLIB_EA_WALK" not in syscall_map
			assert "trap_EA_Walk" not in g_syscalls
			assert "trap_EA_Walk" not in g_local
			assert "botlib_export->ea.EA_Walk( client );" in ql_imports
			continue

		assert f"case {legacy_name}: return {native_name};" in syscall_map
		assert f"void\t{wrapper.replace('QL_G_', '')}" in g_local

	for source_anchor in (
		"#define ACTION_WALK\t\t\t\t0x0080000",
		"void\t(*EA_Walk)(int client);",
		"ea->EA_Walk = EA_Walk;",
		"void EA_Walk(int client)",
		"bi->actionflags |= ACTION_WALK;",
	):
		assert source_anchor in (botlib_h + be_interface + be_ea)
