#ifndef PLATFORM_STEAMWORKS_H
#define PLATFORM_STEAMWORKS_H

#include "platform_config.h"

#include <stddef.h>
#include <stdint.h>

#include "../auth_credentials.h"

typedef struct {
	uint64_t value;
} CSteamID;

typedef enum {
	QL_STEAM_AVATAR_SMALL = 0,
	QL_STEAM_AVATAR_MEDIUM = 1,
	QL_STEAM_AVATAR_LARGE = 2
} ql_steam_avatar_size_t;

#if QL_BUILD_STEAMWORKS

#include "platform_backend_shared.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t HAuthTicket;

typedef enum {
	k_EBeginAuthSessionResultOK = 0,
	k_EBeginAuthSessionResultInvalidTicket = 1,
	k_EBeginAuthSessionResultDuplicateRequest = 2,
	k_EBeginAuthSessionResultInvalidVersion = 3,
	k_EBeginAuthSessionResultGameMismatch = 4,
	k_EBeginAuthSessionResultExpiredTicket = 5
} EBeginAuthSessionResult;

qboolean QL_Steamworks_LoadLibrary( void );

void QL_Steamworks_UnloadLibrary( void );

qboolean QL_Steamworks_Init( void );

void QL_Steamworks_Shutdown( void );

void QL_Steamworks_RunCallbacks( void );

void QL_Steamworks_RunServerCallbacks( void );

qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated );

void QL_Steamworks_ServerShutdown( void );

qboolean QL_Steamworks_ServerIsInitialised( void );

qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable );

qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated );

qboolean QL_Steamworks_ServerLogOn( const char *account );

qboolean QL_Steamworks_ServerSetProduct( const char *product );

qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir );

qboolean QL_Steamworks_ServerSetGameDescription( const char *description );

qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers );

qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers );

qboolean QL_Steamworks_ServerSetServerName( const char *name );

qboolean QL_Steamworks_ServerSetMapName( const char *mapName );

qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected );

qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh );

qboolean QL_Steamworks_ServerSetGameTags( const char *tags );

qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value );

qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString );

qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score );

uint32_t QL_Steamworks_ServerGetPublicIP( void );

qboolean QL_Steamworks_ClearStats( qboolean achievementsToo );

qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize );

qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize );

qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel );

qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel );

qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel );

int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort );

qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize );

qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength );

qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle );

qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle );

qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response );

qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId );

qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal );

qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value );

qboolean QL_Steamworks_CreateLobby( int maxMembers );

qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort );

qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message );

qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh );

uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh );

qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority );

qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight );

void QL_Steamworks_FreeBuffer( void *buffer );

#ifdef __cplusplus
}
#endif

#else

/*
=============
QL_Steamworks_LoadLibrary
=============
*/
static inline qboolean QL_Steamworks_LoadLibrary( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_UnloadLibrary
=============
*/
static inline void QL_Steamworks_UnloadLibrary( void ) {
}

/*
=============
QL_Steamworks_Init
=============
*/
static inline qboolean QL_Steamworks_Init( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_Shutdown
=============
*/
static inline void QL_Steamworks_Shutdown( void ) {
}

/*
=============
QL_Steamworks_RunCallbacks
=============
*/
static inline void QL_Steamworks_RunCallbacks( void ) {
}

/*
=============
QL_Steamworks_RunServerCallbacks
=============
*/
static inline void QL_Steamworks_RunServerCallbacks( void ) {
}

/*
=============
QL_Steamworks_ServerInit
=============
*/
static inline qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated ) {
	(void)ip;
	(void)gamePort;
	(void)secure;
	(void)dedicated;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerShutdown
=============
*/
static inline void QL_Steamworks_ServerShutdown( void ) {
}

/*
=============
QL_Steamworks_ServerIsInitialised
=============
*/
static inline qboolean QL_Steamworks_ServerIsInitialised( void ) {
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetDedicated
=============
*/
static inline qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated ) {
	(void)dedicated;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerLogOn
=============
*/
static inline qboolean QL_Steamworks_ServerLogOn( const char *account ) {
	(void)account;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetProduct
=============
*/
static inline qboolean QL_Steamworks_ServerSetProduct( const char *product ) {
	(void)product;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetGameDir
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir ) {
	(void)gameDir;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetGameDescription
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameDescription( const char *description ) {
	(void)description;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetMaxPlayerCount
=============
*/
static inline qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers ) {
	(void)maxPlayers;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetBotPlayerCount
=============
*/
static inline qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers ) {
	(void)botPlayers;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetServerName
=============
*/
static inline qboolean QL_Steamworks_ServerSetServerName( const char *name ) {
	(void)name;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetMapName
=============
*/
static inline qboolean QL_Steamworks_ServerSetMapName( const char *mapName ) {
	(void)mapName;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetPasswordProtected
=============
*/
static inline qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected ) {
	(void)passwordProtected;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerEnableHeartbeats
=============
*/
static inline qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable ) {
	(void)enable;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetSteamID
=============
*/
static inline qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh ) {
	if ( outIdLow ) {
		*outIdLow = 0u;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0u;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetGameTags
=============
*/
static inline qboolean QL_Steamworks_ServerSetGameTags( const char *tags ) {
	(void)tags;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetKeyValue
=============
*/
static inline qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSetKeyValuesFromInfoString
=============
*/
static inline qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString ) {
	(void)infoString;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerUpdateUserData
=============
*/
static inline qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score ) {
	(void)steamId;
	(void)playerName;
	(void)score;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetPublicIP
=============
*/
static inline uint32_t QL_Steamworks_ServerGetPublicIP( void ) {
	return 0u;
}

/*
=============
QL_Steamworks_ClearStats
=============
*/
static inline qboolean QL_Steamworks_ClearStats( qboolean achievementsToo ) {
	(void)achievementsToo;
	return qfalse;
}

/*
=============
QL_Steamworks_GetPersonaName
=============
*/
static inline qboolean QL_Steamworks_GetPersonaName( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_GetIPCountry
=============
*/
static inline qboolean QL_Steamworks_GetIPCountry( char *buffer, size_t bufferSize ) {
	if ( buffer && bufferSize > 0 ) {
		buffer[0] = '\0';
	}
	return qfalse;
}

/*
=============
QL_Steamworks_SetRichPresence
=============
*/
static inline qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value ) {
	(void)key;
	(void)value;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerSendP2PPacket
=============
*/
static inline qboolean QL_Steamworks_ServerSendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel ) {
	(void)steamId;
	(void)data;
	(void)length;
	(void)sendType;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerIsP2PPacketAvailable
=============
*/
static inline qboolean QL_Steamworks_ServerIsP2PPacketAvailable( uint32_t *outSize, int channel ) {
	(void)outSize;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerReadP2PPacket
=============
*/
static inline qboolean QL_Steamworks_ServerReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel ) {
	(void)data;
	(void)dataSize;
	(void)outSize;
	(void)outSteamId;
	(void)channel;
	return qfalse;
}

/*
=============
QL_Steamworks_ServerGetNextOutgoingPacket
=============
*/
static inline int QL_Steamworks_ServerGetNextOutgoingPacket( void *data, int dataSize, uint32_t *outIp, uint16_t *outPort ) {
	(void)data;
	(void)dataSize;
	(void)outIp;
	(void)outPort;
	return 0;
}

/*
=============
QL_Steamworks_HexEncode
=============
*/
static inline qboolean QL_Steamworks_HexEncode( const uint8_t *data, uint32_t length, char *out, size_t outSize ) {
	(void)data;
	(void)length;
	(void)out;
	(void)outSize;
	return qfalse;
}

/*
=============
QL_Steamworks_HexDecode
=============
*/
static inline qboolean QL_Steamworks_HexDecode( const char *hex, uint8_t *out, size_t outSize, uint32_t *outLength ) {
	(void)hex;
	(void)out;
	(void)outSize;
	(void)outLength;
	return qfalse;
}

/*
=============
QL_Steamworks_RequestAuthTicket
=============
*/
static inline qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
	(void)ticketBuffer;
	(void)ticketBufferSize;
	(void)ticketLength;
	(void)ticketHandle;
	return qfalse;
}

/*
=============
QL_Steamworks_CancelAuthTicket
=============
*/
static inline qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {
	(void)ticketHandle;
	return qfalse;
}

/*
=============
QL_Steamworks_ValidateTicket
=============
*/
static inline qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
	(void)ticketHex;
	(void)response;
	return qfalse;
}

/*
=============
QL_Steamworks_IsSubscribedApp
=============
*/
static inline qboolean QL_Steamworks_IsSubscribedApp( uint32_t appId ) {
	(void)appId;
	return qfalse;
}

/*
=============
QL_Steamworks_GetItemDownloadInfo
=============
*/
static inline qboolean QL_Steamworks_GetItemDownloadInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outDownloaded, uint64_t *outTotal ) {
	(void)idLow;
	(void)idHigh;
	(void)outDownloaded;
	(void)outTotal;
	return qfalse;
}

/*
=============
QL_Steamworks_ActivateOverlayToUser
=============
*/
static inline qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh ) {
	(void)dialog;
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_CreateLobby
=============
*/
static inline qboolean QL_Steamworks_CreateLobby( int maxMembers ) {
	(void)maxMembers;
	return qfalse;
}

/*
=============
QL_Steamworks_LeaveLobby
=============
*/
static inline qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_JoinLobby
=============
*/
static inline qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_SetLobbyServer
=============
*/
static inline qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort ) {
	(void)idLow;
	(void)idHigh;
	(void)serverIp;
	(void)serverPort;
	return qfalse;
}

/*
=============
QL_Steamworks_ShowInviteOverlay
=============
*/
static inline qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_SayLobby
=============
*/
static inline qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message ) {
	(void)idLow;
	(void)idHigh;
	(void)message;
	return qfalse;
}

/*
=============
QL_Steamworks_RequestUserStats
=============
*/
static inline qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_GetItemState
=============
*/
static inline uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return 0;
}

/*
=============
QL_Steamworks_SubscribeItem
=============
*/
static inline qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_UnsubscribeItem
=============
*/
static inline qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh ) {
	(void)idLow;
	(void)idHigh;
	return qfalse;
}

/*
=============
QL_Steamworks_DownloadItem
=============
*/
static inline qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority ) {
	(void)idLow;
	(void)idHigh;
	(void)highPriority;
	return qfalse;
}

/*
=============
QL_Steamworks_LoadAvatarRGBA
=============
*/
static inline qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight ) {
	(void)idLow;
	(void)idHigh;
	(void)size;
	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}
	return qfalse;
}

/*
=============
QL_Steamworks_FreeBuffer
=============
*/
static inline void QL_Steamworks_FreeBuffer( void *buffer ) {
	(void)buffer;
}

#endif

#endif // PLATFORM_STEAMWORKS_H

