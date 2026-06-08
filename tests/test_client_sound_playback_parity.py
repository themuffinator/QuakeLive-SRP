"""Guard retail-backed engine sound playback entrypoint behavior."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil.txt"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_LOCAL = REPO_ROOT / "src" / "code" / "client" / "snd_local.h"
WIN_SND = REPO_ROOT / "src" / "code" / "win32" / "win_snd.c"


CORE_SOUND_ALIASES = {
	"sub_4D9C50": ("S_ChannelSetup", "FUN_004d9c50", "74"),
	"sub_4D9CA0": ("S_Shutdown", "FUN_004d9ca0", "83"),
	"sub_4D9EF0": ("S_SpatializeOrigin", "FUN_004d9ef0", "352"),
	"sub_4DA050": ("S_StartSoundVolume", "FUN_004da050", "760"),
	"sub_4DA350": ("S_StartSound", "FUN_004da350", "35"),
	"sub_4DA380": ("S_StartLocalSoundVolume", "FUN_004da380", "83"),
	"sub_4DA3E0": ("S_ClearSoundBuffer", "FUN_004da3e0", "163"),
	"sub_4DA4C0": ("S_AddLoopingSound", "FUN_004da4c0", "558"),
	"sub_4DA6F0": ("S_AddLoopSounds", "FUN_004da6f0", "328"),
	"sub_4DA840": ("S_RawSamples", "FUN_004da840", "688"),
	"sub_4DAC80": ("S_UpdateEntityPosition", "FUN_004dac80", "72"),
	"sub_4DACD0": ("S_Respatialize", "FUN_004dacd0", "351"),
	"sub_4DAE30": ("S_ScanChannelStarts", "FUN_004dae30", "413"),
	"sub_4DB490": ("S_GetSoundtime", "FUN_004db490", "209"),
	"sub_4DB3F0": ("S_StartLocalSound", "FUN_004db3f0", "82"),
	"sub_4DB450": ("S_StopAllSounds", "FUN_004db450", "49"),
	"sub_4DB570": ("S_Update_", "FUN_004db570", "262"),
	"sub_4DB680": ("S_Update", "FUN_004db680", "129"),
	"sub_4DB870": ("S_Init", "FUN_004db870", "593"),
	"sub_4DBAD0": ("S_DisableSounds", "FUN_004dbad0", "59"),
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_block(source: str, marker: str) -> str:
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


def _function_rows() -> dict[str, dict[str, str]]:
	return {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}


def test_sound_playback_aliases_cover_retail_core_entrypoints() -> None:
	aliases = json.loads(_read(ALIASES))["quakelive_steam_srp"]
	rows = _function_rows()

	for alias, (name, ghidra_name, size) in CORE_SOUND_ALIASES.items():
		assert aliases[alias] == name
		assert rows[ghidra_name]["size"] == size

	assert aliases["sub_4DA490"] == "S_ClearLoopingSoundsFrame"
	assert aliases["j_sub_4DA490"] == "QLCGImport_S_ClearLoopingSoundsFrame"
	assert aliases["j_sub_4DA3E0"] == "QLCGImport_S_ClearLoopingSoundsKillAll"


def test_sound_init_cvar_surface_drops_legacy_rate_and_separation_controls() -> None:
	hlil = _read(QL_STEAM_HLIL)
	snd_dma = _read(SND_DMA)
	snd_local = _read(SND_LOCAL)
	win_snd = _read(WIN_SND)
	init_block = _function_block(snd_dma, "void S_Init( void )")

	for expected in (
		'"s_announcerVolume"',
		'"s_doppler"',
		'"s_initsound"',
		'"s_mixahead"',
		'"s_mixPreStep"',
		'"s_musicvolume"',
		'"s_pvs"',
		'"s_voiceVolume"',
		'"s_voiceStep"',
		'"s_show"',
		'"s_testsound"',
		'"s_volume"',
		"004db870    int32_t sub_4db870()",
	):
		assert expected in hlil

	assert '"s_khz"' not in hlil
	assert '"s_separation"' not in hlil
	assert 's_khz = Cvar_Get ("s_khz", "22", CVAR_ARCHIVE);' not in init_block
	assert 's_separation = Cvar_Get ("s_separation", "0.5", CVAR_ARCHIVE);' not in init_block
	assert "cvar_t\t\t*s_khz;" not in snd_dma
	assert "cvar_t\t\t*s_separation;" not in snd_dma
	assert "extern cvar_t\t*s_khz;" not in snd_local
	assert "extern cvar_t\t*s_separation;" not in snd_local
	assert "s_khz->integer" not in win_snd
	assert "\tdma.speed = 22050;" in win_snd


def test_sound_lifecycle_setup_shutdown_and_disable_match_retail_state_edges() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	channel_setup_block = _function_block(source, "void S_ChannelSetup()")
	shutdown_block = _function_block(source, "void S_Shutdown( void )")
	init_block = _function_block(source, "void S_Init( void )")
	disable_block = _function_block(source, "void S_DisableSounds( void )")

	for expected in (
		"004d9c50    void* sub_4d9c50()",
		"004d9c5c  sub_4c95e0(&data_14298c0, 0, 0x1500)",
		"004d9c7c  for (i = &data_142ad88; i u> &data_14298c0; i -= 0x38)",
		"004d9c89  data_12c5b78 = &data_142ad88",
		'004d9c99  return sub_4c9ab0("Channel memory manager started\\n")',
		"004d9ca0    void sub_4d9ca0()",
		"004d9ca9      sub_4dbba0()",
		"004d9cae      sub_4efa30()",
		"004d9cb8      data_126094c = 0",
		'004d9cc2      sub_4c8270("play")',
		'004d9ccc      sub_4c8270("music")',
		'004d9cd6      sub_4c8270("s_list")',
		'004d9ce0      sub_4c8270("s_info")',
		'004d9cea      sub_4c8270("s_stop")',
		"004dba70  data_126094c = 1",
		"004dba75  data_1260934 = 1",
		"004dba7a  data_1260928 = 0",
		"004dba80  sub_4c95e0(&data_12c5950, 0, 0x200)",
		"004dbab5      sub_4da3e0()",
		"004dbad0    void sub_4dbad0()",
		"004dbafb      sub_4da3e0()",
		"004dbb00  data_1260934 = 1",
	):
		assert expected in hlil

	for expected in (
		"Com_Memset( s_channels, 0, sizeof( s_channels ) );",
		"while (--q > p) {",
		"*(channel_t **)q = q-1;",
		"*(channel_t **)q = NULL;",
		"freelist = p + MAX_CHANNELS - 1;",
		'Com_DPrintf("Channel memory manager started\\n");',
	):
		assert expected in channel_setup_block

	assert "s_channelInitPrinted" not in channel_setup_block
	assert 'if ( !s_channelInitPrinted ) {' not in channel_setup_block

	for expected in (
		"SND_shutdown();",
		"SNDDMA_Shutdown();",
		"s_soundStarted = 0;",
		'Cmd_RemoveCommand("play");',
		'Cmd_RemoveCommand("music");',
		'Cmd_RemoveCommand("s_list");',
		'Cmd_RemoveCommand("s_info");',
		'Cmd_RemoveCommand("s_stop");',
	):
		assert expected in shutdown_block

	for expected in (
		"s_soundStarted = 1;",
		"s_soundMuted = 1;",
		"s_numSfx = 0;",
		"Com_Memset(sfxHash, 0, sizeof(sfx_t *)*LOOP_HASH);",
		"s_soundtime = 0;",
		"s_paintedtime = 0;",
		"S_StopAllSounds ();",
		"S_SoundInfo_f();",
	):
		assert expected in init_block

	assert "//\t\ts_numSfx = 0;" not in init_block
	assert "S_StopAllSounds();" in disable_block
	assert "s_soundMuted = qtrue;" in disable_block


def test_sound_spatializer_uses_retail_max_distance_falloff() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	spatialize_block = _function_block(source, "void S_SpatializeOrigin")

	for expected in (
		"004d9ef0    int32_t sub_4d9ef0(int32_t* arg1 @ esi, int32_t* arg2 @ edi, float* arg3, int32_t arg4)",
		"004d9f35  long double x87_r7_7 = fconvert.t(1250f)",
		"004d9f3b  long double x87_r6 = fconvert.t(fconvert.s(sub_4d8190(&var_14)))",
		"004d9f47  if ((eax_3:1.b & 1) == 0)",
		"004d9f49      *arg1 = 0",
		"004d9f51      *arg2 = 0",
		"004d9f72  float var_28_1 = fconvert.s(x87_r7_7 * fconvert.t(0.00079999997979030013))",
		"004d9f75  if (data_142c320 == 1)",
		"004d9fa5  sub_4d7cb0(&var_14, &data_12c5b50, &var_20)",
		"004da013      sub_526000(fconvert.t(fconvert.s(fconvert.t(var_2c) * x87_r7_17)) * x87_r5_2)",
	):
		assert expected in hlil

	for expected in (
		"#define\t\tSOUND_MAXDISTANCE\t1250.0f",
		"#define\t\tSOUND_ATTENUATE\t\t0.0008f",
	):
		assert expected in source

	for expected in (
		"dist = VectorNormalize(source_vec);",
		"if ( dist >= SOUND_MAXDISTANCE ) {",
		"*left_vol = 0;",
		"*right_vol = 0;",
		"return;",
		"dist *= dist_mult;",
		"if (dma.channels == 1)",
		"rscale = 0.5 * (1.0 + dot);",
		"lscale = 0.5 * (1.0 - dot);",
		"scale = (1.0 - dist) * rscale;",
		"scale = (1.0 - dist) * lscale;",
	):
		assert expected in spatialize_block

	assert "SOUND_FULLVOLUME" not in source
	assert "dist -= SOUND_FULLVOLUME;" not in spatialize_block
	assert "#define\t\tSOUND_FULLVOLUME\t80" not in source


def test_start_sound_volume_reconstructs_retail_duplicate_and_steal_policy() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	start_block = _function_block(source, "static void S_StartSoundInternal")

	for expected in (
		"004da050    void sub_4da050(float* arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5)",
		'char const data_54401c[0x28] = "^3S_StartSound: handle %i out of range\\n", 0',
		'char const data_544050[0x1b] = "double sound start: %d %s\\n", 0',
		'char const data_544078[0x1f] = "S_StartSound: bad entitynum %i", 0',
		"004da0fa      if (arg2 != 0x3fe)",
		'004da142                  sub_4c9ab0("double sound start: %d %s\\n")',
		"004da172              if (*(edx_2 - 4) == arg2 && *edx_2 != 7",
		"004da243              if (*(edx_3 - 0x30) == 0x3fe",
		"004da309          int32_t eax_10 =",
		"004da350    int32_t sub_4da350(float* arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"004da372  return sub_4da050(arg1, arg2, arg3, arg4, fconvert.s(float.t(1)))",
		"004da380    void sub_4da380(int32_t arg1, int32_t arg2, float arg3)",
		"004da3b9          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(fconvert.t(arg3)))",
		"004db3f0    void sub_4db3f0(int32_t arg1, int32_t arg2)",
		"004db428          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(float.t(1)))",
	):
		assert expected in hlil

	for expected in (
		'Com_Error( ERR_DROP, "S_StartSound: bad entitynum %i", entityNum );',
		'Com_Printf( S_COLOR_YELLOW "S_StartSound: handle %i out of range\\n", sfxHandle );',
		"if ( entityNum != ENTITYNUM_WORLD ) {",
		"if ( ch->entnum == entityNum && ch->thesfx == sfx ) {",
		"if ( time - ch->allocTime < 50 ) {",
		'Com_DPrintf( "double sound start: %d %s\\n", entityNum, sfx->soundName );',
		"if (ch->entnum == entityNum && ch->allocTime<oldest && ch->entchannel != CHAN_ANNOUNCER) {",
		"if (ch->entnum == ENTITYNUM_WORLD && ch->allocTime<oldest) {",
		"ch->startSample = START_SAMPLE_IMMEDIATE;",
		"ch->doppler = qfalse;",
	):
		assert expected in start_block

	for legacy in (
		"int\t\t\tinplay;",
		"int\t\t\tallowed;",
		"allowed = 4;",
		"if (inplay>allowed) {",
		'Com_Printf("dropping sound\\n");',
		'Com_Printf( S_COLOR_YELLOW, "S_StartSound: handle %i out of range\\n", sfxHandle );',
	):
		assert legacy not in start_block


def test_local_and_loop_warning_paths_preserve_retail_yellow_diagnostics() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	local_block = _function_block(source, "void S_StartLocalSound( sfxHandle_t sfxHandle, int channelNum )")
	local_volume_block = _function_block(source, "void S_StartLocalSoundVolume")
	loop_block = _function_block(source, "void S_AddLoopingSound")
	real_loop_block = _function_block(source, "void S_AddRealLoopingSound")

	for expected in (
		'char const data_544098[0x2d] = "^3S_StartLocalSound: handle %i out of range\\n", 0',
		'char const data_5440c8[0x2d] = "^3S_AddLoopingSound: handle %i out of range\\n", 0',
		"004da6e1      sub_4c9860(arg4, \"^3S_AddLoopingSound: handle %i o…\")",
		"004db438      sub_4c9860(esi, \"^3S_StartLocalSound: handle %i o…\")",
	):
		assert expected in hlil

	for block in (local_block, local_volume_block):
		assert 'Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\\n", sfxHandle );' in block
		assert 'Com_Printf( S_COLOR_YELLOW, "S_StartLocalSound: handle %i out of range\\n", sfxHandle );' not in block

	assert 'Com_Printf( S_COLOR_YELLOW "S_AddLoopingSound: handle %i out of range\\n", sfxHandle );' in loop_block
	assert 'Com_Printf( S_COLOR_YELLOW, "S_AddLoopingSound: handle %i out of range\\n", sfxHandle );' not in loop_block
	assert 'Com_Printf( S_COLOR_YELLOW "S_AddRealLoopingSound: handle %i out of range\\n", sfxHandle );' in real_loop_block
	assert 'Com_Printf( S_COLOR_YELLOW, "S_AddRealLoopingSound: handle %i out of range\\n", sfxHandle );' not in real_loop_block


def test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	clear_buffer_block = _function_block(source, "void S_ClearSoundBuffer( void )")
	frame_clear_block = _function_block(source, "void S_ClearLoopingSoundsFrame( void )")
	clear_loops_block = _function_block(source, "void S_ClearLoopingSounds")
	add_loop_block = _function_block(source, "void S_AddLoopingSound")
	add_loop_sounds_block = _function_block(source, "void S_AddLoopSounds")
	raw_block = _function_block(source, "void S_RawSamples")
	position_block = _function_block(source, "void S_UpdateEntityPosition")
	respatialize_block = _function_block(source, "void S_Respatialize")
	update_block = _function_block(source, "void S_Update( void )")
	soundtime_block = _function_block(source, "int S_GetSoundtime(void)")
	update_paint_block = _function_block(source, "void S_Update_(void)")

	for expected in (
		"004da3e0    void sub_4da3e0()",
		"004da490    void* sub_4da490()",
		"004da4a0      *i = 0",
		"004da4b0  data_142c2f0 = 0",
		"004da4c0    void sub_4da4c0(int32_t arg1, float* arg2, float* arg3, int32_t arg4)",
		"004da6f0    void* sub_4da6f0()",
		"sub_4d9ef0(&var_8, &var_c, i - 0x2c, 0x7f)",
		"sub_4d9ef0(&var_20, &var_1c, j - 0x28, 0x7f)",
		"004da840    void sub_4da840(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t arg5, float arg6)",
		"004da876      int32_t eax_2 = sub_526000(fconvert.t(*(data_13e185c + 0x2c)) * fconvert.t(arg6)",
		"* fconvert.t(256.0))",
		'char const data_544108[0x22] = "S_RawSamples: overflowed %i > %i\\n", 0',
		'char const data_54412c[0x2a] = "S_RawSamples: resetting minimum: %i < %i\\n", 0',
		"004db9d9  data_13e185c =",
		'004db9d9      sub_4cdd30(x87_r2, x87_r3, x87_r4, "s_volume", "0.8", "0.0", "2.0", 0x81801)',
		"004dac80    void* sub_4dac80(int32_t arg1, float* arg2)",
		'char const data_544270[0x29] = "S_UpdateEntityPosition: bad entitynum %i", 0',
		"004dacd0    float* sub_4dacd0(int32_t arg1, float* arg2, float* arg3, int32_t arg4)",
		"004dae30    int32_t sub_4dae30()",
		"004db490    int32_t sub_4db490()",
		"004db557          return eax_8",
		"004db560  return eax_6",
		"004db570    void sub_4db570()",
		"004db5a6      if (data_142c334 != 0)",
		"004db5b2          if (data_142c2ec s> 0x40000000)",
		"004db5c8          data_142c2e0 = data_142c2ec",
		"004db5d2          esi_1 = sub_4efb80()",
		"004db5d6      sub_4db490()",
		"004db655          sub_4efbf0()",
		"004db680    void sub_4db680()",
		"004db690  if (data_126094c == 0 || data_1260934 != 0)",
		"004db69b  if (*(data_142c2fc + 0x30) == 2)",
		'004db6cf                  sub_4c9860(esi_1, "%3i %3i %s\\n")',
		'char const data_5443ac[0xc] = "%3i %3i %s\\n", 0',
		'char const data_544390[0x1a] = "----(%i)---- painted: %i\\n", 0',
		'004db6f6  sub_4db1c0()',
		"004db6fb  return sub_4db570() __tailcall",
	):
		assert expected in hlil

	for expected in (
		"Com_Memset(loopSounds, 0, MAX_GENTITIES*sizeof(loopSound_t));",
		"Com_Memset(loop_channels, 0, MAX_CHANNELS*sizeof(channel_t));",
		"S_ChannelSetup();",
		"s_rawend = 0;",
		"Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );",
		"SNDDMA_BeginPainting ();",
		"Snd_Memset(dma.buffer, clear, dma.samples * dma.samplebits/8);",
		"SNDDMA_Submit ();",
	):
		assert expected in clear_buffer_block

	for expected in (
		"loopSounds[i].active = qfalse;",
		"numLoopChannels = 0;",
	):
		assert expected in frame_clear_block
	assert "loopSounds[i].kill = qfalse;" not in frame_clear_block
	assert "S_StopLoopingSound(i);" not in frame_clear_block

	for expected in (
		"if (killall || loopSounds[i].kill == qtrue || (loopSounds[i].sfx && loopSounds[i].sfx->soundLength == 0)) {",
		"S_StopLoopingSound(i);",
		"numLoopChannels = 0;",
	):
		assert expected in clear_loops_block

	for expected in (
		"VectorCopy( origin, loopSounds[entityNum].origin );",
		"VectorCopy( velocity, loopSounds[entityNum].velocity );",
		"loopSounds[entityNum].active = qtrue;",
		"loopSounds[entityNum].kill = qtrue;",
		"loopSounds[entityNum].oldDopplerScale = 1.0;",
		"if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {",
		"loopSounds[entityNum].framenum = cls.framecount;",
	):
		assert expected in add_loop_block

	for expected in (
		"S_SpatializeOrigin( loop->origin, 127, &left_total, &right_total);",
		"S_SpatializeOrigin( loop2->origin, 127, &left, &right);",
	):
		assert expected in add_loop_sounds_block
	assert "S_SpatializeOrigin( loop->origin, 90" not in add_loop_sounds_block
	assert "S_SpatializeOrigin( loop2->origin, 90" not in add_loop_sounds_block

	for expected in (
		'Com_DPrintf( "S_RawSamples: resetting minimum: %i < %i\\n", s_rawend, s_soundtime );',
		"scale = (float)rate / dma.speed;",
		"intVolume = 256 * volume * s_volume->value;",
		"intVolume *= 256;",
		'Com_DPrintf( "S_RawSamples: overflowed %i > %i\\n", s_rawend, s_soundtime );',
	):
		assert expected in raw_block
	assert "intVolume = 256 * volume;" not in raw_block

	assert 'Com_Error( ERR_DROP, "S_UpdateEntityPosition: bad entitynum %i", entityNum );' in position_block
	assert "VectorCopy( origin, loopSounds[entityNum].origin );" in position_block

	for expected in (
		"listener_number = entityNum;",
		"VectorCopy(head, listener_origin);",
		"if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {",
		"S_SpatializeOrigin (origin, ch->master_vol, &ch->leftvol, &ch->rightvol);",
		"S_AddLoopSounds ();",
	):
		assert expected in respatialize_block

	for expected in (
		"if ( s_show->integer == 2 ) {",
		'Com_Printf ("%3i %3i %s\\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);',
		'Com_Printf ("----(%i)---- painted: %i\\n", total, s_paintedtime);',
		"S_UpdateBackgroundTrack();",
		"S_Update_();",
	):
		assert expected in update_block
	assert 'Com_DPrintf ("not started or muted\\n");' not in update_block
	assert 'Com_Printf ("%f %f %s\\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);' not in update_block

	for expected in (
		"S_GetSoundtime();",
		"S_ScanChannelStarts();",
		"ma = s_mixahead->value * dma.speed;",
		"endtime = (endtime + dma.submission_chunk-1)",
		"SNDDMA_BeginPainting ();",
		"S_PaintChannels (endtime);",
		"SNDDMA_Submit ();",
	):
		assert expected in update_paint_block

	for expected in (
		"int S_GetSoundtime(void)",
		"s_soundtime = buffers*fullsamples + samplepos/dma.channels;",
		"if ( dma.submission_chunk < 256 ) {",
		"s_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;",
		"return s_paintedtime;",
		"s_paintedtime = s_soundtime + dma.submission_chunk;",
		"return s_soundtime;",
	):
		assert expected in soundtime_block
