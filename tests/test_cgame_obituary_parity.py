"""Guard the retail-backed cgame obituary feed against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_NEWDRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_newdraw.c"
CGAME_GHIDRA_DECOMPILE = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
CGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil.txt"
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


def test_obituary_struct_uses_retail_cached_feed_shape() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "#define\tMAX_OBITUARIES\t\t16" in source
	assert "#define\tCG_OBITUARY_NAME_SIZE\t40" in source
	assert "#define\tOBITUARY_TIME\t\t2000" in source

	struct_block = _block_from_marker(source, "typedef struct {\n\tqboolean\tactive;")
	for expected in (
		"qboolean\tactive;",
		"char\t\ttargetName[CG_OBITUARY_NAME_SIZE];",
		"int\t\ttargetColorIndex;",
		"char\t\tattackerName[CG_OBITUARY_NAME_SIZE];",
		"int\t\tattackerColorIndex;",
		"qboolean\thasAttacker;",
		"qhandle_t\ticon;",
	):
		assert expected in struct_block
	for stale in (
		"int\t\tattacker;",
		"int\t\ttarget;",
		"int\t\tmod;",
		"obituaryIndex",
	):
		assert stale not in source


def test_obituary_event_caches_retail_feed_rows() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	hlil_source = CGAME_HLIL.read_text(encoding="utf-8")
	obituary_block = _block_from_marker(source, "static void CG_Obituary( entityState_t *ent )")
	record_block = _block_from_marker(source, "static void CG_RecordObituaryFeedEntry")
	name_block = _block_from_marker(source, "static void CG_SetObituaryName")
	retail_record = _text_between(
		hlil_source,
		"10018f60    int32_t __convention(\"regparm\") sub_10018f60",
		"10019130",
	)

	for marker in (
		"static int CG_ObituaryFeedLimit( void )",
		"static int CG_ObituaryColorIndexForClient( int clientNum )",
		"static void CG_SanitizeObituaryText( char *text )",
		"static void CG_RecordObituaryFeedEntry(",
		"void CG_PruneObituaryFeed( void )",
	):
		assert marker in source

	for expected in (
		"memmove(&data_10ab8fec, 0x10ab9054, 0x67f)",
		"memset(0x10ab9604, 0, 0x68)",
		"strncpy(esi * 0x68 + 0x10ab8ff4, arg1, 0x27)",
		"strncpy(edi_1, arg2, 0x27)",
		"*(esi * 0x68 + &data_10ab904c) = arg5",
		"*(esi * 0x68 + 0x10ab901c) = arg3",
		"*(esi * 0x68 + 0x10ab9048) = arg4",
		"*(esi * 0x68 + 0x10ab9050) = arg6",
	):
		assert expected in retail_record

	assert "#define CG_OBITUARY_RETAIL_NAME_CHARS 29" in source
	assert "copySize = CG_OBITUARY_RETAIL_NAME_CHARS + 1;" in name_block
	assert "CG_SanitizeObituaryText( buffer );" not in name_block
	assert "CG_SetObituaryName( targetName, sizeof( targetName ), targetInfo );" in obituary_block
	assert "icon = CG_GetObituaryIcon( mod );" in obituary_block
	assert "cg.killerName[0] = '\\0';" in obituary_block
	assert "CG_RecordObituaryFeedEntry( targetName, targetColorIndex, \"\", attackerColorIndex," in obituary_block
	assert "CG_RecordObituaryFeedEntry( targetName, targetColorIndex,\n\t\t\t\tattackerName, attackerColorIndex, qtrue, icon );" in obituary_block
	assert "CG_Printf( \"%s %s %s%s\\n\"," in obituary_block
	for stale in (
		"entry->attacker = attacker;",
		"entry->target = target;",
		"entry->mod = mod;",
		"attacker, target, mod",
	):
		assert stale not in record_block


def test_obituary_draw_uses_cached_feed_payload() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	newdraw_source = CG_NEWDRAW.read_text(encoding="utf-8")
	ghidra_source = CGAME_GHIDRA_DECOMPILE.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static float CG_DrawObituaries( float y )")
	draw2d_block = _block_from_marker(source, "static void CG_Draw2D")
	color_block = _block_from_marker(source, "void CG_ObituaryColorForIndex")
	ownerdraw_block = _block_from_marker(newdraw_source, "static void CG_DrawPlayerObituary")
	retail_draw = _text_between(
		ghidra_source,
		"/* FUN_1002e9b0 @ 1002e9b0 size",
		"/* FUN_10033040 @ 10033040 size",
	)

	assert "CG_PruneObituaryFeed();" in block
	assert "const cgObituary_t\t*entry;" in block
	assert "entry = &cg.obituaries[i];" in block
	assert "entry->targetName[0]" in block
	assert "entry->hasAttacker && entry->attackerName[0]" in block
	assert "entry->icon" in block
	assert "CG_ObituaryColorForIndex( entry->targetColorIndex, alpha, targetColor );" in block
	assert "CG_ObituaryColorForIndex( entry->attackerColorIndex, alpha, attackerColor );" in block
	assert "if ( !menuHudActive ) {\n\t\tCG_DrawObituaries( 150.0f );\n\t}" in draw2d_block
	for expected in (
		"*piVar6 + 2000 <= iVar3",
		"if ((int)local_c < 200)",
		"FUN_10008440(*param_1,(float)(int)local_20,0,param_2,pfVar4,piVar6 + -0xb,0,0,0);",
		"local_c = (float)local_1c + *param_1 + (float)(iVar3 * 2);",
		"FUN_10008440(local_c,(float)(int)fVar7,0,param_2,pfVar4,piVar6 + -0x16,0,0,0);",
		"pfVar2 = (float *)&DAT_10078650;",
	):
		assert expected in retail_draw
	for expected in (
		"case 0:",
		"color[0] = 1.0f;",
		"color[1] = 0.8f;",
		"color[2] = 0.2f;",
	):
		assert expected in color_block
	for expected in (
		"y = (float)(int)rect->y;",
		"attackerWidth = 0.0f;",
		"CG_Text_Paint( rect->x, y, scale, attackerColor, entry->attackerName, 0, 0, textStyle );",
		"attackerWidth = (float)CG_Text_Width( entry->attackerName, scale, 0 );",
		"iconX = rect->x + attackerWidth + rowHeight * 0.5f;",
		"CG_DrawPic( iconX, y - iconSize, iconSize, iconSize, entry->icon );",
		"targetX = rect->x + attackerWidth + rowHeight * 2.0f;",
		"CG_Text_Paint( targetX, y, scale, targetColor, entry->targetName, 0, 0, textStyle );",
	):
		assert expected in ownerdraw_block
	assert ownerdraw_block.index("entry->attackerName") < ownerdraw_block.index("entry->icon")
	assert ownerdraw_block.index("entry->icon") < ownerdraw_block.index("entry->targetName")

	for stale in (
		"attacker = cg.obituaries[i].attacker;",
		"target = cg.obituaries[i].target;",
		"mod = cg.obituaries[i].mod;",
		"attackerName = cgs.clientinfo[attacker].name;",
		"targetName = cgs.clientinfo[target].name;",
		"icon = CG_GetObituaryIcon( mod );",
	):
		assert stale not in block
