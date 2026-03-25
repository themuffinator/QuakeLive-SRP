from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_client_visibility_export_matches_retail_branch_surface() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_CanClientSeeClient( int viewerClientNum, int targetClientNum );" in local_h
	assert "static qboolean G_RedRoverClientVisibilityEnabled( void ) {" in team_c
	assert "static qboolean G_IsOneFlagBotCarrier( const gentity_t *ent, const gclient_t *client ) {" in team_c
	assert "qboolean G_CanClientSeeClient( int viewerClientNum, int targetClientNum ) {" in team_c
	assert "if ( G_IsOneFlagBotCarrier( &g_entities[targetClientNum], NULL ) ) {" in team_c
	assert "if ( g_gametype.integer >= GT_TEAM && G_ClientNumsOnSameTeam( viewerClientNum, targetClientNum ) ) {" in team_c
	assert "if ( G_IsClientSpectator( viewerClientNum ) ) {" in team_c
	assert "if ( G_RedRoverClientVisibilityEnabled()" in team_c
	assert "&& !G_ClientNumsOnSameTeam( viewerClientNum, targetClientNum ) ) {" in team_c
	assert "if ( viewerClientNum == targetClientNum ) {" not in team_c
	assert "return client->ps.powerups[PW_NEUTRALFLAG] ? qtrue : qfalse;" not in team_c


def test_duel_queue_selection_is_split_into_retail_helper() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "gentity_t *G_FindNextTournamentPlayer( void );" in local_h
	assert "gentity_t *G_FindNextTournamentPlayer( void ) {" in main_c
	assert "if ( client->sess.spectateOnly ) {" in main_c
	assert "if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ||" in main_c
	assert "client->sess.spectatorClient < 0 ) {" in main_c
	assert "if ( !nextInLine || client->sess.spectatorTime < nextInLine->client->sess.spectatorTime ) {" in main_c
	assert "nextInLine = G_FindNextTournamentPlayer();" in main_c
	assert 'SetTeam( nextInLine, "f" );' in main_c
