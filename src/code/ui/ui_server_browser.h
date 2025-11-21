/*
=============
ui_server_browser.h

Server browser refresh helpers exposed for tests and menu scripts.
=============
*/
#ifndef UI_SERVER_BROWSER_H
#define UI_SERVER_BROWSER_H

#include "ui_menu_flow.h"

void UI_UpdatePendingPings( void );
void UI_StartServerRefresh( qboolean full );

#endif /* UI_SERVER_BROWSER_H */
