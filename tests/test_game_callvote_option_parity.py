from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_cmd_callvote_exposes_retail_random_and_toggle_votes() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "#define VF_NO_TIME_LIMIT\t\t0x0020" in game_cmds
	assert "#define VF_NO_FRAG_LIMIT\t\t0x0040" in game_cmds
	assert "#define VF_NO_SHUFFLE\t\t\t0x0080" in game_cmds
	assert "#define VF_NO_TEAMSIZE\t\t\t0x0100" in game_cmds
	assert "#define VF_NO_RANDOM\t\t\t0x0200" in game_cmds
	assert "#define VF_NO_LOADOUTS\t\t\t0x0400" in game_cmds
	assert "#define VF_NO_ENDVOTE\t\t\t0x0800" in game_cmds
	assert "#define VF_NO_AMMO\t\t\t0x1000" in game_cmds
	assert "#define VF_NO_TIMERS\t\t\t0x2000" in game_cmds
	assert "#define VF_NO_WEAPRESPAWN\t\t0x4000" in game_cmds
	assert "#define VF_NO_BOTS" not in game_cmds
	assert "static qboolean G_IsVoteTokenIdentifier( const char *token ) {" in game_cmds
	assert "static qboolean G_IsSafeVoteToken( const char *token ) {" in game_cmds
	assert "static qboolean G_CallVoteTargetPlayerExists( const char *name ) {" in game_cmds
	assert "static qboolean G_CallVoteClientSlotIsActive( int clientNum ) {" in game_cmds
	assert "static qboolean G_VoteArgumentIsNumericValue( const char *text ) {" in game_cmds
	assert "static qboolean G_VoteArgumentIsUnsignedInteger( const char *text ) {" not in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to coin toss is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Valid cointoss parameters are:    ^5heads    ^5tails ^7\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "cointoss %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Random number generation is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid upper limit, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid upper limit. (Valid Range: 2 - 100)\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "random %d", upperLimit );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter loadouts is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter loadouts is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "loadouts %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the ammo system is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the ammo system is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "ammo %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the item timers is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to alter the item timers is only allowed during the warm up period.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "timers %s", arg2 );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to change the weapon respawn time is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired weapon respawn time.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired weapon respawn time, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "weaprespawn %d", atoi( arg2 ) );' in game_cmds

	assert '!Q_stricmp( arg1, "kickbot" )' not in game_cmds
	assert '!Q_stricmp( arg1, "addbot" )' not in game_cmds
	assert '!Q_stricmp( arg1, "scorelimit" )' not in game_cmds
	assert '!Q_stricmp( arg1, "roundlimit" )' not in game_cmds
	assert '!Q_stricmp( arg1, "randommap" )' not in game_cmds
	assert '!Q_stricmp( arg1, "ruleset" )' not in game_cmds


def test_cmd_callvote_restores_retail_privileged_bypass() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static qboolean G_ClientBypassesCallVoteRestrictions( const gclient_t *client ) {" in game_cmds
	assert "return ( client->sess.privilege >= PRIV_MOD ) ? qtrue : qfalse;" in game_cmds
	assert "privilegedCallVote = G_ClientBypassesCallVoteRestrictions( client );" in game_cmds

	assert "if ( !g_allowVote.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( g_voteLimit.integer > 0 && client->pers.voteCount >= g_voteLimit.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( isSpectator && !g_allowSpecVote.integer && !privilegedCallVote ) {" in game_cmds
	assert "if ( !g_allowVoteMidGame.integer && midGame && !privilegedCallVote ) {" in game_cmds

	assert "if ( ( g_voteFlags.integer & VF_NO_MAP_RESTART ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_NEXTMAP ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_MAP ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_GAMETYPE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_SHUFFLE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_TEAMSIZE ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_KICK ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_TIME_LIMIT ) && !privilegedCallVote ) {" in game_cmds
	assert "if ( ( g_voteFlags.integer & VF_NO_FRAG_LIMIT ) && !privilegedCallVote ) {" in game_cmds


def test_cmd_callvote_restores_retail_map_nextmap_and_kick_validation() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert 'trap_Argv( 1, arg1, sizeof( arg1 ) );' in game_cmds
	assert 'if ( !G_IsSafeVoteToken( arg1 ) || !G_IsSafeVoteToken( arg2 ) || !G_IsSafeVoteToken( arg3 ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid vote string.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"No nextmap is currently set.\\\\n\\"" );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "map %s; set nextmap' not in game_cmds
	assert 'Q_strncpyz( level.voteString, buffer, sizeof( level.voteString ) );' in game_cmds
	assert 'Q_strncpyz( level.voteDisplayString, buffer, sizeof( level.voteDisplayString ) );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Factory does not exist.\\\\n\\"" );' in game_cmds

	assert 'if ( !G_CallVoteTargetPlayerExists( arg2 ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, va( "print \\"Player %s is not on the server.\\\\n\\"", arg2 ) );' in game_cmds
	assert 'Com_sprintf( level.voteString, sizeof( level.voteString ), "kick \\"%s\\"", arg2 );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing player id.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid player id, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert 'if ( !G_CallVoteClientSlotIsActive( clientNum ) ) {' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to kick a server admin is not allowed.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired timelimit.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired timelimit, parameter must be an integer in minutes.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired fraglimit.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired fraglimit, parameter must be an integer.\\\\n\\"" );' in game_cmds


def test_cmd_callvote_promotes_pending_vote_through_retail_start_helper() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "static void G_StartPublicVote( void ) {" in game_cmds
	assert "clientNum = level.pendingVoteClientNum;" in game_cmds
	assert "voteSelection = client->pers.voteLastSelection;" in game_cmds
	assert "G_RegisterVoteCall( client, clientNum, voteSelection );" in game_cmds
	assert 'trap_SendServerCommand( -1, va( "print \\"%s called a vote.\\\\n\\"", client->pers.netname ) );' in game_cmds
	assert "client->pers.voteState = VOTE_STATE_YES;" in game_cmds
	assert "level.pendingVoteClientNum = -1;" in game_cmds
	assert 'trap_SetConfigstring( CS_VOTE_TIME, va( "%i", level.voteTime ) );' in game_cmds
	assert 'trap_SetConfigstring( CS_VOTE_STRING, level.voteDisplayString );' in game_cmds
	assert "client->pers.voteLastSelection = voteSelection;" in game_cmds
	assert "level.pendingVoteClientNum = ent-g_entities;" in game_cmds
	assert "G_StartPublicVote();" in game_cmds


def test_cmd_callvote_restores_retail_shuffle_teamsize_and_help_listing() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to shuffle the teams is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to shuffle the teams is only permitted during warmup.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Too many parameters called for a shuffle.\\\\n\\"" );' in game_cmds

	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Teamsize is not available in Duel.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Voting to change team size is disabled on this server.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Missing desired teamsize.\\\\n\\"" );' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Invalid desired teamsize, parameter must be an integer.\\\\n\\"" );' in game_cmds
	assert "G_CountActivePlayersByTeam( activeCounts );" in game_cmds
	assert 'va( "print \\"^1The arena has more than %d players. Players must leave before this teamsize can be set.^7\\"", desiredSize )' in game_cmds
	assert 'va( "print \\"^1%s has more than %d players. Players must leave the team before this teamsize can be set.^7\\"",' in game_cmds
	assert 'va( "print \\"Invalid team size. (Valid Range: %d - %d)\\\\n\\"", 0, maxSize )' in game_cmds

	assert "static int G_CallVoteHelpColor( int voteFlagMask ) {" in game_cmds
	assert "if ( g_voteFlags.integer & voteFlagMask ) {" in game_cmds
	assert "static void G_CallVotePrintHelp( gentity_t *ent ) {" in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"^3Callvote commands:\\\\n\\"" );' in game_cmds
	assert 'va( "print \\"^%imap           ^%inextmap        ^%imap_restart   ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%ikick          ^%iclientkick                      ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%ishuffle       ^%iteamsize       ^%icointoss      ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%itimelimit     ^%ifraglimit      ^%iweaprespawn   ^7\\\\n\\"",' in game_cmds
	assert 'va( "print \\"^%iloadouts      ^%iammo           ^%itimers        ^7\\\\n\\"",' in game_cmds
	assert 'trap_SendServerCommand( ent-g_entities, "print \\"Usage: ^3\\\\\\\\callvote <command> <params>^7\\\\n\\"" );' in game_cmds
	assert "G_CallVotePrintHelp( ent );" in game_cmds
