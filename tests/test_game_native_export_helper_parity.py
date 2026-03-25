from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_voice_suppression_helper_matches_retail_export_policy() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_ShouldSuppressVoiceToClient( int senderClientNum, int recipientClientNum );" in local_h
	assert "qboolean G_ShouldSuppressVoiceToClient( int senderClientNum, int recipientClientNum ) {" in team_c
	assert "if ( recipientEnt->r.svFlags & SVF_BOT ) {" in team_c
	assert "if ( sender->sess.muted ) {" in team_c
	assert "if ( g_gametype.integer < GT_TEAM || g_allTalk.integer ) {" in team_c
	assert "if ( senderClientNum == recipientClientNum ) {" in team_c
	assert "return G_ClientNumsOnSameTeam( senderClientNum, recipientClientNum ) ? qfalse : qtrue;" in team_c


def test_objective_classifier_covers_retail_flag_and_obelisk_paths() -> None:
	local_h = _read("src/code/game/g_local.h")
	team_c = _read("src/code/game/g_team.c")

	assert "qboolean G_IsObjectiveEntity( int entNum );" in local_h
	assert "static qboolean G_IsObjectiveFlagItemEntity( const gentity_t *ent, qboolean allowNeutralFlag ) {" in team_c
	assert "static qboolean G_IsOverloadObjectiveEntity( const gentity_t *ent ) {" in team_c
	assert "qboolean G_IsObjectiveEntity( int entNum ) {" in team_c
	assert "case GT_CTF:" in team_c
	assert "case GT_ATTACK_DEFEND:" in team_c
	assert "case GT_1FCTF:" in team_c
	assert "case GT_OBELISK:" in team_c
	assert "if ( ent->client && ent->target_ent && G_IsObjectiveFlagItemEntity( ent->target_ent, qtrue ) ) {" in team_c
	assert 'return G_IsOverloadObjectiveEntity( ent );' in team_c


def test_freeze_visibility_helper_matches_retail_export_boundary() -> None:
	local_h = _read("src/code/game/g_local.h")
	freeze_c = _read("src/code/game/g_freeze.c")

	assert "qboolean\tG_FreezeCanSeeThawProgressEvent( int clientNum, int entNum );" in local_h
	assert "#define QL_EV_FREEZE_THAW_PROGRESS\t0x58" in freeze_c
	assert "static int G_FreezeResolveThawProgressTarget( const gentity_t *ent ) {" in freeze_c
	assert "qboolean G_FreezeCanSeeThawProgressEvent( int clientNum, int entNum ) {" in freeze_c
	assert "if ( level.roundState != ROUNDSTATE_ACTIVE ) {" in freeze_c
	assert "if ( ent->s.eType != ET_EVENTS + QL_EV_FREEZE_THAW_PROGRESS ) {" in freeze_c
	assert "targetClientNum = ent->s.otherEntityNum;" in freeze_c
	assert "targetClientNum = ent->s.clientNum;" in freeze_c
	assert "return G_ClientNumsOnSameTeam( clientNum, targetClientNum );" in freeze_c
