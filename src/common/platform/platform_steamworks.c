#include "platform_steamworks.h"

#if QL_BUILD_STEAMWORKS

#include <limits.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#define QL_STEAMWORKS_LIB_PRIMARY "steam_api64.dll"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api.dll"
#define QL_STEAMWORKS_SYM( name ) GetProcAddress( (HMODULE)state.library, name )
#define QL_STEAMWORKS_CLOSE() FreeLibrary( (HMODULE)state.library )
#define QL_STEAMWORKS_OPEN( name ) LoadLibraryA( name )
#else
#include <dlfcn.h>
#define QL_STEAMWORKS_LIB_PRIMARY "libsteam_api.so"
#define QL_STEAMWORKS_LIB_SECONDARY "steam_api64.so"
#define QL_STEAMWORKS_SYM( name ) dlsym( state.library, name )
#define QL_STEAMWORKS_CLOSE() dlclose( state.library )
#define QL_STEAMWORKS_OPEN( name ) dlopen( name, RTLD_LAZY | RTLD_LOCAL )
#endif

typedef qboolean (*QL_SteamAPI_InitFn)( void );
typedef void (*QL_SteamAPI_ShutdownFn)( void );
typedef void (*QL_SteamAPI_RunCallbacksFn)( void );
typedef void *(*QL_SteamAPI_InterfaceFn)( void );
typedef qboolean (*QL_SteamAPI_SteamGameServerInitFn)( uint32_t, uint16_t, uint16_t, uint16_t, int, const char * );
typedef void *(*QL_SteamAPI_SteamGameServerFn)( void );
typedef void (*QL_SteamAPI_SteamGameServerShutdownFn)( void );
typedef void (*QL_SteamAPI_SteamGameServerRunCallbacksFn)( void );
typedef void *(*QL_SteamAPI_SteamGameServerNetworkingFn)( void );
typedef HAuthTicket (*QL_SteamAPI_GetAuthSessionTicketFn)( void *, void *, int, uint32_t * );
typedef EBeginAuthSessionResult (*QL_SteamAPI_BeginAuthSessionFn)( void *, const void *, int, CSteamID );
typedef void (*QL_SteamAPI_CancelAuthTicketFn)( void *, HAuthTicket );
typedef void (*QL_SteamAPI_EndAuthSessionFn)( void *, CSteamID );
typedef CSteamID (*QL_SteamAPI_GetSteamIDFn)( void * );
typedef qboolean (*QL_SteamNetworking_SendP2PPacketFn)( void *, CSteamID, const void *, uint32_t, int, int );
typedef qboolean (*QL_SteamNetworking_IsP2PPacketAvailableFn)( void *, uint32_t *, int );
typedef qboolean (*QL_SteamNetworking_ReadP2PPacketFn)( void *, void *, uint32_t, uint32_t *, CSteamID *, int );
typedef uint32_t (*QL_SteamGameServer_GetPublicIPFn)( void * );
typedef int (*QL_SteamGameServer_GetNextOutgoingPacketFn)( void *, void *, int, uint32_t *, uint16_t * );
typedef void (*QL_SteamGameServer_EnableHeartbeatsFn)( void *, int );
typedef void (*QL_SteamGameServer_SetDedicatedFn)( void *, int );
typedef void (*QL_SteamGameServer_LogOnFn)( void *, const char * );
typedef void (*QL_SteamGameServer_LogOnAnonymousFn)( void * );
typedef void (*QL_SteamGameServer_SetStringFn)( void *, const char * );
typedef void (*QL_SteamGameServer_SetIntFn)( void *, int );
typedef void (*QL_SteamGameServer_SetKeyValueFn)( void *, const char *, const char * );
typedef int (*QL_SteamGameServer_UpdateUserDataFn)( void *, uint32_t, uint32_t, const char *, uint32_t );

typedef struct {
	void *library;
	qboolean initialised;
	QL_SteamAPI_InitFn SteamAPI_Init;
	QL_SteamAPI_ShutdownFn SteamAPI_Shutdown;
	QL_SteamAPI_RunCallbacksFn SteamAPI_RunCallbacks;
	QL_SteamAPI_InterfaceFn SteamUser;
	QL_SteamAPI_InterfaceFn SteamFriends;
	QL_SteamAPI_InterfaceFn SteamUtils;
	QL_SteamAPI_InterfaceFn SteamUserStats;
	QL_SteamAPI_InterfaceFn SteamMatchmaking;
	QL_SteamAPI_InterfaceFn SteamApps;
	QL_SteamAPI_InterfaceFn SteamUGC;
	QL_SteamAPI_InterfaceFn SteamGameServerUGC;
	QL_SteamAPI_SteamGameServerInitFn SteamGameServer_Init;
	QL_SteamAPI_SteamGameServerFn SteamGameServer;
	QL_SteamAPI_SteamGameServerShutdownFn SteamGameServer_Shutdown;
	QL_SteamAPI_SteamGameServerRunCallbacksFn SteamGameServer_RunCallbacks;
	QL_SteamAPI_SteamGameServerNetworkingFn SteamGameServerNetworking;
	QL_SteamAPI_GetAuthSessionTicketFn GetAuthSessionTicket;
	QL_SteamAPI_BeginAuthSessionFn BeginAuthSession;
	QL_SteamAPI_CancelAuthTicketFn CancelAuthTicket;
	QL_SteamAPI_EndAuthSessionFn EndAuthSession;
	QL_SteamAPI_GetSteamIDFn GetSteamID;
	qboolean gameServerInitialised;
	qboolean useGameServerUGC;
} ql_steamworks_state_t;

static ql_steamworks_state_t state;

#define QL_STEAM_GAMESERVER_VERSION "1069"
#define QL_STEAM_GAMESERVER_MODE_NO_AUTH 2
#define QL_STEAM_GAMESERVER_MODE_AUTH_SECURE 3

/*
=============
QL_Steamworks_ResetState

Clears cached state and function pointers.
=============
*/
static void QL_Steamworks_ResetState( void ) {
	memset( &state, 0, sizeof( state ) );
}

/*
=============
QL_Steamworks_LoadSymbol

Resolves a symbol from the loaded Steam library.
=============
*/
static qboolean QL_Steamworks_LoadSymbol( void **target, const char *name ) {
	if ( !target || !name ) {
		return qfalse;
	}

	*target = QL_STEAMWORKS_SYM( name );

	return *target != NULL;
}

/*
=============
QL_Steamworks_LoadOptionalSymbol

Resolves a symbol without failing if it is missing.
=============
*/
static void QL_Steamworks_LoadOptionalSymbol( void **target, const char *name ) {
	if ( !target || !name ) {
		return;
	}

	*target = QL_STEAMWORKS_SYM( name );
}

/*
=============
QL_Steamworks_LoadLibrary

Dynamically loads the Steamworks runtime and resolves required exports.
=============
*/
qboolean QL_Steamworks_LoadLibrary( void ) {
	if ( state.library ) {
		return qtrue;
	}

	const char *candidates[] = {
		QL_STEAMWORKS_LIB_PRIMARY,
		QL_STEAMWORKS_LIB_SECONDARY
	};

	for ( size_t i = 0; i < sizeof( candidates ) / sizeof( candidates[0] ); ++i ) {
		state.library = QL_STEAMWORKS_OPEN( candidates[i] );
		if ( state.library ) {
			break;
		}
	}

	if ( !state.library ) {
		QL_Steamworks_ResetState();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Init, "SteamAPI_Init" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_Shutdown, "SteamAPI_Shutdown" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamAPI_RunCallbacks, "SteamAPI_RunCallbacks" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamUser, "SteamAPI_SteamUser" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamFriends, "SteamAPI_SteamFriends" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamUtils, "SteamAPI_SteamUtils" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamUserStats, "SteamAPI_SteamUserStats" );

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamMatchmaking, "SteamAPI_SteamMatchmaking" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamApps, "SteamAPI_SteamApps" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.SteamUGC, "SteamAPI_SteamUGC" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetAuthSessionTicket, "SteamAPI_ISteamUser_GetAuthSessionTicket" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.BeginAuthSession, "SteamAPI_ISteamUser_BeginAuthSession" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.CancelAuthTicket, "SteamAPI_ISteamUser_CancelAuthTicket" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.EndAuthSession, "SteamAPI_ISteamUser_EndAuthSession" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	if ( !QL_Steamworks_LoadSymbol( (void **)&state.GetSteamID, "SteamAPI_ISteamUser_GetSteamID" ) ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer, "SteamGameServer" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerUGC, "SteamGameServerUGC" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Init, "SteamGameServer_Init" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_Shutdown, "SteamGameServer_Shutdown" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServer_RunCallbacks, "SteamGameServer_RunCallbacks" );
	QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamGameServerNetworking, "SteamGameServerNetworking" );

	return qtrue;
}

/*
=============
QL_Steamworks_UnloadLibrary

Unloads the Steamworks runtime if it was loaded.
=============
*/
void QL_Steamworks_UnloadLibrary( void ) {
	if ( state.library ) {
		QL_STEAMWORKS_CLOSE();
	}

	QL_Steamworks_ResetState();
}

/*
=============
QL_Steamworks_Init

Initialises the Steamworks runtime, loading the library as needed.
=============
*/
qboolean QL_Steamworks_Init( void ) {
	if ( state.initialised ) {
		return qtrue;
	}

	if ( !QL_Steamworks_LoadLibrary() ) {
		return qfalse;
	}

	if ( !state.SteamAPI_Init() ) {
		QL_Steamworks_UnloadLibrary();
		return qfalse;
	}

	state.initialised = qtrue;
	return qtrue;
}

/*
=============
QL_Steamworks_Shutdown

Shuts down Steamworks and releases any loaded handles.
=============
*/
void QL_Steamworks_Shutdown( void ) {
	if ( !state.initialised && !state.gameServerInitialised ) {
		return;
	}

	if ( state.initialised && state.SteamAPI_Shutdown ) {
		state.SteamAPI_Shutdown();
	}
	state.initialised = qfalse;
	QL_Steamworks_ServerShutdown();
	QL_Steamworks_UnloadLibrary();
}

/*
=============
QL_Steamworks_RunCallbacks

Runs pending Steam callbacks if the runtime is initialised.
=============
*/
void QL_Steamworks_RunCallbacks( void ) {
	if ( !state.initialised || !state.SteamAPI_RunCallbacks ) {
		return;
	}

	state.SteamAPI_RunCallbacks();
}

/*
=============
QL_Steamworks_ClearStats
=============
*/
qboolean QL_Steamworks_ClearStats( qboolean achievementsToo ) {
	void *userStats;
	void **vtable;
	typedef int (__fastcall *QL_SteamUserStats_ResetAllStatsFn)( void *self, void *unused, int achievementsToo );
	QL_SteamUserStats_ResetAllStatsFn fn;

	if ( !state.initialised || !state.SteamUserStats ) {
		return qfalse;
	}

	userStats = state.SteamUserStats();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = *(void ***)userStats;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_ResetAllStatsFn)vtable[0x54 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, achievementsToo ? 1 : 0 ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetPersonaName
=============
*/
qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	void *friends;
	void **vtable;
	typedef const char *(__fastcall *QL_SteamFriends_GetPersonaNameFn)( void *self, void *unused );
	QL_SteamFriends_GetPersonaNameFn fn;
	const char *personaName;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 || !state.initialised || !state.SteamFriends ) {
		return qfalse;
	}

	friends = state.SteamFriends();
	if ( !friends ) {
		return qfalse;
	}

	vtable = *(void ***)friends;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_GetPersonaNameFn)vtable[0];
	if ( !fn ) {
		return qfalse;
	}

	personaName = fn( friends, NULL );
	if ( !personaName || !personaName[0] ) {
		return qfalse;
	}

	Q_strncpyz( buffer, personaName, bufferSize );
	return qtrue;
}

/*
=============
QL_Steamworks_GetIPCountry
=============
*/
qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	void *utils;
	void **vtable;
	typedef const char *(__fastcall *QL_SteamUtils_GetIPCountryFn)( void *self, void *unused );
	QL_SteamUtils_GetIPCountryFn fn;
	const char *country;

	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}

	if ( !buffer || bufferSize == 0 || !state.initialised || !state.SteamUtils ) {
		return qfalse;
	}

	utils = state.SteamUtils();
	if ( !utils ) {
		return qfalse;
	}

	vtable = *(void ***)utils;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUtils_GetIPCountryFn)vtable[0x10 / 4];
	if ( !fn ) {
		return qfalse;
	}

	country = fn( utils, NULL );
	if ( !country || !country[0] ) {
		return qfalse;
	}

	Q_strncpyz( buffer, country, bufferSize );
	return qtrue;
}

/*
=============
QL_Steamworks_CombineIdentityWords
=============
*/
static CSteamID QL_Steamworks_CombineIdentityWords( uint32_t idLow, uint32_t idHigh ) {
	CSteamID steamId;

	steamId.value = ( (uint64_t)idHigh << 32 ) | idLow;
	return steamId;
}

/*
=============
QL_Steamworks_GetInterfaceVTable
=============
*/
static void **QL_Steamworks_GetInterfaceVTable( void *interfaceObject ) {
	if ( !interfaceObject ) {
		return NULL;
	}

	return *(void ***)interfaceObject;
}

/*
=============
QL_Steamworks_GetUserInterface
=============
*/
static void *QL_Steamworks_GetUserInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamUser ) {
		return NULL;
	}

	return state.SteamUser();
}

/*
=============
QL_Steamworks_GetFriendsInterface
=============
*/
static void *QL_Steamworks_GetFriendsInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamFriends ) {
		return NULL;
	}

	return state.SteamFriends();
}

/*
=============
QL_Steamworks_GetMatchmakingInterface
=============
*/
static void *QL_Steamworks_GetMatchmakingInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamMatchmaking ) {
		return NULL;
	}

	return state.SteamMatchmaking();
}

/*
=============
QL_Steamworks_GetUserStatsInterface
=============
*/
static void *QL_Steamworks_GetUserStatsInterface( void ) {
	if ( !QL_Steamworks_Init() || !state.SteamUserStats ) {
		return NULL;
	}

	return state.SteamUserStats();
}

/*
=============
QL_Steamworks_SetRichPresence
=============
*/
qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value ) {
	void *friends;
	void **vtable;
	typedef int (__fastcall *QL_SteamFriends_SetRichPresenceFn)( void *self, void *unused, const char *key, const char *value );
	QL_SteamFriends_SetRichPresenceFn fn;

	if ( !key || !key[0] || !value ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_SetRichPresenceFn)vtable[0xac / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( friends, NULL, key, value ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ActivateOverlayToUser
=============
*/
qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayToUserFn)( void *self, void *unused, const char *dialog, CSteamID steamId );
	QL_SteamFriends_ActivateGameOverlayToUserFn fn;

	if ( !dialog || !dialog[0] ) {
		return qfalse;
	}

	friends = QL_Steamworks_GetFriendsInterface();
	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayToUserFn)vtable[0x74 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, dialog, QL_Steamworks_CombineIdentityWords( idLow, idHigh ) );
	return qtrue;
}

/*
=============
QL_Steamworks_CreateLobby
=============
*/
qboolean QL_Steamworks_CreateLobby( int maxMembers ) {
	void *matchmaking;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamMatchmaking_CreateLobbyFn)( void *self, void *unused, int lobbyType, int maxMembers );
	QL_SteamMatchmaking_CreateLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_CreateLobbyFn)vtable[0x34 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, 2, maxMembers ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_LeaveLobby
=============
*/
qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef void (__fastcall *QL_SteamMatchmaking_LeaveLobbyFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_LeaveLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_LeaveLobbyFn)vtable[0x3c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( matchmaking, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_JoinLobby
=============
*/
qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	void *matchmaking;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamMatchmaking_JoinLobbyFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamMatchmaking_JoinLobbyFn fn;

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_JoinLobbyFn)vtable[0x38 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( matchmaking, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_SetLobbyServer
=============
*/
qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	void *user;
	void *matchmaking;
	void **userVTable;
	void **matchmakingVTable;
	CSteamID localSteamId;
	CSteamID lobbyOwnerId;
	typedef CSteamID *(__fastcall *QL_SteamUser_GetSteamIDFn)( void *self, void *unused, CSteamID *outSteamId );
	typedef CSteamID *(__fastcall *QL_SteamMatchmaking_GetLobbyOwnerFn)( void *self, void *unused, CSteamID *outSteamId, uint32_t idLow, uint32_t idHigh );
	typedef void (__fastcall *QL_SteamMatchmaking_SetLobbyGameServerFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort, uint32_t serverIdLow, uint32_t serverIdHigh );
	QL_SteamUser_GetSteamIDFn getSteamIdFn;
	QL_SteamMatchmaking_GetLobbyOwnerFn getLobbyOwnerFn;
	QL_SteamMatchmaking_SetLobbyGameServerFn setLobbyServerFn;

	user = QL_Steamworks_GetUserInterface();
	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !user || !matchmaking ) {
		return qfalse;
	}

	userVTable = QL_Steamworks_GetInterfaceVTable( user );
	matchmakingVTable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !userVTable || !matchmakingVTable ) {
		return qfalse;
	}

	getSteamIdFn = (QL_SteamUser_GetSteamIDFn)userVTable[0x08 / 4];
	getLobbyOwnerFn = (QL_SteamMatchmaking_GetLobbyOwnerFn)matchmakingVTable[0x8c / 4];
	setLobbyServerFn = (QL_SteamMatchmaking_SetLobbyGameServerFn)matchmakingVTable[0x74 / 4];
	if ( !getSteamIdFn || !getLobbyOwnerFn || !setLobbyServerFn ) {
		return qfalse;
	}

	localSteamId.value = 0;
	lobbyOwnerId.value = 0;
	getSteamIdFn( user, NULL, &localSteamId );
	getLobbyOwnerFn( matchmaking, NULL, &lobbyOwnerId, idLow, idHigh );
	if ( lobbyOwnerId.value != localSteamId.value ) {
		return qfalse;
	}

	setLobbyServerFn( matchmaking, NULL, idLow, idHigh, serverIp, serverPort, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_ShowInviteOverlay
=============
*/
qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	void *friends;
	void **vtable;
	typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayInviteDialogFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamFriends_ActivateGameOverlayInviteDialogFn fn;

	friends = QL_Steamworks_GetFriendsInterface();
	if ( !friends ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( friends );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamFriends_ActivateGameOverlayInviteDialogFn)vtable[0x84 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( friends, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_SayLobby
=============
*/
qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	void *matchmaking;
	void **vtable;
	typedef int (__fastcall *QL_SteamMatchmaking_SendLobbyChatMsgFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, const char *message, int messageLength );
	QL_SteamMatchmaking_SendLobbyChatMsgFn fn;
	int messageLength;

	if ( !message ) {
		return qfalse;
	}

	matchmaking = QL_Steamworks_GetMatchmakingInterface();
	if ( !matchmaking ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( matchmaking );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamMatchmaking_SendLobbyChatMsgFn)vtable[0x68 / 4];
	if ( !fn ) {
		return qfalse;
	}

	messageLength = (int)strlen( message ) + 1;
	return fn( matchmaking, NULL, idLow, idHigh, message, messageLength ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RequestUserStats
=============
*/
qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	void *userStats;
	void **vtable;
	typedef uint64_t (__fastcall *QL_SteamUserStats_RequestUserStatsFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUserStats_RequestUserStatsFn fn;

	userStats = QL_Steamworks_GetUserStatsInterface();
	if ( !userStats ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( userStats );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUserStats_RequestUserStatsFn)vtable[0x40 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( userStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetUGCInterface
=============
*/
static void *QL_Steamworks_GetUGCInterface( void ) {
	if ( !QL_Steamworks_Init() ) {
		return NULL;
	}

	if ( state.useGameServerUGC && state.gameServerInitialised && state.SteamGameServerUGC ) {
		return state.SteamGameServerUGC();
	}

	if ( !state.SteamUGC ) {
		return NULL;
	}

	return state.SteamUGC();
}

/*
=============
QL_Steamworks_GetItemState
=============
*/
uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef uint32_t (__fastcall *QL_SteamUGC_GetItemStateFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_GetItemStateFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return 0;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return 0;
	}

	fn = (QL_SteamUGC_GetItemStateFn)vtable[0xd0 / 4];
	if ( !fn ) {
		return 0;
	}

	return fn( ugc, NULL, idLow, idHigh );
}

/*
=============
QL_Steamworks_SubscribeItem
=============
*/
qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_SubscribeItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_SubscribeItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_SubscribeItemFn)vtable[0xc0 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( ugc, NULL, idLow, idHigh );
	return qtrue;
}

/*
=============
QL_Steamworks_UnsubscribeItem
=============
*/
qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_UnsubscribeItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh );
	QL_SteamUGC_UnsubscribeItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_UnsubscribeItemFn)vtable[0xc4 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_DownloadItem
=============
*/
qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority ) {
	void *ugc;
	void **vtable;
	typedef int (__fastcall *QL_SteamUGC_DownloadItemFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, int highPriority );
	QL_SteamUGC_DownloadItemFn fn;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamUGC_DownloadItemFn)vtable[0xdc / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh, highPriority ? 1 : 0 ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetAvatarMethodIndex
=============
*/
static int QL_Steamworks_GetAvatarMethodIndex( ql_steam_avatar_size_t size ) {
	switch ( size ) {
	case QL_STEAM_AVATAR_SMALL:
		return 0x88 / 4;
	case QL_STEAM_AVATAR_MEDIUM:
		return 0x8c / 4;
	case QL_STEAM_AVATAR_LARGE:
	default:
		return 0x90 / 4;
	}
}

/*
=============
QL_Steamworks_LoadAvatarRGBA
=============
*/
qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight ) {
	void *friends;
	void *utils;
	void **friendsVTable;
	void **utilsVTable;
	typedef int (__fastcall *QL_SteamFriends_GetAvatarFn)( void *self, void *unused, CSteamID steamId );
	typedef int (__fastcall *QL_SteamUtils_GetImageSizeFn)( void *self, void *unused, int image, uint32_t *width, uint32_t *height );
	typedef int (__fastcall *QL_SteamUtils_GetImageRGBAFn)( void *self, void *unused, int image, uint8_t *buffer, int length );
	QL_SteamFriends_GetAvatarFn getAvatar;
	QL_SteamUtils_GetImageSizeFn getImageSize;
	QL_SteamUtils_GetImageRGBAFn getImageRGBA;
	CSteamID steamId;
	int image;
	uint32_t width;
	uint32_t height;
	size_t pixelCount;
	size_t bufferSize;
	uint8_t *pixels;

	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}

	if ( !outPixels || !outWidth || !outHeight ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() || !state.SteamFriends || !state.SteamUtils ) {
		return qfalse;
	}

	friends = state.SteamFriends();
	utils = state.SteamUtils();
	if ( !friends || !utils ) {
		return qfalse;
	}

	friendsVTable = QL_Steamworks_GetInterfaceVTable( friends );
	utilsVTable = QL_Steamworks_GetInterfaceVTable( utils );
	if ( !friendsVTable || !utilsVTable ) {
		return qfalse;
	}

	getAvatar = (QL_SteamFriends_GetAvatarFn)friendsVTable[QL_Steamworks_GetAvatarMethodIndex( size )];
	getImageSize = (QL_SteamUtils_GetImageSizeFn)utilsVTable[0x14 / 4];
	getImageRGBA = (QL_SteamUtils_GetImageRGBAFn)utilsVTable[0x18 / 4];
	if ( !getAvatar || !getImageSize || !getImageRGBA ) {
		return qfalse;
	}

	steamId = QL_Steamworks_CombineIdentityWords( idLow, idHigh );
	image = getAvatar( friends, NULL, steamId );
	if ( image <= 0 ) {
		return qfalse;
	}

	width = 0;
	height = 0;
	if ( !getImageSize( utils, NULL, image, &width, &height ) || width == 0 || height == 0 ) {
		return qfalse;
	}

	pixelCount = (size_t)width * (size_t)height;
	if ( pixelCount > ( (size_t)INT_MAX / 4 ) ) {
		return qfalse;
	}

	bufferSize = pixelCount * 4;
	pixels = (uint8_t *)malloc( bufferSize );
	if ( !pixels ) {
		return qfalse;
	}

	if ( !getImageRGBA( utils, NULL, image, pixels, (int)bufferSize ) ) {
		free( pixels );
		return qfalse;
	}

	*outPixels = pixels;
	*outWidth = width;
	*outHeight = height;
	return qtrue;
}

/*
=============
QL_Steamworks_FreeBuffer
=============
*/
void QL_Steamworks_FreeBuffer( void *buffer ) {
	if ( buffer ) {
		free( buffer );
	}
}

/*
=============
QL_Steamworks_IsSubscribedApp
=============
*/
qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId ) {
	void *apps;
	void **vtable;

	if ( !state.initialised || !state.SteamApps ) {
		return qfalse;
	}

	apps = state.SteamApps();
	if ( !apps ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( apps );
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__fastcall *QL_SteamApps_BIsSubscribedAppFn)( void *self, void *unused, uint32_t appId );
	QL_SteamApps_BIsSubscribedAppFn fn = (QL_SteamApps_BIsSubscribedAppFn)vtable[0x1c / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( apps, NULL, appId ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_GetItemDownloadInfo
=============
*/
qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	void *ugc;
	void **vtable;

	ugc = QL_Steamworks_GetUGCInterface();
	if ( !ugc ) {
		return qfalse;
	}

	vtable = QL_Steamworks_GetInterfaceVTable( ugc );
	if ( !vtable ) {
		return qfalse;
	}

	typedef int (__fastcall *QL_SteamUGC_GetItemDownloadInfoFn)( void *self, void *unused, uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );
	QL_SteamUGC_GetItemDownloadInfoFn fn = (QL_SteamUGC_GetItemDownloadInfoFn)vtable[0xd8 / 4];
	if ( !fn ) {
		return qfalse;
	}

	return fn( ugc, NULL, idLow, idHigh, outDownloaded, outTotal ) ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_RunServerCallbacks

Runs Steam server callbacks if the GameServer interface is available.
=============
*/
void QL_Steamworks_RunServerCallbacks( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServer_RunCallbacks ) {
		return;
	}

	state.SteamGameServer_RunCallbacks();
}

/*
=============
QL_Steamworks_ServerInit

Reconstructs the retail Steam game-server init gate and remembers which UGC
owner should back workshop calls for the active server path.
=============
*/
qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	int serverMode;

	if ( gamePort == 0 ) {
		return qfalse;
	}

	if ( state.gameServerInitialised ) {
		state.useGameServerUGC = dedicated ? qtrue : qfalse;
		return qtrue;
	}

	if ( !QL_Steamworks_Init() || !state.SteamGameServer_Init ) {
		return qfalse;
	}

	serverMode = secure ? QL_STEAM_GAMESERVER_MODE_AUTH_SECURE : QL_STEAM_GAMESERVER_MODE_NO_AUTH;
	if ( !state.SteamGameServer_Init( ip, 0, gamePort, 0xffffu, serverMode, QL_STEAM_GAMESERVER_VERSION ) ) {
		return qfalse;
	}

	state.gameServerInitialised = qtrue;
	state.useGameServerUGC = dedicated ? qtrue : qfalse;
	return qtrue;
}

/*
=============
QL_Steamworks_ServerShutdown

Reconstructs the retail game-server shutdown gate and clears the active server
UGC owner.
=============
*/
void QL_Steamworks_ServerShutdown( void ) {
	if ( state.gameServerInitialised && state.SteamGameServer_Shutdown ) {
		state.SteamGameServer_Shutdown();
	}

	state.gameServerInitialised = qfalse;
	state.useGameServerUGC = qfalse;
}

/*
=============
QL_Steamworks_ServerIsInitialised
=============
*/
qboolean QL_Steamworks_ServerIsInitialised( void ) {
	return state.gameServerInitialised;
}

/*
=============
QL_Steamworks_GetGameServerNetworking

Returns the Steam GameServer networking interface when available.
=============
*/
static void *QL_Steamworks_GetGameServerNetworking( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServerNetworking ) {
		return NULL;
	}

	return state.SteamGameServerNetworking();
}

/*
=============
QL_Steamworks_GetGameServer

Returns the Steam GameServer interface when available.
=============
*/
static void *QL_Steamworks_GetGameServer( void ) {
	if ( !state.initialised || !state.gameServerInitialised || !state.SteamGameServer ) {
		return NULL;
	}

	return state.SteamGameServer();
}

/*
=============
QL_Steamworks_ServerSetDedicated

Mirrors the retail dedicated-state bootstrap write for the Steam game-server.
=============
*/
qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetDedicatedFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetDedicatedFn)vtable[0x10 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, dedicated ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerLogOn

Uses the mapped retail Steam account bootstrap path, including anonymous fallback.
=============
*/
qboolean QL_Steamworks_ServerLogOn( const char *account ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_LogOnFn logOnFn;
	QL_SteamGameServer_LogOnAnonymousFn anonymousFn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	if ( account && account[0] ) {
		logOnFn = (QL_SteamGameServer_LogOnFn)vtable[0x14 / 4];
		if ( !logOnFn ) {
			return qfalse;
		}

		logOnFn( gameServer, account );
		return qtrue;
	}

	anonymousFn = (QL_SteamGameServer_LogOnAnonymousFn)vtable[0x18 / 4];
	if ( !anonymousFn ) {
		return qfalse;
	}

	anonymousFn( gameServer );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetProduct

Publishes the retail Steam game-server product string.
=============
*/
qboolean QL_Steamworks_ServerSetProduct( const char *product ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !product || !product[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x04 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, product );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameDir

Publishes the retail Steam game-server mod/game-dir string.
=============
*/
qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !gameDir || !gameDir[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x0c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, gameDir );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameDescription

Publishes the retail Steam game-server description string.
=============
*/
qboolean QL_Steamworks_ServerSetGameDescription( const char *description ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !description || !description[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x08 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, description );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetMaxPlayerCount

Publishes the retail Steam game-server max-player count.
=============
*/
qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	if ( maxPlayers < 0 ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x30 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, maxPlayers );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetBotPlayerCount

Publishes the retail Steam game-server bot-player count.
=============
*/
qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	if ( botPlayers < 0 ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x34 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, botPlayers );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetServerName

Publishes the retail Steam game-server name string.
=============
*/
qboolean QL_Steamworks_ServerSetServerName( const char *name ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !name || !name[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x38 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, name );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetMapName

Publishes the retail Steam game-server map string.
=============
*/
qboolean QL_Steamworks_ServerSetMapName( const char *mapName ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !mapName || !mapName[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x3c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, mapName );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetPasswordProtected

Publishes the retail Steam game-server passworded state.
=============
*/
qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetIntFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetIntFn)vtable[0x40 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, passwordProtected ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerEnableHeartbeats

Toggles the Steam game-server heartbeat state through the mapped server slot.
=============
*/
qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_EnableHeartbeatsFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_EnableHeartbeatsFn)vtable[0x9c / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, enable ? 1 : 0 );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerGetSteamID

Returns the current Steam game-server identity split into low/high words.
=============
*/
qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	void *gameServer;
	void **vtable;
	CSteamID steamId;
	typedef CSteamID *(__fastcall *QL_SteamGameServer_GetSteamIDFn)( void *self, void *unused, CSteamID *outSteamId );
	QL_SteamGameServer_GetSteamIDFn fn;

	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}

	if ( !outIdLow || !outIdHigh ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_GetSteamIDFn)vtable[0x28 / 4];
	if ( !fn ) {
		return qfalse;
	}

	steamId.value = 0ull;
	if ( !fn( gameServer, NULL, &steamId ) ) {
		return qfalse;
	}

	*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );
	*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetGameTags

Publishes the retail Steam game-server game-tags string.
=============
*/
qboolean QL_Steamworks_ServerSetGameTags( const char *tags ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetStringFn fn;

	if ( !tags ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetStringFn)vtable[0x54 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, tags );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetKeyValue

Publishes a single key/value pair through the mapped Steam game-server slot.
=============
*/
qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_SetKeyValueFn fn;

	if ( !key || !key[0] || !value ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_SetKeyValueFn)vtable[0x50 / 4];
	if ( !fn ) {
		return qfalse;
	}

	fn( gameServer, key, value );
	return qtrue;
}

/*
=============
QL_Steamworks_ServerSetKeyValuesFromInfoString

Publishes server-info key/value pairs through the mapped Steam game-server slot.
=============
*/
qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	const char *head;
	char key[MAX_INFO_KEY];
	char value[MAX_INFO_VALUE];

	if ( !infoString ) {
		return qfalse;
	}

	head = infoString;
	while ( head && head[0] ) {
		Info_NextPair( &head, key, value );
		if ( !key[0] ) {
			break;
		}

		if ( !QL_Steamworks_ServerSetKeyValue( key, value ) ) {
			return qfalse;
		}
	}

	return qtrue;
}

/*
=============
QL_Steamworks_ServerUpdateUserData

Publishes a player's Steam identity, display name, and score.
=============
*/
qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_UpdateUserDataFn fn;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !steamId || steamId->value == 0ull || !playerName || !playerName[0] ) {
		return qfalse;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return qfalse;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return qfalse;
	}

	fn = (QL_SteamGameServer_UpdateUserDataFn)vtable[0x6c / 4];
	if ( !fn ) {
		return qfalse;
	}

	idLow = (uint32_t)( steamId->value & 0xffffffffu );
	idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );

	return fn( gameServer, idLow, idHigh, playerName, score ) != 0 ? qtrue : qfalse;
}

/*
=============
QL_Steamworks_ServerGetPublicIP

Returns the Steam-reported public IP for the current game-server instance.
=============
*/
uint32_t QL_Steamworks_ServerGetPublicIP( void ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_GetPublicIPFn fn;

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return 0u;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return 0u;
	}

	fn = (QL_SteamGameServer_GetPublicIPFn)vtable[0x90 / 4];
	if ( !fn ) {
		return 0u;
	}

	return fn( gameServer );
}

/*
=============
QL_Steamworks_ServerSendP2PPacket

Dispatches a P2P packet through the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_SendP2PPacketFn sendPacket;

	if ( !steamId || !data || length == 0 ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	sendPacket = (QL_SteamNetworking_SendP2PPacketFn)vtable[0];
	if ( !sendPacket ) {
		return qfalse;
	}

	return sendPacket( networking, *steamId, data, length, sendType, channel );
}

/*
=============
QL_Steamworks_ServerIsP2PPacketAvailable

Checks for pending P2P packets for the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_IsP2PPacketAvailableFn isAvailable;

	if ( !outSize ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	isAvailable = (QL_SteamNetworking_IsP2PPacketAvailableFn)vtable[1];
	if ( !isAvailable ) {
		return qfalse;
	}

	return isAvailable( networking, outSize, channel );
}

/*
=============
QL_Steamworks_ServerReadP2PPacket

Reads a pending P2P packet from the Steam GameServer networking interface.
=============
*/
qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	void *networking;
	void **vtable;
	QL_SteamNetworking_ReadP2PPacketFn readPacket;

	if ( !data || dataSize == 0 || !outSize || !outSteamId ) {
		return qfalse;
	}

	networking = QL_Steamworks_GetGameServerNetworking();
	if ( !networking ) {
		return qfalse;
	}

	vtable = *(void ***)networking;
	if ( !vtable ) {
		return qfalse;
	}

	readPacket = (QL_SteamNetworking_ReadP2PPacketFn)vtable[2];
	if ( !readPacket ) {
		return qfalse;
	}

	return readPacket( networking, data, dataSize, outSize, outSteamId, channel );
}

/*
=============
QL_Steamworks_ServerGetNextOutgoingPacket

Pulls the next outgoing Steam GameServer packet destined for a UDP socket.
=============
*/
int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	void *gameServer;
	void **vtable;
	QL_SteamGameServer_GetNextOutgoingPacketFn getPacket;

	if ( !data || dataSize <= 0 || !outIp || !outPort ) {
		return 0;
	}

	gameServer = QL_Steamworks_GetGameServer();
	if ( !gameServer ) {
		return 0;
	}

	vtable = *(void ***)gameServer;
	if ( !vtable ) {
		return 0;
	}

	getPacket = (QL_SteamGameServer_GetNextOutgoingPacketFn)vtable[0x98 / 4];
	if ( !getPacket ) {
		return 0;
	}

	return getPacket( gameServer, data, dataSize, outIp, outPort );
}

/*
=============
QL_Steamworks_HexEncode

Converts binary data to a lower-case hexadecimal representation.
=============
*/
qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize ) {
	static const char *hex = "0123456789abcdef";

	if ( !data || !out || outSize == 0 ) {
		return qfalse;
	}

	size_t required = (size_t)length * 2 + 1;
	if ( outSize < required ) {
		return qfalse;
	}

	for ( uint32_t i = 0; i < length; ++i ) {
		out[i * 2] = hex[data[i] >> 4];
		out[i * 2 + 1] = hex[data[i] & 0x0F];
	}

	out[length * 2] = '\0';
	return qtrue;
}

/*
=============
QL_Steamworks_HexDecode

Decodes a hexadecimal string back into binary data.
=============
*/
qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength ) {
	if ( !hex || !out ) {
		return qfalse;
	}

	size_t hexLength = strlen( hex );
	if ( hexLength % 2 != 0 ) {
		return qfalse;
	}

	size_t required = hexLength / 2;
	if ( outSize < required ) {
		return qfalse;
	}

	for ( size_t i = 0; i < required; ++i ) {
		char hi = hex[i * 2];
		char lo = hex[i * 2 + 1];

		uint8_t value = 0;

		if ( hi >= '0' && hi <= '9' ) {
			value |= (uint8_t)( (hi - '0') << 4 );
		} else if ( hi >= 'a' && hi <= 'f' ) {
			value |= (uint8_t)( (hi - 'a' + 10) << 4 );
		} else if ( hi >= 'A' && hi <= 'F' ) {
			value |= (uint8_t)( (hi - 'A' + 10) << 4 );
		} else {
			return qfalse;
		}

		if ( lo >= '0' && lo <= '9' ) {
			value |= (uint8_t)( lo - '0' );
		} else if ( lo >= 'a' && lo <= 'f' ) {
			value |= (uint8_t)( lo - 'a' + 10 );
		} else if ( lo >= 'A' && lo <= 'F' ) {
			value |= (uint8_t)( lo - 'A' + 10 );
		} else {
			return qfalse;
		}

		out[i] = value;
	}

	if ( outLength ) {
		*outLength = (uint32_t)required;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_RequestAuthTicket

Requests an auth session ticket and returns it encoded as hex.
=============
*/
qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	if ( !ticketBuffer || ticketBufferSize == 0 ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		return qfalse;
	}

	void *user = state.SteamUser ? state.SteamUser() : NULL;
	if ( !user || !state.GetAuthSessionTicket ) {
		return qfalse;
	}

	uint8_t rawTicket[1024];
	uint32_t rawLength = 0;
	HAuthTicket handle = state.GetAuthSessionTicket( user, rawTicket, sizeof( rawTicket ), &rawLength );

	if ( handle == 0 || rawLength == 0 ) {
		return qfalse;
	}

	if ( !QL_Steamworks_HexEncode( rawTicket, rawLength, ticketBuffer, ticketBufferSize ) ) {
		return qfalse;
	}

	if ( ticketLength ) {
		*ticketLength = (int)( rawLength * 2 );
	}

	if ( ticketHandle ) {
		*ticketHandle = handle;
	}

	return qtrue;
}

/*
=============
QL_Steamworks_CancelAuthTicket

Cancels a previously issued auth session ticket.
=============
*/
qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {
	void *user;

	if ( ticketHandle == 0 || !state.initialised || !state.SteamUser || !state.CancelAuthTicket ) {
		return qfalse;
	}

	user = state.SteamUser();
	if ( !user ) {
		return qfalse;
	}

	state.CancelAuthTicket( user, (HAuthTicket)ticketHandle );
	return qtrue;
}

/*
=============
QL_Steamworks_MapAuthResult

Converts a BeginAuthSession result into a ql_auth_response_t.
=============
*/
static void QL_Steamworks_MapAuthResult( EBeginAuthSessionResult result, ql_auth_response_t *response ) {
	if ( !response ) {
		return;
	}

	switch ( result ) {
		case k_EBeginAuthSessionResultOK:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ACCEPTED, "Steam ticket accepted" );
			break;
		case k_EBeginAuthSessionResultDuplicateRequest:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING, "Steam already processing auth ticket" );
			break;
		case k_EBeginAuthSessionResultInvalidTicket:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket invalid" );
			break;
		case k_EBeginAuthSessionResultInvalidVersion:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket version mismatch" );
			break;
		case k_EBeginAuthSessionResultGameMismatch:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket issued for another game" );
			break;
		case k_EBeginAuthSessionResultExpiredTicket:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_PENDING, "Steam ticket expired, request refresh" );
			break;
		default:
			QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam returned unknown auth result (%d)", (int)result );
			break;
	}
}

/*
=============
QL_Steamworks_ValidateTicket

Validates a hex-encoded auth ticket with Steam and populates a response.
=============
*/
qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
	if ( !ticketHex || !response ) {
		return qfalse;
	}

	if ( !QL_Steamworks_Init() ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam runtime unavailable" );
		return qtrue;
	}

	void *user = state.SteamUser ? state.SteamUser() : NULL;
	if ( !user || !state.BeginAuthSession || !state.GetSteamID ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "Steam user interface unavailable" );
		return qtrue;
	}

	uint8_t ticketData[1024];
	uint32_t ticketLength = 0;

	if ( !QL_Steamworks_HexDecode( ticketHex, ticketData, sizeof( ticketData ), &ticketLength ) ) {
		QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_DENIED, "Steam ticket malformed" );
		return qtrue;
	}

	CSteamID steamId = state.GetSteamID( user );
	EBeginAuthSessionResult result = state.BeginAuthSession( user, ticketData, (int)ticketLength, steamId );
	QL_Steamworks_MapAuthResult( result, response );

	if ( result == k_EBeginAuthSessionResultOK && state.EndAuthSession ) {
		state.EndAuthSession( user, steamId );
	}

	return qtrue;
}

#endif
