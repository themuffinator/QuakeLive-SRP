"""Guard the retail-backed cgame scoreboard social path against source drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_CONSOLECMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_consolecmds.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_SERVERCMDS = REPO_ROOT / "src" / "code" / "cgame" / "cg_servercmds.c"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_clientmute_command_toggles_local_client_mute_state() -> None:
	source = CG_CONSOLECMDS.read_text(encoding="utf-8")
	block = _block_from_marker(source, "static void CG_ClientMute_f")

	assert '{ "clientmute", CG_ClientMute_f },' in source
	assert 'trap_Argv( 1, arg, sizeof( arg ) );' in block
	assert 'clientNum = atoi( arg );' in block
	assert 'clientNum < 0 || clientNum >= MAX_CLIENTS' in block
	assert 'cg.clientMuted[clientNum] = (qboolean)!cg.clientMuted[clientNum];' in block


def test_scoreboard_headers_track_local_social_state_and_media() -> None:
	source = CG_LOCAL.read_text(encoding="utf-8")

	assert "qboolean\t\tclientMuted[MAX_CLIENTS];" in source
	assert "qhandle_t\tscoreMutedShader;" in source
	assert "qhandle_t\tscoreSpeakingShader;" in source


def test_scoreboard_feeders_register_and_return_retail_social_icons() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	helper_block = _block_from_marker(source, "static qhandle_t CG_FeederSocialHandle")
	text_block = _block_from_marker(source, "static const char *CG_FeederItemText")
	image_block = _block_from_marker(source, "static qhandle_t CG_FeederItemImage")

	for expected in (
		'cgs.media.scoreMutedShader = trap_R_RegisterShaderNoMip( "ui/assets/score/muted" );',
		'cgs.media.scoreSpeakingShader = trap_R_RegisterShaderNoMip( "ui/assets/score/speaking" );',
	):
		assert expected in source

	assert "if ( cg.clientMuted[clientNum] ) {" in helper_block
	assert "return cgs.media.scoreMutedShader;" in helper_block
	assert "if ( !CG_ShouldDisplayVoiceIndicator() ) {" in helper_block
	assert "if ( cg.time - cg.voiceTime > 2500 ) {" in helper_block
	assert "return cgs.media.scoreSpeakingShader;" in helper_block

	assert "socialHandle = CG_FeederSocialHandle( clientNum );" in text_block
	assert "if ( socialHandle ) {" in text_block
	assert "*handle = socialHandle;" in text_block
	assert "*handle = CG_StatusHandle(info->teamTask);" in text_block

	assert "return CG_FeederSocialHandle( clientNum );" in image_block
	assert "return 0;" in image_block


def test_speaking_sidecar_helper_tracks_retail_voice_indicator_state() -> None:
	main_source = CG_MAIN.read_text(encoding="utf-8")
	servercmds_source = CG_SERVERCMDS.read_text(encoding="utf-8")
	helper_block = _block_from_marker(main_source, "void *CG_SetClientSpeakingState")

	assert "cgs.currentVoiceClient = clientNum;" in helper_block
	assert "cg.voiceTime = cg.time;" in helper_block
	assert "cgs.currentVoiceClient = -1;" in helper_block
	assert "return ci;" in helper_block
	assert "CG_SetClientSpeakingState( clientNum, qtrue );" in servercmds_source
