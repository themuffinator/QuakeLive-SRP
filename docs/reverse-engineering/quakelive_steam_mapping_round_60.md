# Quake Live Steam Host Mapping Round 60

## Scope

This round continues the retained Quake III sound-system mapping immediately
after round 59 and closes the next clean source-aligned host tranche:

- the retained `snd_mem.c` resampling / load path
- the retained top-level `snd_mix.c` transfer and paint pipeline
- separation of those source-aligned Quake III carries from the adjacent
  Quake Live-specific background-track and decoder helpers

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/snd_mem.c`
- `src/code/client/snd_mix.c`
- `assets/quake3/src/code/client/snd_mem.c`
- `assets/quake3/src/code/client/snd_mix.c`

## Retained `snd_mem.c` Resample / Load Closures

The next sound-cache block matches the retained `snd_mem.c` ownership directly:

- `sub_4DBC00 -> ResampleSfx`
- `sub_4DBD00 -> S_LoadSound`

Observed facts:

1. `sub_4DBC00` computes the output sample count from the input rate and DMA
   speed, allocates `sndBuffer` chunks through the same freelist path, and
   converts both 8-bit and 16-bit source samples exactly like `ResampleSfx`.
2. `sub_4DBD00` preserves the retained `S_LoadSound` role and control flow:
   it rejects `*` player-specific sounds, opens the requested asset, chooses
   the load path from the detected format, populates `lastTimeUsed`, and then
   resamples into the cache through `ResampleSfx`.
3. The Quake Live host adds the expected modernized `.ogg` fallback branch in
   `sub_4DBD00`, but the function still retains the same source ownership and
   caller role as the stock Quake III `S_LoadSound` body.

## Retained `snd_mix.c` Transfer / Paint Closures

The adjacent mixing block also closes cleanly against Quake III `snd_mix.c`:

- `sub_4DBDF0 -> S_TransferStereo16`
- `sub_4DBED0 -> S_TransferPaintBuffer`
- `sub_4DC030 -> S_PaintChannelFrom16`
- `sub_4DC350 -> S_PaintChannels`

Observed facts:

1. `sub_4DBDF0` is the retained optimized stereo-16 transfer loop, including
   the circular DMA position handling, `snd_linear_count` calculation, and the
   final call into the linear blast writer.
2. `sub_4DBED0` preserves the exact `S_TransferPaintBuffer` ownership: the
   optional sine-wave testsound fill, the optimized stereo-16 fast path, and
   the general 8-bit / 16-bit clamped output path are all present.
3. `sub_4DC030` matches the static `S_PaintChannelFrom16` helper one-for-one:
   its parameters line up with `(channel_t*, sfx_t*, count, sampleOffset,
   bufferOffset)`, and the body preserves both the normal chunk-walk mixer and
   the doppler-scaled averaging path from the retained source.
4. `sub_4DC350` is the retained `S_PaintChannels` driver, including raw-stream
   copy / zero-fill setup, voice-channel accumulation, channel and
   loop-channel paint passes, and the final `S_TransferPaintBuffer(end)` call.

## Deferred Adjacent Audio Helpers

The following nearby starts remain intentionally unresolved after this pass:

- `0x004DB1C0`
- `0x004DBBA0`
- `0x004DC670`
- `0x004DC6A0`
- `0x004DC6E0`
- `0x004DC720`
- `0x004DC730`
- `0x004DC920`
- `0x004DC960`
- `0x004DC980`
- `0x004DC9A0`
- `0x004DCA40`
- `0x004DCA50`
- `0x004DCAD0`
- `0x004DCB20`
- `0x004DCC70`
- `0x004DCDB0`
- `0x004DCE10`
- `0x004DCF90`

Observed facts:

1. `0x004DB1C0` is still tied to the later Quake Live background-track update
   path rather than a clean retained Quake III standalone body.
2. `0x004DBBA0` sits beside the retained `snd_mem.c` helpers but does not map
   cleanly to a named standalone function in the committed Quake III source.
3. The `0x004DC670-0x004DCF90` cluster is dominated by stream / decoder /
   file-wrapper helpers, including Quake Live-specific `.ogg` and background
   music handling, so it should be mapped separately from the retained
   `snd_mix.c` tranche closed here.

## Completion Summary

This round promotes `6` retained aliases:

- `snd_mem.c`: `ResampleSfx`, `S_LoadSound`
- `snd_mix.c`: `S_TransferStereo16`, `S_TransferPaintBuffer`,
  `S_PaintChannelFrom16`, `S_PaintChannels`

Focused band results after this pass:

- retained `snd_mem` / `snd_mix` core `0x4DBC00-0x4DC660`: `6 -> 0`
- retained `snd_mix` top-level tranche `0x4DBDF0-0x4DC660`: `4 -> 0`
- broader sound band `0x4DB000-0x4DD000`: `25 -> 19`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `793 -> 799`
- address-backed aliases: `792 -> 798`
- Ghidra function coverage: `14.471% -> 14.581%` of `5473`

The immediate remaining unresolved standalone starts in the current broader
audio focus area are the `19` addresses listed above. This round fully closes
the retained Quake III `snd_mem.c` resample/load seam and the adjacent
top-level `snd_mix.c` pipeline, leaving the remaining gaps concentrated in
Quake Live-specific decoder and music-stream helpers rather than in the stock
source-owned sound core.
