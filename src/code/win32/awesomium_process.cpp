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

#include <windows.h>

#include "platform/platform_config.h"

#ifndef QL_AWESOMIUM_USE_SDK
#define QL_AWESOMIUM_USE_SDK 0
#endif

#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_AWESOMIUM_USE_SDK
#include <Awesomium/ChildProcess.h>
#endif

#if QL_PLATFORM_HAS_ONLINE_SERVICES && !QL_AWESOMIUM_USE_SDK
#define QLR_AWESOMIUM_RUNTIME_DLL "awesomium.dll"
#define QLR_AWESOMIUM_CHILD_PROCESS_MAIN_SYMBOL "?ChildProcessMain@Awesomium@@YAHPAUHINSTANCE__@@@Z"
#define QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER "QLR_AWESOMIUM_CHILDPROCESSMAIN_DYNAMIC"

typedef int (__cdecl *awesomium_child_process_main_fn)( HINSTANCE instance );

/*
=============
AwesomiumProcess_ReportLoadFailure
=============
*/
static int AwesomiumProcess_ReportLoadFailure( const char *message ) {
	OutputDebugStringA( message );
	OutputDebugStringA( "\n" );
	return 1;
}

/*
=============
AwesomiumProcess_RunDynamicChildProcessMain
=============
*/
static int AwesomiumProcess_RunDynamicChildProcessMain( HINSTANCE instance ) {
	HMODULE awesomium;
	FARPROC symbol;
	awesomium_child_process_main_fn childProcessMain;

	awesomium = LoadLibraryA( QLR_AWESOMIUM_RUNTIME_DLL );
	if ( !awesomium ) {
		return AwesomiumProcess_ReportLoadFailure( QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER ": failed to load awesomium.dll" );
	}

	symbol = GetProcAddress( awesomium, QLR_AWESOMIUM_CHILD_PROCESS_MAIN_SYMBOL );
	if ( !symbol ) {
		FreeLibrary( awesomium );
		return AwesomiumProcess_ReportLoadFailure( QLR_AWESOMIUM_DYNAMIC_HELPER_MARKER ": failed to resolve Awesomium::ChildProcessMain" );
	}

	childProcessMain = (awesomium_child_process_main_fn)symbol;
	return childProcessMain( instance );
}
#endif

/*
=============
AwesomiumProcess_RunChildProcessMain
=============
*/
static int AwesomiumProcess_RunChildProcessMain( HINSTANCE instance ) {
#if QL_PLATFORM_HAS_ONLINE_SERVICES
#if QL_AWESOMIUM_USE_SDK
	return Awesomium::ChildProcessMain( instance );
#else
	return AwesomiumProcess_RunDynamicChildProcessMain( instance );
#endif
#else
	(void)instance;
	return 0;
#endif
}

/*
=============
WinMain
=============
*/
int APIENTRY WinMain( HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow ) {
	(void)hPrevInstance;
	(void)lpCmdLine;
	(void)nCmdShow;

	return AwesomiumProcess_RunChildProcessMain( hInstance );
}
