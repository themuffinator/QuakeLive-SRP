#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>

#if defined(_WIN32)
#define QLR_TEST_EXPORT __declspec(dllexport)
#else
#define QLR_TEST_EXPORT
#endif

#define MAX_CLIENTS 64
#define MAX_AVOIDGOALS 256
#define MAX_GOALSTACK 8
#define MAX_AVOIDREACH 1
#define MAX_AVOIDSPOTS 32

#define PRT_MESSAGE 1
#define PRT_WARNING 2
#define PRT_ERROR 3
#define PRT_FATAL 4

#define PRESENCE_NORMAL 2
#define PRESENCE_CROUCH 4

#define MFL_ONGROUND 2
#define MFL_SWIMMING 4
#define MFL_WATERJUMP 16
#define MFL_TELEPORTED 32
#define MFL_GRAPPLEPULL 64
#define MFL_WALK 512

#define TRAVELFLAG_NOTTEAM1 ( 1 << 24 )
#define TRAVELFLAG_NOTTEAM2 ( 2 << 24 )

#define AVOID_MINIMUM_TIME 10
#define AVOID_DEFAULT_TIME 30

typedef float vec3_t[ 3 ];

typedef struct bot_goal_s {
	vec3_t origin;
	int areanum;
	vec3_t mins;
	vec3_t maxs;
	int entitynum;
	int number;
	int flags;
	int iteminfo;
	int qlGoalExtra[ 2 ];
} bot_goal_t;

typedef struct iteminfo_s {
	float respawntime;
} iteminfo_t;

typedef struct itemconfig_s {
	iteminfo_t *iteminfo;
} itemconfig_t;

typedef struct levelitem_s {
	int number;
	int iteminfo;
	struct levelitem_s *next;
} levelitem_t;

typedef struct bot_goalstate_s {
	void *itemweightconfig;
	int *itemweightindex;
	int client;
	int lastreachabilityarea;
	bot_goal_t goalstack[ MAX_GOALSTACK ];
	int goalstacktop;
	int avoidgoals[ MAX_AVOIDGOALS ];
	float avoidgoaltimes[ MAX_AVOIDGOALS ];
} bot_goalstate_t;

typedef struct bot_avoidspot_s {
	vec3_t origin;
	float radius;
	int type;
} bot_avoidspot_t;

typedef struct bot_initmove_s {
	vec3_t origin;
	vec3_t velocity;
	vec3_t viewoffset;
	int entitynum;
	int client;
	float thinktime;
	int presencetype;
	vec3_t viewangles;
	int or_moveflags;
} bot_initmove_t;

typedef struct bot_movestate_s {
	vec3_t origin;
	vec3_t velocity;
	vec3_t viewoffset;
	int entitynum;
	int client;
	float thinktime;
	int presencetype;
	vec3_t viewangles;
	int areanum;
	int lastareanum;
	int lastgoalareanum;
	int lastreachnum;
	vec3_t lastorigin;
	int reachareanum;
	int moveflags;
	int jumpreach;
	float grapplevisible_time;
	float lastgrappledist;
	float reachability_time;
	int avoidreach[ MAX_AVOIDREACH ];
	float avoidreachtimes[ MAX_AVOIDREACH ];
	int avoidreachtries[ MAX_AVOIDREACH ];
	bot_avoidspot_t avoidspots[ MAX_AVOIDSPOTS ];
	int numavoidspots;
} bot_movestate_t;

typedef struct qlr_bot_import_s {
	void ( *Print )( int type, char *fmt, ... );
} qlr_bot_import_t;

typedef struct qlr_aassettings_s {
	float phys_gravity;
	float phys_maxvelocity;
	float rs_maxjumpfallheight;
} qlr_aassettings_t;

static qlr_bot_import_t botimport;
static bot_goalstate_t *botgoalstates[ MAX_CLIENTS + 1 ];
static bot_movestate_t *botmovestates[ MAX_CLIENTS + 1 ];
static itemconfig_t *itemconfig = NULL;
static levelitem_t *levelitems = NULL;
static qlr_aassettings_t qlr_aassettings;
static float qlr_aas_time;
static int qlr_last_print_type;
static char qlr_last_print_message[ 512 ];
static int qlr_bot_notteam_present;
static int qlr_bot_notteam_value;

/*
=============
QLR_ResetPrintCapture

Clears the captured botlib print channel state used by the harness.
=============
*/
static void QLR_ResetPrintCapture( void ) {
	qlr_last_print_type = 0;
	qlr_last_print_message[ 0 ] = '\0';
}

/*
=============
QLR_CapturePrint

Minimal botlib import print hook that records the last emitted retail-style message.
=============
*/
static void QLR_CapturePrint( int type, char *fmt, ... ) {
	va_list argptr;

	qlr_last_print_type = type;
	va_start( argptr, fmt );
	vsnprintf( qlr_last_print_message, sizeof( qlr_last_print_message ), fmt, argptr );
	va_end( argptr );
}

/*
=============
QLR_VecSubtract

Subtracts one vector from another for the copied AAS math helpers.
=============
*/
static void QLR_VecSubtract( const vec3_t a, const vec3_t b, vec3_t out ) {
	out[ 0 ] = a[ 0 ] - b[ 0 ];
	out[ 1 ] = a[ 1 ] - b[ 1 ];
	out[ 2 ] = a[ 2 ] - b[ 2 ];
}

/*
=============
QLR_DotProduct

Returns the dot product for the copied AAS projection helper.
=============
*/
static float QLR_DotProduct( const vec3_t a, const vec3_t b ) {
	return a[ 0 ] * b[ 0 ] + a[ 1 ] * b[ 1 ] + a[ 2 ] * b[ 2 ];
}

/*
=============
QLR_VectorNormalize

Normalizes the copied vector in-place for the AAS projection helper.
=============
*/
static void QLR_VectorNormalize( vec3_t v ) {
	float length;

	length = (float) sqrt( QLR_DotProduct( v, v ) );
	if ( length == 0.0f ) {
		return;
	}

	v[ 0 ] /= length;
	v[ 1 ] /= length;
	v[ 2 ] /= length;
}

/*
=============
AAS_Time

Copied harness view of the botlib AAS clock used by avoid-goal timing helpers.
=============
*/
static float AAS_Time( void ) {
	return qlr_aas_time;
}

/*
=============
AAS_PresenceTypeBoundingBox

Copied retail-shaped presence bounding-box helper from be_aas_sample.c.
=============
*/
static void AAS_PresenceTypeBoundingBox( int presencetype, vec3_t mins, vec3_t maxs ) {
	int index;
	vec3_t boxmins[ 3 ] = { { 0, 0, 0 }, { -15, -15, -24 }, { -15, -15, -24 } };
	vec3_t boxmaxs[ 3 ] = { { 0, 0, 0 }, { 15, 15, 32 }, { 15, 15, 8 } };

	if ( presencetype == PRESENCE_NORMAL ) {
		index = 1;
	}
	else if ( presencetype == PRESENCE_CROUCH ) {
		index = 2;
	}
	else {
		botimport.Print( PRT_FATAL, "AAS_PresenceTypeBoundingBox: unknown presence type\n" );
		index = 2;
	}

	memcpy( mins, boxmins[ index ], sizeof( vec3_t ) );
	memcpy( maxs, boxmaxs[ index ], sizeof( vec3_t ) );
}

/*
=============
AAS_ProjectPointOntoVector

Copied AAS projection helper from be_aas_main.c.
=============
*/
static void AAS_ProjectPointOntoVector( vec3_t point, vec3_t vStart, vec3_t vEnd, vec3_t vProj ) {
	vec3_t pVec;
	vec3_t vec;
	float projectedDistance;

	QLR_VecSubtract( point, vStart, pVec );
	QLR_VecSubtract( vEnd, vStart, vec );
	QLR_VectorNormalize( vec );
	projectedDistance = QLR_DotProduct( pVec, vec );
	vProj[ 0 ] = vStart[ 0 ] + vec[ 0 ] * projectedDistance;
	vProj[ 1 ] = vStart[ 1 ] + vec[ 1 ] * projectedDistance;
	vProj[ 2 ] = vStart[ 2 ] + vec[ 2 ] * projectedDistance;
}

/*
=============
AAS_FallDamageDistance

Copied reachability fall-distance helper from be_aas_reach.c.
=============
*/
static int AAS_FallDamageDistance( void ) {
	float maxzvelocity;
	float gravity;
	float t;

	maxzvelocity = (float) sqrt( 30 * 10000 );
	gravity = qlr_aassettings.phys_gravity;
	t = maxzvelocity / gravity;
	return (int) ( 0.5f * gravity * t * t );
}

/*
=============
AAS_FallDelta

Copied reachability fall-delta helper from be_aas_reach.c.
=============
*/
static float AAS_FallDelta( float distance ) {
	float t;
	float delta;
	float gravity;

	gravity = qlr_aassettings.phys_gravity;
	t = (float) sqrt( fabs( distance ) * 2.0f / gravity );
	delta = t * gravity;
	return delta * delta * 0.0001f;
}

/*
=============
AAS_MaxJumpHeight

Copied jump-height helper from be_aas_reach.c.
=============
*/
static float AAS_MaxJumpHeight( float phys_jumpvel ) {
	float phys_gravity;

	phys_gravity = qlr_aassettings.phys_gravity;
	return 0.5f * phys_gravity * ( phys_jumpvel / phys_gravity ) * ( phys_jumpvel / phys_gravity );
}

/*
=============
AAS_MaxJumpDistance

Copied jump-distance helper from be_aas_reach.c.
=============
*/
static float AAS_MaxJumpDistance( float phys_jumpvel ) {
	float phys_gravity;
	float phys_maxvelocity;
	float t;

	phys_gravity = qlr_aassettings.phys_gravity;
	phys_maxvelocity = qlr_aassettings.phys_maxvelocity;
	t = (float) sqrt( qlr_aassettings.rs_maxjumpfallheight / ( 0.5f * phys_gravity ) );
	return phys_maxvelocity * ( t + phys_jumpvel / phys_gravity );
}

/*
=============
AAS_IntForBSPEpairKey

Stubbed BSP epair lookup that lets the harness drive the team travel-flag helper.
=============
*/
static int AAS_IntForBSPEpairKey( int ent, const char *key, int *value ) {
	(void) ent;
	if ( strcmp( key, "bot_notteam" ) != 0 || !qlr_bot_notteam_present ) {
		return 0;
	}

	*value = qlr_bot_notteam_value;
	return 1;
}

/*
=============
AAS_TravelFlagsForTeam

Copied notteam epair translator from be_aas_reach.c.
=============
*/
static int AAS_TravelFlagsForTeam( int ent ) {
	int notteam;

	if ( !AAS_IntForBSPEpairKey( ent, "bot_notteam", &notteam ) ) {
		return 0;
	}
	if ( notteam == 1 ) {
		return TRAVELFLAG_NOTTEAM1;
	}
	if ( notteam == 2 ) {
		return TRAVELFLAG_NOTTEAM2;
	}
	return 0;
}

/*
=============
BotMoveStateFromHandle

Copied move-state handle validator from be_ai_move.c.
=============
*/
static bot_movestate_t *BotMoveStateFromHandle( int handle ) {
	if ( handle <= 0 || handle > MAX_CLIENTS ) {
		botimport.Print( PRT_FATAL, "move state handle %d out of range\n", handle );
		return NULL;
	}
	if ( !botmovestates[ handle ] ) {
		botimport.Print( PRT_FATAL, "invalid move state %d\n", handle );
		return NULL;
	}
	return botmovestates[ handle ];
}

/*
=============
BotAllocMoveState

Copied move-state allocator from be_ai_move.c.
=============
*/
static int BotAllocMoveState( void ) {
	int i;

	for ( i = 1; i <= MAX_CLIENTS; i++ ) {
		if ( !botmovestates[ i ] ) {
			botmovestates[ i ] = (bot_movestate_t *) calloc( 1, sizeof( bot_movestate_t ) );
			return i;
		}
	}
	return 0;
}

/*
=============
BotFreeMoveState

Copied move-state free helper from be_ai_move.c.
=============
*/
static void BotFreeMoveState( int handle ) {
	if ( handle <= 0 || handle > MAX_CLIENTS ) {
		botimport.Print( PRT_FATAL, "move state handle %d out of range\n", handle );
		return;
	}
	if ( !botmovestates[ handle ] ) {
		botimport.Print( PRT_FATAL, "invalid move state %d\n", handle );
		return;
	}

	free( botmovestates[ handle ] );
	botmovestates[ handle ] = NULL;
}

/*
=============
BotInitMoveState

Copied movement input initializer from be_ai_move.c.
=============
*/
static void BotInitMoveState( int handle, bot_initmove_t *initmove ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return;
	}

	memcpy( ms->origin, initmove->origin, sizeof( vec3_t ) );
	memcpy( ms->velocity, initmove->velocity, sizeof( vec3_t ) );
	memcpy( ms->viewoffset, initmove->viewoffset, sizeof( vec3_t ) );
	ms->entitynum = initmove->entitynum;
	ms->client = initmove->client;
	ms->thinktime = initmove->thinktime;
	ms->presencetype = initmove->presencetype;
	memcpy( ms->viewangles, initmove->viewangles, sizeof( vec3_t ) );

	ms->moveflags &= ~MFL_ONGROUND;
	if ( initmove->or_moveflags & MFL_ONGROUND ) {
		ms->moveflags |= MFL_ONGROUND;
	}
	ms->moveflags &= ~MFL_TELEPORTED;
	if ( initmove->or_moveflags & MFL_TELEPORTED ) {
		ms->moveflags |= MFL_TELEPORTED;
	}
	ms->moveflags &= ~MFL_WATERJUMP;
	if ( initmove->or_moveflags & MFL_WATERJUMP ) {
		ms->moveflags |= MFL_WATERJUMP;
	}
	ms->moveflags &= ~MFL_WALK;
	if ( initmove->or_moveflags & MFL_WALK ) {
		ms->moveflags |= MFL_WALK;
	}
	ms->moveflags &= ~MFL_GRAPPLEPULL;
	if ( initmove->or_moveflags & MFL_GRAPPLEPULL ) {
		ms->moveflags |= MFL_GRAPPLEPULL;
	}
}

/*
=============
BotResetAvoidReach

Copied avoid-reach reset helper from be_ai_move.c.
=============
*/
static void BotResetAvoidReach( int movestate ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( movestate );
	if ( !ms ) {
		return;
	}

	memset( ms->avoidreach, 0, MAX_AVOIDREACH * sizeof( int ) );
	memset( ms->avoidreachtimes, 0, MAX_AVOIDREACH * sizeof( float ) );
	memset( ms->avoidreachtries, 0, MAX_AVOIDREACH * sizeof( int ) );
}

/*
=============
BotResetLastAvoidReach

Retail-shaped reset-last helper from be_ai_move.c, using a safe read for the post-loop +0x80 gate.
=============
*/
static void BotResetLastAvoidReach( int movestate ) {
	int i;
	int latest;
	int gate;
	float latesttime;
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( movestate );
	if ( !ms ) {
		return;
	}

	latesttime = 0;
	latest = 0;
	for ( i = 0; i < MAX_AVOIDREACH; i++ ) {
		if ( ms->avoidreachtimes[ i ] > latesttime ) {
			latesttime = ms->avoidreachtimes[ i ];
			latest = i;
		}
	}
	if ( latesttime ) {
		ms->avoidreachtimes[ latest ] = 0;
		memcpy( &gate, ( (char *) ms ) + offsetof( bot_movestate_t, avoidspots ), sizeof( gate ) );
		if ( gate > 0 ) {
			ms->avoidreachtries[ latest ]--;
		}
	}
}

/*
=============
BotResetMoveState

Copied full move-state reset helper from be_ai_move.c.
=============
*/
static void BotResetMoveState( int movestate ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( movestate );
	if ( !ms ) {
		return;
	}

	memset( ms, 0, sizeof( bot_movestate_t ) );
}

/*
=============
BotGoalStateFromHandle

Copied goal-state handle validator from be_ai_goal.c.
=============
*/
static bot_goalstate_t *BotGoalStateFromHandle( int handle ) {
	if ( handle <= 0 || handle > MAX_CLIENTS ) {
		botimport.Print( PRT_FATAL, "goal state handle %d out of range\n", handle );
		return NULL;
	}
	if ( !botgoalstates[ handle ] ) {
		botimport.Print( PRT_FATAL, "invalid goal state %d\n", handle );
		return NULL;
	}
	return botgoalstates[ handle ];
}

/*
=============
BotResetAvoidGoals

Copied avoid-goal reset helper from be_ai_goal.c.
=============
*/
static void BotResetAvoidGoals( int goalstate ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}

	memset( gs->avoidgoals, 0, MAX_AVOIDGOALS * sizeof( int ) );
	memset( gs->avoidgoaltimes, 0, MAX_AVOIDGOALS * sizeof( float ) );
}

/*
=============
BotAddToAvoidGoals

Copied avoid-goal insert/update helper from be_ai_goal.c.
=============
*/
static void BotAddToAvoidGoals( bot_goalstate_t *gs, int number, float avoidtime ) {
	int i;

	for ( i = 0; i < MAX_AVOIDGOALS; i++ ) {
		if ( gs->avoidgoals[ i ] == number ) {
			gs->avoidgoals[ i ] = number;
			gs->avoidgoaltimes[ i ] = AAS_Time() + avoidtime;
			return;
		}
	}

	for ( i = 0; i < MAX_AVOIDGOALS; i++ ) {
		if ( gs->avoidgoaltimes[ i ] < AAS_Time() ) {
			gs->avoidgoals[ i ] = number;
			gs->avoidgoaltimes[ i ] = AAS_Time() + avoidtime;
			return;
		}
	}
}

/*
=============
BotRemoveFromAvoidGoals

Copied avoid-goal removal helper from be_ai_goal.c.
=============
*/
static void BotRemoveFromAvoidGoals( int goalstate, int number ) {
	int i;
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}

	for ( i = 0; i < MAX_AVOIDGOALS; i++ ) {
		if ( gs->avoidgoals[ i ] == number && gs->avoidgoaltimes[ i ] >= AAS_Time() ) {
			gs->avoidgoaltimes[ i ] = 0;
			return;
		}
	}
}

/*
=============
BotAvoidGoalTime

Copied avoid-goal timer query from be_ai_goal.c.
=============
*/
static float BotAvoidGoalTime( int goalstate, int number ) {
	int i;
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return 0;
	}

	for ( i = 0; i < MAX_AVOIDGOALS; i++ ) {
		if ( gs->avoidgoals[ i ] == number && gs->avoidgoaltimes[ i ] >= AAS_Time() ) {
			return gs->avoidgoaltimes[ i ] - AAS_Time();
		}
	}
	return 0;
}

/*
=============
BotSetAvoidGoalTime

Copied avoid-goal setter from be_ai_goal.c for deterministic positive-time probes.
=============
*/
static void BotSetAvoidGoalTime( int goalstate, int number, float avoidtime ) {
	bot_goalstate_t *gs;
	levelitem_t *li;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}

	if ( avoidtime < 0 ) {
		if ( !itemconfig ) {
			return;
		}
		for ( li = levelitems; li; li = li->next ) {
			if ( li->number == number ) {
				avoidtime = itemconfig->iteminfo[ li->iteminfo ].respawntime;
				if ( !avoidtime ) {
					avoidtime = AVOID_DEFAULT_TIME;
				}
				if ( avoidtime < AVOID_MINIMUM_TIME ) {
					avoidtime = AVOID_MINIMUM_TIME;
				}
				BotAddToAvoidGoals( gs, number, avoidtime );
				return;
			}
		}
		return;
	}

	BotAddToAvoidGoals( gs, number, avoidtime );
}

/*
=============
BotDumpGoalStack

No-op harness stub for the overflow path in BotPushGoal.
=============
*/
static void BotDumpGoalStack( int goalstate ) {
	(void) goalstate;
}

/*
=============
BotPushGoal

Copied goal-stack push helper from be_ai_goal.c.
=============
*/
static void BotPushGoal( int goalstate, bot_goal_t *goal ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}
	if ( gs->goalstacktop >= MAX_GOALSTACK - 1 ) {
		botimport.Print( PRT_ERROR, "goal heap overflow\n" );
		BotDumpGoalStack( goalstate );
		return;
	}

	gs->goalstacktop++;
	memcpy( &gs->goalstack[ gs->goalstacktop ], goal, sizeof( bot_goal_t ) );
}

/*
=============
BotPopGoal

Copied goal-stack pop helper from be_ai_goal.c.
=============
*/
static void BotPopGoal( int goalstate ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}
	if ( gs->goalstacktop > 0 ) {
		gs->goalstacktop--;
	}
}

/*
=============
BotEmptyGoalStack

Copied goal-stack clear helper from be_ai_goal.c.
=============
*/
static void BotEmptyGoalStack( int goalstate ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}
	gs->goalstacktop = 0;
}

/*
=============
BotGetTopGoal

Copied top-goal query helper from be_ai_goal.c.
=============
*/
static int BotGetTopGoal( int goalstate, bot_goal_t *goal ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return 0;
	}
	if ( !gs->goalstacktop ) {
		return 0;
	}

	memcpy( goal, &gs->goalstack[ gs->goalstacktop ], sizeof( bot_goal_t ) );
	return 1;
}

/*
=============
BotGetSecondGoal

Copied second-goal query helper from be_ai_goal.c.
=============
*/
static int BotGetSecondGoal( int goalstate, bot_goal_t *goal ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return 0;
	}
	if ( gs->goalstacktop <= 1 ) {
		return 0;
	}

	memcpy( goal, &gs->goalstack[ gs->goalstacktop - 1 ], sizeof( bot_goal_t ) );
	return 1;
}

/*
=============
BotResetGoalState

Copied goal-state reset helper from be_ai_goal.c.
=============
*/
static void BotResetGoalState( int goalstate ) {
	bot_goalstate_t *gs;

	gs = BotGoalStateFromHandle( goalstate );
	if ( !gs ) {
		return;
	}

	memset( gs->goalstack, 0, MAX_GOALSTACK * sizeof( bot_goal_t ) );
	gs->goalstacktop = 0;
	BotResetAvoidGoals( goalstate );
}

/*
=============
BotFreeItemWeights

Minimal harness stub matching the cleanup call shape used by BotFreeGoalState.
=============
*/
static void BotFreeItemWeights( int goalstate ) {
	bot_goalstate_t *gs;

	if ( goalstate <= 0 || goalstate > MAX_CLIENTS ) {
		return;
	}

	gs = botgoalstates[ goalstate ];
	if ( !gs ) {
		return;
	}

	gs->itemweightconfig = NULL;
	gs->itemweightindex = NULL;
}

/*
=============
BotAllocGoalState

Copied goal-state allocator from be_ai_goal.c.
=============
*/
static int BotAllocGoalState( int client ) {
	int i;

	for ( i = 1; i <= MAX_CLIENTS; i++ ) {
		if ( !botgoalstates[ i ] ) {
			botgoalstates[ i ] = (bot_goalstate_t *) calloc( 1, sizeof( bot_goalstate_t ) );
			if ( !botgoalstates[ i ] ) {
				return 0;
			}

			botgoalstates[ i ]->client = client;
			return i;
		}
	}
	return 0;
}

/*
=============
BotFreeGoalState

Copied goal-state free helper from be_ai_goal.c.
=============
*/
static void BotFreeGoalState( int handle ) {
	if ( handle <= 0 || handle > MAX_CLIENTS ) {
		botimport.Print( PRT_FATAL, "goal state handle %d out of range\n", handle );
		return;
	}
	if ( !botgoalstates[ handle ] ) {
		botimport.Print( PRT_FATAL, "invalid goal state handle %d\n", handle );
		return;
	}

	BotFreeItemWeights( handle );
	free( botgoalstates[ handle ] );
	botgoalstates[ handle ] = NULL;
}

/*
=============
QLR_BotlibResetState

Resets the harness state so each Python test starts from a clean botlib snapshot.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibResetState( void ) {
	int i;

	for ( i = 1; i <= MAX_CLIENTS; i++ ) {
		if ( botgoalstates[ i ] ) {
			free( botgoalstates[ i ] );
			botgoalstates[ i ] = NULL;
		}
		if ( botmovestates[ i ] ) {
			free( botmovestates[ i ] );
			botmovestates[ i ] = NULL;
		}
	}

	memset( &qlr_aassettings, 0, sizeof( qlr_aassettings ) );
	qlr_aas_time = 0.0f;
	qlr_bot_notteam_present = 0;
	qlr_bot_notteam_value = 0;
	QLR_ResetPrintCapture();
	botimport.Print = QLR_CapturePrint;
}

/*
=============
QLR_BotlibSetTime

Sets the copied AAS clock used by avoid-goal timing probes.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetTime( float time ) {
	qlr_aas_time = time;
}

/*
=============
QLR_BotlibSetReachabilitySettings

Seeds the copied reachability physics globals used by the formula helpers.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetReachabilitySettings( float gravity, float maxvelocity, float maxjumpfallheight ) {
	qlr_aassettings.phys_gravity = gravity;
	qlr_aassettings.phys_maxvelocity = maxvelocity;
	qlr_aassettings.rs_maxjumpfallheight = maxjumpfallheight;
}

/*
=============
QLR_BotlibSetTravelFlagsForTeamValue

Configures the stubbed bot_notteam epair value used by AAS_TravelFlagsForTeam.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetTravelFlagsForTeamValue( int present, int value ) {
	qlr_bot_notteam_present = present;
	qlr_bot_notteam_value = value;
}

/*
=============
QLR_BotlibPresenceTypeBoundingBoxFromArrays

Array-friendly presence-bounds wrapper for ctypes callers.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibPresenceTypeBoundingBoxFromArrays( int presencetype, float *mins, float *maxs ) {
	vec3_t localMins;
	vec3_t localMaxs;

	AAS_PresenceTypeBoundingBox( presencetype, localMins, localMaxs );
	memcpy( mins, localMins, sizeof( vec3_t ) );
	memcpy( maxs, localMaxs, sizeof( vec3_t ) );
}

/*
=============
QLR_BotlibProjectPointOntoVector

Wrapper used by the Python harness to exercise the copied vector projection helper.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibProjectPointOntoVector( const float *point, const float *start, const float *end, float *projected ) {
	vec3_t localPoint;
	vec3_t localStart;
	vec3_t localEnd;
	vec3_t localProjected;

	memcpy( localPoint, point, sizeof( vec3_t ) );
	memcpy( localStart, start, sizeof( vec3_t ) );
	memcpy( localEnd, end, sizeof( vec3_t ) );
	AAS_ProjectPointOntoVector( localPoint, localStart, localEnd, localProjected );
	memcpy( projected, localProjected, sizeof( vec3_t ) );
}

/*
=============
QLR_BotlibFallDamageDistance

Wrapper used by the Python harness to exercise the copied fall-distance helper.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibFallDamageDistance( void ) {
	return AAS_FallDamageDistance();
}

/*
=============
QLR_BotlibFallDelta

Wrapper used by the Python harness to exercise the copied fall-delta helper.
=============
*/
QLR_TEST_EXPORT float QLR_BotlibFallDelta( float distance ) {
	return AAS_FallDelta( distance );
}

/*
=============
QLR_BotlibMaxJumpHeight

Wrapper used by the Python harness to exercise the copied jump-height helper.
=============
*/
QLR_TEST_EXPORT float QLR_BotlibMaxJumpHeight( float jumpvel ) {
	return AAS_MaxJumpHeight( jumpvel );
}

/*
=============
QLR_BotlibMaxJumpDistance

Wrapper used by the Python harness to exercise the copied jump-distance helper.
=============
*/
QLR_TEST_EXPORT float QLR_BotlibMaxJumpDistance( float jumpvel ) {
	return AAS_MaxJumpDistance( jumpvel );
}

/*
=============
QLR_BotlibTravelFlagsForTeam

Wrapper used by the Python harness to exercise the copied bot_notteam flag translator.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibTravelFlagsForTeam( int ent ) {
	return AAS_TravelFlagsForTeam( ent );
}

/*
=============
QLR_BotlibAllocMoveState

Wrapper used by the Python harness to allocate a copied move state.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibAllocMoveState( void ) {
	return BotAllocMoveState();
}

/*
=============
QLR_BotlibFreeMoveState

Wrapper used by the Python harness to free a copied move state.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibFreeMoveState( int handle ) {
	BotFreeMoveState( handle );
}

/*
=============
QLR_BotlibMoveStateExists

Returns whether the copied move-state handle is currently allocated.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibMoveStateExists( int handle ) {
	if ( handle <= 0 || handle > MAX_CLIENTS ) {
		return 0;
	}
	return botmovestates[ handle ] != NULL;
}

/*
=============
QLR_BotlibInitMoveState

Wrapper used by the Python harness to initialize copied move-state input.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibInitMoveState( int handle, bot_initmove_t *initmove ) {
	BotInitMoveState( handle, initmove );
}

/*
=============
QLR_BotlibSetMoveFlags

Seeds move flags directly for masking and reset probes.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetMoveFlags( int handle, int moveflags ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return;
	}
	ms->moveflags = moveflags;
}

/*
=============
QLR_BotlibMoveFlags

Returns the copied move-state flags.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibMoveFlags( int handle ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return 0;
	}
	return ms->moveflags;
}

/*
=============
QLR_BotlibSeedAvoidReach

Seeds the first avoid-reach slot for reset probes.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSeedAvoidReach( int handle, int reach, float time, int tries ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return;
	}
	ms->avoidreach[ 0 ] = reach;
	ms->avoidreachtimes[ 0 ] = time;
	ms->avoidreachtries[ 0 ] = tries;
}

/*
=============
QLR_BotlibSetAvoidReachGateWord

Seeds the retail +0x80 gate word that follows avoidreachtries when MAX_AVOIDREACH is one.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetAvoidReachGateWord( int handle, int gate ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return;
	}
	memcpy( ( (char *) ms ) + offsetof( bot_movestate_t, avoidspots ), &gate, sizeof( gate ) );
}

/*
=============
QLR_BotlibAvoidReach

Returns the first copied avoid-reach id.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibAvoidReach( int handle ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return 0;
	}
	return ms->avoidreach[ 0 ];
}

/*
=============
QLR_BotlibAvoidReachTime

Returns the first copied avoid-reach time.
=============
*/
QLR_TEST_EXPORT float QLR_BotlibAvoidReachTime( int handle ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return 0.0f;
	}
	return ms->avoidreachtimes[ 0 ];
}

/*
=============
QLR_BotlibAvoidReachTries

Returns the first copied avoid-reach try counter.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibAvoidReachTries( int handle ) {
	bot_movestate_t *ms;

	ms = BotMoveStateFromHandle( handle );
	if ( !ms ) {
		return 0;
	}
	return ms->avoidreachtries[ 0 ];
}

/*
=============
QLR_BotlibResetAvoidReach

Wrapper used by the Python harness to reset copied avoid-reach arrays.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibResetAvoidReach( int handle ) {
	BotResetAvoidReach( handle );
}

/*
=============
QLR_BotlibResetLastAvoidReach

Wrapper used by the Python harness to reset the latest copied avoid-reach slot.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibResetLastAvoidReach( int handle ) {
	BotResetLastAvoidReach( handle );
}

/*
=============
QLR_BotlibResetMoveState

Wrapper used by the Python harness to clear a copied move state.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibResetMoveState( int handle ) {
	BotResetMoveState( handle );
}

/*
=============
QLR_BotlibAllocGoalState

Wrapper used by the Python harness to allocate a copied goal state.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibAllocGoalState( int client ) {
	return BotAllocGoalState( client );
}

/*
=============
QLR_BotlibFreeGoalState

Wrapper used by the Python harness to free a copied goal state.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibFreeGoalState( int handle ) {
	BotFreeGoalState( handle );
}

/*
=============
QLR_BotlibResetGoalState

Wrapper used by the Python harness to reset a copied goal state.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibResetGoalState( int handle ) {
	BotResetGoalState( handle );
}

/*
=============
QLR_BotlibPushGoal

Wrapper used by the Python harness to push a copied goal onto the stack.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibPushGoal( int handle, bot_goal_t *goal ) {
	BotPushGoal( handle, goal );
}

/*
=============
QLR_BotlibPopGoal

Wrapper used by the Python harness to pop a copied goal from the stack.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibPopGoal( int handle ) {
	BotPopGoal( handle );
}

/*
=============
QLR_BotlibEmptyGoalStack

Wrapper used by the Python harness to clear the copied goal stack.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibEmptyGoalStack( int handle ) {
	BotEmptyGoalStack( handle );
}

/*
=============
QLR_BotlibGetTopGoal

Wrapper used by the Python harness to read the copied top goal.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibGetTopGoal( int handle, bot_goal_t *goal ) {
	return BotGetTopGoal( handle, goal );
}

/*
=============
QLR_BotlibGetSecondGoal

Wrapper used by the Python harness to read the copied second goal.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibGetSecondGoal( int handle, bot_goal_t *goal ) {
	return BotGetSecondGoal( handle, goal );
}

/*
=============
QLR_BotlibSetAvoidGoalTime

Wrapper used by the Python harness to drive copied avoid-goal timing logic.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibSetAvoidGoalTime( int handle, int number, float avoidtime ) {
	BotSetAvoidGoalTime( handle, number, avoidtime );
}

/*
=============
QLR_BotlibAvoidGoalTime

Wrapper used by the Python harness to query copied avoid-goal timing logic.
=============
*/
QLR_TEST_EXPORT float QLR_BotlibAvoidGoalTime( int handle, int number ) {
	return BotAvoidGoalTime( handle, number );
}

/*
=============
QLR_BotlibRemoveFromAvoidGoals

Wrapper used by the Python harness to clear a copied avoid-goal entry.
=============
*/
QLR_TEST_EXPORT void QLR_BotlibRemoveFromAvoidGoals( int handle, int number ) {
	BotRemoveFromAvoidGoals( handle, number );
}

/*
=============
QLR_BotlibLastPrintType

Returns the last captured print severity for invalid-handle regression checks.
=============
*/
QLR_TEST_EXPORT int QLR_BotlibLastPrintType( void ) {
	return qlr_last_print_type;
}

/*
=============
QLR_BotlibLastPrintMessage

Returns the last captured print text for invalid-handle regression checks.
=============
*/
QLR_TEST_EXPORT const char *QLR_BotlibLastPrintMessage( void ) {
	return qlr_last_print_message;
}
