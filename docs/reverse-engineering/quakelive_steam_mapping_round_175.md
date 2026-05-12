# quakelive_steam.exe Mapping Round 175

Date: 2026-04-27

Scope: exact retained libvorbis infrastructure recovery across the adjacent
bitrate, mapping, and scale helper seam from `0x00520C20` through
`0x00521230`. This pass stayed mapping-only and used the committed HLIL corpus
plus the checked-in Vorbis source in `bitrate.c`, `mapping0.c`, and
`scales.h` as the exact naming anchor.

## Summary

This round resolved `6` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old anonymous seam between the retained
psychoacoustic setup work and `mapping0_forward` now reads as the exact public
support layer around it: `vorbis_bitrate_clear`, `vorbis_bitrate_managed`,
`mapping0_free_info`, `mapping0_pack`, `mapping0_unpack`, and the local
`todB` helper. That closes the real descriptor/setup lane for `mapping0`
without having to guess at the still-transformed `sub_520C70` or
`sub_520CF0` neighbors.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_520F10` | `332` | support-library | `mapping0_pack` | High | Closed from the exact retained bitstream writer: submap flag bit, coupling flag and `coupling_steps-1`, `ov_ilog(channels-1)` widths for mag/ang, reserved `0,2` bits, optional `chmuxlist`, and the `floorsubmap` / `residuesubmap` triplets. |
| 2 | `sub_521060` | `460` | support-library | `mapping0_unpack` | High | Closed from the exact retained unpack/range-check path: `_ogg_calloc(1,0xC88)`, submap and coupling decoding, the `testM/testA` validation, reserved-bit rejection, channel mux validation, and the `mapping0_free_info` error tail. |
| 3 | `sub_520EE0` | `36` | support-library | `mapping0_free_info` | High | Closed from the exact retained teardown helper that zeroes the `vorbis_info_mapping0` object and frees it when non-null. |
| 4 | `sub_520C20` | `21` | support-library | `vorbis_bitrate_clear` | High | Closed from the exact `memset(bm,0,sizeof(*bm))` body against the `bitrate_manager_state` tail inside `private_state`. |
| 5 | `sub_520C40` | `33` | support-library | `vorbis_bitrate_managed` | High | Closed from the exact `backend_state->bms.managed` probe returning `1` when bitrate management is active and `0` otherwise. |
| 6 | `sub_521230` | `54` | support-library | `todB` | High | Closed from the exact IEEE-float retained formula: clear the sign bit, multiply by `7.17711438e-7`, then subtract the retained `764.6161886` offset. |

## Evidence Notes

- The decisive source anchors are
  [vorbis_bitrate_clear](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/bitrate.c:58>),
  [vorbis_bitrate_managed](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/bitrate.c:63>),
  [mapping0_free_info](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mapping0.c:39>),
  [mapping0_pack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mapping0.c:47>),
  [mapping0_unpack](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/mapping0.c:91>),
  and [todB](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/scales.h:43>).
- The committed HLIL mirrors those bodies directly:
  `sub_520C20` is the bare `memset(...,0,0x30)` clear over the bitrate
  manager state, `sub_520C40` reads the backend-state `managed` flag,
  `sub_520EE0` clears and frees a `0xC88` mapping-info object, `sub_520F10`
  emits the same submap/coupling/reserved/channel-submap fields as the
  checked-in `mapping0_pack`, and `sub_521060` reconstructs the same structure
  with the exact range checks before the shared error cleanup.
- `sub_521230` is particularly stable because both the call sites and the body
  match the retained `todB` inline helper exactly: the sign-bit clear and the
  `7.17711438e-7 / 764.6161886` constants are unique to the checked-in
  IEEE-fastpath formula.
- I intentionally left `sub_520C70` and `sub_520CF0` deferred in this pass.
  Both clearly belong to the same retained Vorbis support corridor, but
  `sub_520C70` sits in a larger teardown seam with less obvious one-to-one
  ownership, and `sub_520CF0` is still a compiler-transformed forward-path
  helper inside `mapping0_forward` rather than a clean standalone source body.

## Aliases Added

- `sub_520C20` -> `vorbis_bitrate_clear`
- `sub_520C40` -> `vorbis_bitrate_managed`
- `sub_520EE0` -> `mapping0_free_info`
- `sub_520F10` -> `mapping0_pack`
- `sub_521060` -> `mapping0_unpack`
- `sub_521230` -> `todB`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2038` raw alias entries, `1970` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.995%` of `5473` functions
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
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x004E6730` | `FUN_004e6730` | `504` |
| 4 | `0x004B4100` | `FUN_004b4100` | `502` |
| 5 | `0x00475200` | `FUN_00475200` | `497` |
| 6 | `0x0047DA20` | `FUN_0047da20` | `497` |
| 7 | `0x00409670` | `FUN_00409670` | `496` |
| 8 | `0x004B3672` | `FUN_004b3672` | `495` |
| 9 | `0x0041C400` | `FUN_0041c400` | `492` |
| 10 | `0x00414AC0` | `FUN_00414ac0` | `490` |

The next pass can stay in this retained Vorbis corridor by returning to the
still-transformed `sub_520CF0` helper and the adjacent teardown seam, or it
can pivot back to the persistent host/STL queue head at `sub_41AD70`.
