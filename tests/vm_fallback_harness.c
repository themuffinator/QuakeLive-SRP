#include <ctype.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef _WIN32
#include <strings.h>
#endif

#ifdef _WIN32
#define QLR_TEST_EXPORT __declspec(dllexport)
#define QLR_STRICMP _stricmp
#else
#define QLR_TEST_EXPORT
#define QLR_STRICMP strcasecmp
#endif

#include "../src/code/game/q_shared.h"
#include "../src/code/qcommon/qcommon.h"
#include "../src/code/qcommon/qfiles.h"
#include "../src/code/qcommon/vm_local.h"

#define QLR_MAX_TEST_FILES 8
#define QLR_MAX_HUNK_ALLOCS 256
#define QLR_TEST_VM_BSS_LENGTH ( 0x20000 + 64 )
#define QLR_COMPILED_RESULT_BIAS 1000

typedef struct {
	cvar_t	cvar;
	char	name[64];
	char	string[MAX_CVAR_VALUE_STRING];
	char	resetString[MAX_CVAR_VALUE_STRING];
} qlr_stub_cvar_t;

typedef struct {
	char	path[MAX_QPATH];
	byte	*data;
	int	length;
} qlr_test_file_t;

static jmp_buf qlr_error_jmp;
static qboolean qlr_error_jmp_active = qfalse;
static char qlr_last_error[1024];
static char qlr_captured_log[8192];
static size_t qlr_captured_log_len = 0;
static void *qlr_hunk_allocations[QLR_MAX_HUNK_ALLOCS];
static int qlr_hunk_allocation_count = 0;
static int qlr_hunk_remaining = 1024 * 1024;
static qlr_test_file_t qlr_test_files[QLR_MAX_TEST_FILES];
static int qlr_test_file_count = 0;
static int qlr_sys_load_dll_calls = 0;
static int qlr_sys_unload_dll_calls = 0;
static qboolean qlr_stub_dll_should_load = qfalse;
static int qlr_stub_compile_calls = 0;
static int qlr_stub_call_compiled_calls = 0;
static int qlr_stub_system_call_count = 0;
static int qlr_stub_system_call_result = 31337;
static int qlr_last_system_call_arg0 = -1;
static char qlr_last_syscall_origin[64];
static char qlr_last_syscall_module[MAX_QPATH];
static int qlr_last_contract_first_arg = -1;

static qlr_stub_cvar_t qlr_cvar_vm_cgame;
static qlr_stub_cvar_t qlr_cvar_vm_game;
static qlr_stub_cvar_t qlr_cvar_vm_ui;
static qlr_stub_cvar_t qlr_cvar_vm_trace;
static qlr_stub_cvar_t qlr_cvar_fs_restrict;
static qlr_stub_cvar_t qlr_cvar_developer;
static qlr_stub_cvar_t qlr_cvar_zero;

cvar_t *com_developer = &qlr_cvar_developer.cvar;

/*
=============
QLR_ClearCapturedLog
=============
*/
static void QLR_ClearCapturedLog( void ) {
	qlr_captured_log[0] = '\0';
	qlr_captured_log_len = 0;
}

/*
=============
QLR_AppendCapturedLog
=============
*/
static void QLR_AppendCapturedLog( const char *text ) {
	size_t available;
	size_t textLength;

	if ( !text || !*text || qlr_captured_log_len >= sizeof( qlr_captured_log ) - 1 ) {
		return;
	}

	available = sizeof( qlr_captured_log ) - qlr_captured_log_len - 1;
	textLength = strlen( text );
	if ( textLength > available ) {
		textLength = available;
	}

	memcpy( qlr_captured_log + qlr_captured_log_len, text, textLength );
	qlr_captured_log_len += textLength;
	qlr_captured_log[qlr_captured_log_len] = '\0';
}

/*
=============
QLR_ResetErrorState
=============
*/
static void QLR_ResetErrorState( void ) {
	qlr_last_error[0] = '\0';
}

/*
=============
QLR_FormatLastError
=============
*/
static void QLR_FormatLastError( const char *fmt, va_list args ) {
	vsnprintf( qlr_last_error, sizeof( qlr_last_error ), fmt, args );
	QLR_AppendCapturedLog( qlr_last_error );
}

/*
=============
QLR_BeginProtectedCall
=============
*/
static int QLR_BeginProtectedCall( void ) {
	QLR_ResetErrorState();
	if ( setjmp( qlr_error_jmp ) != 0 ) {
		qlr_error_jmp_active = qfalse;
		return 0;
	}

	qlr_error_jmp_active = qtrue;
	return 1;
}

/*
=============
QLR_EndProtectedCall
=============
*/
static int QLR_EndProtectedCall( void ) {
	qlr_error_jmp_active = qfalse;
	return 1;
}

/*
=============
QLR_InitStubCvar
=============
*/
static void QLR_InitStubCvar( qlr_stub_cvar_t *stub, const char *name, const char *value ) {
	if ( !stub ) {
		return;
	}

	memset( stub, 0, sizeof( *stub ) );
	Q_strncpyz( stub->name, name ? name : "", sizeof( stub->name ) );
	Q_strncpyz( stub->string, value ? value : "", sizeof( stub->string ) );
	Q_strncpyz( stub->resetString, value ? value : "", sizeof( stub->resetString ) );
	stub->cvar.name = stub->name;
	stub->cvar.string = stub->string;
	stub->cvar.resetString = stub->resetString;
	stub->cvar.integer = atoi( stub->string );
	stub->cvar.value = (float)atof( stub->string );
}

/*
=============
QLR_SetStubCvarValue
=============
*/
static void QLR_SetStubCvarValue( qlr_stub_cvar_t *stub, const char *value ) {
	if ( !stub ) {
		return;
	}

	Q_strncpyz( stub->string, value ? value : "", sizeof( stub->string ) );
	stub->cvar.integer = atoi( stub->string );
	stub->cvar.value = (float)atof( stub->string );
	stub->cvar.modified = qtrue;
	stub->cvar.modificationCount++;
}

/*
=============
QLR_FindStubCvar
=============
*/
static qlr_stub_cvar_t *QLR_FindStubCvar( const char *name ) {
	qlr_stub_cvar_t *known[] = {
		&qlr_cvar_vm_cgame,
		&qlr_cvar_vm_game,
		&qlr_cvar_vm_ui,
		&qlr_cvar_vm_trace,
		&qlr_cvar_fs_restrict,
		&qlr_cvar_developer,
		&qlr_cvar_zero,
	};
	size_t i;

	if ( !name ) {
		return &qlr_cvar_zero;
	}

	for ( i = 0; i < sizeof( known ) / sizeof( known[0] ); i++ ) {
		if ( QLR_STRICMP( known[i]->name, name ) == 0 ) {
			return known[i];
		}
	}

	return &qlr_cvar_zero;
}

/*
=============
QLR_ResetCvars
=============
*/
static void QLR_ResetCvars( void ) {
	QLR_InitStubCvar( &qlr_cvar_vm_cgame, "vm_cgame", "0" );
	QLR_InitStubCvar( &qlr_cvar_vm_game, "vm_game", "0" );
	QLR_InitStubCvar( &qlr_cvar_vm_ui, "vm_ui", "0" );
	QLR_InitStubCvar( &qlr_cvar_vm_trace, "vm_trace", "0" );
	QLR_InitStubCvar( &qlr_cvar_fs_restrict, "fs_restrict", "0" );
	QLR_InitStubCvar( &qlr_cvar_developer, "developer", "0" );
	QLR_InitStubCvar( &qlr_cvar_zero, "qlr_zero", "0" );
	com_developer = &qlr_cvar_developer.cvar;
}

/*
=============
QLR_FreeTrackedHunkAllocs
=============
*/
static void QLR_FreeTrackedHunkAllocs( void ) {
	int i;

	for ( i = 0; i < qlr_hunk_allocation_count; i++ ) {
		free( qlr_hunk_allocations[i] );
		qlr_hunk_allocations[i] = NULL;
	}

	qlr_hunk_allocation_count = 0;
}

/*
=============
QLR_ClearTestFiles
=============
*/
static void QLR_ClearTestFiles( void ) {
	int i;

	for ( i = 0; i < qlr_test_file_count; i++ ) {
		free( qlr_test_files[i].data );
		qlr_test_files[i].data = NULL;
		qlr_test_files[i].path[0] = '\0';
		qlr_test_files[i].length = 0;
	}

	qlr_test_file_count = 0;
}

/*
=============
QLR_ResetSyscallContractLog
=============
*/
static void QLR_ResetSyscallContractLog( void ) {
	qlr_last_syscall_origin[0] = '\0';
	qlr_last_syscall_module[0] = '\0';
	qlr_last_contract_first_arg = -1;
	qlr_last_system_call_arg0 = -1;
	qlr_stub_system_call_count = 0;
}

/*
=============
QLR_ResetHarnessState
=============
*/
static void QLR_ResetHarnessState( void ) {
	VM_Clear();
	QLR_FreeTrackedHunkAllocs();
	QLR_ClearTestFiles();
	QLR_ClearCapturedLog();
	QLR_ResetErrorState();
	QLR_ResetSyscallContractLog();
	qlr_hunk_remaining = 1024 * 1024;
	qlr_sys_load_dll_calls = 0;
	qlr_sys_unload_dll_calls = 0;
	qlr_stub_dll_should_load = qfalse;
	qlr_stub_compile_calls = 0;
	qlr_stub_call_compiled_calls = 0;
	qlr_stub_system_call_result = 31337;
	QLR_ResetCvars();
}

/*
=============
QLR_WriteLittleInt
=============
*/
static void QLR_WriteLittleInt( byte *dest, int value ) {
	dest[0] = value & 0xff;
	dest[1] = ( value >> 8 ) & 0xff;
	dest[2] = ( value >> 16 ) & 0xff;
	dest[3] = ( value >> 24 ) & 0xff;
}

/*
=============
QLR_RegisterTestFile
=============
*/
static void QLR_RegisterTestFile( const char *path, const byte *data, int length ) {
	qlr_test_file_t *entry;

	if ( qlr_test_file_count >= QLR_MAX_TEST_FILES ) {
		Com_Error( ERR_DROP, "QLR test file registry overflow" );
		return;
	}

	entry = &qlr_test_files[qlr_test_file_count++];
	Q_strncpyz( entry->path, path, sizeof( entry->path ) );
	entry->data = malloc( (size_t)length );
	if ( !entry->data ) {
		Com_Error( ERR_DROP, "QLR failed to allocate %d bytes for %s", length, path );
		return;
	}

	memcpy( entry->data, data, (size_t)length );
	entry->length = length;
}

/*
=============
QLR_RegisterVmCodeFile
=============
*/
static void QLR_RegisterVmCodeFile( const char *module, const byte *code, int codeLength, int instructionCount ) {
	byte *buffer;
	int totalLength;
	char path[MAX_QPATH];

	totalLength = (int)sizeof( vmHeader_t ) + codeLength;
	buffer = malloc( (size_t)totalLength );
	if ( !buffer ) {
		Com_Error( ERR_DROP, "QLR failed to allocate VM image for %s", module );
		return;
	}

	memset( buffer, 0, (size_t)totalLength );
	QLR_WriteLittleInt( buffer + 0, VM_MAGIC );
	QLR_WriteLittleInt( buffer + 4, instructionCount );
	QLR_WriteLittleInt( buffer + 8, (int)sizeof( vmHeader_t ) );
	QLR_WriteLittleInt( buffer + 12, codeLength );
	QLR_WriteLittleInt( buffer + 16, (int)sizeof( vmHeader_t ) + codeLength );
	QLR_WriteLittleInt( buffer + 20, 0 );
	QLR_WriteLittleInt( buffer + 24, 0 );
	QLR_WriteLittleInt( buffer + 28, QLR_TEST_VM_BSS_LENGTH );
	memcpy( buffer + sizeof( vmHeader_t ), code, (size_t)codeLength );

	Com_sprintf( path, sizeof( path ), "vm/%s.qvm", module );
	QLR_RegisterTestFile( path, buffer, totalLength );
	free( buffer );
}

/*
=============
QLR_RegisterAddVmFile
=============
*/
static void QLR_RegisterAddVmFile( const char *module ) {
	byte code[32];
	int offset;

	offset = 0;
	code[offset++] = OP_ENTER;
	QLR_WriteLittleInt( &code[offset], 0 );
	offset += 4;
	code[offset++] = OP_LOCAL;
	QLR_WriteLittleInt( &code[offset], 8 );
	offset += 4;
	code[offset++] = OP_LOAD4;
	code[offset++] = OP_LOCAL;
	QLR_WriteLittleInt( &code[offset], 12 );
	offset += 4;
	code[offset++] = OP_LOAD4;
	code[offset++] = OP_ADD;
	code[offset++] = OP_LEAVE;
	QLR_WriteLittleInt( &code[offset], 0 );
	offset += 4;

	QLR_RegisterVmCodeFile( module, code, offset, 7 );
}

/*
=============
QLR_RegisterSyscallVmFile
=============
*/
static void QLR_RegisterSyscallVmFile( const char *module, int syscallNum ) {
	byte code[24];
	int offset;

	offset = 0;
	code[offset++] = OP_ENTER;
	/*
	 * Negative OP_CALL stores its return address at programStack. Give the
	 * synthetic syscall probe a real frame so LEAVE restores the top-level
	 * -1 return address instead of looping on itself.
	 */
	QLR_WriteLittleInt( &code[offset], 8 );
	offset += 4;
	code[offset++] = OP_CONST;
	QLR_WriteLittleInt( &code[offset], -1 - syscallNum );
	offset += 4;
	code[offset++] = OP_CALL;
	code[offset++] = OP_LEAVE;
	QLR_WriteLittleInt( &code[offset], 8 );
	offset += 4;

	QLR_RegisterVmCodeFile( module, code, offset, 4 );
}

/*
=============
QLR_FakeDllEntryPoint
=============
*/
static int QDECL QLR_FakeDllEntryPoint( int callNum, ... ) {
	(void)callNum;
	return 0;
}

/*
=============
QLR_VM_TestSystemCall
=============
*/
static int QLR_VM_TestSystemCall( int *args ) {
	qlr_stub_system_call_count++;
	qlr_last_system_call_arg0 = args ? args[0] : -1;
	return qlr_stub_system_call_result;
}

/*
=============
Q_stricmp
=============
*/
int Q_stricmp( const char *s1, const char *s2 ) {
	if ( !s1 ) {
		s1 = "";
	}
	if ( !s2 ) {
		s2 = "";
	}

	return QLR_STRICMP( s1, s2 );
}

/*
=============
Q_strncpyz
=============
*/
void Q_strncpyz( char *dest, const char *src, int destsize ) {
	if ( !dest || destsize <= 0 ) {
		return;
	}

	if ( !src ) {
		dest[0] = '\0';
		return;
	}

	strncpy( dest, src, (size_t)( destsize - 1 ) );
	dest[destsize - 1] = '\0';
}

/*
=============
Com_Memset
=============
*/
void Com_Memset( void *dest, const int fill, const size_t count ) {
	memset( dest, fill, count );
}

/*
=============
Com_Memcpy
=============
*/
void Com_Memcpy( void *dest, const void *src, const size_t count ) {
	memcpy( dest, src, count );
}

/*
=============
Com_sprintf
=============
*/
int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	int written;

	va_start( args, fmt );
	written = vsnprintf( dest, (size_t)size, fmt, args );
	va_end( args );

	if ( size > 0 ) {
		dest[size - 1] = '\0';
	}

	return written;
}

/*
=============
Com_Printf
=============
*/
void QDECL Com_Printf( const char *fmt, ... ) {
	va_list args;
	char message[1024];

	va_start( args, fmt );
	vsnprintf( message, sizeof( message ), fmt, args );
	va_end( args );
	QLR_AppendCapturedLog( message );
}

/*
=============
Com_DPrintf
=============
*/
void QDECL Com_DPrintf( const char *fmt, ... ) {
	va_list args;
	char message[1024];

	va_start( args, fmt );
	vsnprintf( message, sizeof( message ), fmt, args );
	va_end( args );
	QLR_AppendCapturedLog( message );
}

/*
=============
Com_Error
=============
*/
void QDECL Com_Error( int level, const char *error, ... ) {
	va_list args;

	(void)level;

	va_start( args, error );
	QLR_FormatLastError( error, args );
	va_end( args );

	if ( qlr_error_jmp_active ) {
		longjmp( qlr_error_jmp, 1 );
	}

	abort();
}

/*
=============
Z_Malloc
=============
*/
void *Z_Malloc( int size ) {
	return calloc( 1, (size_t)size );
}

/*
=============
Z_Free
=============
*/
void Z_Free( void *ptr ) {
	free( ptr );
}

/*
=============
Hunk_Alloc
=============
*/
void *Hunk_Alloc( int size, ha_pref preference ) {
	void *memory;

	(void)preference;

	if ( qlr_hunk_allocation_count >= QLR_MAX_HUNK_ALLOCS ) {
		Com_Error( ERR_DROP, "QLR hunk allocation tracker overflow" );
		return NULL;
	}

	memory = calloc( 1, (size_t)size );
	if ( !memory ) {
		Com_Error( ERR_DROP, "QLR failed to allocate %d hunk bytes", size );
		return NULL;
	}

	qlr_hunk_allocations[qlr_hunk_allocation_count++] = memory;
	qlr_hunk_remaining -= size;
	if ( qlr_hunk_remaining < 0 ) {
		qlr_hunk_remaining = 0;
	}

	return memory;
}

/*
=============
Hunk_MemoryRemaining
=============
*/
int Hunk_MemoryRemaining( void ) {
	return qlr_hunk_remaining;
}

/*
=============
Cmd_AddCommand
=============
*/
void Cmd_AddCommand( const char *cmd_name, xcommand_t function ) {
	(void)cmd_name;
	(void)function;
}

/*
=============
COM_StripExtension
=============
*/
void COM_StripExtension( const char *in, char *out ) {
	size_t length;

	if ( !out ) {
		return;
	}

	if ( !in ) {
		out[0] = '\0';
		return;
	}

	length = strlen( in );
	while ( length > 0 && in[length - 1] != '.' && in[length - 1] != '/' && in[length - 1] != '\\' ) {
		length--;
	}

	if ( length > 0 && in[length - 1] == '.' ) {
		memcpy( out, in, length - 1 );
		out[length - 1] = '\0';
		return;
	}

	Q_strncpyz( out, in, MAX_QPATH );
}

/*
=============
COM_Parse
=============
*/
char *COM_Parse( char **data_p ) {
	static char token[MAX_TOKEN_CHARS];
	char *data;
	int length;

	token[0] = '\0';
	if ( !data_p || !*data_p ) {
		return token;
	}

	data = *data_p;
	while ( *data && isspace( (unsigned char)*data ) ) {
		data++;
	}

	length = 0;
	while ( *data && !isspace( (unsigned char)*data ) && length < MAX_TOKEN_CHARS - 1 ) {
		token[length++] = *data++;
	}
	token[length] = '\0';
	*data_p = data;
	return token;
}

/*
=============
Cvar_Get
=============
*/
cvar_t *Cvar_Get( const char *var_name, const char *value, int flags ) {
	qlr_stub_cvar_t *stub;

	(void)flags;

	stub = QLR_FindStubCvar( var_name );
	if ( stub == &qlr_cvar_zero && value && value[0] ) {
		QLR_SetStubCvarValue( stub, value );
	}

	if ( stub != &qlr_cvar_zero && value && !stub->cvar.string[0] ) {
		QLR_SetStubCvarValue( stub, value );
	}

	return &stub->cvar;
}

/*
=============
Cvar_VariableValue
=============
*/
float Cvar_VariableValue( const char *var_name ) {
	return QLR_FindStubCvar( var_name )->cvar.value;
}

/*
=============
FS_FOpenFileAppend
=============
*/
fileHandle_t FS_FOpenFileAppend( const char *filename ) {
	(void)filename;
	return 1;
}

/*
=============
FS_Write
=============
*/
int FS_Write( const void *buffer, int len, fileHandle_t f ) {
	(void)buffer;
	(void)f;
	return len;
}

/*
=============
FS_FCloseFile
=============
*/
void FS_FCloseFile( fileHandle_t f ) {
	(void)f;
}

/*
=============
FS_ReadFile
=============
*/
int FS_ReadFile( const char *qpath, void **buffer ) {
	int i;

	if ( buffer ) {
		*buffer = NULL;
	}

	for ( i = 0; i < qlr_test_file_count; i++ ) {
		if ( QLR_STRICMP( qlr_test_files[i].path, qpath ) == 0 ) {
			void *copy;

			copy = malloc( (size_t)qlr_test_files[i].length );
			if ( !copy ) {
				Com_Error( ERR_DROP, "QLR failed to allocate read buffer for %s", qpath );
				return -1;
			}

			memcpy( copy, qlr_test_files[i].data, (size_t)qlr_test_files[i].length );
			if ( buffer ) {
				*buffer = copy;
			}
			return qlr_test_files[i].length;
		}
	}

	return -1;
}

/*
=============
FS_FreeFile
=============
*/
void FS_FreeFile( void *buffer ) {
	free( buffer );
}

/*
=============
Sys_LoadDll
=============
*/
void *QDECL Sys_LoadDll( const char *name, char *fqpath, int (QDECL **entryPoint)(int, ...),
	void **dllExports, void *imports, int *apiVersion, int (QDECL *systemcalls)(int, ...) ) {
	(void)imports;
	(void)apiVersion;
	(void)systemcalls;

	qlr_sys_load_dll_calls++;

	if ( fqpath ) {
		Com_sprintf( fqpath, MAX_QPATH + 1, "qlr/%sx86.dll", name ? name : "unknown" );
	}
	if ( entryPoint ) {
		*entryPoint = NULL;
	}
	if ( dllExports ) {
		*dllExports = NULL;
	}

	if ( !qlr_stub_dll_should_load ) {
		return NULL;
	}

	if ( entryPoint ) {
		*entryPoint = QLR_FakeDllEntryPoint;
	}

	return (void *)(intptr_t)0x1;
}

/*
=============
Sys_UnloadDll
=============
*/
void Sys_UnloadDll( void *dllHandle ) {
	(void)dllHandle;
	qlr_sys_unload_dll_calls++;
}

/*
=============
SyscallContract_ResetLog
=============
*/
void SyscallContract_ResetLog( void ) {
	QLR_ResetSyscallContractLog();
}

/*
=============
SyscallContract_Shutdown
=============
*/
void SyscallContract_Shutdown( void ) {
}

/*
=============
SyscallContract_LogEvent
=============
*/
void SyscallContract_LogEvent( const char *origin, const char *module, const int *stack, int count ) {
	(void)count;

	Q_strncpyz( qlr_last_syscall_origin, origin ? origin : "", sizeof( qlr_last_syscall_origin ) );
	Q_strncpyz( qlr_last_syscall_module, module ? module : "", sizeof( qlr_last_syscall_module ) );
	qlr_last_contract_first_arg = stack ? stack[0] : -1;
}

/*
=============
VM_Compile
=============
*/
void VM_Compile( vm_t *vm, vmHeader_t *header ) {
	(void)header;

	qlr_stub_compile_calls++;
	vm->codeBase = Hunk_Alloc( 4, h_low );
}

/*
=============
VM_CallCompiled
=============
*/
int VM_CallCompiled( vm_t *vm, int *args ) {
	qlr_stub_call_compiled_calls++;
	vm->currentlyInterpreting = qtrue;
	vm->currentlyInterpreting = qfalse;
	return args[0] + args[1] + QLR_COMPILED_RESULT_BIAS;
}

/*
=============
QLR_VM_TestLastError
=============
*/
QLR_TEST_EXPORT const char *QLR_VM_TestLastError( void ) {
	return qlr_last_error;
}

/*
=============
QLR_VM_TestCapturedLog
=============
*/
QLR_TEST_EXPORT const char *QLR_VM_TestCapturedLog( void ) {
	return qlr_captured_log;
}

/*
=============
QLR_VM_TestLastSyscallOrigin
=============
*/
QLR_TEST_EXPORT const char *QLR_VM_TestLastSyscallOrigin( void ) {
	return qlr_last_syscall_origin;
}

/*
=============
QLR_VM_TestLastSyscallModule
=============
*/
QLR_TEST_EXPORT const char *QLR_VM_TestLastSyscallModule( void ) {
	return qlr_last_syscall_module;
}

/*
=============
QLR_VM_TestInitDefaults
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestInitDefaults( int *outVmCgame, int *outVmGame, int *outVmUi ) {
	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();

	if ( outVmCgame ) {
		*outVmCgame = qlr_cvar_vm_cgame.cvar.integer;
	}
	if ( outVmGame ) {
		*outVmGame = qlr_cvar_vm_game.cvar.integer;
	}
	if ( outVmUi ) {
		*outVmUi = qlr_cvar_vm_ui.cvar.integer;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestNativeFallbackToCompiled
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestNativeFallbackToCompiled( int *outCompiled, int *outDllLoadCalls, int *outCompileCalls, int *outCallResult ) {
	vm_t *vm;
	int args[2];
	int callResult;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	QLR_RegisterAddVmFile( "testvm" );
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_NATIVE, NULL, 0 );
	args[0] = 40;
	args[1] = 2;
	callResult = vm ? VM_CallCompiled( vm, args ) : -1;

	if ( outCompiled ) {
		*outCompiled = vm && vm->compiled ? 1 : 0;
	}
	if ( outDllLoadCalls ) {
		*outDllLoadCalls = qlr_sys_load_dll_calls;
	}
	if ( outCompileCalls ) {
		*outCompileCalls = qlr_stub_compile_calls;
	}
	if ( outCallResult ) {
		*outCallResult = callResult;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestRestrictForcesCompiled
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestRestrictForcesCompiled( int *outCompiled, int *outDllLoadCalls, int *outCompileCalls, int *outCallResult ) {
	vm_t *vm;
	int args[2];
	int callResult;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	QLR_SetStubCvarValue( &qlr_cvar_fs_restrict, "1" );
	qlr_stub_dll_should_load = qtrue;
	QLR_RegisterAddVmFile( "testvm" );
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_NATIVE, NULL, 0 );
	args[0] = 4;
	args[1] = 3;
	callResult = vm ? VM_CallCompiled( vm, args ) : -1;

	if ( outCompiled ) {
		*outCompiled = vm && vm->compiled ? 1 : 0;
	}
	if ( outDllLoadCalls ) {
		*outDllLoadCalls = qlr_sys_load_dll_calls;
	}
	if ( outCompileCalls ) {
		*outCompileCalls = qlr_stub_compile_calls;
	}
	if ( outCallResult ) {
		*outCallResult = callResult;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestMissingQvmAfterNativeFailure
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestMissingQvmAfterNativeFailure( int *outCreated, int *outDllLoadCalls ) {
	vm_t *vm;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_NATIVE, NULL, 0 );

	if ( outCreated ) {
		*outCreated = vm ? 1 : 0;
	}
	if ( outDllLoadCalls ) {
		*outDllLoadCalls = qlr_sys_load_dll_calls;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestInterpreterAdd
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestInterpreterAdd( int *outCompiled, int *outInstructionPointersLength, int *outCurrentlyInterpreting, int *outCallResult ) {
	vm_t *vm;
	int args[2];
	int callResult;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	QLR_RegisterAddVmFile( "testvm" );
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_BYTECODE, NULL, 0 );
	args[0] = 40;
	args[1] = 2;
	currentVM = vm;
	callResult = vm ? VM_CallInterpreted( vm, args ) : -1;
	currentVM = NULL;

	if ( outCompiled ) {
		*outCompiled = vm && vm->compiled ? 1 : 0;
	}
	if ( outInstructionPointersLength ) {
		*outInstructionPointersLength = vm ? vm->instructionPointersLength : 0;
	}
	if ( outCurrentlyInterpreting ) {
		*outCurrentlyInterpreting = vm && vm->currentlyInterpreting ? 1 : 0;
	}
	if ( outCallResult ) {
		*outCallResult = callResult;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestInterpreterSyscall
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestInterpreterSyscall( int *outCallResult, int *outSystemCallCount, int *outSystemCallArg0, int *outContractFirstArg ) {
	vm_t *vm;
	int args[1];
	int callResult;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	QLR_RegisterSyscallVmFile( "testvm", 5 );
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_BYTECODE, NULL, 0 );
	args[0] = 0;
	currentVM = vm;
	callResult = vm ? VM_CallInterpreted( vm, args ) : -1;
	currentVM = NULL;

	if ( outCallResult ) {
		*outCallResult = callResult;
	}
	if ( outSystemCallCount ) {
		*outSystemCallCount = qlr_stub_system_call_count;
	}
	if ( outSystemCallArg0 ) {
		*outSystemCallArg0 = qlr_last_system_call_arg0;
	}
	if ( outContractFirstArg ) {
		*outContractFirstArg = qlr_last_contract_first_arg;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestRestartNativeFallback
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestRestartNativeFallback( int *outCompiled, int *outDllLoadCalls, int *outDllUnloadCalls, int *outCompileCalls, int *outCallResult ) {
	vm_t *vm;
	int args[2];
	int callResult;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	VM_Init();
	qlr_stub_dll_should_load = qtrue;
	vm = VM_Create( "testvm", QLR_VM_TestSystemCall, VMI_NATIVE, NULL, 0 );
	QLR_RegisterAddVmFile( "testvm" );
	qlr_stub_dll_should_load = qfalse;
	vm = VM_Restart( vm );
	args[0] = 40;
	args[1] = 2;
	callResult = vm ? VM_CallCompiled( vm, args ) : -1;

	if ( outCompiled ) {
		*outCompiled = vm && vm->compiled ? 1 : 0;
	}
	if ( outDllLoadCalls ) {
		*outDllLoadCalls = qlr_sys_load_dll_calls;
	}
	if ( outDllUnloadCalls ) {
		*outDllUnloadCalls = qlr_sys_unload_dll_calls;
	}
	if ( outCompileCalls ) {
		*outCompileCalls = qlr_stub_compile_calls;
	}
	if ( outCallResult ) {
		*outCallResult = callResult;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_VM_TestArgPtrModes
=============
*/
QLR_TEST_EXPORT int QLR_VM_TestArgPtrModes( intptr_t *outMasked, intptr_t *outEntry, intptr_t *outDllInterface ) {
	vm_t vm;
	byte data[64];

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	memset( &vm, 0, sizeof( vm ) );
	memset( data, 0, sizeof( data ) );
	vm.dataBase = data;
	vm.dataMask = 0x1f;

	currentVM = &vm;
	if ( outMasked ) {
		*outMasked = (intptr_t)VM_ArgPtr( 0x23 ) - (intptr_t)vm.dataBase;
	}

	vm.entryPoint = QLR_FakeDllEntryPoint;
	if ( outEntry ) {
		*outEntry = (intptr_t)VM_ExplicitArgPtr( &vm, 0x23 ) - (intptr_t)vm.dataBase;
	}

	vm.entryPoint = NULL;
	vm.dllInterface = qtrue;
	if ( outDllInterface ) {
		*outDllInterface = (intptr_t)VM_ExplicitArgPtr( &vm, 0x23 );
	}

	currentVM = NULL;
	return QLR_EndProtectedCall();
}
