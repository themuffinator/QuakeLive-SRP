import ctypes
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = REPO_ROOT / "src" / "code"
GAME_DIR = CODE_DIR / "game"
QCOMMON_DIR = CODE_DIR / "qcommon"

C_SOURCE = r"""
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "q_shared.h"
#include "qcommon.h"

typedef struct qlr_ps_values_s {
	int		doubleJumpTime;
	int		doubleJumpEntNum;
	float	doubleJumpNormal[3];
	int		crouchTime;
	int		crouchSlideTime;
} qlr_ps_values_t;

static cvar_t qlr_localShownet;
cvar_t *cl_shownet = &qlr_localShownet;

/*
=============
Com_Printf

Stubbed logger for network serialization tests.
=============
*/
void QDECL Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
Com_Error

Aborts the test harness if the message code fails.
=============
*/
void QDECL Com_Error( int level, const char *fmt, ... ) {
	(void)level;
	(void)fmt;
	abort();
}

/*
=============
Com_Memcpy

Test-friendly memcpy shim.
=============
*/
void Com_Memcpy( void *dest, const void *src, size_t count ) {
	memcpy( dest, src, count );
}

/*
=============
Com_Memset

Test-friendly memset shim.
=============
*/
void Com_Memset( void *dest, int c, size_t count ) {
	memset( dest, c, count );
}

/*
=============
QLR_WriteAndReadPlayerState

Encodes the server playerstate delta and immediately decodes it to produce the client result.
=============
*/
static void QLR_WriteAndReadPlayerState( const playerState_t *from, const playerState_t *to, playerState_t *out ) {
	msg_t msg;
	byte buffer[2048];

	MSG_Init( &msg, buffer, sizeof( buffer ) );
	MSG_WriteDeltaPlayerstate( &msg, (playerState_t *)from, (playerState_t *)to );
	MSG_BeginReading( &msg );
	MSG_ReadDeltaPlayerstate( &msg, (playerState_t *)from, out );
}

/*
=============
QLR_ReplicateDoubleJump

Generates a double jump delta and captures the replicated fields for verification.
=============
*/
void QLR_ReplicateDoubleJump( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.doubleJumpTime = 1337331;
	server.doubleJumpEntNum = 42;
	server.doubleJumpNormal[0] = -0.25f;
	server.doubleJumpNormal[1] = 0.5f;
	server.doubleJumpNormal[2] = 0.75f;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->doubleJumpTime = client.doubleJumpTime;
	values->doubleJumpEntNum = client.doubleJumpEntNum;
	values->doubleJumpNormal[0] = client.doubleJumpNormal[0];
	values->doubleJumpNormal[1] = client.doubleJumpNormal[1];
	values->doubleJumpNormal[2] = client.doubleJumpNormal[2];
}

/*
=============
QLR_ReplicateCrouchSlide

Generates a crouch slide delta and captures the replicated timers for verification.
=============
*/
void QLR_ReplicateCrouchSlide( qlr_ps_values_t *values ) {
	playerState_t from;
	playerState_t server;
	playerState_t client;

	Com_Memset( &from, 0, sizeof( from ) );
	Com_Memset( &server, 0, sizeof( server ) );
	Com_Memset( &client, 0, sizeof( client ) );
	Com_Memset( values, 0, sizeof( *values ) );

	server.crouchTime = 777;
	server.crouchSlideTime = 1600;

	QLR_WriteAndReadPlayerState( &from, &server, &client );

	values->crouchTime = client.crouchTime;
	values->crouchSlideTime = client.crouchSlideTime;
}
"""

pytestmark = pytest.mark.skipif(os.name == "nt", reason="MSVC build configuration not supported in tests")


class PlayerStateReplication(ctypes.Structure):
	_fields_ = [
		("doubleJumpTime", ctypes.c_int),
		("doubleJumpEntNum", ctypes.c_int),
		("doubleJumpNormal", ctypes.c_float * 3),
		("crouchTime", ctypes.c_int),
		("crouchSlideTime", ctypes.c_int),
	]


def _build_test_library(tmp_path: Path) -> Path:
	src_path = tmp_path / "playerstate_replication_test.c"
	src_path.write_text(C_SOURCE, encoding="utf-8")

	if sys.platform == "darwin":
		lib_path = tmp_path / "libplayerstate_replication_test.dylib"
		compile_cmd = [
			"cc",
			"-std=c99",
			"-dynamiclib",
			"-I",
			str(CODE_DIR),
			"-I",
			str(GAME_DIR),
			"-I",
			str(QCOMMON_DIR),
			"-o",
			str(lib_path),
			str(src_path),
			str(QCOMMON_DIR / "huffman.c"),
			str(QCOMMON_DIR / "msg.c"),
			str(GAME_DIR / "q_shared.c"),
		]
	elif os.name == "nt":
		lib_path = tmp_path / "playerstate_replication_test.dll"
		compile_cmd = [
			"cl",
			"/LD",
			f"/I{CODE_DIR}",
			f"/I{GAME_DIR}",
			f"/I{QCOMMON_DIR}",
			str(src_path),
			str(QCOMMON_DIR / "huffman.c"),
			str(QCOMMON_DIR / "msg.c"),
			str(GAME_DIR / "q_shared.c"),
			f"/Fe:{lib_path}",
		]
	else:
		lib_path = tmp_path / "libplayerstate_replication_test.so"
		compile_cmd = [
			"cc",
			"-std=c99",
			"-shared",
			"-fPIC",
			"-I",
			str(CODE_DIR),
			"-I",
			str(GAME_DIR),
			"-I",
			str(QCOMMON_DIR),
			"-o",
			str(lib_path),
			str(src_path),
			str(QCOMMON_DIR / "huffman.c"),
			str(QCOMMON_DIR / "msg.c"),
			str(GAME_DIR / "q_shared.c"),
		]

	subprocess.run(compile_cmd, check=True)
	return lib_path


def _load_library(lib_path: Path) -> ctypes.CDLL:
	library = ctypes.CDLL(str(lib_path))
	library.QLR_ReplicateDoubleJump.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicateDoubleJump.restype = None
	library.QLR_ReplicateCrouchSlide.argtypes = [ctypes.POINTER(PlayerStateReplication)]
	library.QLR_ReplicateCrouchSlide.restype = None
	return library


@pytest.fixture(scope="module")
def playerstate_library(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	tmp_path = tmp_path_factory.mktemp("playerstate_replication")
	lib_path = _build_test_library(tmp_path)
	return _load_library(lib_path)


def test_double_jump_state_round_trip(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicateDoubleJump(ctypes.byref(values))

	assert values.doubleJumpTime == 1337331
	assert values.doubleJumpEntNum == 42
	normal = tuple(values.doubleJumpNormal)
	assert normal[0] == pytest.approx(-0.25, rel=1e-6)
	assert normal[1] == pytest.approx(0.5, rel=1e-6)
	assert normal[2] == pytest.approx(0.75, rel=1e-6)


def test_crouch_slide_timers_round_trip(playerstate_library: ctypes.CDLL) -> None:
	values = PlayerStateReplication()
	playerstate_library.QLR_ReplicateCrouchSlide(ctypes.byref(values))

	assert values.crouchTime == 777
	assert values.crouchSlideTime == 1600
