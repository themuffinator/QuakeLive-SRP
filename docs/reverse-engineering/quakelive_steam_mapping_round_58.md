# Quake Live Steam Host Mapping Round 58

## Scope

This round continues the retained Quake III helper mapping immediately after
the `msg.c` / `net_chan.c` closures from round 57:

- the contiguous `q_math.c` helper block starting at `0x004D7990`
- the adjacent retained `q_shared.c` utility, parser, and string block
- separation of retained Quake III ownership from nearby tiny stubs and later
  Quake Live-only helper bodies

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/game/q_math.c`
- `src/code/game/q_shared.c`
- `assets/quake3/src/code/game/q_math.c`
- `assets/quake3/src/code/game/q_shared.c`

## Retained `q_math.c` Closures

The next contiguous helper band matches Quake III `q_math.c` in source order
and behavior:

- `sub_4D7990 -> Q_random`
- `sub_4D79C0 -> ClampChar`
- `sub_4D79E0 -> ColorBytes4`
- `sub_4D7A80 -> vectoangles`
- `sub_4D7BA0 -> AxisClear`
- `sub_4D7BD0 -> AxisCopy`
- `sub_4D7C10 -> ProjectPointOnPlane`
- `sub_4D7CB0 -> VectorRotate`
- `sub_4D7D10 -> Q_rsqrt`
- `sub_4D7D60 -> Q_fabs`
- `sub_4D7D80 -> SetPlaneSignbits`
- `sub_4D7DC0 -> BoxOnPlaneSide`
- `sub_4D8000 -> RadiusFromBounds`
- `sub_4D80D0 -> ClearBounds`
- `sub_4D8100 -> AddPointToBounds`
- `sub_4D8190 -> VectorNormalize`
- `sub_4D8200 -> VectorNormalize2`
- `sub_4D8280 -> Q_log2`
- `sub_4D82A0 -> MatrixMultiply`
- `sub_4D8390 -> AnglesToAxis`
- `sub_4D84F0 -> PerpendicularVector`
- `sub_4D85F0 -> PlaneFromPoints`
- `sub_4D86C0 -> RotatePointAroundVector`
- `sub_4D8890 -> MakeNormalVectors`

Observed facts:

1. `sub_4D7990` preserves the exact Quake III linear-congruential random path,
   updating `*seed = 69069 * *seed + 1` and returning the low `16` bits scaled
   by `1 / 65536.0`.
2. `sub_4D7D80` writes the cached sign-bit mask into the plane byte at offset
   `0x11`, and `sub_4D7DC0` is the retained optimized `BoxOnPlaneSide`
   jumptable path built on those sign bits.
3. `sub_4D84F0`, `sub_4D85F0`, `sub_4D86C0`, and `sub_4D8890` preserve the
   Quake III perpendicular-vector, plane construction, axis-rotation, and
   normal-basis helpers in the same call order used by the GPL source.
4. `sub_4D7CB0` is the retained `VectorRotate` helper and `sub_4D82A0` is the
   separate retained `MatrixMultiply` body; HLIL confirms the former computes a
   row-dot vector transform while the latter performs a full `3x3 * 3x3`
   multiply.

That fully closes the retained Quake III `q_math.c` core in this focused band.

## Retained `q_shared.c` Utility And Parser Closures

The adjacent helper block then transitions into retained Quake III
`q_shared.c` ownership:

- `sub_4D8940 -> Com_Clamp`
- `sub_4D89E0 -> COM_SkipPath`
- `sub_4D8A10 -> COM_StripExtension`
- `sub_4D8AC0 -> ShortSwap`
- `sub_4D8AE0 -> LongSwap`
- `sub_4D8B10 -> COM_Compress`
- `sub_4D8C10 -> COM_ParseExt`
- `sub_4D8D80 -> SkipBracedSection`
- `sub_4D8EC0 -> SkipRestOfLine`
- `sub_4D8F10 -> Q_strrchr`
- `sub_4D8F40 -> Q_strncpyz`
- `sub_4D8FA0 -> Q_stricmpn`
- `sub_4D9020 -> Q_strncmp`
- `sub_4D9060 -> Q_stricmp`
- `sub_4D9090 -> Q_strlwr`
- `sub_4D90C0 -> Q_strcat`
- `sub_4D9110 -> Q_CleanStr`
- `sub_4D9160 -> Com_sprintf`

Observed facts:

1. `sub_4D8B10` preserves the retained Quake III comment-stripping and
   whitespace-compaction behavior from `COM_Compress`, including quoted-string
   preservation.
2. `sub_4D8C10` is the retained `COM_ParseExt` tokenizer: it accepts the
   `allowLineBreaks` flag, skips comments and whitespace, updates the parse
   line counter, and preserves the quoted-token path.
3. `sub_4D8D80` and `sub_4D8EC0` are the companion retained parser helpers,
   matching the stock brace-depth walk and line-skip behavior.
4. `sub_4D8F10` through `sub_4D9160` preserve the familiar Quake III string
   helper sequence, including the exact overflow diagnostic in `Com_sprintf`.

## Deferred Non-Quake III Helpers

Not every start in `0x004D7970-0x004D9170` is a retained Quake III helper.
This pass intentionally leaves the following starts unresolved:

- `0x004D7970`
- `0x004D7980`
- `0x004D8970`
- `0x004D8990`
- `0x004D8A40`
- `0x004D8A80`
- `0x004D8EF0`

Observed facts:

1. `0x004D7970` and `0x004D7980` are tiny stub-like bodies rather than
   meaningful retained Quake III helpers.
2. `0x004D8970` and `0x004D8990` do not line up cleanly with the retained GPL
   `q_shared.c` sequence adjacent to `Com_Clamp`.
3. `0x004D8A40`, `0x004D8A80`, and `0x004D8EF0` appear to be later helper
   additions or codegen-local utility bodies rather than direct retained
   Quake III functions.

## Completion Summary

This round promotes `42` retained Quake III aliases:

- `q_math.c`: `Q_random`, `ClampChar`, `ColorBytes4`, `vectoangles`,
  `AxisClear`, `AxisCopy`, `ProjectPointOnPlane`, `VectorRotate`, `Q_rsqrt`,
  `Q_fabs`, `SetPlaneSignbits`, `BoxOnPlaneSide`, `RadiusFromBounds`,
  `ClearBounds`, `AddPointToBounds`, `VectorNormalize`, `VectorNormalize2`,
  `Q_log2`, `MatrixMultiply`, `AnglesToAxis`, `PerpendicularVector`,
  `PlaneFromPoints`, `RotatePointAroundVector`, `MakeNormalVectors`
- `q_shared.c`: `Com_Clamp`, `COM_SkipPath`, `COM_StripExtension`,
  `ShortSwap`, `LongSwap`, `COM_Compress`, `COM_ParseExt`,
  `SkipBracedSection`, `SkipRestOfLine`, `Q_strrchr`, `Q_strncpyz`,
  `Q_stricmpn`, `Q_strncmp`, `Q_stricmp`, `Q_strlwr`, `Q_strcat`,
  `Q_CleanStr`, `Com_sprintf`

Focused band results after this pass:

- `0x4D7970-0x4D9170`: `49 -> 7` remaining standalone gaps
- retained `q_math` core `0x4D7990-0x4D8940`: `24 -> 0`
- retained `q_shared` tranche `0x4D8940-0x4D9170`: `23 -> 5`

Global `quakelive_steam.exe` coverage after this pass:

- raw alias entries: `719 -> 761`
- address-backed aliases: `718 -> 760`
- Ghidra function coverage: `13.119% -> 13.886%` of `5473`

The next nearby unresolved standalone starts remain:

- `0x004D7970`
- `0x004D7980`
- `0x004D8970`
- `0x004D8990`
- `0x004D8A40`
- `0x004D8A80`
- `0x004D8EF0`

That means the retained Quake III ownership in this band is now essentially
closed, with the residual starts concentrated in tiny stubs and later helper
logic rather than in the stock `q_math.c` / `q_shared.c` bodies targeted here.
