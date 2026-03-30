/*
=============
src-re/ui/include/ui_local.h

Quake Live UI Module — reverse-engineered local declarations.

This header is part of the src-re/ui reconstruction workspace and pulls
together the function prototypes, key types, and syscall-table entry offsets
that were recovered from:

  references/symbol-maps/ui.json
  references/reverse-engineering/ghidra/uix86/
  references/hlil/quakelive/uix86.all/

It is separate from the read-only src/code/ui/ui_local.h.  Include that
header for the open-source Quake III Arena baseline; include this one for
Quake Live-specific reconstruction additions.

Binary reference: assets/quakelive/baseq3/uix86.dll
MD5: 64321E7C6357A59063AE8900E2A20732
=============
*/

#ifndef QLR_UI_LOCAL_H
#define QLR_UI_LOCAL_H

#include "../../../src/code/game/q_shared.h"
#include "../../../src/code/ui/ui_public.h"

/* -----------------------------------------------------------------------
   Retail syscall-table layout (DAT_106b40a8 in Ghidra).
   Indices are 32-bit-pointer slots; slot i == table_base + i*4.
   Recovered from decompile_annotated.c call patterns.
   ----------------------------------------------------------------------- */

#define QL_UITRAP_CVAR_REGISTER         0x00	/* (*(code *)DAT_106b40a8[0x00])  */
#define QL_UITRAP_CVAR_UPDATE           0x01
#define QL_UITRAP_CVAR_SET              0x02	/* slot 2  = UI_CVAR_SET          */
#define QL_UITRAP_CVAR_VARIABLEVALUE    0x07
#define QL_UITRAP_CVAR_SETVALUE         0x08
#define QL_UITRAP_CVAR_INFOSTRINGBUFFER 0x0A
#define QL_UITRAP_ARGC                  0x0B
#define QL_UITRAP_ARGV                  0x0C
#define QL_UITRAP_CMD_EXECUTETEXT       0x0D
#define QL_UITRAP_FS_FOPENFILE          0x0F
#define QL_UITRAP_FS_READ               0x10
#define QL_UITRAP_FS_WRITE              0x11
#define QL_UITRAP_FS_FCLOSEFILE         0x12
#define QL_UITRAP_FS_GETFILELIST        0x13
#define QL_UITRAP_R_REGISTERSHADERNOMIP 0x14
#define QL_UITRAP_R_DRAWSTRETCHPIC      0x18
#define QL_UITRAP_R_MODELBOUNDS         0x1C
#define QL_UITRAP_R_REGISTERMODEL       0x1E
#define QL_UITRAP_R_REGISTERFONT        0x20
#define QL_UITRAP_R_SETCOLOR            0x22
#define QL_UITRAP_UPDATESCREEN          0x23
#define QL_UITRAP_CM_LERPTAG            0x24
#define QL_UITRAP_S_REGISTERSOUND       0x27
#define QL_UITRAP_S_STARTLOCALSOUND     0x28
#define QL_UITRAP_KEY_KEYNUMTOSTRINGBUF 0x29
#define QL_UITRAP_KEY_GETBINDINGBUF     0x2A
#define QL_UITRAP_KEY_SETBINDING        0x2B
#define QL_UITRAP_KEY_ISDOWN            0x2C
#define QL_UITRAP_KEY_GETOVERSTRIKEMODE 0x2D
#define QL_UITRAP_KEY_SETOVERSTRIKEMODE 0x2E
#define QL_UITRAP_KEY_CLEARSTATES       0x2F
#define QL_UITRAP_KEY_GETCATCHER        0x30
#define QL_UITRAP_KEY_SETCATCHER        0x31
#define QL_UITRAP_GETCLIPBOARDDATA      0x32
#define QL_UITRAP_GETGLCONFIG           0x33
#define QL_UITRAP_GETCLIENTSTATE        0x34
#define QL_UITRAP_GETCONFIGSTRING       0x35
#define QL_UITRAP_LAN_GETPINGINFO       0x36
#define QL_UITRAP_LAN_GETPING           0x37
#define QL_UITRAP_LAN_MARKSERVERVISIBLE 0x38
#define QL_UITRAP_LAN_UPDATEVISIBLEPINGS 0x39
#define QL_UITRAP_LAN_RESETPINGS        0x3A
#define QL_UITRAP_LAN_LOADCACHEDSERVERS 0x3B
#define QL_UITRAP_LAN_SAVECACHEDSERVERS 0x3C
#define QL_UITRAP_LAN_ADDSERVER         0x3D
#define QL_UITRAP_LAN_REMOVESERVER      0x3E
#define QL_UITRAP_SNAPSHOTINFO          0x3F
#define QL_UITRAP_SETPBCLSTATUS         0x40
#define QL_UITRAP_GETSAVEDGAMES         0x41
#define QL_UITRAP_LOADSAVEGAME          0x42
#define QL_UITRAP_AUTOSAVE              0x43
#define QL_UITRAP_LAN_GETSERVERADDRESS  0x52
#define QL_UITRAP_GETMAPNAME            0x53
#define QL_UITRAP_GETSKILLRATING        0x54
#define QL_UITRAP_GETMATCHSTARTTIME     0x55

/* -----------------------------------------------------------------------
   Retail display-context scale state (recovered from UI_RefreshDisplayContextScale).
   ----------------------------------------------------------------------- */

typedef struct {
	float	xscale;		/* pixel-width  / 640.0 */
	float	yscale;		/* pixel-height / 480.0 */
	float	xbias;		/* horizontal letter-box offset */
	float	ybias;		/* vertical letter-box offset */
	int		width;		/* current renderer width  (glconfig.vidWidth)  */
	int		height;		/* current renderer height (glconfig.vidHeight) */
} qlr_ui_scale_t;

/* -----------------------------------------------------------------------
   Key entry-point prototypes — exported from uix86.dll and recovered from
   references/reverse-engineering/ghidra/uix86/decompile_annotated.c.
   ----------------------------------------------------------------------- */

/* Module bootstrap — Ordinal 1 / dllEntry @ 0x10003970 */
void	dllEntry( void *syscallTable );

/* Secondary entry point @ 0x10020d66 (CRT init, not a UI API function) */
/* void	entry( void ); */

/* -----------------------------------------------------------------------
   Native UI API dispatch — _UI_* functions are the engine-facing entry
   points called via the DLL export table set up in dllEntry.
   ----------------------------------------------------------------------- */

void	_UI_Init( int singlePlayerMenu );
void	_UI_Shutdown( void );
void	_UI_KeyEvent( int key, qboolean down );
void	_UI_MouseEvent( int dx, int dy );
void	_UI_Refresh( int realtime );
qboolean _UI_IsFullscreen( void );
void	_UI_SetActiveMenu( uiMenuCommand_t menu );
qboolean _UI_ConsoleCommand( int realtime );
void	UI_DrawConnectScreen( qboolean overlay );

/* -----------------------------------------------------------------------
   Display-context refresh helpers.
   ----------------------------------------------------------------------- */

void	UI_RefreshDisplayContext( void );
void	UI_RefreshDisplayContextScale( void );
void	UI_RegisterCvars( void );

/* -----------------------------------------------------------------------
   Gametype / callvote helpers (recovered from UI_GetCallvoteGametypeToken).
   ----------------------------------------------------------------------- */

const char	*UI_GetCallvoteGametypeToken( int gametype );
int	UI_StartingWeaponIndexFromToken( void );

/* -----------------------------------------------------------------------
   Math utilities — thin wrappers that mirror the cgame/game copies.
   ----------------------------------------------------------------------- */

void	AnglesToAxis( const vec3_t angles, vec3_t axis[3] );
void	AngleSubtract( float a1, float a2, float *out );
void	MatrixMultiply( float in1[3][3], float in2[3][3], float out[3][3] );
void	AngleVectors( const vec3_t angles, vec3_t forward, vec3_t right, vec3_t up );

/* -----------------------------------------------------------------------
   String / parse utilities.
   ----------------------------------------------------------------------- */

int	COM_Compress( char *data_p );
char	*COM_ParseExt( char **data_p, qboolean allowLineBreaks );
qboolean String_IsNumeric( const char *s );
int	Q_stricmpn( const char *s1, const char *s2, int n );
int	Q_stricmp( const char *s1, const char *s2 );
void	Q_strncpyz( char *dest, const char *src, int destsize );
void	Q_CleanStr( char *string );
void	Com_sprintf( char *dest, int size, const char *fmt, ... );
char	*va( const char *format, ... );

#endif /* QLR_UI_LOCAL_H */
