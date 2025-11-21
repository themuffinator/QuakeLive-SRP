/*
=============
ui_menu_flow.h

Menu flow selection utilities shared between the UI VM and test harnesses.
=============
*/
#ifndef UI_MENU_FLOW_H
#define UI_MENU_FLOW_H

#include "ui_local.h"

#define UI_MENU_FILE_LEGACY		"ui/menus.txt"
#define UI_MENU_FILE_QUAKELIVE	"ui/menus_quakelive.txt"
#define UI_INGAME_FILE_LEGACY	"ui/ingame.txt"
#define UI_INGAME_FILE_QUAKELIVE	"ui/ingame_quakelive.txt"

qboolean UI_BrowserOverlayAvailable( void );
void UI_SetBrowserActive( qboolean active );
uiMenuFlow_t UI_RequestedMenuFlow( void );
uiMenuFlow_t UI_ResolveMenuFlowInternal( void );
void UI_SetActiveMenuFlow( uiMenuFlow_t flow );
qboolean UI_UsingLegacyMenuFlow( void );
qboolean UI_ServerBrowserEnabled( void );
void UI_UpdateActiveMenuFlowForFile( const char *menuFile );
const char *UI_DefaultMenuFile( void );
const char *UI_DefaultIngameFile( void );
void UI_UpdateActiveMenuFlow( void );
void UI_ApplyMenuFlowChange( uiMenuFlow_t flow, qboolean reload );

#endif /* UI_MENU_FLOW_H */
