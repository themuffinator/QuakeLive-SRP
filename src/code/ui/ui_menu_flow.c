/*
=============
ui_menu_flow.c

Implements menu flow selection and browser activation helpers.
=============
*/

#include "ui_menu_flow.h"

static uiMenuFlow_t ui_activeMenuFlow = UI_MENU_FLOW_LEGACY;
static qboolean ui_browserActiveKnown = qfalse;
static qboolean ui_browserActiveState = qfalse;

void UI_Load( void );

/*
=============
UI_MenuFileEquals

Compare two menu paths for equality, safely handling NULL inputs.
=============
*/
static qboolean UI_MenuFileEquals( const char *lhs, const char *rhs ) {
	return ( lhs && rhs ) ? ( Q_stricmp( lhs, rhs ) == 0 ) : qfalse;
}

/*
=============
UI_BrowserOverlayAvailable

Report whether the embedded browser layer is available for menu rendering.
=============
*/
qboolean UI_BrowserOverlayAvailable( void ) {
	return ui_browserAwesomium.integer != 0;
}

/*
=============
UI_RequestedMenuFlow

Read the requested menu flow from the console variable.
=============
*/
uiMenuFlow_t UI_RequestedMenuFlow( void ) {
	return ( ui_menuFlow.integer > 0 ) ? UI_MENU_FLOW_QUAKELIVE : UI_MENU_FLOW_LEGACY;
}

/*
=============
UI_ResolveMenuFlowInternal

Pick an active flow, falling back to legacy menus if the browser overlay is absent.
=============
*/
uiMenuFlow_t UI_ResolveMenuFlowInternal( void ) {
	uiMenuFlow_t requested;

	requested = UI_RequestedMenuFlow();
	if ( requested == UI_MENU_FLOW_QUAKELIVE && !UI_BrowserOverlayAvailable() ) {
		return UI_MENU_FLOW_LEGACY;
	}
	return requested;
}

/*
=============
UI_SetBrowserActive

Inform the engine overlay about whether the Awesomium-driven UI is active.
=============
*/
void UI_SetBrowserActive( qboolean active ) {
	if ( ui_browserActiveKnown && ui_browserActiveState == active ) {
		return;
	}

	ui_browserActiveState = active;
	ui_browserActiveKnown = qtrue;
	trap_Cmd_ExecuteText( EXEC_NOW, active ? "web_browserActive 1\n" : "web_browserActive 0\n" );
}

/*
=============
UI_SetActiveMenuFlow

Record the resolved flow and synchronize helper CVars.
=============
*/
void UI_SetActiveMenuFlow( uiMenuFlow_t flow ) {
	ui_activeMenuFlow = flow;
	ui_new.integer = ( flow == UI_MENU_FLOW_QUAKELIVE );
	UI_SetBrowserActive( flow == UI_MENU_FLOW_QUAKELIVE );
}

/*
=============
UI_UsingLegacyMenuFlow

Expose whether legacy (Q3-style) menus are active.
=============
*/
qboolean UI_UsingLegacyMenuFlow( void ) {
	return ( ui_activeMenuFlow == UI_MENU_FLOW_LEGACY );
}

/*
=============
UI_ServerBrowserEnabled

Server browser interactions are only valid in the legacy flow.
=============
*/
qboolean UI_ServerBrowserEnabled( void ) {
	return UI_UsingLegacyMenuFlow();
}

/*
=============
UI_UpdateActiveMenuFlowForFile

Shift the active flow when a specific menu file is loaded.
=============
*/
void UI_UpdateActiveMenuFlowForFile( const char *menuFile ) {
	if ( UI_MenuFileEquals( menuFile, UI_MENU_FILE_QUAKELIVE ) || UI_MenuFileEquals( menuFile, UI_INGAME_FILE_QUAKELIVE ) ) {
		UI_SetActiveMenuFlow( UI_MENU_FLOW_QUAKELIVE );
	} else if ( UI_MenuFileEquals( menuFile, UI_MENU_FILE_LEGACY ) || UI_MenuFileEquals( menuFile, UI_INGAME_FILE_LEGACY ) ) {
		UI_SetActiveMenuFlow( UI_MENU_FLOW_LEGACY );
	}
}

/*
=============
UI_DefaultMenuFile

Return the menu definition file that matches the active flow.
=============
*/
const char *UI_DefaultMenuFile( void ) {
	return UI_UsingLegacyMenuFlow() ? UI_MENU_FILE_LEGACY : UI_MENU_FILE_QUAKELIVE;
}

/*
=============
UI_DefaultIngameFile

Return the ingame menu definition file that matches the active flow.
=============
*/
const char *UI_DefaultIngameFile( void ) {
	return UI_UsingLegacyMenuFlow() ? UI_INGAME_FILE_LEGACY : UI_INGAME_FILE_QUAKELIVE;
}

/*
=============
UI_UpdateActiveMenuFlow

Refresh the active flow after a configuration change.
=============
*/
void UI_UpdateActiveMenuFlow( void ) {
	UI_SetActiveMenuFlow( UI_ResolveMenuFlowInternal() );
}

/*
=============
UI_ApplyMenuFlowChange

Apply a user-requested flow change and optionally reload menus.
=============
*/
void UI_ApplyMenuFlowChange( uiMenuFlow_t flow, qboolean reload ) {
	trap_Cvar_SetValue( "ui_menuFlow", flow );
	UI_UpdateActiveMenuFlow();
	if ( reload ) {
		UI_Load();
	}
}
