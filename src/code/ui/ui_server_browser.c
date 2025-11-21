/*
=============
ui_server_browser.c

Server browser refresh helpers extracted for reuse.
=============
*/

#include "ui_server_browser.h"

static const char *MonthAbbrev[] = {
	"Jan","Feb","Mar",
	"Apr","May","Jun",
	"Jul","Aug","Sep",
	"Oct","Nov","Dec"
};

/*
=============
UI_UpdatePendingPings

Reset LAN ping state and mark the browser as actively refreshing.
=============
*/
void UI_UpdatePendingPings( void ) {
	if ( !UI_ServerBrowserEnabled() ) {
		return;
	}
	trap_LAN_ResetPings( ui_netSource.integer );
	uiInfo.serverStatus.refreshActive = qtrue;
	uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 1000;
}

/*
=============
UI_StartServerRefresh

Begin or continue a server browser refresh cycle.
=============
*/
void UI_StartServerRefresh( qboolean full ) {
	int i;
	char *ptr;
	qtime_t q;

	if ( !UI_ServerBrowserEnabled() ) {
		uiInfo.serverStatus.refreshActive = qfalse;
		return;
	}

	trap_RealTime( &q );
	trap_Cvar_Set( va( "ui_lastServerRefresh_%i", ui_netSource.integer ), va( "%s-%i, %i at %i:%i", MonthAbbrev[q.tm_mon], q.tm_mday, 1900 + q.tm_year, q.tm_hour, q.tm_min ) );

	if ( !full ) {
		UI_UpdatePendingPings();
		return;
	}

	uiInfo.serverStatus.refreshActive = qtrue;
	uiInfo.serverStatus.nextDisplayRefresh = uiInfo.uiDC.realTime + 1000;
	uiInfo.serverStatus.numDisplayServers = 0;
	uiInfo.serverStatus.numPlayersOnServers = 0;
	trap_LAN_MarkServerVisible( ui_netSource.integer, -1, qtrue );
	trap_LAN_ResetPings( ui_netSource.integer );

	if ( ui_netSource.integer == AS_LOCAL ) {
		trap_Cmd_ExecuteText( EXEC_NOW, "localservers\n" );
		uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 1000;
		return;
	}

	uiInfo.serverStatus.refreshtime = uiInfo.uiDC.realTime + 5000;
	if ( ui_netSource.integer == AS_GLOBAL || ui_netSource.integer == AS_MPLAYER ) {
		if ( ui_netSource.integer == AS_GLOBAL ) {
			i = 0;
		} else {
			i = 1;
		}

		ptr = UI_Cvar_VariableString( "debug_protocol" );
		if ( strlen( ptr ) ) {
			trap_Cmd_ExecuteText( EXEC_NOW, va( "globalservers %d %s full empty\n", i, ptr ) );
		} else {
			trap_Cmd_ExecuteText( EXEC_NOW, va( "globalservers %d %d full empty\n", i, (int)trap_Cvar_VariableValue( "protocol" ) ) );
		}
	}
}
