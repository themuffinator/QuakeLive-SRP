#include "client.h"

#include <limits.h>
#include <stdlib.h>

#include "../../common/platform/platform_services.h"
#include "../../common/platform/platform_steamworks.h"

#define MAX_STEAM_RESOURCES 64
#define STEAM_URL_PREFIX "steam://"
#define QL_RESOURCE_INTERCEPTOR_HOST "ql"
#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH "/screenshot"
#define QL_RESOURCE_INTERCEPTOR_WEB_FALLBACK_PREFIX "https://cdn.quakelive.com/"
#define QL_RESOURCE_INTERCEPTOR_SCREENSHOT_FALLBACK_PREFIX "quakelive://screenshots/"

typedef struct {
	char		url[MAX_QPATH];
	char		rendererName[MAX_QPATH];
	qhandle_t	shader;
} clSteamResource_t;

typedef struct {
	byte		*buffer;
	int			bufferLength;
	byte		*rgbaPixels;
	int			width;
	int			height;
	char		mimeType[64];
	qboolean	fromSteamDataSource;
} clSteamDataSourceResponse_t;

typedef struct {
	uint32_t	idLow;
	uint32_t	idHigh;
} clSteamPendingAvatar_t;

typedef struct {
	char	host[64];
	char	path[MAX_QPATH];
	char	filename[MAX_QPATH];
} clResourceInterceptorUrl_t;

typedef struct {
	const char	*retailOwner;
	const char	*retailMember;
	unsigned int	retailVtableAddress;
	unsigned int	retailOffset;
	unsigned int	retailAddress;
	const char	*sourceOwner;
	const char	*scope;
} clSteamDataSourceRetailMapping_t;

typedef struct {
	const char	*retailOwner;
	const char	*retailMember;
	unsigned int	retailVtableAddress;
	unsigned int	retailOffset;
	unsigned int	retailAddress;
	const char	*retailLiteral;
	const char	*sourceOwner;
	const char	*scope;
} clSteamResponseThreadRetailMapping_t;

#define CL_STEAM_DATA_SOURCE_SCOPE_COMPATIBILITY_OWNER "bounded compatibility owner"
#define CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK "avatar callback bridge"
#define CL_STEAM_DATA_SOURCE_SCOPE_ASYNC_BOUNDARY "bounded async response owner"
#define CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY "retail lifecycle boundary"
#define CL_STEAM_DATA_SOURCE_SCOPE_DESTRUCTOR "retail destructor-owned"

static const clSteamDataSourceRetailMapping_t cl_steamDataSourceRetailMappings[] = {
	{ "SteamDataSource", "destroy", 0x00532B80u, 0x00u, 0x00464510u, "CL_ShutdownSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_DESTRUCTOR },
	{ "SteamDataSource", "OnRequest", 0x00532B80u, 0x04u, 0x004640C0u, "CL_SteamDataSource_Request", CL_STEAM_DATA_SOURCE_SCOPE_COMPATIBILITY_OWNER },
	{ "SteamDataSource", "StartResponseThread", 0u, 0u, 0x00463550u, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_DATA_SOURCE_SCOPE_ASYNC_BOUNDARY },
	{ "SteamDataSource", "Init", 0u, 0u, 0x00464300u, "CL_InitSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY },
	{ "SteamDataSource", "Shutdown", 0u, 0u, 0x00464440u, "CL_ShutdownSteamResources", CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY },
	{ "CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>", "callback target", 0x00532B68u, 0x10u, 0x00464290u, "CL_SteamResources_OnAvatarImageLoaded", CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK },
	{ "CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>", "callback id", 0x00532B68u, 0x14Eu, 0x00464300u, "CL_SteamResources_RegisterAvatarCallbacks", CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK },
	{ NULL, NULL, 0u, 0u, 0u, NULL, NULL }
};

#undef CL_STEAM_DATA_SOURCE_SCOPE_DESTRUCTOR
#undef CL_STEAM_DATA_SOURCE_SCOPE_LIFECYCLE_BOUNDARY
#undef CL_STEAM_DATA_SOURCE_SCOPE_ASYNC_BOUNDARY
#undef CL_STEAM_DATA_SOURCE_SCOPE_AVATAR_CALLBACK
#undef CL_STEAM_DATA_SOURCE_SCOPE_COMPATIBILITY_OWNER

#define CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE 0x00532B44u
#define CL_STEAM_RESPONSE_THREAD_MIME_TYPE "image/png"
#define CL_STEAM_RESPONSE_THREAD_THREAD_NAME "request_%i"
#define CL_STEAM_RESPONSE_THREAD_PNG_VERSION "1.2.24"
#define CL_STEAM_RESPONSE_THREAD_WRITE_ERROR "Write Error"
#define CL_STEAM_RESPONSE_THREAD_STACK_RESERVE "0x100000"
#define CL_STEAM_RESPONSE_THREAD_SCOPE_ASYNC_BOUNDARY "bounded async response owner"
#define CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER "retail PNG helper"
#define CL_STEAM_RESPONSE_THREAD_SCOPE_SEND_RESPONSE "Awesomium SendResponse boundary"
#define CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START "retail thread-start contract"

static const clSteamResponseThreadRetailMapping_t cl_steamResponseThreadRetailMappings[] = {
	{ "ResponseThread", "run", CL_STEAM_RESPONSE_THREAD_RETAIL_VTABLE, 0x04u, 0x00463440u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_ASYNC_BOUNDARY },
	{ "ResponseThread", "PNGWriteCallback", 0u, 0u, 0x00463110u, CL_STEAM_RESPONSE_THREAD_WRITE_ERROR, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER },
	{ "ResponseThread", "EncodeAvatarPNG", 0u, 0u, 0x00463180u, CL_STEAM_RESPONSE_THREAD_PNG_VERSION, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER },
	{ "Awesomium::DataSource", "SendResponse import", 0u, 0u, 0x0052C6B0u, CL_STEAM_RESPONSE_THREAD_MIME_TYPE, "QLResourceInterceptor_OnRequest", CL_STEAM_RESPONSE_THREAD_SCOPE_SEND_RESPONSE },
	{ "SteamDataSource", "StartResponseThread", 0u, 0u, 0x00463550u, CL_STEAM_RESPONSE_THREAD_THREAD_NAME, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START },
	{ "SteamDataSource", "ResponseThread stack reserve", 0u, 0x100000u, 0x00463550u, CL_STEAM_RESPONSE_THREAD_STACK_RESERVE, "CL_SteamResources_RequestAvatarRGBA", CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START },
	{ NULL, NULL, 0u, 0u, 0u, NULL, NULL, NULL }
};

#undef CL_STEAM_RESPONSE_THREAD_SCOPE_THREAD_START
#undef CL_STEAM_RESPONSE_THREAD_SCOPE_SEND_RESPONSE
#undef CL_STEAM_RESPONSE_THREAD_SCOPE_PNG_HELPER
#undef CL_STEAM_RESPONSE_THREAD_SCOPE_ASYNC_BOUNDARY

static clSteamResource_t cl_steamResources[MAX_STEAM_RESOURCES];
static clSteamPendingAvatar_t cl_steamPendingAvatars[MAX_STEAM_RESOURCES];
static unsigned int cl_steamResourceGeneration = 1;
static qboolean cl_steamAvatarCallbacksRegistered = qfalse;

qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize );
void Sys_Steam_FreeRequestBuffer( byte *buffer );

/*
=============
CL_GetSteamResourceServiceDescriptor

Returns the retained platform-service descriptor that owns the browser/live
resource bridge compatibility boundary.
=============
*/
static const ql_platform_feature_descriptor *CL_GetSteamResourceServiceDescriptor( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();

	if ( !services ) {
		return NULL;
	}

	return &services->overlay;
}

/*
=============
CL_GetSteamResourceServiceProviderLabel

Returns the human-readable provider label for the browser/live resource bridge.
=============
*/
static const char *CL_GetSteamResourceServiceProviderLabel( void ) {
	const ql_platform_feature_descriptor *descriptor = CL_GetSteamResourceServiceDescriptor();

	if ( !descriptor || !descriptor->provider ) {
		return "Unavailable";
	}

	return descriptor->provider;
}

/*
=============
CL_GetSteamResourceServicePolicyLabel

Returns the short compatibility policy label for the browser/live resource
bridge.
=============
*/
static const char *CL_GetSteamResourceServicePolicyLabel( void ) {
	return QL_DescribePlatformFeaturePolicy( CL_GetSteamResourceServiceDescriptor() );
}

/*
=============
CL_GetSteamDataSourceSubsetLabel

Returns the currently reconstructed SteamDataSource ownership scope.
=============
*/
static const char *CL_GetSteamDataSourceSubsetLabel( void ) {
	return "avatar-only SteamDataSource";
}

/*
=============
CL_GetSteamDataSourceNativeGapLabel

Returns the broader SteamDataSource owner that is intentionally not
reconstructed by the current avatar-only subset.
=============
*/
static const char *CL_GetSteamDataSourceNativeGapLabel( void ) {
	return "missing non-avatar SteamDataSource owner";
}

/*
=============
CL_GetSteamDataSourceFallbackOwnerLabel

Returns the retained resource owner that receives SteamDataSource requests
outside the reconstructed avatar-native subset.
=============
*/
static const char *CL_GetSteamDataSourceFallbackOwnerLabel( void ) {
	return "QLResourceInterceptor launcher/web fallback";
}

/*
=============
CL_CountSteamDataSourceRetailMappings

Returns the number of recovered retail SteamDataSource and callback wiring
anchors retained by the bounded browser resource bridge.
=============
*/
static int CL_CountSteamDataSourceRetailMappings( void ) {
	int count;
	int i;

	count = 0;
	for ( i = 0; cl_steamDataSourceRetailMappings[i].retailOwner; i++ ) {
		if ( cl_steamDataSourceRetailMappings[i].retailAddress != 0u ) {
			count++;
		}
	}

	return count;
}

/*
=============
CL_CountSteamResponseThreadRetailMappings

Returns the number of recovered retail ResponseThread anchors retained as a
bounded async response contract for the SteamDataSource avatar lane.
=============
*/
static int CL_CountSteamResponseThreadRetailMappings( void ) {
	int count;
	int i;

	count = 0;
	for ( i = 0; cl_steamResponseThreadRetailMappings[i].retailOwner; i++ ) {
		if ( cl_steamResponseThreadRetailMappings[i].retailAddress != 0u ) {
			count++;
		}
	}

	return count;
}

/*
=============
CL_LogSteamResourceBridgeUnavailable

Publishes provider-aware diagnostics whenever the retained Steam resource
bridge cannot satisfy a request.
=============
*/
static void CL_LogSteamResourceBridgeUnavailable( const char *url, const char *reason ) {
	Com_Printf( "Steam resource bridge unavailable for %s via %s [%s] (%s; fallback=%s; gap=%s); %s\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel(),
		CL_GetSteamDataSourceSubsetLabel(),
		CL_GetSteamDataSourceFallbackOwnerLabel(),
		CL_GetSteamDataSourceNativeGapLabel(),
		reason ? reason : "request could not be satisfied" );
}

/*
=============
CL_LogLauncherResourceFallbackUnavailable

Publishes provider-aware diagnostics when the retained launcher/web fallback
owner cannot satisfy a live resource request.
=============
*/
static void CL_LogLauncherResourceFallbackUnavailable( const char *url, const char *reason ) {
	Com_Printf( "Launcher/web fallback unavailable for %s via %s [%s]; %s\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel(),
		reason ? reason : "no launcher/web resource owner is available" );
}

/*
=============
CL_LogSteamResourceRequestStubbed

Publishes provider-aware diagnostics when the UI-side Steam resource request is
stubbed by the current compatibility policy.
=============
*/
static void CL_LogSteamResourceRequestStubbed( const char *url ) {
	Com_DPrintf( "UI: Steam resource request stubbed for %s via %s [%s]\n",
		url ? url : "<null>",
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel() );
}

/*
=============
CL_RefreshSteamResourceBridgeCvars

Mirrors the retained live-resource bridge provider, policy, and parity-scope
labels through ROM cvars for diagnostics and bounded compatibility reporting.
=============
*/
static void CL_RefreshSteamResourceBridgeCvars( void ) {
	Cvar_Set( "ui_resourceBridgeProvider", CL_GetSteamResourceServiceProviderLabel() );
	Cvar_Set( "ui_resourceBridgePolicy", CL_GetSteamResourceServicePolicyLabel() );
	Cvar_Set( "ui_resourceBridgeParityScope", QL_GetOnlineServicesParityScopeLabel() );
	Cvar_Set( "ui_resourceBridgeParityReason", QL_GetOnlineServicesParityReasonLabel() );
	Cvar_Set( "ui_resourceBridgeSteamDataSourceSubset", CL_GetSteamDataSourceSubsetLabel() );
	Cvar_Set( "ui_resourceBridgeSteamDataSourceNativeGap", CL_GetSteamDataSourceNativeGapLabel() );
	Cvar_Set( "ui_resourceBridgeSteamDataSourceFallbackOwner", CL_GetSteamDataSourceFallbackOwnerLabel() );
	Cvar_Set( "ui_resourceBridgeSteamDataSourceMappings", va( "%i", CL_CountSteamDataSourceRetailMappings() ) );
	Cvar_Set( "ui_resourceBridgeResponseThreadMappings", va( "%i", CL_CountSteamResponseThreadRetailMappings() ) );
}

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
through the launcher/Steam live-resource bridge instead of the normal shader
loader.
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
CL_SteamResources_ClearPendingAvatars
=============
*/
static void CL_SteamResources_ClearPendingAvatars( void ) {
	Com_Memset( cl_steamPendingAvatars, 0, sizeof( cl_steamPendingAvatars ) );
}

/*
=============
CL_SteamResources_IsPendingAvatar
=============
*/
static qboolean CL_SteamResources_IsPendingAvatar( uint32_t idLow, uint32_t idHigh ) {
	int i;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		if ( cl_steamPendingAvatars[i].idLow == idLow && cl_steamPendingAvatars[i].idHigh == idHigh ) {
			return ( idLow != 0 || idHigh != 0 ) ? qtrue : qfalse;
		}
	}

	return qfalse;
}

/*
=============
CL_SteamResources_MarkPendingAvatar
=============
*/
static void CL_SteamResources_MarkPendingAvatar( uint32_t idLow, uint32_t idHigh ) {
	int i;
	int freeIndex;

	if ( idLow == 0 && idHigh == 0 ) {
		return;
	}

	freeIndex = -1;
	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		if ( cl_steamPendingAvatars[i].idLow == idLow && cl_steamPendingAvatars[i].idHigh == idHigh ) {
			return;
		}

		if ( freeIndex < 0 && cl_steamPendingAvatars[i].idLow == 0 && cl_steamPendingAvatars[i].idHigh == 0 ) {
			freeIndex = i;
		}
	}

	if ( freeIndex < 0 ) {
		return;
	}

	cl_steamPendingAvatars[freeIndex].idLow = idLow;
	cl_steamPendingAvatars[freeIndex].idHigh = idHigh;
}

/*
=============
CL_SteamResources_ClearPendingAvatar
=============
*/
static qboolean CL_SteamResources_ClearPendingAvatar( uint32_t idLow, uint32_t idHigh ) {
	int i;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		if ( cl_steamPendingAvatars[i].idLow == idLow && cl_steamPendingAvatars[i].idHigh == idHigh ) {
			cl_steamPendingAvatars[i].idLow = 0;
			cl_steamPendingAvatars[i].idHigh = 0;
			return qtrue;
		}
	}

	return qfalse;
}

/*
=============
CL_SteamResources_IsPendingAvatarURL
=============
*/
static qboolean CL_SteamResources_IsPendingAvatarURL( const char *url ) {
	ql_steam_avatar_size_t size;
	uint32_t idLow;
	uint32_t idHigh;

	if ( !CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh ) ) {
		return qfalse;
	}

	return CL_SteamResources_IsPendingAvatar( idLow, idHigh );
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

Stores the resolved shader and renderer-owned resource name for a Steam
resource.
=============
*/
static void CL_SteamResources_AssignSlot( clSteamResource_t *slot, const char *url, const char *rendererName, qhandle_t shader ) {
	if ( !slot ) {
		return;
	}

	Q_strncpyz( slot->url, url, sizeof( slot->url ) );
	Q_strncpyz( slot->rendererName, rendererName, sizeof( slot->rendererName ) );
	slot->shader = shader;
}

/*
=============
CL_SteamResources_BuildRendererName

Builds a short, renderer-owned name for one retained live resource slot. The
generation counter keeps reloads from silently reusing stale renderer images
after the client-side resource table is cleared.
=============
*/
static void CL_SteamResources_BuildRendererName( const char *url, const clSteamResource_t *slot, char *rendererName, size_t rendererNameSize ) {
	unsigned checksum;
	int slotIndex;

	if ( !rendererName || rendererNameSize == 0 || !url ) {
		return;
	}

	slotIndex = 0;
	if ( slot ) {
		slotIndex = (int)( slot - cl_steamResources );
	}

	checksum = Com_BlockChecksum( url, strlen( url ) );
	Com_sprintf( rendererName, rendererNameSize, "*steamres/%u/%02d/%08x", cl_steamResourceGeneration, slotIndex, checksum );
}

/*
=============
CL_SteamResources_ClearSlot

Drops one cached live-resource slot.
=============
*/
static void CL_SteamResources_ClearSlot( clSteamResource_t *slot, qboolean clearPersisted ) {
	(void)clearPersisted;

	if ( !slot ) {
		return;
	}

	Com_Memset( slot, 0, sizeof( *slot ) );
}

/*
=============
CL_SteamResources_OnAvatarImageLoaded
=============
*/
static void CL_SteamResources_OnAvatarImageLoaded( void *context, const ql_steam_avatar_image_loaded_t *event ) {
	unsigned long long steamIdValue;

	(void)context;

	if ( !event ) {
		return;
	}

	steamIdValue = event->steamId.value;
	if ( !CL_SteamResources_ClearPendingAvatar( (uint32_t)steamIdValue, (uint32_t)( steamIdValue >> 32 ) ) ) {
		return;
	}

	Com_DPrintf( "Steam avatar image loaded for %llu via %s [%s]; pending avatar request may be retried.\n",
		(unsigned long long)steamIdValue,
		CL_GetSteamResourceServiceProviderLabel(),
		CL_GetSteamResourceServicePolicyLabel() );
}

/*
=============
CL_SteamResources_RegisterAvatarCallbacks
=============
*/
static void CL_SteamResources_RegisterAvatarCallbacks( void ) {
	ql_steam_avatar_callback_bindings_t bindings;

	if ( cl_steamAvatarCallbacksRegistered || !CL_SteamServicesEnabled() ) {
		return;
	}

	Com_Memset( &bindings, 0, sizeof( bindings ) );
	bindings.onAvatarImageLoaded = CL_SteamResources_OnAvatarImageLoaded;
	if ( !QL_Steamworks_RegisterAvatarCallbacks( &bindings ) ) {
		Com_DPrintf( "Steam avatar callback owner unavailable for %s [%s]; keeping synchronous retry path.\n",
			CL_GetSteamResourceServiceProviderLabel(),
			CL_GetSteamResourceServicePolicyLabel() );
		return;
	}

	cl_steamAvatarCallbacksRegistered = qtrue;
}

/*
=============
CL_SteamResources_UnregisterAvatarCallbacks
=============
*/
static void CL_SteamResources_UnregisterAvatarCallbacks( void ) {
	if ( !cl_steamAvatarCallbacksRegistered ) {
		return;
	}

	QL_Steamworks_UnregisterAvatarCallbacks();
	cl_steamAvatarCallbacksRegistered = qfalse;
}

/*
=============
CL_SteamResources_RequestAvatarRGBA

Resolves a steam://avatar URL through the Steamworks avatar APIs and returns
the live RGBA payload directly for renderer-owned image creation.
=============
*/
static qboolean CL_SteamResources_RequestAvatarRGBA( const char *url, byte **outPixels, int *outWidth, int *outHeight ) {
	ql_steam_avatar_size_t size;
	uint32_t idLow;
	uint32_t idHigh;
	uint8_t *rgbaPixels;
	uint32_t width;
	uint32_t height;
	ql_steam_avatar_image_state_t avatarState;

	if ( outPixels ) {
		*outPixels = NULL;
	}
	if ( outWidth ) {
		*outWidth = 0;
	}
	if ( outHeight ) {
		*outHeight = 0;
	}

	if ( !CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh ) ) {
		return qfalse;
	}

	avatarState = QL_Steamworks_RequestAvatarImage( idLow, idHigh, size, NULL );
	if ( avatarState == QL_STEAM_AVATAR_IMAGE_PENDING ) {
		CL_SteamResources_MarkPendingAvatar( idLow, idHigh );
		return qfalse;
	}

	CL_SteamResources_ClearPendingAvatar( idLow, idHigh );
	if ( avatarState != QL_STEAM_AVATAR_IMAGE_READY ) {
		return qfalse;
	}

	rgbaPixels = NULL;
	width = 0;
	height = 0;
	if ( !QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height ) || !rgbaPixels ) {
		return qfalse;
	}

	if ( width == 0 || height == 0 || width > INT_MAX || height > INT_MAX ) {
		QL_Steamworks_FreeBuffer( rgbaPixels );
		return qfalse;
	}

	if ( outPixels ) {
		*outPixels = rgbaPixels;
	}
	if ( outWidth ) {
		*outWidth = (int)width;
	}
	if ( outHeight ) {
		*outHeight = (int)height;
	}

	return qtrue;
}

/*
=============
CL_SteamDataSource_ClearResponse
=============
*/
static void CL_SteamDataSource_ClearResponse( clSteamDataSourceResponse_t *response ) {
	if ( !response ) {
		return;
	}

	Com_Memset( response, 0, sizeof( *response ) );
}

/*
=============
CL_SteamDataSource_GuessMimeType
=============
*/
static const char *CL_SteamDataSource_GuessMimeType( const char *url ) {
	const char *extension;

	if ( !url ) {
		return "application/octet-stream";
	}

	extension = strrchr( url, '.' );
	if ( !extension ) {
		return "application/octet-stream";
	}

	if ( !Q_stricmp( extension, ".jpg" ) || !Q_stricmp( extension, ".jpeg" ) ) {
		return "image/jpeg";
	}

	if ( !Q_stricmp( extension, ".png" ) ) {
		return "image/png";
	}

	if ( !Q_stricmp( extension, ".gif" ) ) {
		return "image/gif";
	}

	if ( !Q_stricmp( extension, ".html" ) || !Q_stricmp( extension, ".htm" ) ) {
		return "text/html";
	}

	if ( !Q_stricmp( extension, ".js" ) ) {
		return "application/javascript";
	}

	if ( !Q_stricmp( extension, ".css" ) ) {
		return "text/css";
	}

	if ( !Q_stricmp( extension, ".json" ) ) {
		return "application/json";
	}

	return "application/octet-stream";
}

/*
=============
QLResourceInterceptor_OnFilterNavigation

Mirrors retail sub_434600: the resource interceptor never blocks navigation.
=============
*/
static qboolean QLResourceInterceptor_OnFilterNavigation( const char *url ) {
	(void)url;
	return qfalse;
}

/*
=============
QLResourceInterceptor_ParseURL
=============
*/
static qboolean QLResourceInterceptor_ParseURL( const char *url, clResourceInterceptorUrl_t *parsed ) {
	const char *scheme;
	const char *hostStart;
	const char *hostEnd;
	const char *pathStart;
	const char *pathEnd;
	const char *filename;
	size_t hostLength;
	size_t pathLength;

	if ( !url || !parsed ) {
		return qfalse;
	}

	Com_Memset( parsed, 0, sizeof( *parsed ) );

	scheme = strstr( url, "://" );
	if ( !scheme ) {
		return qfalse;
	}

	hostStart = scheme + 3;
	if ( !hostStart[0] ) {
		return qfalse;
	}

	hostEnd = hostStart;
	while ( *hostEnd && *hostEnd != '/' && *hostEnd != '\\' && *hostEnd != '?' && *hostEnd != '#' ) {
		++hostEnd;
	}

	hostLength = (size_t)( hostEnd - hostStart );
	if ( hostLength == 0 || hostLength >= sizeof( parsed->host ) ) {
		return qfalse;
	}

	memcpy( parsed->host, hostStart, hostLength );
	parsed->host[hostLength] = '\0';

	pathStart = hostEnd;
	if ( *pathStart != '/' && *pathStart != '\\' ) {
		Q_strncpyz( parsed->path, "/", sizeof( parsed->path ) );
		parsed->filename[0] = '\0';
		return qtrue;
	}

	pathEnd = pathStart;
	while ( *pathEnd && *pathEnd != '?' && *pathEnd != '#' ) {
		++pathEnd;
	}

	pathLength = (size_t)( pathEnd - pathStart );
	if ( pathLength == 0 || pathLength >= sizeof( parsed->path ) ) {
		return qfalse;
	}

	memcpy( parsed->path, pathStart, pathLength );
	parsed->path[pathLength] = '\0';

	for ( filename = parsed->path + strlen( parsed->path ); filename > parsed->path; --filename ) {
		if ( filename[-1] == '/' || filename[-1] == '\\' ) {
			break;
		}
	}

	Q_strncpyz( parsed->filename, filename, sizeof( parsed->filename ) );
	return qtrue;
}

/*
=============
QLResourceInterceptor_IsRetailHost
=============
*/
static qboolean QLResourceInterceptor_IsRetailHost( const clResourceInterceptorUrl_t *parsed ) {
	return ( parsed && !Q_stricmp( parsed->host, QL_RESOURCE_INTERCEPTOR_HOST ) ) ? qtrue : qfalse;
}

/*
=============
QLResourceInterceptor_IsScreenshotPath
=============
*/
static qboolean QLResourceInterceptor_IsScreenshotPath( const char *path ) {
	size_t prefixLength;

	if ( !path ) {
		return qfalse;
	}

	prefixLength = strlen( QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH );
	if ( Q_strnicmp( path, QL_RESOURCE_INTERCEPTOR_SCREENSHOT_PATH, prefixLength ) != 0 ) {
		return qfalse;
	}

	return ( path[prefixLength] == '\0' || path[prefixLength] == '/' || path[prefixLength] == '\\' ) ? qtrue : qfalse;
}

/*
=============
QLResourceInterceptor_BuildMappedRequest
=============
*/
static qboolean QLResourceInterceptor_BuildMappedRequest( const clResourceInterceptorUrl_t *parsed, char *mappedUrl, size_t mappedUrlSize ) {
	const char *path;

	if ( !parsed || !mappedUrl || mappedUrlSize == 0 || !QLResourceInterceptor_IsRetailHost( parsed ) ) {
		return qfalse;
	}

	mappedUrl[0] = '\0';
	if ( QLResourceInterceptor_IsScreenshotPath( parsed->path ) ) {
		if ( !parsed->filename[0] ) {
			return qfalse;
		}

		Com_sprintf( mappedUrl, mappedUrlSize, "%s%s", QL_RESOURCE_INTERCEPTOR_SCREENSHOT_FALLBACK_PREFIX, parsed->filename );
		return qtrue;
	}

	path = parsed->path;
	while ( *path == '/' || *path == '\\' ) {
		++path;
	}

	if ( !path[0] ) {
		return qfalse;
	}

	Com_sprintf( mappedUrl, mappedUrlSize, "%s%s", QL_RESOURCE_INTERCEPTOR_WEB_FALLBACK_PREFIX, path );
	return qtrue;
}

/*
=============
QLResourceInterceptor_RequestRetailHost

Projects retail host `ql` requests onto the repository's mapped launcher
fallback roots while keeping the broader compatibility fallback intact.
=============
*/
static qboolean QLResourceInterceptor_RequestRetailHost( const char *url, clSteamDataSourceResponse_t *response ) {
	clResourceInterceptorUrl_t parsed;
	char mappedUrl[MAX_QPATH * 2];

	if ( !url || !response ) {
		return qfalse;
	}

	if ( !QLResourceInterceptor_ParseURL( url, &parsed ) || !QLResourceInterceptor_BuildMappedRequest( &parsed, mappedUrl, sizeof( mappedUrl ) ) ) {
		return qfalse;
	}

	CL_SteamDataSource_ClearResponse( response );
	if ( !CL_LauncherRequestData( mappedUrl, (void **)&response->buffer, &response->bufferLength ) ) {
		return qfalse;
	}

	Q_strncpyz( response->mimeType, CL_SteamDataSource_GuessMimeType( mappedUrl ), sizeof( response->mimeType ) );
	return qtrue;
}

/*
=============
CL_SteamDataSource_Request

Reconstructs the retail SteamDataSource owner by servicing `steam://` resource
requests through the retained avatar/image bridge and launcher-compatible URL
loader surface.
=============
*/
static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {
	if ( !url || !response || !CL_SteamResources_IsSteamURL( url ) ) {
		return qfalse;
	}

	CL_SteamDataSource_ClearResponse( response );
	response->fromSteamDataSource = qtrue;

	if ( CL_SteamResources_IsAvatarURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			CL_LogSteamResourceBridgeUnavailable( url, "keeping launcher/web fallback resource bridge" );
			return qfalse;
		}

		if ( !CL_SteamResources_RequestAvatarRGBA( url, &response->rgbaPixels, &response->width, &response->height ) ) {
			if ( CL_SteamResources_IsPendingAvatarURL( url ) ) {
				CL_LogSteamResourceBridgeUnavailable( url, "avatar request deferred pending AvatarImageLoaded callback" );
			} else {
				CL_LogSteamResourceBridgeUnavailable( url, "avatar request could not be satisfied" );
			}
			return qfalse;
		}

		Q_strncpyz( response->mimeType, "image/rgba", sizeof( response->mimeType ) );
		return qtrue;
	}

	if ( !CL_SteamServicesEnabled() ) {
		CL_LogSteamResourceBridgeUnavailable( url, "non-avatar Steam URI routed to launcher/web fallback owner" );
		return qfalse;
	}

	CL_LogSteamResourceBridgeUnavailable( url, "non-avatar Steam URI routed to launcher/web fallback owner" );
	return qfalse;
}

/*
=============
QLResourceInterceptor_OnRequest

Reconstructs the retained browser-resource interceptor by routing `steam://`
requests through SteamDataSource, projecting retail `ql` host resources onto
the launcher/web filesystem roots, and retaining the broader compatibility
fallback owner for other URI requests.
=============
*/
static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {
	if ( !url || !response ) {
		return qfalse;
	}

	if ( QLResourceInterceptor_OnFilterNavigation( url ) ) {
		return qfalse;
	}

	if ( CL_SteamDataSource_Request( url, response ) ) {
		return qtrue;
	}

	if ( QLResourceInterceptor_RequestRetailHost( url, response ) ) {
		return qtrue;
	}

	CL_SteamDataSource_ClearResponse( response );
	if ( CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength ) ) {
		Q_strncpyz( response->mimeType, CL_SteamDataSource_GuessMimeType( url ), sizeof( response->mimeType ) );
		return qtrue;
	}

	CL_LogLauncherResourceFallbackUnavailable( url, "no launcher/web resource owner is available" );
	return qfalse;
}

/*
=============
CL_Steam_RegisterShader

Resolves a live Steam- or launcher-backed image resource into a renderer
handle compatible with the menu image cache.
=============
*/
qhandle_t CL_Steam_RegisterShader( const char *url ) {
	clSteamResource_t *slot;
	char rendererName[MAX_QPATH];
	byte *buffer;
	int bufferLength;
	byte *rgbaPixels;
	int width;
	int height;
	qhandle_t shader = 0;

	if ( !CL_SteamResources_IsURIResource( url ) ) {
		return re.RegisterShaderNoMip( url );
	}

	if ( CL_SteamResources_IsSteamURL( url ) ) {
		if ( !CL_SteamServicesEnabled() ) {
			CL_LogSteamResourceRequestStubbed( url );
			return 0;
		}
	}

	slot = CL_SteamResources_FindSlot( url );
	if ( !slot ) {
		Com_Printf( "UI: unable to allocate live resource slot for %s\n", url );
		return 0;
	}

	if ( slot->shader ) {
		return slot->shader;
	}

	CL_SteamResources_BuildRendererName( url, slot, rendererName, sizeof( rendererName ) );

	if ( CL_SteamResources_IsAvatarURL( url ) ) {
		if ( !CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height ) ) {
			if ( CL_SteamResources_IsPendingAvatarURL( url ) ) {
				Com_Printf( "UI: avatar resource request pending for %s via %s [%s]; retry after AvatarImageLoaded callback.\n",
					url,
					CL_GetSteamResourceServiceProviderLabel(),
					CL_GetSteamResourceServicePolicyLabel() );
			} else {
				Com_Printf( "UI: unable to satisfy avatar resource request for %s via %s [%s]\n",
					url,
					CL_GetSteamResourceServiceProviderLabel(),
					CL_GetSteamResourceServicePolicyLabel() );
			}
			return 0;
		}

		shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );
		QL_Steamworks_FreeBuffer( rgbaPixels );
	} else {
		clSteamDataSourceResponse_t response;

		CL_SteamDataSource_ClearResponse( &response );
		if ( !QLResourceInterceptor_OnRequest( url, &response ) ) {
			Com_Printf( "UI: unable to satisfy in-memory resource request for %s via %s [%s]\n",
				url,
				CL_GetSteamResourceServiceProviderLabel(),
				CL_GetSteamResourceServicePolicyLabel() );
			return 0;
		}

		rgbaPixels = response.rgbaPixels;
		width = response.width;
		height = response.height;
		buffer = response.buffer;
		bufferLength = response.bufferLength;

		if ( buffer && bufferLength > 0 ) {
			shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );
			Sys_Steam_FreeRequestBuffer( buffer );
		} else if ( rgbaPixels ) {
			shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );
			QL_Steamworks_FreeBuffer( rgbaPixels );
		} else {
			return 0;
		}
	}

	if ( !shader ) {
		Com_Printf( "UI: unable to register live resource image for %s via %s [%s]\n",
			url,
			CL_GetSteamResourceServiceProviderLabel(),
			CL_GetSteamResourceServicePolicyLabel() );
		return 0;
	}

	CL_SteamResources_AssignSlot( slot, url, rendererName, shader );
	return shader;
}

/*
=============
SteamClient_GetAvatarImageHandle

Mirrors retail sub_460F30's public client helper boundary: cgame provides the
two SteamID words and the Steam resource bridge resolves the large avatar into
a renderer-visible image handle.
=============
*/
qhandle_t SteamClient_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {
	uint64_t identity;
	char url[MAX_QPATH];

	identity = ( (uint64_t)identityHigh << 32 ) | identityLow;
	if ( !identity ) {
		return 0;
	}

	Com_sprintf( url, sizeof( url ), "steam://avatar/large/%llu", (unsigned long long)identity );
	return CL_Steam_RegisterShader( url );
}

/*
=============
CL_ClearSteamResourceCache

Clears the retained live-resource bookkeeping and forces future registrations
onto fresh renderer-owned names.
=============
*/
void CL_ClearSteamResourceCache( qboolean clearPersisted ) {
	int i;

	for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {
		CL_SteamResources_ClearSlot( &cl_steamResources[i], clearPersisted );
	}

	CL_SteamResources_ClearPendingAvatars();
	cl_steamResourceGeneration++;
	if ( cl_steamResourceGeneration == 0 ) {
		cl_steamResourceGeneration = 1;
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
	CL_SteamResources_ClearPendingAvatars();
	cl_steamResourceGeneration = 1;
	cl_steamAvatarCallbacksRegistered = qfalse;
	CL_RefreshSteamResourceBridgeCvars();

	if ( !CL_SteamServicesEnabled() ) {
		Com_Printf( "Steam resource bridge disabled for %s [%s]; keeping launcher/web fallback resource bridge.\n",
			CL_GetSteamResourceServiceProviderLabel(),
			CL_GetSteamResourceServicePolicyLabel() );
		return;
	}

	CL_SteamResources_RegisterAvatarCallbacks();
}

/*
=============
CL_ShutdownSteamResources

Clears any retained Steam resource bookkeeping.
=============
*/
void CL_ShutdownSteamResources( void ) {
	CL_SteamResources_UnregisterAvatarCallbacks();
	CL_ClearSteamResourceCache( qfalse );
}

/*
=============
Sys_Steam_RequestURL

Retrieves an encoded Steam-backed or launcher-backed URL payload for the live
renderer image bridge.
=============
*/
qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {
	clSteamDataSourceResponse_t response;

	if ( outBuffer ) {
		*outBuffer = NULL;
	}

	if ( outSize ) {
		*outSize = 0;
	}

	CL_SteamDataSource_ClearResponse( &response );
	if ( !QLResourceInterceptor_OnRequest( url, &response ) ) {
		CL_LogLauncherResourceFallbackUnavailable( url, "request could not be resolved" );
		return qfalse;
	}

	if ( !response.buffer || response.bufferLength <= 0 ) {
		if ( response.rgbaPixels ) {
			QL_Steamworks_FreeBuffer( response.rgbaPixels );
		}
		CL_LogLauncherResourceFallbackUnavailable( url, "no binary buffer was produced" );
		return qfalse;
	}

	if ( outBuffer ) {
		*outBuffer = response.buffer;
	}
	if ( outSize ) {
		*outSize = response.bufferLength;
	}

	return qtrue;
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

