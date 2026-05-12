# quakelive_steam.exe Mapping Round 156

Date: 2026-04-27

Scope: support-library mapping around the retained `vorbisfile.c` seek/page
helpers adjacent to the existing `ov_raw_seek` lane, plus one host-owned Steam
server auth-lifecycle helper from the server initialization path. This pass
stayed mapping-only.

## Summary

This round resolved `6` additional `quakelive_steam.exe` rows. Classification
mix:

- `1` engine-owned function
- `0` platform-service-owned functions
- `5` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main outcome is that the old `0x004FBED0` through `0x004FC150` slab now
reads cleanly as the private `vorbisfile.c` page/serial helpers underneath the
already mapped `_fetch_headers`, `_bisect_forward_serialno`, and `ov_raw_seek`
lane. I also closed the queue-head-adjacent Steam auth helper at `0x00466B90`,
which is the retail server-side cleanup pass that ends tracked Steam auth
sessions no longer owned by a live client before fresh server initialization
continues.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_466B90` | `535` | engine-owned | `SteamServer_EndOrphanedAuthSessions` | Medium-high | Closed from the exact server-init callsite, the `EndAuthSession` import use, the SteamID auth-tree erase path, and the `"Found an authed client..."` / `"Called EndAuthSession..."` log strings. |
| 2 | `sub_4FBF30` | `165` | support-library | `_get_next_page` | High | Closed from the exact `ogg_sync_pageseek` loop, boundary handling, `_get_data` refill path, and `vf->offset` update logic from `vorbisfile.c`. |
| 3 | `sub_4FBFE0` | `184` | support-library | `_get_prev_page` | High | Closed from the exact backward `CHUNKSIZE` walk, `_seek_helper` probe, `_get_next_page` scan, and page re-read fallback when `header_len == 0`. |
| 4 | `sub_4FBED0` | `95` | support-library | `_seek_helper` | High | Closed from the exact callback seek guard, `vf->offset` update, and `ogg_sync_reset` path on successful reposition. |
| 5 | `sub_4FC100` | `73` | support-library | `_add_serialno` | High | Closed from the exact `ogg_page_serialno` extraction plus `_ogg_malloc` / `_ogg_realloc` growth path for the serial-number list. |

## Evidence Notes

- `sub_4FBED0`, `sub_4FBF30`, `sub_4FBFE0`, `sub_4FC100`, and `sub_4FC150`
  map one-to-one against the bundled
  [vorbisfile.c](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:80>)
  helper lane:
  [\_seek_helper](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:80>),
  [\_get_next_page](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:110>),
  [\_get_prev_page](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:147>),
  [\_add_serialno](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:188>),
  and [\_lookup_page_serialno](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/vorbisfile.c:212>).
  The HLIL preserves the same `ogg_sync_*`, `ogg_page_*`, and callback flow
  as the bundled source.
- `sub_4FC150` is specifically `_lookup_page_serialno`, not
  `_lookup_serialno`. The body begins by calling `ogg_page_serialno()` on the
  supplied page before checking the long-list entries, which matches the exact
  wrapper in `vorbisfile.c`.
- I intentionally left `sub_4FC180` and `sub_4FC240` unresolved in this pass.
  Their behavior is bounded inside the same `vorbisfile.c` seek/index lane, but
  the retail compiler has split part of the surrounding `_bisect_forward_serialno`
  / header-collection flow into shapes that are not yet stable enough for a
  one-to-one alias.
- `sub_466B90` is host-owned Steam server code, not a support library. The
  strongest signals are:
  it is called during server initialization just before the retained Steam/ZMQ
  startup lane; it walks the Steam auth-session tree rooted at `data_e30360`;
  it calls the same `SteamGameServer()->EndAuthSession` virtual used by
  [SteamServer_EndAuthSession](</E:/Repositories/QuakeLive-reverse/references/analysis/quakelive_symbol_aliases.json:2117>);
  and it removes the ended SteamIDs from the tracked auth tree afterward.
  The “orphaned” wording is an inference from the observed `svs.clients` scan
  and the `"Found an authed client..."` log path.

## Aliases Added

- `sub_466B90` -> `SteamServer_EndOrphanedAuthSessions`
- `sub_4FBED0` -> `_seek_helper`
- `sub_4FBF30` -> `_get_next_page`
- `sub_4FBFE0` -> `_get_prev_page`
- `sub_4FC100` -> `_add_serialno`
- `sub_4FC150` -> `_lookup_page_serialno`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1783` raw alias entries, `1712` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `31.281%` of `5473` functions
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
| 1 | `0x004940D0` | `FUN_004940d0` | `547` |
| 2 | `0x004FC240` | `FUN_004fc240` | `537` |
| 3 | `0x0051FF40` | `FUN_0051ff40` | `535` |
| 4 | `0x004FAF60` | `FUN_004faf60` | `534` |
| 5 | `0x00510410` | `FUN_00510410` | `533` |
| 6 | `0x00501ED0` | `FUN_00501ed0` | `529` |
| 7 | `0x00498BB0` | `FUN_00498bb0` | `526` |
| 8 | `0x00503630` | `FUN_00503630` | `526` |
| 9 | `0x004AC440` | `FUN_004ac440` | `521` |
| 10 | `0x00511670` | `FUN_00511670` | `520` |

The next pass can return to the still-opaque route-search helper
`sub_4940D0`, finish the remaining transformed Vorbis seek/index piece at
`sub_4FC240`, or move onward to the larger support-library leftovers beginning
at `sub_51FF40`.
