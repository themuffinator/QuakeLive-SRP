#include "client.h"

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#include "../../common/platform/platform_steamworks.h"

#define MAX_STEAM_RESOURCES 64
#define STEAM_URL_PREFIX "steam://"

typedef struct {
	char		url[MAX_QPATH];
	char		cachePath[MAX_QPATH];
	qhandle_t	shader;
	qboolean	persisted;
} clSteamResource_t;

static clSteamResource_t cl_steamResources[MAX_STEAM_RESOURCES];
static cvar_t *cl_steamCachePersist;
static cvar_t *cl_steamCachePath;

qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize );
void Sys_Steam_FreeRequestBuffer( byte *buffer );
char *FS_BuildOSPath( const char *base, const char *game, const char *qpath );

/*
=============
CL_SteamResources_IsSteamURL

Returns qtrue when the provided resource begins with the Steam URL scheme.
=============
*/
static qboolean CL_SteamResources_IsSteamURL( const char *url ) {
	if ( !url ) {
		return qfalse;
	}

	return ( Q_strnicmp( url, STEAM_URL_PREFIX, strlen( STEAM_URL_PREFIX ) ) == 0 );
}

/*
=============
CL_SteamResources_IsURIResource

Returns qtrue when the provided resource uses a URI scheme and should route
through the launcher/Steam cache bridge instead of the normal shader loader.
=============
*/
static qboolean CL_SteamResources_IsURIResource( const char *url ) {
	if ( !url ) {
		return qfalse;
	}

	return ( strstr( url, "://" ) != NULL ) ? qtrue : qfalse;
}

/*
=============
CL_SteamResources_IsAvatarURL

Returns qtrue when the provided Steam URL targets the avatar data source.
=============
*/
static qboolean CL_SteamResources_IsAvatarURL( const char *url ) {
	static const char *avatarPrefix = STEAM_URL_PREFIX "avatar/";

	if ( !url ) {
		return qfalse;
	}

	return ( Q_strnicmp( url, avatarPrefix, strlen( avatarPrefix ) ) == 0 );
}

/*
=============
CL_SteamResources_ParseAvatarSizeToken

Maps a Steam avatar size token to the matching Steamworks selector.
=============
*/
static qboolean CL_SteamResources_ParseAvatarSizeToken( const char *token, ql_steam_avatar_size_t *outSize ) {
	if ( !token || !token[0] || !outSize ) {
		return qfalse;
	}

	if ( !Q_stricmp( token, "small" ) ) {
		*outSize = QL_STEAM_AVATAR_SMALL;
		return qtrue;
	}

	if ( !Q_stricmp( token, "medium" ) ) {
		*outSize = QL_STEAM_AVATAR_MEDIUM;
		return qtrue;
	}

	if ( !Q_stricmp( token, "large" ) ) {
		*outSize = QL_STEAM_AVATAR_LARGE;
		return qtrue;
	}

	return qfalse;
}

/*
=============
CL_SteamResources_ParseAvatarURL

Extracts a SteamID and optional size token from a steam://avatar URL.
=============
*/
static qboolean CL_SteamResources_ParseAvatarURL( const char *url, ql_steam_avatar_size_t *outSize, uint32_t *outIdLow, uint32_t *outIdHigh ) {
	static const char *avatarPrefix = STEAM_URL_PREFIX "avatar/";
	char token[MAX_QPATH];
	size_t prefixLength;
	const char *cursor;
	const char *slash;
	char *end;
	unsigned long long steamIdValue;

	if ( outSize ) {
		*outSize = QL_STEAM_AVATAR_LARGE;
	}
	if ( outIdLow ) {
		*outIdLow = 0;
	}
	if ( outIdHigh ) {
		*outIdHigh = 0;
	}

	if ( !url || !outSize || !outIdLow || !outIdHigh ) {
		return qfalse;
	}

	prefixLength = strlen( avatarPrefix );
	if ( Q_strnicmp( url, avatarPrefix, prefixLength ) != 0 ) {
		return qfalse;
	}

	cursor = url + prefixLength;
	if ( !cursor[0] ) {
		return qfalse;
	}

	slash = strchr( cursor, '/' );
	if ( slash ) {
		size_t tokenLength = (size_t)( slash - cursor );

		if ( tokenLength == 0 || tokenLength >= sizeof( token ) ) {
			return qfalse;
		}

		memcpy( token, cursor, tokenLength );
		token[tokenLength] = '\0';
		if ( !CL_SteamResources_ParseAvatarSizeToken( token, outSize ) ) {
			return qfalse;
		}

		cursor = slash + 1;
	}

	if ( !cursor[0] ) {
		return qfalse;
	}

	steamIdValue = strtoull( cursor, &end, 10 );
	if ( end == cursor || *end != '\0' ) {
		return qfalse;
	}

	*outIdLow = (uint32_t)steamIdValue;
	*outIdHigh = (uint32_t)( steamIdValue >> 32 );
	return qtrue;
}

/*
=============
CL_SteamResources_FindSlot

Returns an existing slot for the URL or the first available free slot.
=============
*/
static clSteamResource_t *CL_SteamResources_FindSlot( const char *url ) {
	int i;
	clSteamResource_t *freeSlot = NULL;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		clSteamResource_t *entry = &cl_steamResources[i];

		if ( entry->url[0] && !Q_stricmp( entry->url, url ) ) {
			return entry;
		}

		if ( !entry->url[0] && !freeSlot ) {
			freeSlot = entry;
		}
	}

	return freeSlot;
}

/*
=============
CL_SteamResources_AssignSlot

Stores the resolved shader and cache path for a Steam resource.
=============
*/
static void CL_SteamResources_AssignSlot( clSteamResource_t *slot, const char *url, const char *cachePath, qhandle_t shader, qboolean persisted ) {
	if ( !slot ) {
		return;
	}

	Q_strncpyz( slot->url, url, sizeof( slot->url ) );
	Q_strncpyz( slot->cachePath, cachePath, sizeof( slot->cachePath ) );
	slot->shader = shader;
	slot->persisted = persisted;
}

/*
=============
CL_SteamResources_SanitizeCacheName

Builds a cache file path under fs_homepath for the provided cached resource URL.
=============
*/
static void CL_SteamResources_SanitizeCacheName( const char *url, char *cachePath, size_t cachePathSize ) {
	const char *payload;
	const char *suffix;
	char sanitized[MAX_QPATH];
	unsigned checksum;
	int i;
	const char *cacheFolder;

	if ( !cachePath || cachePathSize == 0 || !url ) {
		return;
	}

	payload = url;
	if ( CL_SteamResources_IsSteamURL( url ) ) {
		payload = url + strlen( STEAM_URL_PREFIX );
	}

	Q_strncpyz( sanitized, payload, sizeof( sanitized ) );
	for ( i = 0; sanitized[i]; i++ ) {
		char ch = sanitized[i];
		if ( !( ( ch >= 'a' && ch <= 'z' ) || ( ch >= 'A' && ch <= 'Z' ) || ( ch >= '0' && ch <= '9' ) || ch == '.' || ch == '-' || ch == '_' ) ) {
			sanitized[i] = '_';
		}
	}

	cacheFolder = ( cl_steamCachePath && cl_steamCachePath->string[0] ) ? cl_steamCachePath->string : "steamcache";
	checksum = Com_BlockChecksum( url, strlen( url ) );
	suffix = CL_SteamResources_IsAvatarURL( url ) ? ".tga" : "";
	Com_sprintf( cachePath, cachePathSize, "%s/%08x_%s%s", cacheFolder, checksum, sanitized, suffix );
}


/*
=============
CL_SteamResources_RegisterCachedShader

Registers a shader from an existing cache file if one is present.
=============
*/
static qboolean CL_SteamResources_RegisterCachedShader( const char *cachePath, qhandle_t *shader ) {
	if ( !cachePath || !cachePath[0] || !shader ) {
		return qfalse;
	}

	if ( !FS_FileExists( cachePath ) ) {
		return qfalse;
	}

	*shader = re.RegisterShaderNoMip( cachePath );
	return ( *shader != 0 );
}

/*
=============
CL_SteamResources_WriteCacheFile

Writes downloaded image bytes to a cache file under fs_homepath.
=============
*/
static qboolean CL_SteamResources_WriteCacheFile( const char *cachePath, const byte *buffer, int length ) {
	fileHandle_t handle;

	if ( !cachePath || !cachePath[0] || !buffer || length <= 0 ) {
		return qfalse;
	}

	handle = FS_FOpenFileWrite( cachePath );
	if ( !handle ) {
		return qfalse;
	}

	FS_Write( buffer, length, handle );
	FS_FCloseFile( handle );
	return qtrue;
}

/*
=============
CL_SteamResources_RemoveCacheFile

Removes a cached launcher/Steam resource file from fs_homepath.
=============
*/
static void CL_SteamResources_RemoveCacheFile( const char *cachePath ) {
	const char *homePath;
	const char *gameDir;
	char *ospath;

	if ( !cachePath || !cachePath[0] ) {
		return;
	}

	homePath = Cvar_VariableString( "fs_homepath" );
	gameDir = Cvar_VariableString( "fs_gamedirvar" );
	if ( !gameDir || !gameDir[0] ) {
		gameDir = Cvar_VariableString( "fs_game" );
	}
	if ( !gameDir || !gameDir[0] ) {
		gameDir = BASEGAME;
	}

	ospath = FS_BuildOSPath( homePath, gameDir, cachePath );
	remove( ospath );
}

/*
=============
CL_SteamResources_ClearSlot

Drops one cached resource slot and removes any session-owned files that should
not survive the current invalidation request.
=============
*/
static void CL_SteamResources_ClearSlot( clSteamResource_t *slot, qboolean clearPersisted ) {
	if ( !slot ) {
		return;
	}

	if ( slot->cachePath[0] && ( clearPersisted || !slot->persisted ) ) {
		CL_SteamResources_RemoveCacheFile( slot->cachePath );
	}

	Com_Memset( slot, 0, sizeof( *slot ) );
}

/*
=============
CL_SteamResources_RequestAndCache

Downloads a Steam resource, stores it to disk when requested, and registers a shader for UI use.
=============
*/
static qboolean CL_SteamResources_RequestAndCache( const char *url, const char *cachePath, qboolean persist, qhandle_t *shader ) {
	byte *buffer = NULL;
	int length = 0;
	qboolean wroteCache;

	if ( !shader ) {
		return qfalse;
	}

	if ( !Sys_Steam_RequestURL( url, &buffer, &length ) || !buffer || length <= 0 ) {
		return qfalse;
	}

	wroteCache = CL_SteamResources_WriteCacheFile( cachePath, buffer, length );
	Sys_Steam_FreeRequestBuffer( buffer );

	if ( !wroteCache ) {
		return qfalse;
	}

	*shader = re.RegisterShaderNoMip( cachePath );
	if ( *shader && !persist ) {
		CL_SteamResources_RemoveCacheFile( cachePath );
	}

	return ( *shader != 0 );
}

/*
=============
CL_SteamResources_EncodeAvatarTGA

Converts Steam RGBA avatar pixels into a bottom-up BGRA TGA payload for the renderer cache.
=============
*/
static qboolean CL_SteamResources_EncodeAvatarTGA( const uint8_t *rgbaPixels, uint32_t width, uint32_t height, byte **outBuffer, int *outSize ) {
	size_t pixelCount;
	size_t imageSize;
	size_t totalSize;
	byte *buffer;
	byte *dst;
	uint32_t y;
	uint32_t x;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}
	if ( outSize ) {
		*outSize = 0;
	}

	if ( !rgbaPixels || width == 0 || height == 0 || !outBuffer || !outSize ) {
		return qfalse;
	}

	pixelCount = (size_t)width * (size_t)height;
	if ( pixelCount > ( (size_t)( INT_MAX - 18 ) / 4 ) ) {
		return qfalse;
	}

	imageSize = pixelCount * 4;
	totalSize = imageSize + 18;
	buffer = (byte *)Z_Malloc( (int)totalSize );
	if ( !buffer ) {
		return qfalse;
	}

	Com_Memset( buffer, 0, (int)totalSize );
	buffer[2] = 2;
	buffer[12] = (byte)( width & 0xff );
	buffer[13] = (byte)( ( width >> 8 ) & 0xff );
	buffer[14] = (byte)( height & 0xff );
	buffer[15] = (byte)( ( height >> 8 ) & 0xff );
	buffer[16] = 32;
	buffer[17] = 8;

	dst = buffer + 18;
	for ( y = 0; y < height; ++y ) {
		const uint8_t *srcRow = rgbaPixels + ( (size_t)( height - y - 1 ) * width * 4 );

		for ( x = 0; x < width; ++x ) {
			const uint8_t *srcPixel = srcRow + (size_t)x * 4;

			*dst++ = srcPixel[2];
			*dst++ = srcPixel[1];
			*dst++ = srcPixel[0];
			*dst++ = srcPixel[3];
		}
	}

	*outBuffer = buffer;
	*outSize = (int)totalSize;
	return qtrue;
}

/*
=============
CL_SteamResources_RequestAvatar

Resolves a steam://avatar URL through the Steamworks avatar APIs and emits a cacheable TGA payload.
=============
*/
static qboolean CL_SteamResources_RequestAvatar( const char *url, byte **outBuffer, int *outSize ) {
	ql_steam_avatar_size_t size;
	uint32_t idLow;
	uint32_t idHigh;
	uint8_t *rgbaPixels;
	uint32_t width;
	uint32_t height;

	if ( !CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh ) ) {
		return qfalse;
	}

	rgbaPixels = NULL;
	width = 0;
	height = 0;
	if ( !QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height ) || !rgbaPixels ) {
		return qfalse;
	}

	if ( !CL_SteamResources_EncodeAvatarTGA( rgbaPixels, width, height, outBuffer, outSize ) ) {
		QL_Steamworks_FreeBuffer( rgbaPixels );
		return qfalse;
	}

	QL_Steamworks_FreeBuffer( rgbaPixels );
	return qtrue;
}

/*
=============
CL_Steam_RegisterShader

Resolves a Steam-backed resource into a renderer handle compatible with the menu image cache.
=============
*/
qhandle_t CL_Steam_RegisterShader( const char *url ) {
	clSteamResource_t *slot;
	char cachePath[MAX_QPATH];
	qhandle_t shader = 0;
	qboolean persist;

	if ( !CL_SteamResources_IsURIResource( url ) ) {
		return re.RegisterShaderNoMip( url );
	}

	if ( CL_SteamResources_IsSteamURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			Com_DPrintf( "UI: Steam resource request stubbed for %s\n", url ? url : "<null>" );
			return 0;
		}
	} else if ( !CL_OnlineServicesEnabled() ) {
		Com_DPrintf( "UI: launcher resource request stubbed for %s\n", url ? url : "<null>" );
		return 0;
	}

	slot = CL_SteamResources_FindSlot( url );
	persist = ( cl_steamCachePersist && cl_steamCachePersist->integer );
	CL_SteamResources_SanitizeCacheName( url, cachePath, sizeof( cachePath ) );

	if ( slot && slot->shader ) {
		return slot->shader;
	}

	if ( CL_SteamResources_RegisterCachedShader( cachePath, &shader ) ) {
		CL_SteamResources_AssignSlot( slot, url, cachePath, shader, qtrue );
		return shader;
	}

	if ( CL_SteamResources_RequestAndCache( url, cachePath, persist, &shader ) ) {
		CL_SteamResources_AssignSlot( slot, url, cachePath, shader, persist );
		return shader;
	}

	Com_Printf( "UI: unable to satisfy cached resource request for %s\n", url );
	return 0;
}


/*
=============
CL_ClearSteamResourceCache

Clears the retained URI cache bookkeeping and removes session-owned cache files.
=============
*/
void CL_ClearSteamResourceCache( qboolean clearPersisted ) {
	int i;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		CL_SteamResources_ClearSlot( &cl_steamResources[i], clearPersisted );
	}
}

/*
=============
CL_InitSteamResources

Initialises the Steam resource bridge and related configuration.
=============
*/
void CL_InitSteamResources( void ) {
	Com_Memset( cl_steamResources, 0, sizeof( cl_steamResources ) );
	cl_steamCachePersist = Cvar_Get( "cl_steamCachePersist", CL_SteamServicesEnabled() ? "1" : "0", CVAR_ARCHIVE );
	cl_steamCachePath = Cvar_Get( "cl_steamCachePath", "steamcache", CVAR_ARCHIVE );

	if ( !CL_SteamServicesEnabled() ) {
		Com_Printf( "Steam resource bridge disabled by build/runtime policy\n" );
	}
}

/*
=============
CL_ShutdownSteamResources

Clears any cached Steam resource bookkeeping.
=============
*/
void CL_ShutdownSteamResources( void ) {
	CL_ClearSteamResourceCache( qfalse );
}

/*
=============
Sys_Steam_RequestURL

Retrieves a Steam-backed or launcher-backed URL payload for the UI image cache.
=============
*/
qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {
	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outSize ) {
		*outSize = 0;
	}

	if ( CL_SteamResources_IsAvatarURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			Com_Printf( "Steam backend disabled by build/runtime policy for %s\n", url ? url : "<null>" );
			return qfalse;
		}

		if ( CL_SteamResources_RequestAvatar( url, outBuffer, outSize ) ) {
			return qtrue;
		}

		Com_Printf( "Steam avatar backend unavailable for %s\n", url ? url : "<null>" );
		return qfalse;
	}

	if ( CL_LauncherRequestData( url, (void **)outBuffer, outSize ) ) {
		return qtrue;
	}

	if ( CL_SteamResources_IsSteamURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			Com_Printf( "Steam backend disabled by build/runtime policy for %s\n", url ? url : "<null>" );
		} else {
			Com_Printf( "Steam backend unavailable for %s\n", url ? url : "<null>" );
		}
	} else if ( !CL_OnlineServicesEnabled() ) {
		Com_Printf( "Launcher backend disabled by build/runtime policy for %s\n", url ? url : "<null>" );
	} else {
		Com_Printf( "Launcher resource backend unavailable for %s\n", url ? url : "<null>" );
	}

	return qfalse;
}

/*
=============
Sys_Steam_FreeRequestBuffer

Releases buffers allocated by Sys_Steam_RequestURL.
=============
*/
void Sys_Steam_FreeRequestBuffer( byte *buffer ) {
	if ( buffer ) {
		Z_Free( buffer );
	}
}

