from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_cgame_binding_bridge_uses_direct_retail_copy_path() -> None:
	client = _read("src/code/client/cl_cgame.c")

	assert "case CG_KEY_GETBINDINGBUF:" in client
	assert 'Q_strncpyz( VMA(2), Key_GetBinding( args[1] ), args[3] );' in client


def test_team_balance_helper_is_split_out_for_setteam_and_readyup() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean Team_CountsBalanced( int redCount, int blueCount ) {" in game_cmds
	assert "if ( g_teamForceBalance.integer && !Team_CountsBalanced( redCount, blueCount ) ) {" in game_cmds
	assert "if ( !Team_CountsBalanced( nextRedCount, nextBlueCount ) ) {" in game_cmds


def test_client_spawn_uses_recovered_loadout_and_rr_helpers() -> None:
	game_client = _read("src/code/game/g_client.c")

	assert "static weapon_t G_FinalizeSpawnLoadout( gentity_t *ent, const factoryCvarConfig_t *factoryConfig ) {" in game_client
	assert "spawnWeapon = G_FinalizeSpawnLoadout( ent, factoryConfig );" in game_client
	assert "static void G_RRFinalizeSpawnLoadout( gentity_t *ent ) {" in game_client
	assert "G_RRFinalizeSpawnLoadout( ent );" in game_client


def test_freeze_helpers_match_recovered_retail_boundaries() -> None:
	freeze_c = _read("src/code/game/g_freeze.c")
	active_c = _read("src/code/game/g_active.c")

	assert "static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum ) {" in freeze_c
	assert "G_FreezeSetClientFrozenState( ent, qfalse, qfalse, wasAuto, helperNum );" in freeze_c
	assert "G_FreezeSetClientFrozenState( self, qtrue, environmental, qfalse, -1 );" in freeze_c

	assert "static void G_FreezeResetClientForRound( gentity_t *ent, qboolean warmup ) {" in active_c
	assert "G_FreezeResetClientForRound( ent, warmup );" in active_c
	assert "static qboolean G_FreezeTeamIsFullyFrozen( team_t team ) {" in active_c
	assert "redFrozen = G_FreezeTeamIsFullyFrozen( TEAM_RED );" in active_c
	assert "static int G_TotalLivingHealthByTeam( team_t team ) {" in active_c
	assert "G_CountActivePlayersByTeam( level.freezeLivingCount );" in active_c
	assert "level.freezeLivingHealth[TEAM_RED] = G_TotalLivingHealthByTeam( TEAM_RED );" in active_c


def test_red_rover_helpers_match_recovered_retail_boundaries() -> None:
	game_client = _read("src/code/game/g_client.c")

	assert "static int G_RRResolveRoundState( void ) {" in game_client
	assert "if ( G_RRResolveRoundState() != ROUNDSTATE_ACTIVE ) {" in game_client
	assert "static void G_RRResetClientForRound( gentity_t *ent ) {" in game_client
	assert "G_RRResetClientForRound( ent );" in game_client
