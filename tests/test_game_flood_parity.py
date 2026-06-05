from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_active_client_flood_helper_uses_retail_drop_path() -> None:
	active_c = _read("src/code/game/g_active.c")
	helper_start = active_c.index("static qboolean G_CheckClientFlood( gentity_t *ent )")
	helper_end = active_c.index("static qboolean G_FactoryHealthRegenEnabled", helper_start)
	helper = active_c[helper_start:helper_end]

	assert "static qboolean G_CheckClientFlood( gentity_t *ent )" in active_c
	assert 'trap_DropClient( ent - g_entities, "Dropped for flooding the server" );' in active_c
	assert "if ( !G_CheckClientFlood( ent ) ) {" in active_c
	assert "if ( maxCount <= 0 ) {" in helper
	assert "decay <= 0" not in helper
	assert "if ( level.time - client->floodLastTime > decay ) {" in helper
	assert "client->floodCount--;" in active_c


def test_command_flood_tracking_no_longer_uses_penalty_window() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")
	helper_start = cmds_c.index("static qboolean G_FloodLimited")
	helper_end = cmds_c.index("static int G_ClampItemTimerHeight", helper_start)
	helper = cmds_c[helper_start:helper_end]

	assert 'client->floodCount++;' in cmds_c
	assert 'client->floodLastTime = level.time;' in cmds_c
	assert 'client->floodPenaltyTime = level.time + penalty;' not in cmds_c
	assert "Flood protection triggered. Please wait" not in cmds_c
	assert "if ( maxCount <= 0 ) {" in helper
	assert "decay <= 0" not in helper
	assert 'G_LogPrintf( "floodprot: client %i (%s) exceeded limit via %s\\n",' in cmds_c


def test_flood_docs_and_status_reflect_drop_on_overflow() -> None:
	main_c = _read("src/code/game/g_main.c")
	svcmds_c = _read("src/code/game/g_svcmds.c")

	assert "retail flood protection drops clients on overflow" in main_c
	assert "drop-on-overflow" in svcmds_c
	assert "pending_drop" in svcmds_c
	assert "Set g_floodprot_maxcount to enable it." in svcmds_c
	assert "g_floodprot_decay to enable it" not in svcmds_c
