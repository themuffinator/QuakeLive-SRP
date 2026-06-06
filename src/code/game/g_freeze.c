#include "g_local.h"

/*
============
G_FreezeResolveThawProgressTarget

Finds the linked frozen client for a retail thaw-progress temp entity.
============
*/
static int G_FreezeResolveThawProgressTarget( const gentity_t *ent ) {
	int		targetClientNum;

	if ( !ent ) {
		return -1;
	}

	targetClientNum = ent->s.otherEntityNum;
	if ( targetClientNum >= 0 && targetClientNum < level.maxclients ) {
		if ( g_entities[targetClientNum].inuse
			&& g_entities[targetClientNum].client
			&& level.clients[targetClientNum].pers.connected == CON_CONNECTED ) {
			return targetClientNum;
		}
	}

	targetClientNum = ent->s.clientNum;
	if ( targetClientNum >= 0 && targetClientNum < level.maxclients ) {
		if ( g_entities[targetClientNum].inuse
			&& g_entities[targetClientNum].client
			&& level.clients[targetClientNum].pers.connected == CON_CONNECTED ) {
			return targetClientNum;
		}
	}

	return -1;
}

/*
============
G_FreezeCanSeeThawProgressEvent

Retail-only native export helper for the Freeze thaw-progress temp entity.
============
*/
qboolean G_FreezeCanSeeThawProgressEvent( int clientNum, int entNum ) {
	gentity_t	*ent;
	int		targetClientNum;

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return qfalse;
	}

	if ( level.clients[clientNum].pers.connected != CON_CONNECTED ) {
		return qfalse;
	}

	if ( !G_FreezeGametypeEnabled() ) {
		return qfalse;
	}

	if ( G_FreezeResolveRoundState() != ROUNDSTATE_ACTIVE ) {
		return qfalse;
	}

	if ( entNum < 0 || entNum >= level.num_entities ) {
		return qfalse;
	}

	ent = &g_entities[entNum];
	if ( !ent->inuse ) {
		return qfalse;
	}

	if ( ent->s.eType != ET_EVENTS + EV_THAW_TICK ) {
		return qfalse;
	}

	targetClientNum = G_FreezeResolveThawProgressTarget( ent );
	if ( targetClientNum < 0 ) {
		return qfalse;
	}

	return G_ClientNumsOnSameTeam( clientNum, targetClientNum );
}

/*
============
G_FreezeSetClientFrozenPowerupMarker

Mirrors the retail synthetic frozen-player marker through ps and entitystate powerups.
============
*/
static void G_FreezeSetClientFrozenPowerupMarker( gentity_t *ent, qboolean frozen ) {
	if ( !ent || !ent->client ) {
		return;
	}

	if ( frozen ) {
		ent->client->ps.powerups[PW_NUM_POWERUPS] = INT_MAX;
		ent->s.powerups = ( 1 << PW_NUM_POWERUPS );
	}
	else {
		ent->client->ps.powerups[PW_NUM_POWERUPS] = 0;
		ent->s.powerups &= ~( 1 << PW_NUM_POWERUPS );
	}
}

/*
============
G_FreezeEmitThawCompletionEvents

Publishes the retail assisted-thaw obituary and global team sound.
============
*/
static void G_FreezeEmitThawCompletionEvents( gentity_t *ent, int helperNum ) {
	gclient_t			*client;
	gentity_t			*tent;
	global_team_sound_t	sound;
	int					thawerNum;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	thawerNum = ENTITYNUM_WORLD;
	if ( helperNum >= 0 && helperNum < level.maxclients ) {
		if ( g_entities[helperNum].inuse && g_entities[helperNum].client ) {
			thawerNum = helperNum;
		}
	}

	tent = G_TempEntity( ent->r.currentOrigin, EV_OBITUARY );
	tent->s.eventParm = MOD_THAW;
	tent->s.otherEntityNum = ent->s.number;
	tent->s.otherEntityNum2 = thawerNum;
	tent->r.svFlags = SVF_BROADCAST;

	sound = ( client->sess.sessionTeam == TEAM_BLUE ) ? GTS_RED_RETURN : GTS_BLUE_RETURN;
	G_BroadcastGlobalTeamSound( ent->s.pos.trBase, sound, -1, TEAM_FREE, 0 );
}

/*
============
G_FreezeAwardThawAssist

Credits the helper who completed a teammate thaw.
============
*/
static void G_FreezeAwardThawAssist( gentity_t *ent, int helperNum ) {
	gclient_t	*client;
	gentity_t	*helper;

	if ( !ent || !ent->client ) {
		return;
	}

	if ( helperNum < 0 || helperNum >= level.maxclients ) {
		return;
	}

	helper = &g_entities[helperNum];
	if ( !helper || !helper->client ) {
		return;
	}

	client = ent->client;
	AddScore( helper, ent->r.currentOrigin, 1 );
	trap_SendServerCommand( -1, va( "cp \"%s thawed %s!\"\n", helper->client->pers.netname, client->pers.netname ) );
	helper->client->ps.persistant[PERS_ASSIST_COUNT]++;
	helper->client->ps.eFlags &= ~( EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
	helper->client->ps.eFlags |= EF_AWARD_ASSIST;
	helper->client->rewardTime = level.time + REWARD_SPRITE_TIME;
	G_RankSendPlayerMedal( helper, "ASSIST" );
}

/*
============
G_FreezeInitClient

Initializes client state for Freeze Tag at the start of a round or upon connecting.
============
*/
void G_FreezeInitClient( gentity_t *ent ) {
	if ( !ent || !ent->client ) {
		return;
	}

	ent->client->freezeFrozen = qfalse;
	ent->client->freezeTime = 0;
	ent->client->freezeThawHelperActive = qfalse;
	ent->client->freezeThawTimeRemaining = 0;
	ent->client->freezeLastHelper = -1;
	ent->client->freezeAutoThawTime = 0;
	ent->client->freezeEnvironmentalRespawnTime = 0;
	ent->client->freezeProtectedUntil = 0;
	G_FreezeSetClientFrozenPowerupMarker( ent, qfalse );

	if ( ent->client->sess.sessionTeam != TEAM_SPECTATOR ) {
		ent->client->ps.pm_type = PM_NORMAL;
	}
}

/*
============
G_FreezeSetClientFrozenState

Shared retail-style Freeze state mutator spanning the frozen and thawed paths.
============
*/
static void G_FreezeSetClientFrozenState( gentity_t *ent, qboolean frozen, qboolean environmental, qboolean wasAuto, int helperNum ) {
	gclient_t	*client;
	int			thawTime;
	int			protectTime;
	gentity_t	*tent;
	qboolean	thawThroughRespawn;

	if ( !ent || !ent->client ) {
		return;
	}

	client = ent->client;
	if ( frozen ) {
		if ( client->freezeFrozen ) {
			return;
		}

		client->freezeFrozen = qtrue;
		client->freezeTime = level.time;
		client->freezeThawHelperActive = qfalse;
		thawTime = level.freezeConfig.thawTime;
		if ( thawTime <= 0 ) {
			thawTime = 2000;
		}
		client->freezeThawTimeRemaining = thawTime;
		client->freezeLastHelper = -1;

		client->freezeAutoThawTime = 0;
		if ( level.freezeConfig.autoThawTime > 0 ) {
			client->freezeAutoThawTime = level.time + level.freezeConfig.autoThawTime;
		}

		client->freezeEnvironmentalRespawnTime = 0;
		if ( environmental && level.freezeConfig.environmentalRespawnDelay > 0 ) {
			client->freezeEnvironmentalRespawnTime = level.time + level.freezeConfig.environmentalRespawnDelay;
		}

		G_FreezeSetClientFrozenPowerupMarker( ent, qtrue );
		client->freezeProtectedUntil = 0;
		client->ps.pm_type = PM_FREEZE;
		client->ps.eFlags &= ~( EF_DEAD | EF_TICKING );
		ent->takedamage = qfalse;
		ent->health = 1;
		client->ps.stats[STAT_HEALTH] = 1;
		return;
	}

	if ( !client->freezeFrozen ) {
		return;
	}

	client->freezeFrozen = qfalse;
	client->freezeTime = 0;
	client->freezeThawHelperActive = qfalse;
	client->freezeThawTimeRemaining = 0;
	client->freezeLastHelper = -1;
	client->freezeAutoThawTime = 0;
	client->freezeEnvironmentalRespawnTime = 0;
	thawThroughRespawn = ( client->ps.powerups[PW_NUM_POWERUPS] != 0 ) ? qtrue : qfalse;
	client->ps.pm_type = PM_NORMAL;
	client->ps.eFlags &= ~( EF_DEAD | EF_TICKING );
	ent->takedamage = qtrue;

	if ( !wasAuto ) {
		G_FreezeEmitThawCompletionEvents( ent, helperNum );
		G_FreezeAwardThawAssist( ent, helperNum );
	}

	if ( thawThroughRespawn ) {
		GibEntity( ent );
		return;
	}

	G_FreezeSetClientFrozenPowerupMarker( ent, qfalse );

	ent->health = client->ps.stats[STAT_MAX_HEALTH];
	client->ps.stats[STAT_HEALTH] = ent->health;
	client->ps.stats[STAT_ARMOR] = g_factoryCvarConfig.startingArmor;
	BG_UpdateArmorTierFromCurrentArmor( &client->ps, g_armorTiered.integer ? qtrue : qfalse );

	protectTime = level.freezeConfig.protectedSpawnTime;
	if ( protectTime > 0 ) {
		client->invulnerabilityTime = level.time + protectTime;
		client->freezeProtectedUntil = client->invulnerabilityTime;
	}
	else {
		client->invulnerabilityTime = 0;
		client->freezeProtectedUntil = 0;
	}
	client->holdableInvulnerabilityTime = 0;

	tent = G_TempEntity( client->ps.origin, EV_THAW_PLAYER );
	tent->s.otherEntityNum = ent->s.number;

	G_Sound( ent, CHAN_AUTO, G_SoundIndex( "sound/items/respawn1.wav" ) );
}

/*
============
G_FreezeThawClient

Unfreezes a player, applies invulnerability, and announces the thaw.
============
*/
void G_FreezeThawClient( gentity_t *ent, qboolean wasAuto, int helperNum ) {
	G_FreezeSetClientFrozenState( ent, qfalse, qfalse, wasAuto, helperNum );
}

/*
============
G_FreezeClientCanHelpThaw

Returns qtrue when helper is a live same-team client inside the thaw envelope.
============
*/
static qboolean G_FreezeClientCanHelpThaw( gentity_t *ent, gentity_t *helper, float thawRadius, float *distSqOut ) {
	vec3_t		delta;
	float		distSq;

	if ( distSqOut ) {
		*distSqOut = 0.0f;
	}

	if ( !ent || !ent->client || !ent->client->freezeFrozen ) {
		return qfalse;
	}
	if ( !helper || !helper->inuse || !helper->client ) {
		return qfalse;
	}
	if ( helper == ent ) {
		return qfalse;
	}
	if ( helper->client->pers.connected != CON_CONNECTED ) {
		return qfalse;
	}
	if ( helper->client->sess.sessionTeam != ent->client->sess.sessionTeam ) {
		return qfalse;
	}
	if ( helper->client->freezeFrozen ) {
		return qfalse;
	}
	if ( helper->client->ps.pm_type != PM_NORMAL ) {
		return qfalse;
	}

	VectorSubtract( helper->r.currentOrigin, ent->r.currentOrigin, delta );
	distSq = VectorLengthSquared( delta );
	if ( distSqOut ) {
		*distSqOut = distSq;
	}
	if ( distSq > thawRadius * thawRadius ) {
		return qfalse;
	}

	if ( !level.freezeConfig.thawThroughSurface ) {
		trace_t		trace;

		trap_Trace( &trace, ent->r.currentOrigin, NULL, NULL, helper->r.currentOrigin, ent->s.number, MASK_SOLID );
		if ( trace.fraction < 1.0f && trace.entityNum != helper->s.number ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
============
G_FreezeCountThawHelpers

Counts nearby allies who can thaw the frozen player and returns a helper.
============
*/
int G_FreezeCountThawHelpers( gentity_t *ent, gentity_t **helperOut ) {
	gentity_t	*helper;
	int			count;
	int			entityList[MAX_GENTITIES];
	int			entityNum;
	int			numListedEntities;
	float		thawRadius;
	vec3_t		maxs;
	vec3_t		mins;
	int			i;

	if ( helperOut ) {
		*helperOut = NULL;
	}

	if ( !ent || !ent->client || !ent->client->freezeFrozen ) {
		return 0;
	}

	thawRadius = (float)level.freezeConfig.thawRadius;
	if ( thawRadius <= 0.0f ) {
		return 0;
	}

	count = 0;
	for ( i = 0; i < 3; i++ ) {
		mins[i] = ent->r.currentOrigin[i] - thawRadius;
		maxs[i] = ent->r.currentOrigin[i] + thawRadius;
	}

	numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );

	for ( i = 0; i < numListedEntities; i++ ) {
		entityNum = entityList[i];
		if ( entityNum < 0 || entityNum >= MAX_GENTITIES ) {
			continue;
		}

		helper = &g_entities[entityNum];
		if ( !G_FreezeClientCanHelpThaw( ent, helper, thawRadius, NULL ) ) {
			continue;
		}

		count++;
		if ( helperOut && !*helperOut ) {
			*helperOut = helper;
		}
	}

	return count;
}

/*
============
G_FreezeFindThawHelperByClientNum

Finds a retained thaw helper by client slot if that helper is still valid.
============
*/
gentity_t *G_FreezeFindThawHelperByClientNum( gentity_t *ent, int helperClientNum ) {
	float	thawRadius;

	if ( helperClientNum < 0 || helperClientNum >= level.maxclients ) {
		return NULL;
	}

	thawRadius = (float)level.freezeConfig.thawRadius;
	if ( thawRadius <= 0.0f ) {
		return NULL;
	}

	if ( !G_FreezeClientCanHelpThaw( ent, &g_entities[helperClientNum], thawRadius, NULL ) ) {
		return NULL;
	}

	return &g_entities[helperClientNum];
}

/*
============
G_FreezeApplyFreezeState

Applies the frozen state to a client after a freeze-tag "death".
============
*/
void G_FreezeApplyFreezeState( gentity_t *self, qboolean environmental ) {
	G_FreezeSetClientFrozenState( self, qtrue, environmental, qfalse, -1 );
}
