from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
	definition = f"{marker} {{"
	if definition in source:
		start = source.index(definition)
	else:
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
				return source[start : index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_domination_capture_rewards_match_retail_hlil() -> None:
	game_team_c = _read("src/code/game/g_team.c")
	hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")

	reward_block = _block_from_marker(game_team_c, "static void G_DominationRewardCaptureParticipants")
	update_block = _block_from_marker(game_team_c, "static void Team_DominationUpdatePointState")
	touch_block = _block_from_marker(game_team_c, "void Team_DominationPointTouch")

	assert "1004aa80" in hlil
	assert "0x19" in hlil
	assert "0xf" in hlil
	assert '"CAPTURE"' in hlil
	assert '"ASSIST"' in hlil

	assert "#define DOMINATION_CAPTURE_BONUS\t25" in game_team_c
	assert "#define DOMINATION_ASSIST_BONUS\t15" in game_team_c
	assert "gentity_t\t*redParticipants[MAX_CLIENTS];" in game_team_c
	assert "gentity_t\t*blueParticipants[MAX_CLIENTS];" in game_team_c
	assert "gentity_t\t*primaryCapturer;" in game_team_c
	assert "Team_DominationAddParticipant( point, other );" in touch_block
	assert "AddScore( participant, origin, DOMINATION_CAPTURE_BONUS );" in reward_block
	assert "participant->client->pers.teamState.captures++;" in reward_block
	assert "participant->client->ps.persistant[PERS_CAPTURES]++;" in reward_block
	assert 'G_RankSendPlayerMedal( participant, "CAPTURE" );' in reward_block
	assert "participant->client->ps.eFlags |= EF_AWARD_CAP;" in reward_block
	assert "AddScore( participant, origin, DOMINATION_ASSIST_BONUS );" in reward_block
	assert "participant->client->pers.teamState.assists++;" in reward_block
	assert "participant->client->ps.persistant[PERS_ASSIST_COUNT]++;" in reward_block
	assert 'G_RankSendPlayerMedal( participant, "ASSIST" );' in reward_block
	assert "participant->client->ps.eFlags |= EF_AWARD_ASSIST;" in reward_block
	assert "participant->client->rewardTime = level.time + REWARD_SPRITE_TIME;" in reward_block
	assert "G_DominationRewardCaptureParticipants( point->redParticipants, point, point->redParticipantCount );" in update_block
	assert "G_DominationRewardCaptureParticipants( point->blueParticipants, point, point->blueParticipantCount );" in update_block


def test_domination_primary_capturer_selection_preserves_retail_owner_stability() -> None:
	game_team_c = _read("src/code/game/g_team.c")
	hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")

	select_block = _block_from_marker(game_team_c, "static void G_DominationSelectPrimaryCapturer")
	update_block = _block_from_marker(game_team_c, "static void Team_DominationUpdatePointState")

	assert "1004abf0" in hlil
	assert "*(arg6 + 0x2e0)" in hlil

	assert "if ( redCount > 0 && blueCount > 0 ) {" in select_block
	assert "point->primaryCapturer = NULL;" in select_block
	assert "G_DominationParticipantInList( point->primaryCapturer, redTeam, redCount )" in select_block
	assert "point->primaryCapturer = redTeam[0];" in select_block
	assert "G_DominationParticipantInList( point->primaryCapturer, blueTeam, blueCount )" in select_block
	assert "point->primaryCapturer = blueTeam[0];" in select_block
	assert "G_DominationSelectPrimaryCapturer( point, point->redParticipantCount, point->blueParticipantCount," in update_block


def test_domination_defense_bonus_is_retail_route_from_frag_bonuses() -> None:
	game_team_c = _read("src/code/game/g_team.c")
	game_main_c = _read("src/code/game/g_main.c")
	hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")

	defense_block = _block_from_marker(game_team_c, "static qboolean G_DominationCheckDefenseBonus")
	frag_block = _block_from_marker(game_team_c, "void Team_FragBonuses")
	rank_block = _block_from_marker(game_main_c, "static rankMedal_t G_RankResolveMedalIndex")

	assert "1004b980" in hlil
	assert "500.0" in hlil
	assert '"DEFENSE"' in hlil
	assert "100689fc" in hlil
	assert "sub_1004b980(arg1, arg2)" in hlil

	assert "#define DOMINATION_DEFENSE_RADIUS\t500.0f" in game_team_c
	assert "point->ownerTeam != team" in defense_block
	assert "VectorLength( delta ) >= DOMINATION_DEFENSE_RADIUS" in defense_block
	assert "trap_InPVS( origin, targ->r.currentOrigin )" in defense_block
	assert "AddScore( attacker, targ->r.currentOrigin, CTF_FLAG_DEFENSE_BONUS );" in defense_block
	assert "attacker->client->pers.teamState.basedefense++;" in defense_block
	assert "attacker->client->ps.persistant[PERS_DEFEND_COUNT]++;" in defense_block
	assert 'G_RankSendPlayerMedal( attacker, "DEFENSE" );' in defense_block
	assert "attacker->client->ps.eFlags |= EF_AWARD_DEFEND;" in defense_block
	assert 'Q_stricmp( medal, "DEFENSE" ) == 0' in rank_block

	assert "if ( g_gametype.integer == GT_DOMINATION ) {" in frag_block
	assert "G_DominationCheckDefenseBonus( attacker, targ );" in frag_block
	assert frag_block.index("if ( g_gametype.integer == GT_DOMINATION ) {") < frag_block.index("// same team, if the flag")


def test_domination_point_activation_and_point_cap_match_retail_qagame() -> None:
	game_local_h = _read("src/code/game/g_local.h")
	game_team_c = _read("src/code/game/g_team.c")
	hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")

	spawn_block = _block_from_marker(game_team_c, "void SP_team_dom_point")
	activate_block = _block_from_marker(game_team_c, "static void G_DominationPointActivate")

	assert "1004b720" in hlil
	assert "1004bb10" in hlil
	assert "if (eax_9 s< 5)" in hlil
	assert "128.0" in hlil
	assert "#define DOMINATION_MAX_POINTS\t5" in game_local_h

	assert "Team_RegisterDominationPoint( ent );" in spawn_block
	assert "ent->think = G_DominationPointActivate;" in spawn_block
	assert "ent->nextthink = level.time + 1;" in spawn_block
	assert "trap_LinkEntity( ent );" not in spawn_block

	assert "VectorSet( mins, -15.0f, -15.0f, -15.0f );" in activate_block
	assert "VectorSet( maxs, 15.0f, 15.0f, 35.0f );" in activate_block
	assert "end[2] -= 256.0f;" in activate_block
	assert "fallbackStart[2] += 128.0f;" in activate_block
	assert "trap_Trace( &tr, start, mins, maxs, end, ent->s.number, MASK_SOLID );" in activate_block
	assert "trap_Trace( &tr, fallbackStart, mins, maxs, end, ent->s.number, MASK_SOLID );" in activate_block
	assert "G_SetOrigin( ent, tr.endpos );" in activate_block
	assert "trap_LinkEntity( ent );" in activate_block
	assert "Team_DominationBuildSpawnList( point );" in activate_block
	assert "ent->think = Team_DominationPointThink;" in activate_block
