#include "platform_services.h"

#include <string.h>

#include "platform_config.h"
#include "platform_backend_auth.h"
static qboolean QL_HybridAuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    qboolean handled = qfalse;

#if QL_BUILD_STEAMWORKS
    if ( QL_PlatformBackendSteamworks_Authenticate( credential, response ) ) {
        handled = qtrue;

        if ( response->result == QL_AUTH_RESULT_ACCEPTED ) {
            return qtrue;
        }
    }
#endif

#if QL_BUILD_OPEN_STEAM
    if ( QL_PlatformBackendOpenSteam_Authenticate( credential, response ) ) {
        if ( handled && response->result == QL_AUTH_RESULT_ACCEPTED ) {
            char preview[32];
            QL_Backend_FormatCredentialPreview( credential, preview, sizeof( preview ) );

            QL_Backend_SetAuthResponse( response, response->result,
                "Hybrid fallback accepted credential via open adapter (token=%s)", preview );
        }

        return response->result == QL_AUTH_RESULT_ACCEPTED ? qtrue : qfalse;
    }
#endif

    return handled;
}

static void QL_FinaliseDescriptor( ql_platform_feature_descriptor *descriptor, const char *fallbackLabel ) {
    if ( !descriptor ) {
        return;
    }

    if ( !descriptor->provider && fallbackLabel ) {
        descriptor->provider = fallbackLabel;
    }
}

static ql_platform_service_table QL_BuildServiceTable( void ) {
    ql_platform_service_table table;
    memset( &table, 0, sizeof( table ) );

#if QL_PLATFORM_BUILD_HYBRID
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Hybrid";
    table.auth.request = QL_HybridAuthFlow;
#elif QL_PLATFORM_HAS_STEAMWORKS
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Steamworks";
    table.auth.request = QL_PlatformBackendSteamworks_Authenticate;
#elif QL_PLATFORM_HAS_OPEN_STEAM
    table.auth.descriptor.supported = qtrue;
    table.auth.descriptor.provider = "Open Steam Adapter";
    table.auth.request = QL_PlatformBackendOpenSteam_Authenticate;
#endif

#if QL_PLATFORM_HAS_STEAMWORKS
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = "Steamworks";
    table.workshop.supported = qtrue;
    table.workshop.provider = "Steam UGC";
    table.overlay.supported = qtrue;
    table.overlay.provider = "Steam Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = "Steam Stats";
#endif

#if QL_PLATFORM_HAS_OPEN_STEAM
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steamworks + GameNetworkingSockets" : "GameNetworkingSockets";
    table.workshop.supported = qtrue;
    table.workshop.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam UGC + REST Mirror" : "REST UGC Service";
    table.overlay.supported = qtrue;
    table.overlay.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Overlay + In-Process UI" : "In-Process UI Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Stats + Metrics REST" : "Metrics REST Adapter";
#endif

    QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
    QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
    QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
    QL_FinaliseDescriptor( &table.stats, "Unavailable" );

    if ( !table.auth.request ) {
        table.auth.descriptor.supported = qfalse;
        table.auth.descriptor.provider = "Unavailable";
    }

    return table;
}

const ql_platform_service_table *QL_GetPlatformServices( void ) {
    static ql_platform_service_table table;
    static qboolean initialised = qfalse;

    if ( !initialised ) {
        table = QL_BuildServiceTable();
        initialised = qtrue;
    }

    return &table;
}

qboolean QL_Platform_RunMockAuthFlow( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {
    if ( !response ) {
        return qfalse;
    }

    QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, NULL );

    if ( !credential ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No credential provided." );
        return qfalse;
    }

    const ql_platform_service_table *services = QL_GetPlatformServices();

    if ( !services->auth.descriptor.supported || !services->auth.request ) {
        QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No authentication backend is compiled in." );
        return qfalse;
    }

    if ( !services->auth.request( credential, response ) ) {
        if ( response->message[0] == '\0' ) {
            QL_Backend_SetAuthResponse( response, QL_AUTH_RESULT_ERROR, "No provider accepted credential kind %d.", credential->kind );
        }

        return qfalse;
    }

    return response->result == QL_AUTH_RESULT_ACCEPTED ? qtrue : qfalse;
}
