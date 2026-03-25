"""Guard the retail-backed cgame obituary feed against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"


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


def test_obituary_struct_uses_retail_cached_feed_shape() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "#define\tMAX_OBITUARIES\t\t16" in source
	assert "#define\tCG_OBITUARY_NAME_SIZE\t40" in source

	struct_block = _block_from_marker(source, "typedef struct {\n\tqboolean\tactive;")
	for expected in (
		"qboolean\tactive;",
		"char\t\ttargetName[CG_OBITUARY_NAME_SIZE];",
		"int\t\ttargetColorIndex;",
		"char\t\tattackerName[CG_OBITUARY_NAME_SIZE];",
		"int\t\tattackerColorIndex;",
		"qboolean\thasAttacker;",
		"qhandle_t\ticon;",
		"int\t\tattacker;",
		"int\t\ttarget;",
		"int\t\tmod;",
	):
		assert expected in struct_block


def test_obituary_event_caches_retail_feed_rows() -> None:
	source = CG_EVENT.read_text(encoding="utf-8")
	obituary_block = _block_from_marker(source, "static void CG_Obituary( entityState_t *ent )")

	for marker in (
		"static int CG_ObituaryFeedLimit( void )",
		"static int CG_ObituaryColorIndexForClient( int clientNum )",
		"static void CG_SanitizeObituaryText( char *text )",
		"static void CG_RecordObituaryFeedEntry(",
		"void CG_PruneObituaryFeed( void )",
	):
		assert marker in source

	assert "CG_SetObituaryName( targetName, sizeof( targetName ), targetInfo );" in obituary_block
	assert "icon = CG_GetObituaryIcon( mod );" in obituary_block
	assert "cg.killerName[0] = '\\0';" in obituary_block
	assert "CG_RecordObituaryFeedEntry( targetName, targetColorIndex, \"\", attackerColorIndex," in obituary_block
	assert "CG_RecordObituaryFeedEntry( targetName, targetColorIndex,\n\t\t\t\tattackerName, attackerColorIndex, qtrue, icon, attacker, target, mod );" in obituary_block
	assert "CG_Printf( \"%s %s %s%s\\n\"," in obituary_block


def test_obituary_draw_uses_cached_feed_payload() -> None:
	source = CG_DRAW.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static float CG_DrawObituaries( float y )")

	assert "CG_PruneObituaryFeed();" in block
	assert "const cgObituary_t\t*entry;" in block
	assert "entry = &cg.obituaries[i];" in block
	assert "entry->targetName[0]" in block
	assert "entry->hasAttacker && entry->attackerName[0]" in block
	assert "entry->icon" in block
	assert "CG_ObituaryColorForIndex( entry->targetColorIndex, alpha, targetColor );" in block
	assert "CG_ObituaryColorForIndex( entry->attackerColorIndex, alpha, attackerColor );" in block

	for stale in (
		"attacker = cg.obituaries[i].attacker;",
		"target = cg.obituaries[i].target;",
		"mod = cg.obituaries[i].mod;",
		"attackerName = cgs.clientinfo[attacker].name;",
		"targetName = cgs.clientinfo[target].name;",
		"icon = CG_GetObituaryIcon( mod );",
	):
		assert stale not in block
