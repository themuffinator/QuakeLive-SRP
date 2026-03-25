from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_award_configstring_slots_match_retail_recovery() -> None:
	bg_public = _read("src/code/game/bg_public.h")

	assert "#define CS_AWARD_BEST_ITEMCONTROL\t0x2B4" in bg_public
	assert "#define CS_AWARD_MOST_ACCURATE\t0x2B5" in bg_public
	assert "#define CS_AWARD_MOST_VALUABLE\t0x2B8" in bg_public
	assert "#define CS_AWARD_MOST_VALUABLE_OFFENSIVE\t0x2B9" in bg_public
	assert "#define CS_AWARD_MOST_VALUABLE_DEFENSIVE\t0x2BA" in bg_public
	assert "#define CS_AWARD_MOST_DAMAGEDEALT\t0x2BB" in bg_public
	assert "#define CS_TUTORIAL_NAME\t\t0x2CA" in bg_public
	assert "#define CS_TUTORIAL_TEXT\t\t0x2CB" in bg_public
	assert "#define CS_FREEZE_TIP_OBJECTIVE\t0x2CC" in bg_public
	assert "#define CS_FREEZE_TIP_SUMMARY\t0x2D0" in bg_public
	assert "#define CS_MAX\t\t\t\t\t(CS_FREEZE_TIP_SUMMARY + 1)" in bg_public


def test_award_helper_and_callsites_follow_retail_boundary() -> None:
	main_c = _read("src/code/game/g_main.c")

	assert "static void G_SetAwardConfigstring( int configstringIndex, int clientNum ) {" in main_c
	assert "static void G_UpdateAwardConfigstrings( void ) {" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_BEST_ITEMCONTROL, bestItemControlClient );" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_MOST_ACCURATE, bestAccuracyClient );" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE, bestMostValuableClient );" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_OFFENSIVE, bestOffensiveClient );" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_MOST_VALUABLE_DEFENSIVE, bestDefensiveClient );" in main_c
	assert "G_SetAwardConfigstring( CS_AWARD_MOST_DAMAGEDEALT, bestDamageClient );" in main_c
	assert "case GT_DOMINATION:" in main_c
	assert "case GT_ATTACK_DEFEND:" in main_c
	assert "G_UpdateAwardConfigstrings();" in main_c
	assert main_c.count("G_UpdateAwardConfigstrings();") >= 2


def test_init_game_uses_retail_spawn_point_count_helper() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "int\t\t\tdeathmatchSpawnPointCount;" in local_h
	assert "int\t\t\tredSpawnPointCount;" in local_h
	assert "int\t\t\tblueSpawnPointCount;" in local_h
	assert "static void G_CountSpawnPoints( void ) {" in main_c
	assert 'if ( Q_stricmp( ent->classname, "info_player_deathmatch" ) ) {' in main_c
	assert 'while ( ( spot = G_Find( spot, FOFS( classname ), "team_CTF_redspawn" ) ) != NULL ) {' in main_c
	assert 'while ( ( spot = G_Find( spot, FOFS( classname ), "team_CTF_bluespawn" ) ) != NULL ) {' in main_c
	assert "G_CountSpawnPoints();" in main_c
