# quakelive_steam.exe Mapping Round 174

Date: 2026-04-27

Scope: exact retained `libvorbis/psy.c` recovery across the tone-mask seed
preparation and public masking wrappers from `0x005197C0` through
`0x0051AB80`. This pass stayed mapping-only and used the committed HLIL corpus
plus the checked-in Vorbis source in `src/libs/_deps/libvorbis/lib/psy.c` as
the exact naming anchor.

## Summary

This round resolved `6` additional `quakelive_steam.exe` rows.
Classification mix:

- `0` engine-owned functions
- `0` platform-service-owned functions
- `6` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old `0x0051A***` psychoacoustic masking seam now
reads cleanly as the retained seed-preparation ladder and its two public
wrappers. The exact ownership is now `seed_curve`, `seed_loop`, `seed_chase`,
`max_seeds`, `_vp_noisemask`, and `_vp_tonemask`, all anchored against the
already-mapped `bark_noise_hybridmp` and the adjacent `_vp_offset_and_mix`.
This also removes the old queue-head `sub_51A990` from the largest-unaliased
set.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_51A990` | `493` | support-library | `_vp_noisemask` | High | Closed from the exact double `bark_noise_hybridmp` pass: the initial `offset=140,fixed=-1` noise envelope, the `work[i]=logmdct[i]-logmask[i]` scratch, the second hybrid pass with `noisewindowfixed`, and the final `noisecompand[dB]` remap. |
| 2 | `sub_51AB80` | `326` | support-library | `_vp_tonemask` | High | Closed from the exact ATH setup and tone-seed flow: `seed[i]=NEGINF`, `att=local_specmax + ath_adjatt` clamped to `ath_maxatt`, `logmask[i]=ath[i]+att`, then `seed_loop` and `max_seeds`. |
| 3 | `sub_519BE0` | `292` | support-library | `max_seeds` | High | Closed from the exact seed-chase consumer that walks `p->octave`, clamps by `tone_abs_limit`, tracks the minimum active seed, and projects it back onto `flr`. |
| 4 | `sub_519A40` | `412` | support-library | `seed_chase` | High | Closed from the exact stack-based seed compaction algorithm: `posstack`, `ampstack`, overlap pruning with `linesper`, and the final straight-through fill of `seeds[pos]=ampstack[i]`. |
| 5 | `sub_519960` | `221` | support-library | `seed_loop` | High | Closed from the exact octave-bucket scan that finds per-octave maxima, checks `max + 6.f > flr[i]`, shifts/clamps `oc`, and dispatches into `seed_curve`. |
| 6 | `sub_5197C0` | `408` | support-library | `seed_curve` | High | Closed from the exact tone-curve writer that computes `choice=(amp+dBoffset-P_LEVEL_0)*.1`, clamps it to `P_LEVELS-1`, walks `posts/curve`, and raises `seed[seedptr]` when the new `lin` value is larger. |

## Evidence Notes

- The decisive source anchors are
  [seed_curve](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:386>),
  [seed_loop](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:413>),
  [seed_chase](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:450>),
  [max_seeds](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:508>),
  [bark_noise_hybridmp](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:543>),
  [_vp_noisemask](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:702>),
  and [_vp_tonemask](</E:/Repositories/QuakeLive-reverse/src/libs/_deps/libvorbis/lib/psy.c:750>).
- The committed HLIL preserves the same control flow directly:
  `sub_5197C0` indexes the tone-curve table and advances `seedptr` by
  `linesper`, `sub_519960` scans consecutive identical octave slots before
  dispatching into `sub_5197C0`, `sub_519A40` builds and prunes the seed
  stack, and `sub_519BE0` consumes the chased seed line while clamping by the
  psychoacoustic absolute limit.
- The public wrappers are equally explicit in the HLIL:
  `sub_51A990` calls the already-mapped `bark_noise_hybridmp` twice with the
  retained `140/-1` and `0/noisewindowfixed` argument pairs, while
  `sub_51AB80` seeds the `NEGINF` work vector, applies the `ath_adjatt`
  clamp, then calls `seed_loop` followed by `max_seeds`.
- I intentionally left the denser coupling helpers around `sub_51A880`,
  `sub_51B490`, `sub_51B640`, `sub_51B7A0`, and `sub_51BE80` deferred in this
  pass. They are adjacent and source-owned, but the current compiler
  transformations in the coupling path make them a worse fit for a quick exact
  tranche than the clean masking-preparation ladder.

## Aliases Added

- `sub_5197C0` -> `seed_curve`
- `sub_519960` -> `seed_loop`
- `sub_519A40` -> `seed_chase`
- `sub_519BE0` -> `max_seeds`
- `sub_51A990` -> `_vp_noisemask`
- `sub_51AB80` -> `_vp_tonemask`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `2032` raw alias entries, `1964` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `35.885%` of `5473` functions
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

The next pass can stay in retained Vorbis work by returning to the transformed
residue helper at `sub_523280` or the remaining psych/coupling helpers, or it
can pivot back to the persistent host/STL queue head at `sub_41AD70`.
