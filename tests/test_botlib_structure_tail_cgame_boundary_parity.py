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
BOTLIB_L_STRUCT = REPO_ROOT / "src" / "code" / "botlib" / "l_struct.c"
BOTLIB_AI_WEAP = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weap.c"
BOTLIB_AI_WEIGHT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_weight.c"
CLIENT_CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CLIENT_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
CGAME_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CGAME_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"

SEAM_START = 0x004AF050
SEAM_END = 0x004AF820

PROMOTED_BOUNDARY_ALIASES = {
	"sub_4AE830": "FindField",
	"sub_4AE8A0": "ReadNumber",
	"sub_4AECD0": "ReadStructure",
	"sub_4AF570": "CL_GetSnapshot",
	"sub_4AF690": "CL_ConfigstringModified",
	"sub_4AF820": "CL_GetServerCommand",
}

INTENTIONALLY_UNPROMOTED_SEAM_ROWS = {
	0x004AF050,
	0x004AF150,
	0x004AF190,
	0x004AF1C0,
	0x004AF2C0,
	0x004AF370,
	0x004AF400,
	0x004AF4C0,
	0x004AF4D0,
	0x004AF4E0,
	0x004AF500,
}

EXPECTED_SEAM_ROWS = {
	0x004AF050: "FUN_004af050,004af050,242,0,unknown",
	0x004AF150: "FUN_004af150,004af150,49,0,unknown",
	0x004AF190: "FUN_004af190,004af190,41,0,unknown",
	0x004AF1C0: "FUN_004af1c0,004af1c0,252,0,unknown",
	0x004AF2C0: "FUN_004af2c0,004af2c0,176,0,unknown",
	0x004AF370: "FUN_004af370,004af370,141,0,unknown",
	0x004AF400: "FUN_004af400,004af400,191,0,unknown",
	0x004AF4C0: "FUN_004af4c0,004af4c0,11,0,unknown",
	0x004AF4D0: "FUN_004af4d0,004af4d0,6,0,unknown",
	0x004AF4E0: "FUN_004af4e0,004af4e0,29,0,unknown",
	0x004AF500: "FUN_004af500,004af500,111,0,unknown",
	0x004AF570: "FUN_004af570,004af570,273,0,unknown",
	0x004AF690: "FUN_004af690,004af690,387,0,unknown",
	0x004AF820: "FUN_004af820,004af820,958,0,unknown",
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam"]


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


def _function_rows_in_seam() -> dict[int, str]:
	rows: dict[int, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			address = int(row["entry"], 16)
			if SEAM_START <= address <= SEAM_END:
				rows[address] = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	return rows


def test_botlib_structure_tail_boundary_promotes_only_evidence_backed_client_owners() -> None:
	aliases = _aliases()
	rows = _function_rows_in_seam()

	assert {address: aliases[address] for address in PROMOTED_BOUNDARY_ALIASES} == PROMOTED_BOUNDARY_ALIASES
	assert rows == EXPECTED_SEAM_ROWS
	assert {
		address for address in rows if f"sub_{address:X}" not in aliases
	} == INTENTIONALLY_UNPROMOTED_SEAM_ROWS

	for source_visible_but_unpromoted in (
		"ReadChar",
		"ReadString",
		"WriteIndent",
		"WriteFloat",
		"WriteStructWithIndent",
		"WriteStructure",
	):
		assert source_visible_but_unpromoted not in aliases.values()


def test_l_struct_write_helpers_are_source_real_but_not_the_adjacent_retail_seam() -> None:
	l_struct = _read(BOTLIB_L_STRUCT)
	ai_weap = _read(BOTLIB_AI_WEAP)
	ai_weight = _read(BOTLIB_AI_WEIGHT)
	hlil = _read(QL_STEAM_HLIL_PART04)

	read_structure = _extract_function_block(l_struct, "int ReadStructure(source_t *source, structdef_t *def, char *structure)")
	write_indent = _extract_function_block(l_struct, "int WriteIndent(FILE *fp, int indent)")
	write_float = _extract_function_block(l_struct, "int WriteFloat(FILE *fp, float value)")
	write_with_indent = _extract_function_block(
		l_struct,
		"int WriteStructWithIndent(FILE *fp, structdef_t *def, char *structure, int indent)",
	)
	write_structure = _extract_function_block(l_struct, "int WriteStructure(FILE *fp, structdef_t *def, char *structure)")

	assert "ReadStructure(source, fd->substruct, (char *) p);" in read_structure
	assert "if (!ReadStructure(source, fd->substruct" not in read_structure
	assert 'SourceError(source, "expected a comma, found %s", token.string);' in read_structure
	assert "while(indent-- > 0)" in write_indent
	assert 'fprintf(fp, "\\t")' in write_indent
	assert 'sprintf(buf, "%f", value);' in write_float
	assert "if (buf[l] != '0' && buf[l] != '.') break;" in write_float
	assert 'fprintf(fp, "%s", buf)' in write_float
	assert 'fprintf(fp, "{\\r\\n")' in write_with_indent
	assert "if (!WriteFloat(fp, *(float *)p)) return qfalse;" in write_with_indent
	assert "if (!WriteStructWithIndent(fp, fd->substruct, structure, indent)) return qfalse;" in write_with_indent
	assert "return WriteStructWithIndent(fp, def, structure, 0);" in write_structure

	dump_weapon_index = ai_weap.index("#ifdef DEBUG_AI_WEAP")
	dump_writer_index = ai_weap.index("WriteStructure(fp, &projectileinfo_struct")
	dump_end_index = ai_weap.index("#endif //DEBUG_AI_WEAP")
	load_weapon_index = ai_weap.index("weaponconfig_t *LoadWeaponConfig")
	assert dump_weapon_index < dump_writer_index < dump_end_index < load_weapon_index

	weight_writer_start = ai_weight.index("#if 0")
	weight_writer_use = ai_weight.index("if (!WriteFloat(fp, fs->weight)) return qfalse;")
	weight_writer_end = ai_weight.index("#endif", weight_writer_use)
	assert weight_writer_start < weight_writer_use < weight_writer_end

	for adjacent_non_botlib_anchor in (
		'004af1ed  sub_4af050(arg1, "camera01")',
		"004af500    int32_t sub_4af500(int32_t arg1)",
		"004af555          char ecx_3 = (eax_2.b - 0x66) ^",
		"004af570    int32_t sub_4af570(void* arg1, int32_t* arg2)",
		"004af690    int32_t sub_4af690()",
		"004af820    int32_t sub_4af820(int32_t arg1)",
	):
		assert adjacent_non_botlib_anchor in hlil


def test_cgame_snapshot_and_configstring_promotions_match_source_hlil_and_import_wiring() -> None:
	aliases = _aliases()
	cl_cgame = _read(CLIENT_CL_CGAME)
	cgame_imports = _read(CLIENT_CGAME_IMPORTS)
	cg_syscalls = _read(CGAME_SYSCALLS)
	cg_public = _read(CGAME_PUBLIC)
	hlil = _read(QL_STEAM_HLIL_PART04)

	get_snapshot = _extract_function_block(cl_cgame, "qboolean\tCL_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )")
	configstring_modified = _extract_function_block(cl_cgame, "void CL_ConfigstringModified( void )")
	cgame_system_calls = _extract_function_block(cl_cgame, "static int CL_CgameSystemCallsImpl( int *args, qboolean logContract )")
	cg_map_native = _extract_function_block(cg_syscalls, "static int CG_MapNativeImport( int arg, const intptr_t *stack )")
	trap_get_snapshot = _extract_function_block(cg_syscalls, "qboolean\ttrap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )")

	assert aliases["sub_4AF570"] == "CL_GetSnapshot"
	assert aliases["sub_4AF690"] == "CL_ConfigstringModified"
	assert aliases["sub_4B0150"] == "QLCGImport_GetSnapshot"
	assert aliases["sub_4B0160"] == "QLCGImport_GetServerCommand"

	for source_anchor in (
		"if ( snapshotNumber > cl.snap.messageNum )",
		"if ( cl.snap.messageNum - snapshotNumber >= PACKET_BACKUP )",
		"clSnap = &cl.snapshots[snapshotNumber & PACKET_MASK];",
		"if ( cl.parseEntitiesNum - clSnap->parseEntitiesNum >= MAX_PARSE_ENTITIES )",
		"snapshot->serverCommandSequence = clSnap->serverCommandNum;",
		"Com_Memcpy( snapshot->areamask, clSnap->areamask, sizeof( snapshot->areamask ) );",
		"snapshot->ps = clSnap->ps;",
		"if ( count > MAX_ENTITIES_IN_SNAPSHOT )",
		"snapshot->entities[i] =",
	):
		assert source_anchor in get_snapshot

	for source_anchor in (
		"index = atoi( Cmd_Argv(1) );",
		"if ( index < 0 || index >= MAX_CONFIGSTRINGS )",
		'Com_Error( ERR_DROP, "configstring > MAX_CONFIGSTRINGS" );',
		"s = Cmd_ArgsFrom(2);",
		"old = cl.gameState.stringData + cl.gameState.stringOffsets[ index ];",
		"oldGs = cl.gameState;",
		"Com_Memset( &cl.gameState, 0, sizeof( cl.gameState ) );",
		"cl.gameState.dataCount = 1;",
		"dup = oldGs.stringData + oldGs.stringOffsets[ i ];",
		"if ( len + 1 + cl.gameState.dataCount > MAX_GAMESTATE_CHARS )",
		"cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;",
		"Com_Memcpy( cl.gameState.stringData + cl.gameState.dataCount, dup, len + 1 );",
		"if ( index == CS_SYSTEMINFO )",
		"CL_SystemInfoChanged();",
	):
		assert source_anchor in configstring_modified

	for hlil_anchor in (
		"004af570    int32_t sub_4af570(void* arg1, int32_t* arg2)",
		"004af573  int32_t eax = data_146cd30",
		"004af599  if (eax - arg1 s< 0x20)",
		"004af5a9      int32_t* ebx_3 = (arg1 & 0x1f) * 0x298 + 0x1472874",
		"004af5f2          sub_4cb7d0(&arg2[3], &ebx_3[6], 0x20)",
		"004af602          __builtin_memcpy(dest: &arg2[0xb], src: &ebx_3[0xf], n: 0x250)",
		"004af613          if (edx_2 s> 0x180)",
		"004af67a                  __builtin_memcpy(dest: edi_2, src: esi_5, n: 0xec)",
		"004af689          return 1",
		"004af690    int32_t sub_4af690()",
		"004af6b7  int32_t esi = atoi(sub_4c7ee0(1))",
		"004af6cc  if (esi s< 0 || esi s>= 0x400)",
		'004af6d5      sub_4c9b60(1, "configstring > MAX_CONFIGSTRINGS")',
		"004af6df  sub_4c7fd0(2)",
		"004af73f      int32_t var_4e8c[0x1399]",
		"004af750      result = sub_4c95e0(&data_146cfd4, 0, 0x4e84)",
		'004af7b0                  sub_4c9b60(1, "MAX_GAMESTATE_CHARS exceeded")',
		"004af807          result = sub_4bd620(esi)",
	):
		assert hlil_anchor in hlil

	assert "case CG_GETSNAPSHOT:" in cgame_system_calls
	assert "return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;" in cgame_system_calls
	assert "case CG_GETSERVERCOMMAND:" in cgame_system_calls
	assert "return CL_GetServerCommand( args[1] ) ? qtrue : qfalse;" in cgame_system_calls
	assert "ql_cgame_imports[CG_QL_IMPORT_GETSNAPSHOT] = (ql_import_f)QL_CG_trap_GetSnapshot;" in cl_cgame
	assert "ql_cgame_imports[CG_QL_IMPORT_GETSERVERCOMMAND] = (ql_import_f)QL_CG_trap_GetServerCommand;" in cl_cgame
	assert "static qboolean QDECL QL_CG_trap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot )" in cgame_imports
	assert "return CG_Import_Syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot );" in cgame_imports
	assert "CG_QL_IMPORT_GETSNAPSHOT = 87," in cg_public
	assert "CG_QL_IMPORT_GETSERVERCOMMAND = 88," in cg_public
	assert "case CG_GETSNAPSHOT: return CG_QL_IMPORT_GETSNAPSHOT;" in cg_map_native
	assert "case CG_GETSERVERCOMMAND: return CG_QL_IMPORT_GETSERVERCOMMAND;" in cg_map_native
	assert "return syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot ) ? qtrue : qfalse;" in trap_get_snapshot
