#include "g_local.h"

/*
=============
G_ResetClientVoteThrottle

Reset the vote throttle bookkeeping for a client so the UI can re-enable immediately.
=============
*/
void G_ResetClientVoteThrottle( gclient_t *client ) {
	if ( !client ) {
		return;
	}

	client->pers.voteDelayTime = 0;
	client->pers.voteLastSelection = -1;
	client->pers.voteLastEnableFrame = -1;
}

/*
=============
G_InitClientVoteThrottle

Initialise vote throttle defaults for a freshly connected client.
=============
*/
void G_InitClientVoteThrottle( gclient_t *client ) {
	G_ResetClientVoteThrottle( client );
}

/*
=============
G_RegisterVoteCall

Record a vote attempt so the caller's UI is hidden until the throttle expires.
=============
*/
void G_RegisterVoteCall( gclient_t *client, int clientNum, int voteSelection ) {
	if ( !client ) {
		return;
	}

	client->pers.voteDelayTime = level.time;
	client->pers.voteLastSelection = voteSelection;
	client->pers.voteLastEnableFrame = -1;

	trap_SendServerCommand( clientNum, "disable_vote_ui" );
}

/*
=============
G_UpdateVoteThrottle

Re-enable the vote UI once the throttle delay has elapsed for any connected client.
=============
*/
void G_UpdateVoteThrottle( void ) {
	int		clientNum;

	for ( clientNum = 0; clientNum < level.maxclients; clientNum++ ) {
		gclient_t	*client;

		client = &level.clients[clientNum];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}

		if ( client->pers.voteDelayTime <= 0 ) {
			continue;
		}

		if ( level.time - client->pers.voteDelayTime < VOTE_THROTTLE_MSEC ) {
			continue;
		}

		if ( client->pers.voteLastEnableFrame == level.framenum ) {
			continue;
		}

		trap_SendServerCommand( clientNum, "enable_vote_ui" );
		client->pers.voteDelayTime = 0;
		client->pers.voteLastEnableFrame = level.framenum;
	}
}

/*
=============
G_ParseVoteCommandType

Translate the vote command name into the enumeration used for guard/flag lookups.
=============
*/
voteCommandType_t G_ParseVoteCommandType( const char *commandName ) {
	if ( !commandName || !*commandName ) {
		return VOTE_CMD_NONE;
	}

	if ( !Q_stricmp( commandName, "map_restart" ) ) {
		return VOTE_CMD_MAP_RESTART;
	}
	if ( !Q_stricmp( commandName, "nextmap" ) ) {
		return VOTE_CMD_NEXTMAP;
	}
	if ( !Q_stricmp( commandName, "map" ) ) {
		return VOTE_CMD_MAP;
	}
	if ( !Q_stricmp( commandName, "g_gametype" ) ) {
		return VOTE_CMD_G_GAMETYPE;
	}
	if ( !Q_stricmp( commandName, "kick" ) ) {
		return VOTE_CMD_KICK;
	}
	if ( !Q_stricmp( commandName, "clientkick" ) ) {
		return VOTE_CMD_CLIENTKICK;
	}
	if ( !Q_stricmp( commandName, "g_doWarmup" ) ) {
		return VOTE_CMD_G_DO_WARMUP;
	}
	if ( !Q_stricmp( commandName, "timelimit" ) ) {
		return VOTE_CMD_TIMELIMIT;
	}
	if ( !Q_stricmp( commandName, "fraglimit" ) ) {
		return VOTE_CMD_FRAGLIMIT;
	}

	return VOTE_CMD_NONE;
}

/*
=============
G_VoteCommandDisableMask

Return the g_voteFlags bit that governs whether the command may be executed.
=============
*/
int G_VoteCommandDisableMask( voteCommandType_t commandType ) {
	switch ( commandType ) {
	case VOTE_CMD_MAP_RESTART:
		return VOTE_FLAG_DISABLE_MAP_RESTART;
	case VOTE_CMD_NEXTMAP:
		return VOTE_FLAG_DISABLE_NEXTMAP;
	case VOTE_CMD_MAP:
		return VOTE_FLAG_DISABLE_MAP;
	case VOTE_CMD_G_GAMETYPE:
		return VOTE_FLAG_DISABLE_G_GAMETYPE;
	case VOTE_CMD_KICK:
		return VOTE_FLAG_DISABLE_KICK;
	case VOTE_CMD_CLIENTKICK:
		return VOTE_FLAG_DISABLE_CLIENTKICK;
	case VOTE_CMD_G_DO_WARMUP:
		return VOTE_FLAG_DISABLE_G_DO_WARMUP;
	case VOTE_CMD_TIMELIMIT:
		return VOTE_FLAG_DISABLE_TIMELIMIT;
	case VOTE_CMD_FRAGLIMIT:
		return VOTE_FLAG_DISABLE_FRAGLIMIT;
	default:
		return 0;
	}
}

/*
=============
G_VoteCommandGuardFlags

Identify the guard mask applied once a vote command executes.
=============
*/
int G_VoteCommandGuardFlags( voteCommandType_t commandType ) {
	if ( commandType <= VOTE_CMD_NONE ) {
		return 0;
	}

	return VOTE_GUARD_DELAY;
}

/*
=============
G_UpdateVoteGuardState

Expire active guard bits when their timers elapse.
=============
*/
void G_UpdateVoteGuardState( void ) {
	if ( !level.voteGuardFlags ) {
		return;
	}

	if ( level.voteGuardFlags & VOTE_GUARD_DELAY ) {
		int delay;

		delay = (int)( g_voteDelay.value * 1000.0f );
		if ( delay <= 0 || level.voteGuardTime <= 0 || level.time >= level.voteGuardTime ) {
			level.voteGuardFlags &= ~VOTE_GUARD_DELAY;
		}
	}

	if ( !level.voteGuardFlags ) {
		level.voteGuardTime = 0;
	}
}

/*
=============
G_ApplyVoteGuard

Latch the guard flags associated with an executed vote command.
=============
*/
void G_ApplyVoteGuard( int commandFlags ) {
	int delay;

	if ( !commandFlags ) {
		return;
	}

	if ( commandFlags & VOTE_GUARD_DELAY ) {
		delay = (int)( g_voteDelay.value * 1000.0f );
		if ( delay <= 0 ) {
			level.voteGuardFlags &= ~VOTE_GUARD_DELAY;
			if ( !level.voteGuardFlags ) {
				level.voteGuardTime = 0;
			}
		} else {
			level.voteGuardFlags |= VOTE_GUARD_DELAY;
			level.voteGuardTime = level.time + delay;
		}
	}
}

/*
=============
G_IsVoteExecutionPending

Report whether a vote execution or guard condition is still active.
=============
*/
qboolean G_IsVoteExecutionPending( void ) {
	G_UpdateVoteGuardState();

	if ( level.voteExecuteTime ) {
		return qtrue;
	}

	if ( level.voteGuardFlags ) {
		return qtrue;
	}

	return qfalse;
}
