from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_freeze_round_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")

	assert "static int G_FreezeResolveRoundState( void ) {" in active_c
	assert "static int Freeze_RoundStateTransition( qboolean announce ) {" in active_c
	assert "switch ( G_FreezeResolveRoundState() ) {" in active_c
	assert "if ( g_gametype.integer == GT_FREEZE ) {" in active_c
	assert "Freeze_RoundStateTransition( qtrue );" in active_c
	assert "if ( G_FreezeResolveRoundState() == ROUNDSTATE_WARMUP ) {" in active_c
	assert "if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in active_c


def test_red_rover_controller_helpers_match_retail_mapping_surface() -> None:
	active_c = _read("src/code/game/g_active.c")
	client_c = _read("src/code/game/g_client.c")

	assert "static void G_RRSeedInfectionTeams( void ) {" in active_c
	assert "static void G_RRInitRoundController( void ) {" in active_c
	assert "static int RR_RoundStateTransition( qboolean announce ) {" in active_c
	assert "G_RRSeedInfectionTeams();" in active_c
	assert "G_RRInitRoundController();" in active_c
	assert "if ( g_gametype.integer == GT_RED_ROVER ) {" in active_c
	assert "RR_RoundStateTransition( qtrue );" in active_c

	assert "static void G_RRApplySurvivalBonus( gentity_t *ent ) {" in client_c
	assert "static qboolean G_RRCheckInfectionSpread( gentity_t *ent ) {" in client_c
	assert "static qboolean G_RRCheckExitRules( void ) {" in client_c
	assert "G_RRApplySurvivalBonus( target );" in client_c
	assert "if ( G_RRCheckInfectionSpread( ent ) ) {" in client_c
	assert "G_RRCheckExitRules();" in client_c


def test_red_rover_autojoin_helper_routes_team_selection() -> None:
	cmds_c = _read("src/code/game/g_cmds.c")

	assert "static team_t G_RRResolveAutoJoinTeam( int clientNum ) {" in cmds_c
	assert "if ( g_gametype.integer != GT_RED_ROVER || !g_rrInfected.integer ) {" in cmds_c
	assert "redCount = TeamCount( clientNum, TEAM_RED );" in cmds_c
	assert "blueCount = TeamCount( clientNum, TEAM_BLUE );" in cmds_c
	assert "team = G_RRResolveAutoJoinTeam( clientNum );" in cmds_c


def test_spawn_filter_exemption_helper_matches_retail_mapping_notes() -> None:
	spawn_c = _read("src/code/game/g_spawn.c")

	assert "static qboolean G_SpawnClassExemptFromSpawnFilter( const char *classname ) {" in spawn_c
	assert 'if ( !Q_stricmp( classname, "item_armor_shard" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_redobelisk" ) ) {' in spawn_c
	assert 'if ( !Q_stricmp( classname, "team_blueobelisk" ) ) {' in spawn_c
	assert 'spawnFilterExempt = G_SpawnClassExemptFromSpawnFilter( classname );' in spawn_c
	assert 'if ( G_SpawnString( "not_gametype", NULL, &value ) ) {' in spawn_c
	assert "if ( G_SpawnGametypeMatchesFilter( value ) ) {" in spawn_c
