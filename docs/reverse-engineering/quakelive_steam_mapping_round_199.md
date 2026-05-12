# quakelive_steam.exe Mapping Round 199

Date: 2026-04-28

Scope: retained Ogg/Vorbis client-audio recovery plus adjacent Win32 GL init
owners around `0x004DC730` and `0x0046A420`.

## Summary

This round resolved `8` additional `quakelive_steam.exe` aliases.
Classification mix:

- `8` engine-owned functions
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the anonymous Ogg decode/background-track seam now
reads as the real retained client audio lane instead of a cluster of opaque
sound helpers, and the old Win32 GL queue head `sub_46A420` is no longer
anonymous either. The main closures are
`sub_4DC730 -> S_VorbisDecodeMemory`,
`sub_4DC9A0 -> S_OpenBackgroundOgg`,
`sub_4DCA50 -> S_OggUpdateBackgroundTrack`, and
`sub_46A420 -> GLW_InitDriver`.

## Evidence Notes

- `sub_4DC6A0`, `sub_4DC6E0`, `sub_4DC720`, and `sub_4DC730` are exact as
  `S_VorbisBufferRead`, `S_VorbisBufferSeek`, `S_VorbisBufferTell`, and
  `S_VorbisDecodeMemory`. The retained HLIL preserves the same callback bundle
  shape as the checked-in [snd_ogg_decode.c](</E:/Repositories/QuakeLive-reverse/src/code/client/snd_ogg_decode.c:23>):
  the read/seek/tell owners feed `ov_open_callbacks`, the decode owner rejects
  non-mono streams with the exact `"%s is not a mono file"` message, allocates
  a temporary PCM buffer, logs the retail `^3OGG_Decode: %s: %i\n` failure
  path, and fills out the mono `wavinfo_t` fields on success.
- `sub_4DC9A0` and `sub_4DCA50` are exact as `S_OpenBackgroundOgg` and
  `S_OggUpdateBackgroundTrack`. The first initializes the retained background
  `OggVorbis_File`, caches format fields in the music-info state, and logs the
  exact `^3OGG_StartBackgroundTrack: %s: …` failure line on open failure; the
  second is the tight buffered `ov_read` loop used by the music mixer and
  preserves the retail `^3OGG_UpdateBackgroundTrack: %i\n` failure logging plus
  immediate decoder teardown. The current source already carries the same
  ownership split in [snd_dma.c](</E:/Repositories/QuakeLive-reverse/src/code/client/snd_dma.c:1717>)
  and [snd_ogg_stream.c](</E:/Repositories/QuakeLive-reverse/src/code/client/snd_ogg_stream.c:91>),
  even though the checked-in tree factors the decoder state through a generic
  `snd_ogg_stream_t` wrapper instead of the retail globals.
- `sub_46A420` is exact as `GLW_InitDriver`. Its HLIL matches the retained
  [win_glimp.c](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_glimp.c:583>)
  owner line-for-line: print `"Initializing OpenGL driver\n"`, acquire the
  window DC if needed, derive depth/stencil targets from desktop depth and
  cvars, build the `PIXELFORMATDESCRIPTOR`, call the retained context-creation
  path, retry once without stencil when the first PFD attempt soft-fails, and
  report the stereo-pixel-format downgrade.
- `sub_46A940` is exact as `PrintCDSError`. The HLIL keeps the same
  `DISP_CHANGE_*` switch table and the exact output strings from
  [win_glimp.c](</E:/Repositories/QuakeLive-reverse/src/code/win32/win_glimp.c:1032>):
  `"restart required\n"`, `"bad param\n"`, `"bad flags\n"`,
  `"DISP_CHANGE_FAILED\n"`, `"bad mode\n"`, `"not updated\n"`, and the default
  `"unknown error %d\n"`.
- I deliberately left `sub_4DC920` and `sub_46A9F0` deferred. `sub_4DC920`
  clearly belongs to the Ogg side of the already-mapped `S_LoadSound` path,
  but the current source does not expose it as a stable separately named
  helper; `sub_46A9F0` is the transformed fullscreen/mode wrapper adjacent to
  `GLW_SetMode`, and the exact one-to-one public source name is still less
  stable than the owners landed here.

## Aliases Added

- `sub_46A420` -> `GLW_InitDriver`
- `sub_46A940` -> `PrintCDSError`
- `sub_4DC6A0` -> `S_VorbisBufferRead`
- `sub_4DC6E0` -> `S_VorbisBufferSeek`
- `sub_4DC720` -> `S_VorbisBufferTell`
- `sub_4DC730` -> `S_VorbisDecodeMemory`
- `sub_4DC9A0` -> `S_OpenBackgroundOgg`
- `sub_4DCA50` -> `S_OggUpdateBackgroundTrack`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2133` raw alias entries, `2060` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `37.639%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004E6730` | `FUN_004e6730` | `504` |
| 2 | `0x004B3672` | `FUN_004b3672` | `495` |
| 3 | `0x004C12F0` | `FUN_004c12f0` | `488` |
| 4 | `0x004368A0` | `FUN_004368a0` | `484` |
| 5 | `0x00429DD0` | `FUN_00429dd0` | `483` |
| 6 | `0x004A4280` | `FUN_004a4280` | `483` |
| 7 | `0x004B6630` | `FUN_004b6630` | `483` |
| 8 | `0x004241C0` | `FUN_004241c0` | `482` |
| 9 | `0x0042A130` | `FUN_0042a130` | `480` |
| 10 | `0x00498890` | `FUN_00498890` | `480` |

The next pass can return to the still-heavy gameplay/engine seam at
`sub_4E6730`, keep untangling the residual `FUN_004b3672` Ghidra split inside
the mapped console search neighborhood, or continue trimming the remaining
audio/renderer leftovers now that this Ogg + GL tranche is no longer opaque.
