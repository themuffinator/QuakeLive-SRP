/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//
// cg_info.c -- display information while data is being loading

#include "cg_local.h"

#define MAX_LOADING_PLAYER_ICONS	16
#define MAX_LOADING_ITEM_ICONS		26
#define LOADING_BANNER_X			-400.0f
#define LOADING_BANNER_WIDTH		1440.0f
#define LOADING_BAR_HEIGHT			64.0f
#define LOADING_INFO_BAND_Y			400.0f
#define LOADING_INFO_BAND_HEIGHT	80.0f
#define LOADING_LOGO_X				0.0f
#define LOADING_LOGO_Y				0.0f
#define LOADING_LOGO_WIDTH			256.0f
#define LOADING_LOGO_HEIGHT			64.0f
#define LOADING_GAMETYPE_BG_X		384.0f
#define LOADING_GAMETYPE_BG_Y		0.0f
#define LOADING_GAMETYPE_BG_WIDTH	256.0f
#define LOADING_GAMETYPE_BG_HEIGHT	64.0f
#define LOADING_STATUS_Y			370.0f
#define LOADING_STATUS_SCALE		0.30f
#define LOADING_AWAITING_GAMESTATE_Y	178.0f
#define LOADING_TITLE_X				10.0f
#define LOADING_TITLE_Y				400.0f
#define LOADING_TITLE_SCALE			0.80f
#define LOADING_AUTHOR_Y			447.0f
#define LOADING_AUTHOR_ALT_Y		462.0f
#define LOADING_META_SCALE			0.25f
#define LOADING_GAMETYPE_Y			10.0f
#define LOADING_GAMETYPE_SCALE		0.80f
#define LOADING_GAMETYPE_RIGHT_X	620.0f
#define LOADING_PROGRESS_COUNT		4
#define LOADING_PROGRESS_X			292.0f
#define LOADING_PROGRESS_Y			380.0f
#define LOADING_PROGRESS_SIZE		8.0f
#define LOADING_PROGRESS_STEP		16.0f

static int			loadingPlayerIconCount;
static int			loadingItemIconCount;
static int			loadingProgressStage;
static qhandle_t	loadingPlayerIcons[MAX_LOADING_PLAYER_ICONS];
static qhandle_t	loadingItemIcons[MAX_LOADING_ITEM_ICONS];
static const vec4_t	loadingBannerColor = { 0.375f, 0.125f, 0.125f, 0.75f };
static const vec4_t	loadingPanelColor = { 0.0f, 0.0f, 0.0f, 0.75f };
static const vec4_t	loadingProgressFilledColor = { 0.375f, 0.125f, 0.125f, 1.0f };
static const vec4_t	loadingProgressEmptyColor = { 0.0f, 0.0f, 0.0f, 0.75f };
static const char	*const loadingGametypeNames[] = {
	"Free For All",
	"Duel",
	"Race",
	"Team Deathmatch",
	"Clan Arena",
	"Capture the Flag",
	"One Flag CTF",
	"Overload",
	"Harvester",
	"Freeze Tag",
	"Domination",
	"Attack and Defend",
	"Red Rover"
};


/*
===================
CG_DrawLoadingBackground
===================
*/
static void CG_DrawLoadingBackground( qhandle_t shader ) {
	float	u1;
	float	v1;
	float	u2;
	float	v2;
	float	targetAspect;
	const float sourceAspect = 16.0f / 9.0f;

	if ( !shader ) {
		return;
	}

	u1 = 0.0f;
	v1 = 0.0f;
	u2 = 1.0f;
	v2 = 1.0f;

	if ( cgs.glconfig.vidWidth > 0 && cgs.glconfig.vidHeight > 0 ) {
		targetAspect = (float)cgs.glconfig.vidWidth / (float)cgs.glconfig.vidHeight;
		if ( targetAspect > sourceAspect ) {
			float visibleHeight;

			visibleHeight = sourceAspect / targetAspect;
			v1 = 0.5f * ( 1.0f - visibleHeight );
			v2 = 1.0f - v1;
		} else if ( targetAspect < sourceAspect ) {
			float visibleWidth;

			visibleWidth = targetAspect / sourceAspect;
			u1 = 0.5f * ( 1.0f - visibleWidth );
			u2 = 1.0f - u1;
		}
	}

	trap_R_SetColor( NULL );
	CG_DrawPicST( 0.0f, 0.0f, SCREEN_WIDTH, SCREEN_HEIGHT, u1, v1, u2, v2, shader );
}


/*
===================
CG_GetLoadingGametype
===================
*/
static const char *CG_GetLoadingGametype( void ) {
	if ( cgs.gametype >= 0 && cgs.gametype < ARRAY_LEN( loadingGametypeNames ) ) {
		return loadingGametypeNames[cgs.gametype];
	}

	return "Unknown Gametype";
}


/*
===================
CG_DrawLoadingText
===================
*/
static void CG_DrawLoadingText( float x, float y, int fontIndex, float scale, const char *text, int style ) {
	if ( !text || !text[0] ) {
		return;
	}

	CG_Text_PaintExt( x, y, scale, colorWhite, text, 0.0f, 0, style, fontIndex );
}


/*
===================
CG_DrawLoadingTextAtTop
===================
*/
static void CG_DrawLoadingTextAtTop( float x, float y, int fontIndex, float scale, const char *text, int style ) {
	int	height;

	if ( !text || !text[0] ) {
		return;
	}

	height = CG_Text_HeightExt( text, scale, 0, fontIndex );
	CG_DrawLoadingText( x, y + height, fontIndex, scale, text, style );
}


/*
===================
CG_SetLoadingScreenText
===================
*/
static void CG_SetLoadingScreenText( const char *text ) {
	Q_strncpyz( cg.infoScreenText, text, sizeof( cg.infoScreenText ) );
	trap_UpdateScreen();
	trap_AdvertisementBridge_UpdateLoadingViewParameters();
	trap_AdvertisementBridge_SetFrameTime( 1000 );
}


/*
===================
CG_DrawLoadingProgress
===================
*/
static void CG_DrawLoadingProgress( void ) {
	int			i;
	float		x;
	const float	*color;

	for ( i = 0; i < LOADING_PROGRESS_COUNT; ++i ) {
		x = LOADING_PROGRESS_X + i * LOADING_PROGRESS_STEP;
		color = ( loadingProgressStage > i ) ? loadingProgressFilledColor : loadingProgressEmptyColor;
		CG_FillRect( x, LOADING_PROGRESS_Y, LOADING_PROGRESS_SIZE, LOADING_PROGRESS_SIZE, color );
	}
}


/*
===================
CG_ResetLoadingState
===================
*/
void CG_ResetLoadingState( void ) {
	loadingPlayerIconCount = 0;
	loadingItemIconCount = 0;
	loadingProgressStage = 0;
	memset( loadingPlayerIcons, 0, sizeof( loadingPlayerIcons ) );
	memset( loadingItemIcons, 0, sizeof( loadingItemIcons ) );
}


/*
=========================
CG_AdvanceLoadingProgress
=========================
*/
void CG_AdvanceLoadingProgress( void ) {
	if ( loadingProgressStage < LOADING_PROGRESS_COUNT ) {
		loadingProgressStage++;
	}
}


/*
======================
CG_LoadingString
======================
*/
void CG_LoadingString( const char *s ) {
	CG_SetLoadingScreenText( s );
}

/*
===================
CG_LoadingItem
===================
*/
void CG_LoadingItem( int itemNum ) {
	gitem_t		*item;

	item = &bg_itemlist[itemNum];
	
	if ( item->icon && loadingItemIconCount < MAX_LOADING_ITEM_ICONS ) {
		loadingItemIcons[loadingItemIconCount++] = trap_R_RegisterShaderNoMip( item->icon );
	}

	CG_SetLoadingScreenText( item->pickup_name );
}

/*
===================
CG_LoadingClient
===================
*/
void CG_LoadingClient( int clientNum ) {
	const char		*info;
	char			*slash;
	char			*skin;
	char			personality[MAX_QPATH];
	char			model[MAX_QPATH];
	char			iconName[MAX_QPATH];

	info = CG_ConfigString( CS_PLAYERS + clientNum );

	if ( loadingPlayerIconCount < MAX_LOADING_PLAYER_ICONS ) {
		Q_strncpyz( model, Info_ValueForKey( info, "model" ), sizeof( model ) );
		slash = Q_strrchr( model, '/' );
		if ( slash ) {
			*slash++ = '\0';
			skin = slash;
		} else {
			skin = "default";
		}

		Com_sprintf( iconName, MAX_QPATH, "models/players/%s/icon_%s.tga", model, skin );
		
		loadingPlayerIcons[loadingPlayerIconCount] = trap_R_RegisterShaderNoMip( iconName );
		if ( !loadingPlayerIcons[loadingPlayerIconCount] ) {
			Com_sprintf( iconName, MAX_QPATH, "models/players/characters/%s/icon_%s.tga", model, skin );
			loadingPlayerIcons[loadingPlayerIconCount] = trap_R_RegisterShaderNoMip( iconName );
		}
		if ( !loadingPlayerIcons[loadingPlayerIconCount] ) {
			Com_sprintf( iconName, MAX_QPATH, "models/players/%s/icon_%s.tga", "sarge", "default" );
			loadingPlayerIcons[loadingPlayerIconCount] = trap_R_RegisterShaderNoMip( iconName );
		}
		if ( loadingPlayerIcons[loadingPlayerIconCount] ) {
			loadingPlayerIconCount++;
		}
	}

	Q_strncpyz( personality, Info_ValueForKey( info, "n" ), sizeof(personality) );
	Q_CleanStr( personality );

	CG_SetLoadingScreenText( personality );
}


/*
====================
CG_DrawInformation

Draw all the status / pacifier stuff during level loading
====================
*/
void CG_DrawInformation( void ) {
	const char	*author;
	const char	*authorAlt;
	const char	*gametype;
	const char	*mapname;
	const char	*status;
	const char	*title;
	const char	*info;
	qhandle_t	levelshot;
	int			width;

	info = CG_ConfigString( CS_SERVERINFO );
	mapname = info ? Info_ValueForKey( info, "mapname" ) : "";
	levelshot = 0;
	if ( mapname && mapname[0] ) {
		levelshot = trap_R_RegisterShaderNoMip( va( "levelshots/%s.tga", mapname ) );
	}
	if ( !levelshot ) {
		levelshot = trap_R_RegisterShaderNoMip( "menu/art/unknownmap" );
	}

	if ( !cg.infoScreenText[0] && cg.snap && ( cg.snap->snapFlags & SNAPFLAG_NOT_ACTIVE ) ) {
		float	statusX;

		CG_SetAdjustFrom640Mode( WIDESCREEN_STRETCH );
		CG_DrawLoadingBackground( cgs.media.menuSmokeShader );
		CG_SetAdjustFrom640Mode( WIDESCREEN_CENTER );
		width = CG_Text_WidthExt( "Awaiting gamestate...", LOADING_STATUS_SCALE, 0, FONT_DEFAULT );
		statusX = SCREEN_WIDTH * 0.5f - width * 0.5f;
		CG_DrawLoadingText( statusX, LOADING_AWAITING_GAMESTATE_Y, FONT_DEFAULT, LOADING_STATUS_SCALE,
			"Awaiting gamestate...", ITEM_TEXTSTYLE_SHADOWEDMORE );
		CG_SetAdjustFrom640Mode( WIDESCREEN_STRETCH );
		return;
	}

	CG_SetAdjustFrom640Mode( WIDESCREEN_STRETCH );
	CG_DrawLoadingBackground( levelshot );
	CG_SetAdjustFrom640Mode( WIDESCREEN_LEFT );
	CG_FillRect( LOADING_BANNER_X, LOADING_LOGO_Y, LOADING_BANNER_WIDTH, LOADING_BAR_HEIGHT, loadingBannerColor );
	CG_FillRect( LOADING_BANNER_X, LOADING_INFO_BAND_Y, LOADING_BANNER_WIDTH, LOADING_INFO_BAND_HEIGHT,
		loadingPanelColor );

	CG_DrawPic( LOADING_LOGO_X, LOADING_LOGO_Y, LOADING_LOGO_WIDTH, LOADING_LOGO_HEIGHT, cgs.media.logoBackground );
	CG_DrawPic( LOADING_LOGO_X, LOADING_LOGO_Y, LOADING_LOGO_WIDTH, LOADING_LOGO_HEIGHT, cgs.media.qlLogo );
	CG_DrawPic( LOADING_GAMETYPE_BG_X, LOADING_GAMETYPE_BG_Y, LOADING_GAMETYPE_BG_WIDTH,
		LOADING_GAMETYPE_BG_HEIGHT, cgs.media.gameTypeBackground );

	title = CG_ConfigString( CS_MESSAGE );
	CG_DrawLoadingTextAtTop( LOADING_TITLE_X, LOADING_TITLE_Y, FONT_DEFAULT, LOADING_TITLE_SCALE, title, 0 );

	author = CG_ConfigString( CS_MAP_AUTHOR );
	authorAlt = CG_ConfigString( CS_MAP_AUTHOR_ALT );
	if ( author && author[0] ) {
		CG_DrawLoadingTextAtTop( LOADING_TITLE_X, LOADING_AUTHOR_Y, FONT_SANS, LOADING_META_SCALE, author, 0 );
		CG_DrawLoadingTextAtTop( LOADING_TITLE_X, LOADING_AUTHOR_ALT_Y, FONT_SANS, LOADING_META_SCALE, authorAlt, 0 );
	}

	CG_SetAdjustFrom640Mode( WIDESCREEN_RIGHT );
	gametype = CG_GetLoadingGametype();
	if ( gametype && gametype[0] ) {
		width = CG_Text_WidthExt( gametype, LOADING_GAMETYPE_SCALE, 0, FONT_DEFAULT );
		CG_DrawLoadingTextAtTop( LOADING_GAMETYPE_RIGHT_X - width, LOADING_GAMETYPE_Y, FONT_DEFAULT, LOADING_GAMETYPE_SCALE,
			gametype, 0 );
	}

	CG_SetAdjustFrom640Mode( WIDESCREEN_CENTER );
	if ( cg.infoScreenText[0] ) {
		float	statusX;

		status = va( "Loading %s", cg.infoScreenText );
		width = CG_Text_WidthExt( status, LOADING_STATUS_SCALE, 0, FONT_SANS );
		statusX = SCREEN_WIDTH * 0.5f - width * 0.5f;
		CG_DrawLoadingText( statusX, LOADING_STATUS_Y, FONT_SANS, LOADING_STATUS_SCALE, status,
			ITEM_TEXTSTYLE_SHADOWEDMORE );
	} else {
		status = "Awaiting Snapshot";
		width = CG_Text_WidthExt( status, LOADING_STATUS_SCALE, 0, FONT_SANS );
		CG_DrawLoadingText( SCREEN_WIDTH * 0.5f - width * 0.5f, LOADING_STATUS_Y, FONT_SANS, LOADING_STATUS_SCALE, status,
			ITEM_TEXTSTYLE_SHADOWEDMORE );
	}
	CG_DrawLoadingProgress();
	CG_SetAdjustFrom640Mode( WIDESCREEN_STRETCH );
}

