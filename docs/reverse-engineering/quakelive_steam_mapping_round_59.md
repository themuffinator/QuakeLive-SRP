# Quake Live Steam Host Mapping Round 59

## Scope

This round continues directly from the retained helper work in round 58 and
pushes through the next adjacent Quake III-owned host tranche:

- the post-`Com_sprintf` `q_shared.c` wrapper and info-string block
- the early retained `snd_dma.c` sound-control and streaming path
- the adjacent retained `snd_mem.c` allocator helpers used by the sound cache

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/game/q_shared.c`
- `src/code/client/snd_dma.c`
- `src/code/client/snd_mem.c`
- `assets/quake3/src/code/game/q_shared.c`
- `assets/quake3/src/code/client/snd_dma.c`
- `assets/quake3/src/code/client/snd_mem.c`

## Retained `q_shared.c` Wrapper And Info Closures

The next post-round-58 helper block closes the retained Quake III wrapper and
info-string sequence:

- `sub_4D9220 -> va`
- `sub_4D9260 -> Info_ValueForKey`
- `sub_4D9380 -> Info_NextPair`
- `sub_4D93E0 -> Info_RemoveKey`
- `sub_4D9500 -> Info_RemoveKey_Big`
- `sub_4D9620 -> Info_SetValueForKey`
- `sub_4D97E0 -> Info_SetValueForKey_Big`
- `sub_4D9A60 -> COM_DefaultExtension`
- `sub_4D9B00 -> COM_Parse`

Observed facts:

1. `sub_4D9220` preserves the classic two-buffer `va` ring and calls
   `vsprintf` exactly like the retained GPL helper.
2. `sub_4D9260`, `sub_4D9380`, `sub_4D93E0`, and `sub_4D9500` preserve the
   exact Quake III info-string walk, including the alternating static value
   buffers in `Info_ValueForKey` and the retained oversize diagnostics.
3. `sub_4D9620` and `sub_4D97E0` preserve the stock slash / semicolon / quote
   rejection path and rebuild the final `\\key\\value` pair using
   `Com_sprintf`, matching `Info_SetValueForKey*`.
4. `sub_4D9A60` is the retained `COM_DefaultExtension` body, walking backward
   to the last slash, returning early on an existing dot, and otherwise
   appending the provided extension to a copied base path.
5. `sub_4D9B00` is the retained `COM_Parse` wrapper, forwarding directly to
   `COM_ParseExt(data_p, qtrue)`.

## Retained `snd_dma.c` Sound-Core Closures

The next host band transitions cleanly into retained Quake III sound-system
ownership:

- `sub_4D8990 -> generateHashValue`
- `sub_4D9B60 -> S_SoundInfo_f`
- `sub_4D9C50 -> S_ChannelSetup`
- `sub_4D9CA0 -> S_Shutdown`
- `sub_4D9D00 -> S_FindName`
- `sub_4D9E10 -> S_memoryLoad`
- `sub_4D9EF0 -> S_SpatializeOrigin`
- `sub_4DA6F0 -> S_AddLoopSounds`
- `sub_4DA840 -> S_RawSamples`
- `sub_4DAE30 -> S_ScanChannelStarts`
- `sub_4DAFD0 -> S_SoundList_f`
- `sub_4DB320 -> S_FreeOldestSound`
- `sub_4DB3A0 -> S_BeginRegistration`
- `sub_4DB490 -> S_GetSoundtime`
- `sub_4DB570 -> S_Update_`
- `sub_4DB680 -> S_Update`
- `sub_4DB710 -> S_Play_f`
- `sub_4DB810 -> S_Music_f`
- `sub_4DB870 -> S_Init`
- `sub_4DBAD0 -> S_DisableSounds`

Observed facts:

1. `sub_4D8990` closes one of the previous ambiguous leftovers as the retained
   shared `generateHashValue` helper: `tolower`, stop-at-dot handling,
   backslash-to-slash normalization, the caller-supplied hash-size argument,
   and the final `(hash & (size - 1))` mask are all present. Round 314
   corrected the earlier sound-only label after revalidating the image and
   shader callers.
2. `sub_4D9D00` is the retained `S_FindName` path, including the exact
   `S_FindName: NULL`, `S_FindName: empty name`, and
   `S_FindName: out of sfx_t` fatal diagnostics plus the hash-chain walk.
3. `sub_4D9EF0`, `sub_4DA6F0`, `sub_4DA840`, and `sub_4DAE30` preserve the
   stock spatialization, loop-sound merge, raw music streaming, and
   channel-start scan logic from Quake III `snd_dma.c`.
4. `sub_4DB490`, `sub_4DB570`, and `sub_4DB680` preserve the Quake III sound
   update spine: DMA position tracking, wrap detection, mix-ahead computation,
   submission-chunk alignment, optional debug printout, and the final call into
   the paint path.
5. `sub_4DB710`, `sub_4DB810`, and `sub_4DB870` preserve the console-command
   and initialization entry points, including the `.wav` append path in
   `S_Play_f`, the `music <musicfile> [loopfile]` usage diagnostic in
   `S_Music_f`, and the retained startup banner / cvar registration in
   `S_Init`.

`sub_4DAFD0 -> S_SoundList_f` and `sub_4DB810 -> S_Music_f` are HLIL-backed
closures rather than standalone `functions.csv` starts, but both roles are
unambiguous from their command-handler bodies and exact retained diagnostics.

## Retained `snd_mem.c` Allocator Closures

The sound-memory helper block adjacent to the DMA path also closes cleanly:

- `sub_4DBB10 -> SND_free`
- `sub_4DBB30 -> SND_setup`
- `sub_4DBBE0 -> S_DisplayFreeMemory`

Observed facts:

1. `sub_4DBB10` links the freed buffer back onto the freelist and updates the
   in-use counter exactly like `SND_free`.
2. `sub_4DBB30` allocates the sound buffer slab from `com_soundMegs`, wires
   the freelist chain, and prints the exact retained
   `Sound memory manager started\n` banner, matching `SND_setup`.
3. `sub_4DBBE0` prints the retained
   `%d bytes free sound buffer memory, %d total used\n` summary, matching
   `S_DisplayFreeMemory`.

## Deferred Non-Source-Aligned Helpers

The following nearby starts remain intentionally unresolved after this pass:

- `0x004D99B0`
- `0x004D9B20`
- `0x004DAB00`
- `0x004DB1C0`
- `0x004DBBA0`

Observed facts:

1. `0x004D99B0` walks a fixed string table and returns remapped tokens, but it
   does not line up cleanly with a retained stock Quake III helper.
2. `0x004D9B20` is a tiny `.ogg` / `.wav` classifier rather than a named
   standalone helper from the committed GPL sources.
3. `0x004DAB00` is a Quake Live voice-channel helper, not a retained Quake III
   `snd_dma.c` body.
4. `0x004DB1C0` appears to be a later background-track smoothing/update helper
   tied to the Quake Live audio path rather than a stock Quake III function.
5. `0x004DBBA0` sits next to the retained `snd_mem.c` helpers but does not
   survive as a named standalone function in the committed GPL source.

## Completion Summary

This round promotes `32` retained aliases:

- `q_shared.c`: `va`, `Info_ValueForKey`, `Info_NextPair`, `Info_RemoveKey`,
  `Info_RemoveKey_Big`, `Info_SetValueForKey`, `Info_SetValueForKey_Big`,
  `COM_DefaultExtension`, `COM_Parse`
- shared hash helper: `generateHashValue`
- `snd_dma.c`: `S_SoundInfo_f`, `S_ChannelSetup`,
  `S_Shutdown`, `S_FindName`, `S_memoryLoad`, `S_SpatializeOrigin`,
  `S_AddLoopSounds`, `S_RawSamples`, `S_ScanChannelStarts`, `S_SoundList_f`,
  `S_FreeOldestSound`, `S_BeginRegistration`, `S_GetSoundtime`, `S_Update_`,
  `S_Update`, `S_Play_f`, `S_Music_f`, `S_Init`, `S_DisableSounds`
- `snd_mem.c`: `SND_free`, `SND_setup`, `S_DisplayFreeMemory`

Focused band results after this pass:

- earlier helper cleanup `0x4D7970-0x4D9170`: `7 -> 6`
- retained info block `0x4D9220-0x4D9B10`: `10 -> 1`
- retained sound-core block `0x4D9B60-0x4DBB00`: `19 -> 2`
- broad retained tranche `0x4D9220-0x4DBBE8`: `34 -> 5`
- extra HLIL-only promotions not present as standalone `functions.csv` starts:
  `0x004DAFD0 -> S_SoundList_f`, `0x004DB810 -> S_Music_f`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `761 -> 793`
- address-backed aliases: `760 -> 792`
- Ghidra function coverage: `13.886% -> 14.471%` of `5473`

The immediate remaining unresolved standalone starts in the current focus area
are:

- `0x004D99B0`
- `0x004D9B20`
- `0x004DAB00`
- `0x004DB1C0`
- `0x004DBBA0`

This round materially closes the retained post-`q_shared` host tranche. The
remaining starts in the area are concentrated in Quake Live-specific audio
helpers or in nearby internal helpers that do not survive as clean standalone
names in the committed Quake III source.
