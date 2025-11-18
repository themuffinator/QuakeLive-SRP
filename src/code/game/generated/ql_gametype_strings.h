/*
===========================================================================
Auto-generated file. Run tools/hlil/generate_gametype_strings.py after editing
tools/hlil/gametype_strings.json.
===========================================================================
*/
#ifndef QL_GAMETYPE_STRINGS_H_
#define QL_GAMETYPE_STRINGS_H_

#include "../bg_public.h"

typedef struct {
	const char	*objective;
	const char	*thaw;
	const char	*freeze;
	const char	*shoot;
	const char	*summary;
} qlFreezeHudTips_t;

typedef struct {
	gametype_t	gametype;
	const char	*name;
	const char	*text;
	const qlFreezeHudTips_t	*freezeTips;
} qlGametypeTutorialDef_t;

static const char *const ql_gametypeHudHints[GT_MAX_GAME_TYPE] = {
	[GT_FFA] = "This is a Free For All game",
	[GT_TOURNAMENT] = "This is a Duel game",
	[GT_SINGLE_PLAYER] = "This is a Race game",
	[GT_TEAM] = "This is a Team Deathmatch game",
	[GT_CLAN_ARENA] = "This is a Clan Arena game",
	[GT_CTF] = "This is a Capture the Flag game",
	[GT_1FCTF] = "This is a One Flag CTF game",
	[GT_OBELISK] = "This is an Overload game",
	[GT_HARVESTER] = "This is a Harvester game",
	[GT_FREEZE] = "This is a Freeze Tag game",
	[GT_DOMINATION] = "This is a Domination game",
	[GT_ATTACK_DEFEND] = "This is an Attack & Defend game",
	[GT_RED_ROVER] = "This is a Red Rover game",
};

static const qlFreezeHudTips_t ql_freezeHudTips = {
	.objective = "Freeze all enemy team members to score a team point.",
	.thaw = "Stand by frozen teammates for 3 seconds to thaw them.",
	.freeze = "Fragging another player freezes them.",
	.shoot = "Shoot everyone on the other team!",
	.summary = "This is a Freeze Tag game",
};

static const qlGametypeTutorialDef_t ql_gametypeTutorials[] = {
	{
		.gametype = GT_DOMINATION,
		.name = "Domination",
		.text = "Capture domination points to earn points for your team.",
		.freezeTips = NULL
	},
	{
		.gametype = GT_FREEZE,
		.name = "Freeze Tag",
		.text = "Freeze all enemy team members to score a team point.",
		.freezeTips = &ql_freezeHudTips
	},
};

#define QL_GAMETYPE_TUTORIAL_COUNT             	( sizeof( ql_gametypeTutorials ) / sizeof( ql_gametypeTutorials[0] ) )

/*
=============
QL_FindGametypeTutorial

Returns the tutorial entry for the supplied gametype, if present.
=============
*/
static inline const qlGametypeTutorialDef_t *QL_FindGametypeTutorial( gametype_t gametype ) {
	int	index;

	for ( index = 0; index < (int)QL_GAMETYPE_TUTORIAL_COUNT; ++index ) {
		if ( ql_gametypeTutorials[index].gametype == gametype ) {
			return &ql_gametypeTutorials[index];
		}
	}

	return NULL;
}

/*
=============
QL_GametypeHudHint

Returns the HUD hint string for the provided gametype, if available.
=============
*/
static inline const char *QL_GametypeHudHint( gametype_t gametype ) {
	if ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
		return NULL;
	}

	return ql_gametypeHudHints[gametype];
}

#endif /* QL_GAMETYPE_STRINGS_H_ */
