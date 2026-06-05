from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_LOG = REPO_ROOT / "src" / "code" / "botlib" / "l_log.c"
BOTLIB_LOG_H = REPO_ROOT / "src" / "code" / "botlib" / "l_log.h"
BOTLIB_MEMORY = REPO_ROOT / "src" / "code" / "botlib" / "l_memory.c"
BOTLIB_MEMORY_H = REPO_ROOT / "src" / "code" / "botlib" / "l_memory.h"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"
GAME_AI_MAIN = REPO_ROOT / "src" / "code" / "game" / "ai_main.c"
GAME_BOTLIB = REPO_ROOT / "src" / "code" / "game" / "botlib.h"
SERVER_BOT = REPO_ROOT / "src" / "code" / "server" / "sv_bot.c"
QL_STEAM_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
QAGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil.txt"
)
QAGAME_GHIDRA_TOP = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "qagamex86"
	/ "decompile_top_functions.c"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


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


def _non_memorymanager_source(memory_source: str) -> str:
	dump_memory = memory_source.find("void DumpMemory(void)")
	if dump_memory == -1:
		raise AssertionError("MEMORYMANEGER DumpMemory branch not found")

	non_manager = memory_source.find("#else", dump_memory)
	if non_manager == -1:
		raise AssertionError("non-MEMORYMANEGER branch not found")

	return memory_source[non_manager:]


def test_botlib_log_runtime_matches_retail_gate_and_file_wrappers() -> None:
	log = _read(BOTLIB_LOG)
	log_h = _read(BOTLIB_LOG_H)
	interface = _read(BOTLIB_INTERFACE)
	ai_main = _read(GAME_AI_MAIN)
	hlil = _read(QL_STEAM_HLIL_PART03)
	qagame_hlil = _read(QAGAME_HLIL)
	qagame_ghidra = _read(QAGAME_GHIDRA_TOP)
	functions = _read(QL_STEAM_FUNCTIONS)

	log_open = _extract_function_block(log, "void Log_Open(char *filename)")
	log_close = _extract_function_block(log, "void Log_Close(void)")
	log_shutdown = _extract_function_block(log, "void Log_Shutdown(void)")
	log_write = _extract_function_block(log, "void QDECL Log_Write(char *fmt, ...)")
	log_write_timed = _extract_function_block(log, "void QDECL Log_WriteTimeStamped(char *fmt, ...)")
	log_file_pointer = _extract_function_block(log, "FILE *Log_FilePointer(void)")
	log_flush = _extract_function_block(log, "void Log_Flush(void)")
	botlib_setup = _extract_function_block(interface, "int Export_BotLibSetup(void)")
	botlib_shutdown = _extract_function_block(interface, "int Export_BotLibShutdown(void)")
	bot_init_library = _extract_function_block(ai_main, "int BotInitLibrary(void)")
	bot_ai_setup = _extract_function_block(ai_main, "int BotAISetup( int restart )")

	assert "#define MAX_LOGFILENAMESIZE\t\t1024" in log
	assert "char filename[MAX_LOGFILENAMESIZE];" in log
	assert "FILE *fp;" in log
	assert "int numwrites;" in log

	assert 'if (!LibVarValue("bot_log", "0")) return;' in log_open
	assert 'LibVarValue("log", "0")' not in log_open
	assert 'botimport.Print(PRT_MESSAGE, "openlog <filename>\\n");' in log_open
	assert 'botimport.Print(PRT_ERROR, "log file %s is already opened\\n", logfile.filename);' in log_open
	assert 'logfile.fp = fopen(filename, "wb");' in log_open
	assert 'botimport.Print(PRT_ERROR, "can\'t open the log file %s\\n", filename);' in log_open
	assert "strncpy(logfile.filename, filename, MAX_LOGFILENAMESIZE);" in log_open
	assert 'botimport.Print(PRT_MESSAGE, "Opened log %s\\n", logfile.filename);' in log_open

	assert "if (!logfile.fp) return;" in log_close
	assert "if (fclose(logfile.fp))" in log_close
	assert 'botimport.Print(PRT_ERROR, "can\'t close log file %s\\n", logfile.filename);' in log_close
	assert "logfile.fp = NULL;" in log_close
	assert 'botimport.Print(PRT_MESSAGE, "Closed log %s\\n", logfile.filename);' in log_close
	assert "if (logfile.fp) Log_Close();" in log_shutdown

	assert "if (!logfile.fp) return;" in log_write
	assert "va_start(ap, fmt);" in log_write
	assert "vfprintf(logfile.fp, fmt, ap);" in log_write
	assert "fflush(logfile.fp);" in log_write

	assert "fprintf(logfile.fp, \"%d   %02d:%02d:%02d:%02d   \"," in log_write_timed
	assert "logfile.numwrites," in log_write_timed
	assert "(int) (botlibglobals.time / 60 / 60)," in log_write_timed
	assert "vfprintf(logfile.fp, fmt, ap);" in log_write_timed
	assert 'fprintf(logfile.fp, "\\r\\n");' in log_write_timed
	assert "logfile.numwrites++;" in log_write_timed
	assert "fflush(logfile.fp);" in log_write_timed

	assert "return logfile.fp;" in log_file_pointer
	assert "if (logfile.fp) fflush(logfile.fp);" in log_flush
	for expected in (
		"void Log_Open(char *filename);",
		"void Log_Close(void);",
		"void Log_Shutdown(void);",
		"void QDECL Log_Write(char *fmt, ...);",
		"void QDECL Log_WriteTimeStamped(char *fmt, ...);",
		"FILE *Log_FilePointer(void);",
		"void Log_Flush(void);",
	):
		assert expected in log_h

	assert 'Log_Open("botlib.log");' in botlib_setup
	assert "PrintMemoryLabels();" in botlib_shutdown
	assert "Log_Shutdown();" in botlib_shutdown
	assert 'trap_Cvar_VariableStringBuffer("bot_log", buf, sizeof(buf));' in bot_init_library
	assert 'trap_BotLibVarSet("bot_log", buf);' in bot_init_library
	assert 'trap_Cvar_Register(&bot_log, "bot_log", "0", 0);' in bot_ai_setup

	for expected in (
		"004a8830    int32_t sub_4a8830(char* arg1)",
		'004a883e  st0, result = sub_4a8770("bot_log", U"0")',
		'004a8893              return data_16dd800(3, "log file %s is already opened\\n", 0xe4a0c8)',
		"004a889a          int32_t eax_3 = fopen(arg1, &data_53c338)",
		'004a88c1              return data_16dd800(3, "can\'t open the log file %s\\n", arg1)',
		"004a88cd          strncpy(0xe4a0c8, arg1, 0x400)",
		'004a88ec          return data_16dd800(1, "Opened log %s\\n", 0xe4a0c8)',
		'004a88f4  return data_16dd800(1, "openlog <filename>\\n")',
		"004a8910    int32_t sub_4a8910()",
		"004a892a  if (fclose(result) != 0)",
		'004a893c      return data_16dd800(3, "can\'t close log file %s\\n", 0xe4a0c8)',
		"004a8944  data_e4a4c8 = 0",
		'004a894e  return data_16dd800(1, "Closed log %s\\n", 0xe4a0c8)',
		"004a8960    void sub_4a8960()",
		"004a8969  return sub_4a8910() __tailcall",
		"004a8970    int32_t sub_4a8970(int32_t arg1)",
		"004a8985  vfprintf(result, arg1, &arg_8)",
		"004a8991  return fflush(data_e4a4c8)",
		'004a7d23  sub_4a8830("botlib.log")',
		"004a7e16  sub_4a8960()",
	):
		assert expected in hlil

	for expected in (
		"FUN_004a8830,004a8830,210,0,unknown",
		"FUN_004a8910,004a8910,72,0,unknown",
		"FUN_004a8960,004a8960,15,0,unknown",
		"FUN_004a8970,004a8970,44,0,unknown",
	):
		assert expected in functions

	assert '10023e02  (*(data_104b13ac + 0x34))("bot_log", &var_94, 0x90)' in qagame_hlil
	assert '10023e1a  (*(data_104b13ac + 0xcc))("bot_log", &var_94)' in qagame_hlil
	assert '100241d9  (*(data_104b13ac + 0x44))(0x105e3360, "bot_log", &data_1007d0a8, 0)' in qagame_hlil
	assert '(**(code **)(DAT_104b13ac + 0x34))("bot_log",local_94,0x90);' in qagame_ghidra
	assert '(**(code **)(DAT_104b13ac + 0xcc))("bot_log",local_94);' in qagame_ghidra


def test_botlib_memory_runtime_matches_retail_import_callback_wrappers() -> None:
	memory = _read(BOTLIB_MEMORY)
	memory_h = _read(BOTLIB_MEMORY_H)
	game_botlib = _read(GAME_BOTLIB)
	interface = _read(BOTLIB_INTERFACE)
	server_bot = _read(SERVER_BOT)
	hlil = _read(QL_STEAM_HLIL_PART03)
	functions = _read(QL_STEAM_FUNCTIONS)
	non_manager = _non_memorymanager_source(memory)

	get_memory = _extract_function_block(non_manager, "void *GetMemory(unsigned long size)")
	get_cleared_memory = _extract_function_block(non_manager, "void *GetClearedMemory(unsigned long size)")
	get_hunk_memory = _extract_function_block(non_manager, "void *GetHunkMemory(unsigned long size)")
	get_cleared_hunk = _extract_function_block(non_manager, "void *GetClearedHunkMemory(unsigned long size)")
	free_memory = _extract_function_block(non_manager, "void FreeMemory(void *ptr)")
	available_memory = _extract_function_block(non_manager, "int AvailableMemory(void)")
	print_used = _extract_function_block(non_manager, "void PrintUsedMemorySize(void)")
	print_labels = _extract_function_block(non_manager, "void PrintMemoryLabels(void)")
	get_botlib_api = _extract_function_block(
		interface,
		"botlib_export_t *GetBotLibAPI(int apiVersion, botlib_import_t *import)",
	)
	bot_import_get = _extract_function_block(server_bot, "void *BotImport_GetMemory(int size)")
	bot_import_free = _extract_function_block(server_bot, "void BotImport_FreeMemory(void *ptr)")
	bot_import_hunk = _extract_function_block(server_bot, "void *BotImport_HunkAlloc( int size )")
	sv_bot_init = _extract_function_block(server_bot, "void SV_BotInitBotLib(void)")

	assert "//#define MEMORYMANEGER" in memory
	assert "#define MEM_ID\t\t0x12345678l" in memory
	assert "#define HUNK_ID\t\t0x87654321l" in memory
	assert "int allocatedmemory;" in memory
	assert "int totalmemorysize;" in memory
	assert "int numblocks;" in memory

	assert "void *GetMemory(unsigned long size);" in memory_h
	assert "void *GetClearedMemory(unsigned long size);" in memory_h
	assert "#define GetHunkMemory GetMemory" in memory_h
	assert "#define GetClearedHunkMemory GetClearedMemory" in memory_h
	assert "void *GetHunkMemory(unsigned long size);" in memory_h
	assert "void *GetClearedHunkMemory(unsigned long size);" in memory_h
	assert "void FreeMemory(void *ptr);" in memory_h
	assert "int AvailableMemory(void);" in memory_h
	assert "void PrintUsedMemorySize(void);" in memory_h
	assert "void PrintMemoryLabels(void);" in memory_h
	assert "int MemoryByteSize(void *ptr);" in memory_h
	assert "void DumpMemory(void);" in memory_h

	assert "ptr = botimport.GetMemory(size + sizeof(unsigned long int));" in get_memory
	assert "if (!ptr) return NULL;" in get_memory
	assert "memid = (unsigned long int *) ptr;" in get_memory
	assert "*memid = MEM_ID;" in get_memory
	assert "return (unsigned long int *) ((char *) ptr + sizeof(unsigned long int));" in get_memory

	assert "ptr = GetMemory(size);" in get_cleared_memory
	assert "Com_Memset(ptr, 0, size);" in get_cleared_memory
	assert "return ptr;" in get_cleared_memory

	assert "ptr = botimport.HunkAlloc(size + sizeof(unsigned long int));" in get_hunk_memory
	assert "if (!ptr) return NULL;" in get_hunk_memory
	assert "*memid = HUNK_ID;" in get_hunk_memory
	assert "return (unsigned long int *) ((char *) ptr + sizeof(unsigned long int));" in get_hunk_memory

	assert "ptr = GetHunkMemory(size);" in get_cleared_hunk
	assert "Com_Memset(ptr, 0, size);" in get_cleared_hunk
	assert "return ptr;" in get_cleared_hunk

	assert "memid = (unsigned long int *) ((char *) ptr - sizeof(unsigned long int));" in free_memory
	assert "if (*memid == MEM_ID)" in free_memory
	assert "botimport.FreeMemory(memid);" in free_memory
	assert "return botimport.AvailableMemory();" in available_memory
	assert print_used.strip() == "void PrintUsedMemorySize(void)\n{\n}"
	assert print_labels.strip() == "void PrintMemoryLabels(void)\n{\n}"

	for expected in (
		"void\t\t*(*GetMemory)(int size);",
		"void\t\t(*FreeMemory)(void *ptr);",
		"int\t\t\t(*AvailableMemory)(void);",
		"void\t\t*(*HunkAlloc)(int size);",
	):
		assert expected in game_botlib

	assert "botimport = *import;" in get_botlib_api
	assert "assert(botimport.Print);" in get_botlib_api
	assert "ptr = Z_TagMalloc( size, TAG_BOTLIB );" in bot_import_get
	assert "Z_Free(ptr);" in bot_import_free
	assert "if( Hunk_CheckMark() )" in bot_import_hunk
	assert 'Com_Error( ERR_DROP, "SV_Bot_HunkAlloc: Alloc with marks already set\\n" );' in bot_import_hunk
	assert "return Hunk_Alloc( size, h_high );" in bot_import_hunk
	assert "botlib_import.GetMemory = BotImport_GetMemory;" in sv_bot_init
	assert "botlib_import.FreeMemory = BotImport_FreeMemory;" in sv_bot_init
	assert "botlib_import.AvailableMemory = Z_AvailableMemory;" in sv_bot_init
	assert "botlib_import.HunkAlloc = BotImport_HunkAlloc;" in sv_bot_init
	assert "botlib_export = (botlib_export_t *)GetBotLibAPI( BOTLIB_API_VERSION, &botlib_import );" in sv_bot_init

	for expected in (
		"004a83c0    int32_t sub_4a83c0(int32_t arg1, int32_t arg2)",
		"004a83de  __builtin_memcpy(dest: &data_16dd800, src: arg2, n: 0x58)",
		"004a89a0    void* sub_4a89a0(int32_t arg1)",
		"004a89aa  int32_t* result = data_16dd820(arg1 + 4)",
		"004a89b9  *result = 0x12345678",
		"004a89c3  return &result[1]",
		"004a89d0    char* sub_4a89d0(int32_t arg1)",
		"004a89dc  int32_t* eax_1 = data_16dd820(arg1 + 4)",
		"004a89ee      sub_4c95e0(nullptr, 0, arg1)",
		"004a8a03  *eax_1 = 0x12345678",
		"004a8a09  sub_4c95e0(&eax_1[1], 0, arg1)",
		"004a8a16  return &eax_1[1]",
		"004a8a20    void* sub_4a8a20(int32_t arg1)",
		"004a8a2a  int32_t* result = data_16dd82c(arg1 + 4)",
		"004a8a39  *result = 0x87654321",
		"004a8a43  return &result[1]",
		"004a8a50    char* sub_4a8a50(int32_t arg1)",
		"004a8a5c  int32_t* eax_1 = data_16dd82c(arg1 + 4)",
		"004a8a83  *eax_1 = 0x87654321",
		"004a8a89  sub_4c95e0(&eax_1[1], 0, arg1)",
		"004a8aa0    int32_t* sub_4a8aa0(void* arg1)",
		"004a8aa6  int32_t* result = arg1 - 4",
		"004a8aaf  if (*result != 0x12345678)",
		"004a8ab2  return data_16dd824(result)",
		"004a8ac0    int32_t sub_4a8ac0()",
		"004a8ac0  jump(data_16dd828)",
	):
		assert expected in hlil

	for expected in (
		"FUN_004a83c0,004a83c0,240,0,unknown",
		"FUN_004a89a0,004a89a0,36,0,unknown",
		"FUN_004a89d0,004a89d0,71,0,unknown",
		"FUN_004a8a20,004a8a20,36,0,unknown",
		"FUN_004a8a50,004a8a50,71,0,unknown",
		"FUN_004a8aa0,004a8aa0,29,0,unknown",
		"FUN_004a8ac0,004a8ac0,6,0,unknown",
	):
		assert expected in functions
