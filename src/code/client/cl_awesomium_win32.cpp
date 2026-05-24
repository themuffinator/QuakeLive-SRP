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
// cl_awesomium_win32.cpp -- runtime Awesomium host adapter

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef QL_BUILD_ONLINE_SERVICES
#define QL_BUILD_ONLINE_SERVICES 0
#endif

typedef int qboolean;
typedef unsigned char byte;

#ifndef qfalse
#define qfalse 0
#endif

#ifndef qtrue
#define qtrue 1
#endif

#if QL_BUILD_ONLINE_SERVICES

typedef void *(__stdcall *awe_new_void_fn)( void );
typedef void (__stdcall *awe_delete_object_fn)( void *object );
typedef void *(__stdcall *awe_webcore_initialize_fn)( void *config );
typedef void (__stdcall *awe_webcore_shutdown_fn)( void );
typedef void (__stdcall *awe_webcore_update_fn)( void *core );
typedef void *(__stdcall *awe_webcore_create_session_fn)( void *core, const unsigned short *dataPath, void *preferences );
typedef void *(__stdcall *awe_webcore_create_view_fn)( void *core, int width, int height, void *session, int type );
typedef void (__stdcall *awe_webcore_set_string_fn)( void *object, const unsigned short *value );
typedef void (__stdcall *awe_webprefs_set_bool_fn)( void *preferences, bool value );
typedef void *(__stdcall *awe_new_datapak_source_fn)( const unsigned short *pakPath );
typedef void (__stdcall *awe_websession_add_source_fn)( void *session, const unsigned short *sourceName, void *dataSource );
typedef void (__stdcall *awe_websession_release_fn)( void *session );
typedef void *(__stdcall *awe_new_weburl_fn)( const unsigned short *url );
typedef void (__stdcall *awe_webview_destroy_fn)( void *view );
typedef void (__stdcall *awe_webview_load_url_fn)( void *view, void *url );
typedef void (__stdcall *awe_webview_resize_fn)( void *view, int width, int height );
typedef void (__stdcall *awe_webview_focus_fn)( void *view );
typedef void (__stdcall *awe_webview_reload_fn)( void *view, bool ignoreCache );
typedef void (__stdcall *awe_webview_stop_fn)( void *view );
typedef void (__stdcall *awe_webview_mouse_move_fn)( void *view, int x, int y );
typedef void (__stdcall *awe_webview_mouse_button_fn)( void *view, int button );
typedef void (__stdcall *awe_webview_mouse_wheel_fn)( void *view, int x, int y );
typedef void *(__stdcall *awe_webview_surface_fn)( void *view );
typedef void (__stdcall *awe_bitmap_copy_to_fn)( void *surface, byte *destination, int rowSpan, int depth, bool convertToRGBA, bool flipY );
typedef int (__stdcall *awe_bitmap_dimension_fn)( void *surface );
typedef bool (__stdcall *awe_bitmap_bool_fn)( void *surface );
typedef void (__stdcall *awe_bitmap_set_bool_fn)( void *surface, bool value );

typedef struct {
	void	*webConfig;
	void	*webPreferences;
	void	*webCore;
	void	*webSession;
	void	*webView;
	void	*dataPakSource;
	HMODULE	module;
	int		bootstrapMappingCount;
	qboolean importsResolved;
	qboolean started;
	qboolean urlLoaded;
	char	lastError[256];
} clAwesomiumState_t;

typedef struct {
	awe_new_void_fn					newWebConfig;
	awe_delete_object_fn			deleteWebConfig;
	awe_new_void_fn					newWebPreferences;
	awe_delete_object_fn			deleteWebPreferences;
	awe_webcore_initialize_fn		webCoreInitialize;
	awe_webcore_shutdown_fn			webCoreShutdown;
	awe_webcore_update_fn			webCoreUpdate;
	awe_webcore_create_session_fn	webCoreCreateWebSession;
	awe_webcore_create_view_fn		webCoreCreateWebView;
	awe_webcore_set_string_fn		webConfigAssetProtocolSet;
	awe_webcore_set_string_fn		webConfigChildProcessPathSet;
	awe_webcore_set_string_fn		webConfigLogPathSet;
	awe_webcore_set_string_fn		webConfigPackagePathSet;
	awe_webcore_set_string_fn		webConfigUserScriptSet;
	awe_webprefs_set_bool_fn			webPrefsEnableJavascriptSet;
	awe_webprefs_set_bool_fn			webPrefsEnableLocalStorageSet;
	awe_webprefs_set_bool_fn			webPrefsEnableDatabasesSet;
	awe_webprefs_set_bool_fn			webPrefsEnableWebSecuritySet;
	awe_webprefs_set_bool_fn			webPrefsAllowFileAccessSet;
	awe_webprefs_set_bool_fn			webPrefsAllowUniversalAccessSet;
	awe_new_datapak_source_fn		newDataPakSource;
	awe_delete_object_fn			deleteDataPakSource;
	awe_new_weburl_fn				newWebURL;
	awe_delete_object_fn			deleteWebURL;
	awe_websession_add_source_fn		webSessionAddDataSource;
	awe_websession_release_fn		webSessionRelease;
	awe_webview_destroy_fn			webViewDestroy;
	awe_webview_load_url_fn			webViewLoadURL;
	awe_webview_resize_fn			webViewResize;
	awe_webview_focus_fn				webViewFocus;
	awe_webview_reload_fn			webViewReload;
	awe_webview_stop_fn				webViewStop;
	awe_webview_mouse_move_fn		webViewInjectMouseMove;
	awe_webview_mouse_button_fn		webViewInjectMouseDown;
	awe_webview_mouse_button_fn		webViewInjectMouseUp;
	awe_webview_mouse_wheel_fn		webViewInjectMouseWheel;
	awe_webview_surface_fn			webViewSurface;
	awe_bitmap_copy_to_fn			bitmapCopyTo;
	awe_bitmap_dimension_fn			bitmapWidth;
	awe_bitmap_dimension_fn			bitmapHeight;
	awe_bitmap_bool_fn				bitmapIsDirty;
	awe_bitmap_set_bool_fn			bitmapSetIsDirty;
} clAwesomiumImports_t;

#define CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT "bounded C-export substitution"
#define CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD "source-owned keyboard event path"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT "bounded C-export bootstrap substitution"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME "retail object lifetime mapped to adapter handle"
#define CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL "retail literal retained in source adapter"

typedef struct {
	unsigned int	retailAddress;
	unsigned int	retailVtableSlot;
	const char		*retailMethod;
	const char		*adapterOwner;
	const char		*adapterBinding;
	const char		*substitutionKind;
} clAwesomiumRetailAbiEquivalence_t;

typedef struct {
	unsigned int	retailOwnerAddress;
	unsigned int	retailAnchor;
	const char		*retailMember;
	const char		*adapterOwner;
	const char		*adapterBinding;
	const char		*substitutionKind;
} clAwesomiumBootstrapRetailMapping_t;

/*
=============
Awesomium retail ABI equivalence table

Retail `quakelive_steam.exe` calls Awesomium through retained C++ object
pointers and vtable slots. This backend intentionally keeps the online-services
path as a dynamically resolved C-export adapter, so each row below records the
source-visible substitution boundary rather than claiming literal ABI identity.
=============
*/
static const clAwesomiumRetailAbiEquivalence_t cl_aweRetailAbiEquivalence[] = {
	{ 0x004F2590u, 0x18u, "WebCore::Update", "CL_Awesomium_Update", "_Awe_WebCore_Update@4", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F25C0u, 0x9cu, "WebView::Resize", "CL_Awesomium_Resize", "_Awe_WebView_Resize@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2750u, 0xd0u, "WebView::InjectMouseMove", "CL_Awesomium_InjectMouseMove", "_Awe_WebView_InjectMouseMove@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F27C0u, 0xd4u, "WebView::InjectMouseDown", "CL_Awesomium_InjectMouseDown", "_Awe_WebView_InjectMouseDown@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2820u, 0xd8u, "WebView::InjectMouseUp", "CL_Awesomium_InjectMouseUp", "_Awe_WebView_InjectMouseUp@8", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F2870u, 0xdcu, "WebView::InjectMouseWheel", "CL_Awesomium_InjectMouseWheel", "_Awe_WebView_InjectMouseWheel@12", CL_AWE_RETAIL_ABI_SCOPE_C_EXPORT },
	{ 0x004F28A0u, 0xe0u, "WebView::InjectKeyboardEvent", "QLWebView_InjectKeyboardEvent", "cl_cgame.c field model", CL_AWE_RETAIL_ABI_SCOPE_SOURCE_KEYBOARD },
};

/*
=============
Awesomium retail bootstrap mapping table

Retail `QLWebHost_OpenURL` constructs the Awesomium core, session, data-source,
view, URL, focus, and shutdown chain directly through C++ constructors and
vtable slots. This backend keeps those seams source-visible while routing them
through the bounded dynamic C-export adapter.
=============
*/
static const clAwesomiumBootstrapRetailMapping_t cl_aweBootstrapRetailMappings[] = {
	{ 0x004F2D30u, 0x0052C6A4u, "WebConfig::WebConfig", "CL_Awesomium_PrepareConfig", "_Awe_new_WebConfig@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C6A0u, "WebCore::Initialize", "CL_Awesomium_Startup", "_Awe_WebCore_Initialize@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x0052C698u, "WebPreferences::WebPreferences", "CL_Awesomium_PreparePreferences", "_Awe_new_WebPreferences@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000000u, "WebCore::CreateWebSession slot 0x00", "CL_Awesomium_CreateSession", "_Awe_WebCore_CreateWebSession@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000018u, "WebSession bootstrap slot 0x18", "CL_Awesomium_CreateSession", "session initialisation boundary", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },
	{ 0x004F2D30u, 0x0052C694u, "DataPakSource::DataPakSource", "CL_Awesomium_CreateSession", "_Awe_new_DataPakSource@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00548068u, "QL data-source name", "CL_Awesomium_CreateSession", "\"QL\"", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_SOURCE_LITERAL },
	{ 0x004F2D30u, 0x00548070u, "DataPakSource::vftable", "CL_Awesomium_CreateSession", "Awesomium built-in DataPakSource", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_OBJECT_LIFETIME },
	{ 0x004F2D30u, 0x00000010u, "WebSession::AddDataSource slot 0x10", "CL_Awesomium_CreateSession", "_Awe_WebSession_AddDataSource@12", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000004u, "WebCore::CreateWebView slot 0x04", "CL_Awesomium_Startup", "_Awe_WebCore_CreateWebView_0@20", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x00000064u, "WebView::LoadURL slot 0x64", "CL_Awesomium_OpenURL", "_Awe_WebView_LoadURL@8", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000ACu, "WebView::Focus slot 0xAC", "CL_Awesomium_OpenURL", "_Awe_WebView_Focus@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2D30u, 0x000000C4u, "WebView::surface slot 0xC4", "CL_Awesomium_Surface", "_Awe_WebView_surface@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x00000000u, "WebView::Destroy slot 0x00", "CL_Awesomium_Shutdown", "_Awe_WebView_Destroy@4", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0x004F2A60u, 0x0052C684u, "WebCore::Shutdown", "CL_Awesomium_Shutdown", "_Awe_WebCore_Shutdown@0", CL_AWE_RETAIL_BOOTSTRAP_SCOPE_C_EXPORT },
	{ 0u, 0u, NULL, NULL, NULL, NULL },
};

static clAwesomiumState_t cl_awesomium;
static clAwesomiumImports_t cl_awe;

extern "C" void CL_Awesomium_Shutdown( void );

/*
=============
CL_Awesomium_CountBootstrapRetailMappings

Returns the number of recovered bootstrap anchors retained as source-visible
documentation for the Win32 Awesomium adapter.
=============
*/
static int CL_Awesomium_CountBootstrapRetailMappings( void ) {
	int i;
	int count;

	count = 0;
	for ( i = 0; cl_aweBootstrapRetailMappings[i].retailMember; i++ ) {
		if ( cl_aweBootstrapRetailMappings[i].retailOwnerAddress != 0u || cl_aweBootstrapRetailMappings[i].retailAnchor != 0u ) {
			count++;
		}
	}

	return count;
}

/*
=============
CL_Awesomium_SetError
=============
*/
static void CL_Awesomium_SetError( const char *message ) {
	if ( !message ) {
		message = "unknown Awesomium error";
	}

	strncpy( cl_awesomium.lastError, message, sizeof( cl_awesomium.lastError ) - 1 );
	cl_awesomium.lastError[sizeof( cl_awesomium.lastError ) - 1] = '\0';
}

/*
=============
CL_Awesomium_ResolveImport
=============
*/
static qboolean CL_Awesomium_ResolveImport( FARPROC *target, const char *name ) {
	*target = GetProcAddress( cl_awesomium.module, name );
	if ( !*target ) {
		char buffer[256];

		_snprintf( buffer, sizeof( buffer ), "missing Awesomium export %s", name );
		buffer[sizeof( buffer ) - 1] = '\0';
		CL_Awesomium_SetError( buffer );
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Awesomium_LoadImports
=============
*/
static qboolean CL_Awesomium_LoadImports( void ) {
	if ( cl_awesomium.importsResolved ) {
		return qtrue;
	}

	if ( !cl_awesomium.module ) {
		cl_awesomium.module = LoadLibraryA( "awesomium.dll" );
		if ( !cl_awesomium.module ) {
			CL_Awesomium_SetError( "awesomium.dll was not found beside quakelive_steam.exe" );
			return qfalse;
		}
	}

#define CL_AWE_IMPORT( field, name ) \
	if ( !CL_Awesomium_ResolveImport( (FARPROC *)&cl_awe.field, name ) ) { \
		return qfalse; \
	}

	CL_AWE_IMPORT( newWebConfig, "_Awe_new_WebConfig@0" );
	CL_AWE_IMPORT( deleteWebConfig, "_Awe_delete_WebConfig@4" );
	CL_AWE_IMPORT( newWebPreferences, "_Awe_new_WebPreferences@0" );
	CL_AWE_IMPORT( deleteWebPreferences, "_Awe_delete_WebPreferences@4" );
	CL_AWE_IMPORT( webCoreInitialize, "_Awe_WebCore_Initialize@4" );
	CL_AWE_IMPORT( webCoreShutdown, "_Awe_WebCore_Shutdown@0" );
	CL_AWE_IMPORT( webCoreUpdate, "_Awe_WebCore_Update@4" );
	CL_AWE_IMPORT( webCoreCreateWebSession, "_Awe_WebCore_CreateWebSession@12" );
	CL_AWE_IMPORT( webCoreCreateWebView, "_Awe_WebCore_CreateWebView_0@20" );
	CL_AWE_IMPORT( webConfigAssetProtocolSet, "_Awe_WebConfig_asset_protocol_set@8" );
	CL_AWE_IMPORT( webConfigChildProcessPathSet, "_Awe_WebConfig_child_process_path_set@8" );
	CL_AWE_IMPORT( webConfigLogPathSet, "_Awe_WebConfig_log_path_set@8" );
	CL_AWE_IMPORT( webConfigPackagePathSet, "_Awe_WebConfig_package_path_set@8" );
	CL_AWE_IMPORT( webConfigUserScriptSet, "_Awe_WebConfig_user_script_set@8" );
	CL_AWE_IMPORT( webPrefsEnableJavascriptSet, "_Awe_WebPreferences_enable_javascript_set@8" );
	CL_AWE_IMPORT( webPrefsEnableLocalStorageSet, "_Awe_WebPreferences_enable_local_storage_set@8" );
	CL_AWE_IMPORT( webPrefsEnableDatabasesSet, "_Awe_WebPreferences_enable_databases_set@8" );
	CL_AWE_IMPORT( webPrefsEnableWebSecuritySet, "_Awe_WebPreferences_enable_web_security_set@8" );
	CL_AWE_IMPORT( webPrefsAllowFileAccessSet, "_Awe_WebPreferences_allow_file_access_from_file_url_set@8" );
	CL_AWE_IMPORT( webPrefsAllowUniversalAccessSet, "_Awe_WebPreferences_allow_universal_access_from_file_url_set@8" );
	CL_AWE_IMPORT( newDataPakSource, "_Awe_new_DataPakSource@4" );
	CL_AWE_IMPORT( deleteDataPakSource, "_Awe_delete_DataPakSource@4" );
	CL_AWE_IMPORT( newWebURL, "_Awe_new_WebURL_1@4" );
	CL_AWE_IMPORT( deleteWebURL, "_Awe_delete_WebURL@4" );
	CL_AWE_IMPORT( webSessionAddDataSource, "_Awe_WebSession_AddDataSource@12" );
	CL_AWE_IMPORT( webSessionRelease, "_Awe_WebSession_Release@4" );
	CL_AWE_IMPORT( webViewDestroy, "_Awe_WebView_Destroy@4" );
	CL_AWE_IMPORT( webViewLoadURL, "_Awe_WebView_LoadURL@8" );
	CL_AWE_IMPORT( webViewResize, "_Awe_WebView_Resize@12" );
	CL_AWE_IMPORT( webViewFocus, "_Awe_WebView_Focus@4" );
	CL_AWE_IMPORT( webViewReload, "_Awe_WebView_Reload@8" );
	CL_AWE_IMPORT( webViewStop, "_Awe_WebView_Stop@4" );
	CL_AWE_IMPORT( webViewInjectMouseMove, "_Awe_WebView_InjectMouseMove@12" );
	CL_AWE_IMPORT( webViewInjectMouseDown, "_Awe_WebView_InjectMouseDown@8" );
	CL_AWE_IMPORT( webViewInjectMouseUp, "_Awe_WebView_InjectMouseUp@8" );
	CL_AWE_IMPORT( webViewInjectMouseWheel, "_Awe_WebView_InjectMouseWheel@12" );
	CL_AWE_IMPORT( webViewSurface, "_Awe_WebView_surface@4" );
	CL_AWE_IMPORT( bitmapCopyTo, "_Awe_BitmapSurface_CopyTo@24" );
	CL_AWE_IMPORT( bitmapWidth, "_Awe_BitmapSurface_width@4" );
	CL_AWE_IMPORT( bitmapHeight, "_Awe_BitmapSurface_height@4" );
	CL_AWE_IMPORT( bitmapIsDirty, "_Awe_BitmapSurface_is_dirty@4" );
	CL_AWE_IMPORT( bitmapSetIsDirty, "_Awe_BitmapSurface_set_is_dirty@8" );

#undef CL_AWE_IMPORT

	cl_awesomium.bootstrapMappingCount = CL_Awesomium_CountBootstrapRetailMappings();
	cl_awesomium.importsResolved = qtrue;
	CL_Awesomium_SetError( "" );
	return qtrue;
}

/*
=============
CL_Awesomium_AllocWideString
=============
*/
static unsigned short *CL_Awesomium_AllocWideString( const char *value ) {
	int required;
	wchar_t *wide;

	if ( !value ) {
		value = "";
	}

	required = MultiByteToWideChar( CP_UTF8, 0, value, -1, NULL, 0 );
	if ( required <= 0 ) {
		required = MultiByteToWideChar( CP_ACP, 0, value, -1, NULL, 0 );
		if ( required <= 0 ) {
			return NULL;
		}

		wide = new wchar_t[required];
		if ( !wide ) {
			return NULL;
		}
		MultiByteToWideChar( CP_ACP, 0, value, -1, wide, required );
		return (unsigned short *)wide;
	}

	wide = new wchar_t[required];
	if ( !wide ) {
		return NULL;
	}

	MultiByteToWideChar( CP_UTF8, 0, value, -1, wide, required );
	return (unsigned short *)wide;
}

/*
=============
CL_Awesomium_SetConfigString
=============
*/
static qboolean CL_Awesomium_SetConfigString( awe_webcore_set_string_fn setter, void *config, const char *value ) {
	unsigned short *wide;

	if ( !setter ) {
		return qtrue;
	}

	wide = CL_Awesomium_AllocWideString( value );
	if ( !wide ) {
		CL_Awesomium_SetError( "could not convert string for Awesomium" );
		return qfalse;
	}

	setter( config, wide );
	delete[] (wchar_t *)wide;
	return qtrue;
}

/*
=============
CL_Awesomium_AppendPath
=============
*/
static void CL_Awesomium_AppendPath( char *buffer, size_t bufferSize, const char *root, const char *fileName ) {
	size_t length;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !root || !root[0] || !fileName || !fileName[0] ) {
		return;
	}

	length = strlen( root );
	if ( root[length - 1] == '\\' || root[length - 1] == '/' ) {
		_snprintf( buffer, bufferSize, "%s%s", root, fileName );
	} else {
		_snprintf( buffer, bufferSize, "%s\\%s", root, fileName );
	}
	buffer[bufferSize - 1] = '\0';
}

/*
=============
CL_Awesomium_EscapeScriptString
=============
*/
static void CL_Awesomium_EscapeScriptString( const char *value, char *buffer, size_t bufferSize ) {
	size_t out;

	if ( !buffer || bufferSize == 0 ) {
		return;
	}

	buffer[0] = '\0';
	if ( !value ) {
		return;
	}

	out = 0;
	while ( *value && out + 2 < bufferSize ) {
		unsigned char ch;

		ch = (unsigned char)*value++;
		if ( ch == '\\' || ch == '"' ) {
			buffer[out++] = '\\';
			buffer[out++] = (char)ch;
		} else if ( ch == '\n' || ch == '\r' || ch == '\t' ) {
			buffer[out++] = ' ';
		} else if ( ch >= 32 ) {
			buffer[out++] = (char)ch;
		}
	}

	buffer[out] = '\0';
}

/*
=============
CL_Awesomium_BuildUserScript
=============
*/
static void CL_Awesomium_BuildUserScript( char *buffer, size_t bufferSize, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh ) {
	char escapedName[256];
	char steamId[64];

	CL_Awesomium_EscapeScriptString( playerName ? playerName : "", escapedName, sizeof( escapedName ) );
	if ( steamIdHigh || steamIdLow ) {
		_snprintf( steamId, sizeof( steamId ), "%u%010u", steamIdHigh, steamIdLow );
	} else {
		strcpy( steamId, "0" );
	}
	steamId[sizeof( steamId ) - 1] = '\0';

	_snprintf(
		buffer,
		bufferSize,
		"(function(){if(window.qz_instance){return;}var noop=function(){return false;};"
		"window.qz_instance={appId:%u,steamId:\"%s\",playerName:\"%s\","
		"SendGameCommand:function(cmd){console.log('qz SendGameCommand: '+cmd);},"
		"WriteTextFile:noop,OpenURL:function(url){document.location.href=url;},"
		"OpenSteamOverlayURL:function(url){console.log('qz OpenSteamOverlayURL: '+url);},"
		"GetClipboardText:function(){return '';},SetClipboardText:noop,"
		"RequestServers:noop,RequestServerDetails:noop,RefreshList:noop,"
		"CreateLobby:noop,LeaveLobby:noop,JoinLobby:noop,SetLobbyServer:noop,"
		"ShowInviteOverlay:noop,SayLobby:noop,RequestUserStats:noop,"
		"ActivateGameOverlayToUser:noop,Invite:noop,GetAllUGC:function(){return [];},"
		"GetNextKeyDown:noop,SetFavoriteServer:noop,"
		"IsPakFilePresent:function(){return true;},IsGameRunning:function(){return false;},"
		"FileExists:function(){return false;},GetCvar:function(){return '';},"
		"SetCvar:noop,ResetCvar:noop,GetMapList:function(){return [];},"
		"GetFactoryList:function(){return [];},GetDemoList:function(){return [];},"
		"GetFriendList:function(){return [];},GetConfig:function(){return {cvars:{},binds:[]};},"
		"GetCursorPosition:function(){return {x:0,y:0};}};})();",
		appId,
		steamId,
		escapedName
	);
	buffer[bufferSize - 1] = '\0';
}

/*
=============
CL_Awesomium_PrepareConfig
=============
*/
static qboolean CL_Awesomium_PrepareConfig( const char *runtimePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh ) {
	char childProcessPath[MAX_PATH];
	char logPath[MAX_PATH];
	char packagePath[MAX_PATH];
	char userScript[4096];

	cl_awesomium.webConfig = cl_awe.newWebConfig();
	if ( !cl_awesomium.webConfig ) {
		CL_Awesomium_SetError( "could not allocate Awesomium WebConfig" );
		return qfalse;
	}

	CL_Awesomium_AppendPath( childProcessPath, sizeof( childProcessPath ), runtimePath, "awesomium_process.exe" );
	CL_Awesomium_AppendPath( logPath, sizeof( logPath ), runtimePath, "awesomium.log" );
	CL_Awesomium_AppendPath( packagePath, sizeof( packagePath ), runtimePath, "web.pak" );
	CL_Awesomium_BuildUserScript( userScript, sizeof( userScript ), playerName, appId, steamIdLow, steamIdHigh );

	if ( !CL_Awesomium_SetConfigString( cl_awe.webConfigAssetProtocolSet, cl_awesomium.webConfig, "asset" )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigChildProcessPathSet, cl_awesomium.webConfig, childProcessPath )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigLogPathSet, cl_awesomium.webConfig, logPath )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigPackagePathSet, cl_awesomium.webConfig, packagePath )
		|| !CL_Awesomium_SetConfigString( cl_awe.webConfigUserScriptSet, cl_awesomium.webConfig, userScript ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
CL_Awesomium_PreparePreferences
=============
*/
static qboolean CL_Awesomium_PreparePreferences( void ) {
	cl_awesomium.webPreferences = cl_awe.newWebPreferences();
	if ( !cl_awesomium.webPreferences ) {
		CL_Awesomium_SetError( "could not allocate Awesomium WebPreferences" );
		return qfalse;
	}

	cl_awe.webPrefsEnableJavascriptSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableLocalStorageSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableDatabasesSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsEnableWebSecuritySet( cl_awesomium.webPreferences, false );
	cl_awe.webPrefsAllowFileAccessSet( cl_awesomium.webPreferences, true );
	cl_awe.webPrefsAllowUniversalAccessSet( cl_awesomium.webPreferences, true );
	return qtrue;
}

/*
=============
CL_Awesomium_CreateSession
=============
*/
static qboolean CL_Awesomium_CreateSession( const char *runtimePath ) {
	unsigned short *dataPath;
	unsigned short *sourceName;
	unsigned short *pakName;

	dataPath = CL_Awesomium_AllocWideString( runtimePath );
	if ( !dataPath ) {
		CL_Awesomium_SetError( "could not convert session path for Awesomium" );
		return qfalse;
	}

	cl_awesomium.webSession = cl_awe.webCoreCreateWebSession( cl_awesomium.webCore, dataPath, cl_awesomium.webPreferences );
	delete[] (wchar_t *)dataPath;
	if ( !cl_awesomium.webSession ) {
		CL_Awesomium_SetError( "could not create Awesomium WebSession" );
		return qfalse;
	}

	pakName = CL_Awesomium_AllocWideString( "web.pak" );
	if ( !pakName ) {
		CL_Awesomium_SetError( "could not convert web.pak path for Awesomium" );
		return qfalse;
	}
	cl_awesomium.dataPakSource = cl_awe.newDataPakSource( pakName );
	delete[] (wchar_t *)pakName;
	if ( !cl_awesomium.dataPakSource ) {
		CL_Awesomium_SetError( "could not create Awesomium DataPakSource for web.pak" );
		return qfalse;
	}

	sourceName = CL_Awesomium_AllocWideString( "QL" );
	if ( !sourceName ) {
		CL_Awesomium_SetError( "could not convert Awesomium data source name" );
		return qfalse;
	}
	cl_awe.webSessionAddDataSource( cl_awesomium.webSession, sourceName, cl_awesomium.dataPakSource );
	delete[] (wchar_t *)sourceName;
	return qtrue;
}

/*
=============
CL_Awesomium_Surface
=============
*/
static void *CL_Awesomium_Surface( void ) {
	if ( !cl_awesomium.webView ) {
		return NULL;
	}

	return cl_awe.webViewSurface( cl_awesomium.webView );
}

/*
=============
CL_Awesomium_Startup
=============
*/
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height ) {
	(void)basePath;

	if ( cl_awesomium.started ) {
		if ( cl_awesomium.webView ) {
			cl_awe.webViewResize( cl_awesomium.webView, width, height );
		}
		return qtrue;
	}

	if ( !runtimePath || !runtimePath[0] ) {
		CL_Awesomium_SetError( "runtime path is empty" );
		return qfalse;
	}

	if ( !CL_Awesomium_LoadImports() ) {
		return qfalse;
	}

	if ( !CL_Awesomium_PrepareConfig( runtimePath, playerName, appId, steamIdLow, steamIdHigh )
		|| !CL_Awesomium_PreparePreferences() ) {
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	cl_awesomium.webCore = cl_awe.webCoreInitialize( cl_awesomium.webConfig );
	if ( !cl_awesomium.webCore ) {
		CL_Awesomium_SetError( "Unable to initialize WebCore" );
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	if ( !CL_Awesomium_CreateSession( runtimePath ) ) {
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	cl_awesomium.webView = cl_awe.webCoreCreateWebView( cl_awesomium.webCore, width, height, cl_awesomium.webSession, 0 );
	if ( !cl_awesomium.webView ) {
		CL_Awesomium_SetError( "could not create Awesomium WebView" );
		CL_Awesomium_Shutdown();
		return qfalse;
	}

	cl_awe.webViewFocus( cl_awesomium.webView );
	cl_awesomium.started = qtrue;
	CL_Awesomium_SetError( "" );
	return qtrue;
}

/*
=============
CL_Awesomium_OpenURL
=============
*/
extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {
	unsigned short *wideUrl;
	void *webURL;

	if ( !cl_awesomium.started || !cl_awesomium.webView ) {
		CL_Awesomium_SetError( "Awesomium WebView is not active" );
		return qfalse;
	}

	if ( !url || !url[0] ) {
		url = "asset://ql/index.html";
	}

	wideUrl = CL_Awesomium_AllocWideString( url );
	if ( !wideUrl ) {
		CL_Awesomium_SetError( "could not convert URL for Awesomium" );
		return qfalse;
	}

	webURL = cl_awe.newWebURL( wideUrl );
	delete[] (wchar_t *)wideUrl;
	if ( !webURL ) {
		CL_Awesomium_SetError( "could not create Awesomium WebURL" );
		return qfalse;
	}

	cl_awe.webViewLoadURL( cl_awesomium.webView, webURL );
	cl_awe.webViewFocus( cl_awesomium.webView );
	cl_awe.deleteWebURL( webURL );
	cl_awesomium.urlLoaded = qtrue;
	return qtrue;
}

/*
=============
CL_Awesomium_Update
=============
*/
extern "C" void CL_Awesomium_Update( void ) {
	if ( cl_awesomium.started && cl_awesomium.webCore ) {
		cl_awe.webCoreUpdate( cl_awesomium.webCore );
	}
}

/*
=============
CL_Awesomium_Resize
=============
*/
extern "C" qboolean CL_Awesomium_Resize( int width, int height ) {
	if ( !cl_awesomium.started || !cl_awesomium.webView || width <= 0 || height <= 0 ) {
		return qfalse;
	}

	cl_awe.webViewResize( cl_awesomium.webView, width, height );
	return qtrue;
}

/*
=============
CL_Awesomium_SurfaceWidth
=============
*/
extern "C" int CL_Awesomium_SurfaceWidth( void ) {
	void *surface = CL_Awesomium_Surface();
	return surface ? cl_awe.bitmapWidth( surface ) : 0;
}

/*
=============
CL_Awesomium_SurfaceHeight
=============
*/
extern "C" int CL_Awesomium_SurfaceHeight( void ) {
	void *surface = CL_Awesomium_Surface();
	return surface ? cl_awe.bitmapHeight( surface ) : 0;
}

/*
=============
CL_Awesomium_SurfaceDirty
=============
*/
extern "C" qboolean CL_Awesomium_SurfaceDirty( void ) {
	void *surface = CL_Awesomium_Surface();
	return ( surface && cl_awe.bitmapIsDirty( surface ) ) ? qtrue : qfalse;
}

/*
=============
CL_Awesomium_CopySurface
=============
*/
extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {
	void *surface;
	int byteCount;

	if ( !destination || width <= 0 || height <= 0 || rowSpan <= 0 ) {
		return qfalse;
	}

	surface = CL_Awesomium_Surface();
	if ( !surface ) {
		return qfalse;
	}

	byteCount = rowSpan * height;
	if ( byteCount > 0 ) {
		memset( destination, 0, byteCount );
	}

	cl_awe.bitmapCopyTo( surface, destination, rowSpan, 4, true, false );
	cl_awe.bitmapSetIsDirty( surface, false );
	return qtrue;
}

/*
=============
CL_Awesomium_InjectMouseMove
=============
*/
extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseMove( cl_awesomium.webView, x, y );
	}
}

/*
=============
CL_Awesomium_InjectMouseDown
=============
*/
extern "C" void CL_Awesomium_InjectMouseDown( int button ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseDown( cl_awesomium.webView, button );
	}
}

/*
=============
CL_Awesomium_InjectMouseUp
=============
*/
extern "C" void CL_Awesomium_InjectMouseUp( int button ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseUp( cl_awesomium.webView, button );
	}
}

/*
=============
CL_Awesomium_InjectMouseWheel
=============
*/
extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewInjectMouseWheel( cl_awesomium.webView, 0, direction * 30 );
	}
}

/*
=============
CL_Awesomium_Stop
=============
*/
extern "C" void CL_Awesomium_Stop( void ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewStop( cl_awesomium.webView );
	}
}

/*
=============
CL_Awesomium_Reload
=============
*/
extern "C" void CL_Awesomium_Reload( qboolean ignoreCache ) {
	if ( cl_awesomium.started && cl_awesomium.webView ) {
		cl_awe.webViewReload( cl_awesomium.webView, ignoreCache ? true : false );
	}
}

/*
=============
CL_Awesomium_Shutdown
=============
*/
extern "C" void CL_Awesomium_Shutdown( void ) {
	if ( cl_awesomium.webView && cl_awe.webViewDestroy ) {
		cl_awe.webViewDestroy( cl_awesomium.webView );
	}
	cl_awesomium.webView = NULL;

	if ( cl_awesomium.webSession && cl_awe.webSessionRelease ) {
		cl_awe.webSessionRelease( cl_awesomium.webSession );
	}
	cl_awesomium.webSession = NULL;
	cl_awesomium.dataPakSource = NULL;

	if ( cl_awesomium.webCore && cl_awe.webCoreShutdown ) {
		cl_awe.webCoreShutdown();
	}
	cl_awesomium.webCore = NULL;

	if ( cl_awesomium.webPreferences && cl_awe.deleteWebPreferences ) {
		cl_awe.deleteWebPreferences( cl_awesomium.webPreferences );
	}
	cl_awesomium.webPreferences = NULL;

	if ( cl_awesomium.webConfig && cl_awe.deleteWebConfig ) {
		cl_awe.deleteWebConfig( cl_awesomium.webConfig );
	}
	cl_awesomium.webConfig = NULL;
	cl_awesomium.started = qfalse;
	cl_awesomium.urlLoaded = qfalse;
}

/*
=============
CL_Awesomium_LastError
=============
*/
extern "C" const char *CL_Awesomium_LastError( void ) {
	return cl_awesomium.lastError[0] ? cl_awesomium.lastError : "";
}

#else

/*
=============
CL_Awesomium_Startup
=============
*/
extern "C" qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height ) {
	(void)runtimePath;
	(void)basePath;
	(void)playerName;
	(void)appId;
	(void)steamIdLow;
	(void)steamIdHigh;
	(void)width;
	(void)height;
	return qfalse;
}

/*
=============
CL_Awesomium_OpenURL
=============
*/
extern "C" qboolean CL_Awesomium_OpenURL( const char *url ) {
	(void)url;
	return qfalse;
}

/*
=============
CL_Awesomium_Update
=============
*/
extern "C" void CL_Awesomium_Update( void ) {
}

/*
=============
CL_Awesomium_Resize
=============
*/
extern "C" qboolean CL_Awesomium_Resize( int width, int height ) {
	(void)width;
	(void)height;
	return qfalse;
}

/*
=============
CL_Awesomium_SurfaceWidth
=============
*/
extern "C" int CL_Awesomium_SurfaceWidth( void ) {
	return 0;
}

/*
=============
CL_Awesomium_SurfaceHeight
=============
*/
extern "C" int CL_Awesomium_SurfaceHeight( void ) {
	return 0;
}

/*
=============
CL_Awesomium_SurfaceDirty
=============
*/
extern "C" qboolean CL_Awesomium_SurfaceDirty( void ) {
	return qfalse;
}

/*
=============
CL_Awesomium_CopySurface
=============
*/
extern "C" qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan ) {
	(void)destination;
	(void)width;
	(void)height;
	(void)rowSpan;
	return qfalse;
}

/*
=============
CL_Awesomium_InjectMouseMove
=============
*/
extern "C" void CL_Awesomium_InjectMouseMove( int x, int y ) {
	(void)x;
	(void)y;
}

/*
=============
CL_Awesomium_InjectMouseDown
=============
*/
extern "C" void CL_Awesomium_InjectMouseDown( int button ) {
	(void)button;
}

/*
=============
CL_Awesomium_InjectMouseUp
=============
*/
extern "C" void CL_Awesomium_InjectMouseUp( int button ) {
	(void)button;
}

/*
=============
CL_Awesomium_InjectMouseWheel
=============
*/
extern "C" void CL_Awesomium_InjectMouseWheel( int direction ) {
	(void)direction;
}

/*
=============
CL_Awesomium_Stop
=============
*/
extern "C" void CL_Awesomium_Stop( void ) {
}

/*
=============
CL_Awesomium_Reload
=============
*/
extern "C" void CL_Awesomium_Reload( qboolean ignoreCache ) {
	(void)ignoreCache;
}

/*
=============
CL_Awesomium_Shutdown
=============
*/
extern "C" void CL_Awesomium_Shutdown( void ) {
}

/*
=============
CL_Awesomium_LastError
=============
*/
extern "C" const char *CL_Awesomium_LastError( void ) {
	return "online services disabled by build settings";
}

#endif
