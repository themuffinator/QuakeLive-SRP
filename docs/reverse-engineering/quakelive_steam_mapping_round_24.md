# Quake Live Steam Host Mapping Round 24

## Scope

This round returns to the sound/music seam from Rounds 20, 22, and 23, but shifts from the raw native `cgamex86.dll` import wrappers to the owning engine-side helpers inside `quakelive_steam.exe`.

The goal was to promote the stable sound helpers that sit behind the already-mapped native cgame callbacks:

- `sub_4AFEC0 -> QLCGImport_S_RegisterSound`
- `sub_4AFED0 -> QLCGImport_S_StartBackgroundTrack`
- raw `data_565A18 / +0xC0` as the native cgame `stopBackgroundTrack` slot

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/snd_dma.c`

## Stable Engine Helper Rows

Observed local facts:

1. The committed Ghidra export now exposes stable rows for all three engine-side helper bodies relevant to this seam:
   - `FUN_004D9E50,004d9e50,151,0,unknown`
   - `FUN_004DB030,004db030,35,0,unknown`
   - `FUN_004DB060,004db060,351,0,unknown`
2. Round 20 already bounded the native cgame wrappers as thin forwards into this same sound core:
   - `sub_4AFEC0` tailcalls `sub_4D9E50`
   - `sub_4AFED0` tailcalls `sub_4DB060`
   - the raw `+0xC0` stop-music thunk remained documented-only because the committed export did not expose a stable `sub_4B02F0` row
3. That means the remaining naming value is now on the engine helpers themselves, not on the raw wrapper band.

## `sub_4D9E50`: `S_RegisterSound`

`sub_4D9E50` is now exact.

Observed local facts:

1. The function bails out immediately when `data_126094C == 0`, matching the source-side `if ( !s_soundStarted ) return 0;`.
2. It checks the incoming qpath length and emits the exact source string `"Sound name exceeds MAX_QPATH\n"`.
3. It calls `sub_4D9D00(arg1)` to find or create the `sfx` record, which matches the `S_FindName( name )` role.
4. On default-sound fallback it emits the exact warning string `^3WARNING: could not find %s - using default\n`.
5. On success it returns `(eax_4 - &data_1260950) s/ 0x58`, which is the same handle computation as `return sfx - s_knownSfx;` in `snd_dma.c`.
6. Round 20 already showed that the native cgame display-context `registerSound` wrapper at `sub_4AFEC0` is a pure tailcall into this helper.

That gives three independent signals: exact strings, matching control flow, and the already-mapped wrapper target.

## `sub_4DB030`: `S_StopBackgroundTrack`

`sub_4DB030` is now exact.

Observed local facts:

1. The committed Ghidra export now has a stable `FUN_004DB030` row even though the raw native cgame thunk at `0x4B02F0` still does not.
2. The body is the minimal streamed-music shutdown helper:
   - if `data_12C5B74 != 0`, call `sub_4DCA40()`
   - set `data_12C5B74 = 0`
   - set `data_13E1850 = 0`
3. That matches the source-side `S_StopBackgroundTrack` behavior in `snd_dma.c`: close the streamed file / decoder state, clear the active background-track handle, and reset the raw-stream progress state.
4. Native cgame still reaches this behavior through the raw `stopMusic` path at `(*(data_1074CCCC + 0xC0))()`, so the wrapper ownership recorded in Rounds 20 and 23 remains unchanged.
5. The raw slot stays unaliased in JSON because the committed export still does not surface a stable `sub_4B02F0` function row; this round only promotes the stable engine helper it jumps into.

## `sub_4DB060`: `S_StartBackgroundTrack`

`sub_4DB060` is now exact.

Observed local facts:

1. The helper takes two string arguments and immediately falls back to `arg1` when `arg2` is null or empty, matching `if ( !loop || !loop[0] ) loop = intro;`.
2. It emits the exact debug string `S_StartBackgroundTrack( %s, %s )\n`.
3. It normalizes the music path and inspects `.ogg` versus `.wav`, matching the retail `S_ResolveMusicFile` / extension-selection flow.
4. Before opening the new track, it tears down any active background stream:
   - if `data_12C5B74 != 0`, call `sub_4DCA40()`
   - clear `data_12C5B74`
5. If the open fails, it prints the same warning family seen in the source path: `^3WARNING: couldn't open music file ...`.
6. Internal callsites reinforce the ownership:
   - `sub_4AFED0` is a pure native cgame wrapper tailcall to `sub_4DB060`
   - `sub_4DB830` reaches it from the local `music` command path
   - `sub_4DB2E3` re-enters it from the background-track loop/restart path

That is enough to promote the owning engine helper, not just the cgame wrapper.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4D9E50` (`0x004D9E50`) | `S_RegisterSound` | Observed | Retail sound-registration helper behind the native cgame `registerSound` wrapper. |
| `sub_4DB030` (`0x004DB030`) | `S_StopBackgroundTrack` | Observed | Retail streamed-music shutdown helper behind the raw native cgame `stopBackgroundTrack` slot. |
| `sub_4DB060` (`0x004DB060`) | `S_StartBackgroundTrack` | Observed | Retail streamed-music startup helper behind the native cgame `startBackgroundTrack` wrapper. |

## Open Questions

1. The raw native cgame thunk at `0x4B02F0` is semantically closed as the `stopBackgroundTrack` wrapper, but it still does not have a stable committed Ghidra function row, so I am leaving that wrapper itself unaliased.
2. `sub_4AFE00` remains the last weak spot in the older raw sound-side thunk band. This round did not find enough direct caller evidence to promote it safely.
