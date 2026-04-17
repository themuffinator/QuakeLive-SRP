from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Retail command-owner evidence for this focused slice comes from
# `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL
# owners in `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4B6D00` -> `Key_Unbind_f`
# `sub_4B6D60` -> `Key_Unbindall_f`
# `sub_4B6DF0` -> `Key_Bind_f`
# `sub_4B8430` -> `CL_Record_f`
# `sub_4BB450` -> `CL_PlayDemo_f`
# `sub_4B8CB0` -> `CL_Reconnect_f`
# `sub_4B8D30` -> `CL_Connect_f`
# `sub_4B4FD0` -> alias execution helper
# `sub_4B5060` -> `Cmd_Alias_f`
# `sub_4B5170` -> `Cmd_UnAlias_f`
# `sub_4B51C0` -> `Cmd_UnAliasAll_f`
# `sub_4B6FE0` -> `Key_Bindlist_f`
# `sub_4C8430` -> `Cmd_List_f`
# `sub_4C84B0` -> `Cmd_Wait_f`
# `sub_4C86D0` -> `Cmd_Exec_f`
# `sub_4C87B0` -> `Cmd_Vstr_f`
# `sub_4C87F0` -> `Cmd_Echo_f`
# `sub_4C93D0` -> `Com_Crash_f`
# `sub_4C9E70` -> `Com_Quit_f`
# `sub_4CA4E0` -> `Com_Meminfo_f`
# `sub_4CAF90` -> `Com_Error_f`
# `sub_4CAFC0` -> `Com_Freeze_f`
# `sub_4CD4D0` -> `Cvar_Add_f`
# `sub_4CD560` -> `Cvar_Mult_f`
# `sub_4CD860` -> `Cvar_Clear_f`
# `sub_4CD9B0` -> `Cvar_List_f`
# `sub_4CDB50` -> `Cvar_Restart_f`
# `sub_4D12E0` -> `FS_Dir_f`
# `sub_4D1510` -> `FS_NewDir_f`
# `sub_4D1610` -> `FS_Path_f`
# `sub_4D1700` -> `FS_TouchFile_f`
# `sub_4D5750` -> `MSG_ReportChangeVectors_f`
# `sub_4DEC60` -> `SV_Status_f`


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_bind_family_commands_match_retail_handler_and_registration_shape() -> None:
	cl_keys = (REPO_ROOT / "src/code/client/cl_keys.c").read_text(encoding="utf-8")

	unbind_block = _extract_function_block(cl_keys, "void Key_Unbind_f (void)")
	unbindall_block = _extract_function_block(cl_keys, "void Key_Unbindall_f (void)")
	bind_block = _extract_function_block(cl_keys, "void Key_Bind_f (void)")
	bindlist_block = _extract_function_block(cl_keys, "void Key_Bindlist_f( void ) {")
	init_block = _extract_function_block(cl_keys, "void CL_InitKeyCommands( void ) {")

	assert 'Com_Printf ("unbind <key> : remove commands from a key\\n");' in unbind_block
	assert 'Key_SetBinding (b, "");' in unbind_block
	assert 'for (i=0 ; i<256 ; i++)' in unbindall_block
	assert 'Key_SetBinding (i, "");' in unbindall_block
	assert 'Com_Printf ("bind <key> [command] : attach a command to a key\\n");' in bind_block
	assert 'Com_Printf ("\\"%s\\" = \\"%s\\"\\n", Cmd_Argv(1), keys[b].binding );' in bind_block
	assert 'Com_Printf ("\\"%s\\" is not bound\\n", Cmd_Argv(1) );' in bind_block
	assert 'Key_SetBinding (b, cmd);' in bind_block
	assert 'Com_Printf( "%s \\"%s\\"\\n", Key_KeynumToString(i), keys[i].binding );' in bindlist_block
	assert 'Cmd_AddCommand ("bind",Key_Bind_f);' in init_block
	assert 'Cmd_AddCommand ("unbind",Key_Unbind_f);' in init_block
	assert 'Cmd_AddCommand ("unbindall",Key_Unbindall_f);' in init_block
	assert 'Cmd_AddCommand ("bindlist",Key_Bindlist_f);' in init_block


def test_console_and_alias_command_families_match_retail_wiring() -> None:
	cl_console = (REPO_ROOT / "src/code/client/cl_console.c").read_text(encoding="utf-8")
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")

	toggle_block = _extract_function_block(cl_console, "void Con_ToggleConsole_f (void) {")
	condump_block = _extract_function_block(cl_console, "void Con_Dump_f (void)")
	find_block = _extract_function_block(cl_console, "void Con_Find_f( void ) {")
	alias_block = _extract_function_block(cmd_c, "void Cmd_Alias_f( void ) {")
	unalias_block = _extract_function_block(cmd_c, "void Cmd_UnAlias_f( void ) {")
	unaliasall_block = _extract_function_block(cmd_c, "void Cmd_UnAliasAll_f( void ) {")
	write_aliases_block = _extract_function_block(cmd_c, "void Cmd_WriteAliases( fileHandle_t f ) {")
	execute_block = _extract_function_block(cmd_c, "Cmd_ExecuteString( const char *text ) {")
	init_block = _extract_function_block(cmd_c, "void Cmd_Init (void) {")

	assert 'Com_Printf( "com_allowConsole won\'t allow toggleconsole command\\n" );' in toggle_block
	assert 'Con_ClearNotify ();' in toggle_block
	assert 'cls.keyCatchers ^= KEYCATCH_CONSOLE;' in toggle_block

	assert 'Com_Printf ("usage: condump <filename>\\n");' in condump_block
	assert 'Com_Printf ("Dumped console text to %s.\\n", Cmd_Argv(1) );' in condump_block
	assert 'Com_Printf ("ERROR: couldn\'t open.\\n");' in condump_block
	assert 'strcat( buffer, "\\n" );' in condump_block

	assert 'Com_Printf( "usage: find <substring>  ; This is a case sensitive search of the console history.\\n" );' in find_block
	assert 'limit = ( con_matchlimit && con_matchlimit->integer > 0 ) ? con_matchlimit->integer : 16;' in find_block
	assert 'if ( strstr( buffer, needle ) && !strstr( buffer, "\\\\find" ) && !strstr( buffer, "usage: find " ) ) {' in find_block

	assert 'Cmd_AddCommand ("toggleconsole", Con_ToggleConsole_f);' in cl_console
	assert 'Cmd_AddCommand ("messagemode", Con_MessageMode_f);' in cl_console
	assert 'Cmd_AddCommand ("messagemode2", Con_MessageMode2_f);' in cl_console
	assert 'Cmd_AddCommand ("clear", Con_Clear_f);' in cl_console
	assert 'Cmd_AddCommand ("condump", Con_Dump_f);' in cl_console
	assert 'Cmd_AddCommand( "find", Con_Find_f );' in cl_console
	assert 'Cmd_AddCommand ("messagemode3", Con_MessageMode3_f);' not in cl_console
	assert 'Cmd_AddCommand ("messagemode4", Con_MessageMode4_f);' not in cl_console

	assert 'Com_Printf( "Usage: alias \\"command\\"\\n" );' in alias_block
	assert 'Com_Printf( "^1No free alias slots. Use UnAlias to remove an alias before adding this one.^7\\n" );' in alias_block
	assert 'Com_Printf( "Alias: %s \\"%s\\"\\n", alias->name, alias->command );' in alias_block
	assert 'Com_Printf( "Usage: unalias \\"command\\"\\n" );' in unalias_block
	assert 'Com_Printf( "Alias List:\\n" );' in cmd_c
	assert 'cmd_aliases[i].inuse = qfalse;' in unaliasall_block
	assert 'FS_Printf( f, "unaliasall\\n" );' in write_aliases_block
	assert 'FS_Printf( f, "alias %s \\"%s\\"\\n", cmd_aliases[i].name, cmd_aliases[i].command );' in write_aliases_block

	assert 'if ( Cmd_FindAlias( cmd_argv[0] ) ) {' in execute_block
	assert 'Cmd_ExecuteAlias();' in execute_block
	assert 'Cmd_AddCommand ("alias",Cmd_Alias_f);' in init_block
	assert 'Cmd_AddCommand ("unalias",Cmd_UnAlias_f);' in init_block
	assert 'Cmd_AddCommand ("unaliasall",Cmd_UnAliasAll_f);' in init_block


def test_qcommon_script_command_surface_matches_retail_registration_order() -> None:
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	cmd_init_block = _extract_function_block(cmd_c, "void Cmd_Init (void) {")
	hunk_init_block = _extract_function_block(common_c, "void Com_InitHunkMemory( void ) {")
	com_init_block = _extract_function_block(common_c, "void Com_Init( char *commandLine ) {")

	command_lines = [
		'Cmd_AddCommand ("cmdlist",Cmd_List_f);',
		'Cmd_AddCommand ("listcmds",Cmd_List_f);',
		'Cmd_AddCommand ("exec",Cmd_Exec_f);',
		'Cmd_AddCommand ("vstr",Cmd_Vstr_f);',
		'Cmd_AddCommand ("echo",Cmd_Echo_f);',
		'Cmd_AddCommand ("wait", Cmd_Wait_f);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in cmd_init_block
		positions.append(cmd_init_block.index(command_line))

	assert positions == sorted(positions)
	assert 'Cmd_AddCommand( "meminfo", Com_Meminfo_f );' in hunk_init_block
	assert 'Cmd_AddCommand ("error", Com_Error_f);' in com_init_block
	assert 'Cmd_AddCommand ("crash", Com_Crash_f );' in com_init_block
	assert 'Cmd_AddCommand ("freeze", Com_Freeze_f);' in com_init_block
	assert 'Cmd_AddCommand ("quit", Com_Quit_f);' in com_init_block


def test_qcommon_script_and_debug_command_handlers_match_retail_contracts() -> None:
	cmd_c = (REPO_ROOT / "src/code/qcommon/cmd.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	wait_block = _extract_function_block(cmd_c, "void Cmd_Wait_f( void ) {")
	exec_block = _extract_function_block(cmd_c, "void Cmd_Exec_f( void ) {")
	vstr_block = _extract_function_block(cmd_c, "void Cmd_Vstr_f( void ) {")
	echo_block = _extract_function_block(cmd_c, "void Cmd_Echo_f (void)")
	list_block = _extract_function_block(cmd_c, "void Cmd_List_f (void)")
	meminfo_block = _extract_function_block(common_c, "void Com_Meminfo_f( void ) {")
	error_block = _extract_function_block(common_c, "static void Com_Error_f (void) {")
	freeze_block = _extract_function_block(common_c, "static void Com_Freeze_f (void) {")
	crash_block = _extract_function_block(common_c, "static void Com_Crash_f( void ) {")
	quit_block = _extract_function_block(common_c, "void Com_Quit_f( void ) {")

	assert 'cmd_wait = atoi( Cmd_Argv( 1 ) );' in wait_block
	assert 'cmd_wait = 1;' in wait_block

	assert 'Com_Printf ("exec <filename> : execute a script file\\n");' in exec_block
	assert 'COM_DefaultExtension( filename, sizeof( filename ), ".cfg" );' in exec_block
	assert 'len = FS_ReadFile( filename, (void **)&f);' in exec_block
	assert 'Com_Printf ("couldn\'t exec %s\\n",Cmd_Argv(1));' in exec_block
	assert 'Com_Printf ("execing %s\\n",Cmd_Argv(1));' in exec_block
	assert 'Cbuf_InsertText (f);' in exec_block
	assert 'FS_FreeFile (f);' in exec_block

	assert 'Com_Printf ("vstr <variablename> : execute a variable command\\n");' in vstr_block
	assert 'v = Cvar_VariableString( Cmd_Argv( 1 ) );' in vstr_block
	assert 'Cbuf_InsertText( va("%s\\n", v ) );' in vstr_block

	assert 'for (i=1 ; i<Cmd_Argc() ; i++)' in echo_block
	assert 'Com_Printf ("%s ",Cmd_Argv(i));' in echo_block
	assert 'Com_Printf ("\\n");' in echo_block

	assert 'if (match && !Com_Filter(match, cmd->name, qfalse)) continue;' in list_block
	assert 'Com_Printf ("%s\\n", cmd->name);' in list_block
	assert 'Com_Printf ("%i commands\\n", i);' in list_block

	assert 'Com_Printf( "%8i bytes total hunk\\n", s_hunkTotal );' in meminfo_block
	assert 'Com_Printf( "%8i bytes total zone\\n", s_zoneTotal );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in dynamic botlib\\n", botlibBytes );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in dynamic renderer\\n", rendererBytes );' in meminfo_block
	assert 'Com_Printf( "        %8i bytes in small Zone memory\\n", smallZoneBytes );' in meminfo_block

	assert 'Com_Error( ERR_DROP, "Testing drop error" );' in error_block
	assert 'Com_Error( ERR_FATAL, "Testing fatal error" );' in error_block

	assert 'Com_Printf( "freeze <seconds>\\n" );' in freeze_block
	assert 's = atof( Cmd_Argv(1) );' in freeze_block
	assert 'start = Com_Milliseconds();' in freeze_block
	assert 'now = Com_Milliseconds();' in freeze_block

	assert '* ( int * ) 0 = 0x12345678;' in crash_block

	assert 'SV_Shutdown ("Server quit\\n");' in quit_block
	assert 'CL_Shutdown ();' in quit_block
	assert 'Com_Shutdown ();' in quit_block
	assert 'FS_Shutdown(qtrue);' in quit_block
	assert 'Sys_Quit ();' in quit_block


def test_qcommon_cvar_and_changevectors_command_surface_matches_retail_registration_order() -> None:
	cvar_c = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	common_c = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

	cvar_init_block = _extract_function_block(cvar_c, "void Cvar_Init (void) {")
	com_init_block = _extract_function_block(common_c, "void Com_Init( char *commandLine ) {")

	command_lines = [
		'Cmd_AddCommand ("reset", Cvar_Reset_f);',
		'Cmd_AddCommand ("clearcvar", Cvar_Clear_f);',
		'Cmd_AddCommand ("cvarlist", Cvar_List_f);',
		'Cmd_AddCommand ("listcvars", Cvar_List_f);',
		'Cmd_AddCommand ("cvar_restart", Cvar_Restart_f);',
		'Cmd_AddCommand ("cvarAdd", Cvar_Add_f);',
		'Cmd_AddCommand ("cvarMult", Cvar_Mult_f);',
	]
	positions = []
	for command_line in command_lines:
		assert command_line in cvar_init_block
		positions.append(cvar_init_block.index(command_line))

	assert positions == sorted(positions)
	assert 'Cmd_AddCommand ("changeVectors", MSG_ReportChangeVectors_f );' in com_init_block


def test_qcommon_cvar_and_changevectors_handlers_match_retail_contracts() -> None:
	cvar_c = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	msg_c = (REPO_ROOT / "src/code/qcommon/msg.c").read_text(encoding="utf-8")

	clear_block = _extract_function_block(cvar_c, "void Cvar_Clear_f( void ) {")
	list_block = _extract_function_block(cvar_c, "void Cvar_List_f( void ) {")
	restart_block = _extract_function_block(cvar_c, "void Cvar_Restart_f( void ) {")
	add_block = _extract_function_block(cvar_c, "void Cvar_Add_f( void ) {")
	mult_block = _extract_function_block(cvar_c, "void Cvar_Mult_f( void ) {")
	change_vectors_block = _extract_function_block(msg_c, "void MSG_ReportChangeVectors_f( void ) {")

	assert 'Com_Printf ("usage: clearcvar <variable>\\n");' in clear_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), "", qtrue );' in clear_block

	assert 'if (match && !Com_Filter(match, var->name, qfalse)) continue;' in list_block
	assert 'Com_Printf (" %s \\"%s\\"\\n", var->name, var->string);' in list_block
	assert 'Com_Printf ("\\n%i total cvars\\n", i);' in list_block
	assert 'Com_Printf ("%i cvar indexes\\n", cvar_numIndexes);' in list_block

	assert 'if ( var->flags & ( CVAR_ROM | CVAR_INIT | CVAR_NORESTART | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD ) ) {' in restart_block
	assert 'Com_DPrintf( "Skipping restart of protected cvar %s\\n", var->name );' in restart_block
	assert 'if ( var->flags & CVAR_USER_CREATED ) {' in restart_block
	assert 'Com_Memset( var, 0, sizeof( *var ) );' in restart_block
	assert 'Cvar_Set( var->name, var->resetString );' in restart_block

	assert 'Com_Printf ("usage: cvarAdd <variable> <amount>\\n");' in add_block
	assert 'var = Cvar_FindVar( Cmd_Argv( 1 ) );' in add_block
	assert 'currentValue = var->value;' in add_block
	assert 'currentValue = 0.0f;' in add_block
	assert 'amount = (float)atof( Cmd_Argv( 2 ) );' in add_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), va("%0.3f", currentValue + amount), qfalse );' in add_block

	assert 'Com_Printf ("usage: cvarMult <variable> <amount>\\n");' in mult_block
	assert 'var = Cvar_FindVar( Cmd_Argv( 1 ) );' in mult_block
	assert 'currentValue = var->value;' in mult_block
	assert 'currentValue = 0.0f;' in mult_block
	assert 'amount = (float)atof( Cmd_Argv( 2 ) );' in mult_block
	assert 'Cvar_Set2( Cmd_Argv( 1 ), va("%0.3f", currentValue * amount), qfalse );' in mult_block

	assert 'for(i=0;i<256;i++) {' in change_vectors_block
	assert 'if (pcount[i]) {' in change_vectors_block
	assert 'Com_Printf("%d used %d\\n", i, pcount[i]);' in change_vectors_block


def test_client_connect_and_demo_commands_match_retail_contracts() -> None:
	cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

	record_block = _extract_function_block(cl_main, "void CL_Record_f( void ) {")
	demo_block = _extract_function_block(cl_main, "void CL_PlayDemo_f( void ) {")
	reconnect_block = _extract_function_block(cl_main, "void CL_Reconnect_f( void ) {")
	connect_block = _extract_function_block(cl_main, "void CL_Connect_f( void ) {")

	assert 'Com_Printf ("Correct usage: record <demoname>\\n");' in record_block
	assert 'Com_Printf ("Already recording.\\n");' in record_block
	assert "CL_StopRecord_f();" in record_block
	assert 'Com_Error( ERR_FATAL, "stoprecord failed" );' in record_block
	assert 'Com_Printf ("recording to %s.\\n", name);' in record_block
	assert 'MSG_WriteByte (&buf, svc_gamestate);' in record_block

	assert 'Com_Printf ("playdemo <demoname>\\n");' in demo_block
	assert 'SV_Shutdown( "Starting Demo.\\n" );' in demo_block
	assert 'CL_Disconnect( qfalse );' in demo_block
	assert 'CL_WalkDemoExt( arg, name, &clc.demofile );' in demo_block

	assert 'Com_Printf( "Can\'t reconnect to localhost.\\n" );' in reconnect_block
	assert 'Cbuf_AddText( va("connect %s\\n", cls.servername ) );' in reconnect_block

	assert 'Com_Printf( "usage: connect [server]\\n");' in connect_block
	assert "CL_RequestMotd();" in connect_block
	assert 'SV_Shutdown( "Server quit\\n" );' in connect_block
	assert 'Cvar_Set( "sv_killserver", "1" );' in connect_block
	assert 'CL_Disconnect( qtrue );' in connect_block
	assert "NET_StringToAdr( cls.servername, &clc.serverAddress)" in connect_block

	assert 'Cmd_AddCommand ("record", CL_Record_f);' in cl_main
	assert 'Cmd_AddCommand ("demo", CL_PlayDemo_f);' in cl_main
	assert 'Cmd_AddCommand ("connect", CL_Connect_f);' in cl_main
	assert 'Cmd_AddCommand ("reconnect", CL_Reconnect_f);' in cl_main


def test_filesystem_command_handlers_match_retail_dir_and_path_contracts() -> None:
	files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")

	dir_block = _extract_function_block(files_c, "void FS_Dir_f( void ) {")
	path_block = _extract_function_block(files_c, "void FS_Path_f( void ) {")

	assert 'Com_Printf( "usage: dir <directory> [extension]\\n" );' in dir_block
	assert "FS_ListFiles( path, extension, &ndirs );" in dir_block
	assert 'Com_Printf( "Directory of %s %s\\n", path, extension );' in dir_block
	assert 'Com_Printf ("%s (0x%08x - %i files)\\n", s->pack->pakFilename, s->pack->checksum, s->pack->numfiles);' in path_block
	assert 'Com_Printf( "    not on the pure list\\n" );' in path_block
	assert 'Com_Printf( "    on the pure list\\n" );' in path_block

	assert 'Cmd_AddCommand ("dir", FS_Dir_f );' in files_c
	assert 'Cmd_AddCommand ("path", FS_Path_f);' in files_c


def test_filesystem_filtered_directory_and_touch_commands_match_retail_contracts() -> None:
	files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")

	newdir_block = _extract_function_block(files_c, "void FS_NewDir_f( void ) {")
	touch_block = _extract_function_block(files_c, "void FS_TouchFile_f( void ) {")

	assert 'Com_Printf( "usage: fdir <filter>\\n" );' in newdir_block
	assert 'Com_Printf( "example: fdir *q3dm*.bsp\\n");' in newdir_block
	assert 'dirnames = FS_ListFilteredFiles( "", "", filter, &ndirs );' in newdir_block
	assert 'FS_SortFileList(dirnames, ndirs);' in newdir_block
	assert 'FS_ConvertPath(dirnames[i]);' in newdir_block
	assert 'Com_Printf( "%d files listed\\n", ndirs );' in newdir_block

	assert 'if ( Cmd_Argc() != 2 ) {' in touch_block
	assert 'Com_Printf( "Usage: touchFile <file>\\n" );' in touch_block
	assert 'FS_FOpenFileRead( Cmd_Argv( 1 ), &f, qfalse );' in touch_block
	assert 'FS_FCloseFile( f );' in touch_block

	assert 'Cmd_AddCommand ("fdir", FS_NewDir_f );' in files_c
	assert 'Cmd_AddCommand ("touchFile", FS_TouchFile_f );' in files_c


def test_server_status_command_matches_retail_wiring_and_output_shape() -> None:
	sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")

	steamid_block = _extract_function_block(sv_ccmds, "static unsigned long long SV_StatusClientSteamId( const client_t *cl ) {")
	status_block = _extract_function_block(sv_ccmds, "static void SV_Status_f( void ) {")

	assert 'steamId = Info_ValueForKey( cl->userinfo, "steamid" );' in steamid_block
	assert "value = value * 10ull + (unsigned long long)( *cursor - '0' );" in steamid_block
	assert 'Com_Printf ("num score ping name            lastmsg address               qport rate  steamid\\n");' in status_block
	assert 'Com_Printf ("--- ----- ---- --------------- ------- --------------------- ----- ----- -----------------\\n");' in status_block
	assert 'steamIdValue = SV_StatusClientSteamId( cl );' in status_block
	assert 'Com_Printf (" %llu", steamIdValue);' in status_block
	assert 'Cmd_AddCommand ("status", SV_Status_f);' in sv_ccmds
