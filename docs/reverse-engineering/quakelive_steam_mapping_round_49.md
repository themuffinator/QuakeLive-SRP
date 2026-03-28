# Quake Live Steam Host Mapping Round 49

## Scope

This round closes the remaining `0x455540-0x455E10` renderer gap cluster by
mapping the shader-parser helpers in `tr_shader.c`.

The newly promoted slice covers:

- vector parsing for shader text
- alpha/blend/genfunc name decoders
- waveform and tcMod parsers
- the full shader stage parser

The primary evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_shader.c`

## Parser Helpers

### `sub_455540`: `ParseVector`

Observed local facts:

1. The helper checks for an opening `"("`, then parses `count` float elements,
   then checks for a closing `")"`.
2. It emits the exact warning strings `"missing parenthesis"` and
   `"missing vector element"` with `shader.name`.
3. It writes parsed `atof` results into the destination vector and returns a
   success/failure boolean.

That is the exact shader parser helper `ParseVector`.

### `sub_455640`: `NameToAFunc`

The helper matches the exact alpha-test tokens `GT0`, `LT128`, and `GE128`,
returns the corresponding `GLS_ATEST_*` bits, and otherwise prints the exact
`invalid alphaFunc name` warning. That is exactly `NameToAFunc`.

### `sub_4556B0`: `NameToSrcBlendMode`

The helper recognizes the exact source-blend names from the GPL parser:
`GL_ONE`, `GL_ZERO`, `GL_DST_COLOR`, `GL_ONE_MINUS_DST_COLOR`,
`GL_SRC_ALPHA`, `GL_ONE_MINUS_SRC_ALPHA`, `GL_DST_ALPHA`,
`GL_ONE_MINUS_DST_ALPHA`, and `GL_SRC_ALPHA_SATURATE`. Its fallback warning
matches `NameToSrcBlendMode` exactly.

### `sub_4557B0`: `NameToDstBlendMode`

The helper recognizes the exact destination-blend names `GL_ONE`, `GL_ZERO`,
`GL_SRC_ALPHA`, `GL_ONE_MINUS_SRC_ALPHA`, `GL_DST_ALPHA`,
`GL_ONE_MINUS_DST_ALPHA`, `GL_SRC_COLOR`, and `GL_ONE_MINUS_SRC_COLOR`, with
the matching fallback warning. That is exactly `NameToDstBlendMode`.

### `sub_455890`: `NameToGenFunc`

The helper maps the exact waveform tokens `sin`, `square`, `triangle`,
`sawtooth`, `inversesawtooth`, and `noise` to the expected enum values and
falls back with the exact `invalid genfunc name` warning. That is exactly
`NameToGenFunc`.

### `sub_455940`: `ParseWaveForm`

Observed local facts:

1. The helper first consumes one token and feeds it through `NameToGenFunc`.
2. It then parses the exact four waveform scalars in order:
   `base`, `amplitude`, `phase`, and `frequency`.
3. Every missing-token path prints the exact `missing waveform parm` warning.

That is the exact waveform parser `ParseWaveForm`.

### `sub_4559E0`: `ParseTexMod`

Observed local facts:

1. The helper enforces the exact `TR_MAX_TEXMODS` limit and raises the exact
   `too many tcMod stages` error.
2. It parses the exact tcMod keywords from the GPL parser:
   `turb`, `scale`, `scroll`, `stretch`, `transform`, `rotate`, and
   `entityTranslate`.
3. Each branch fills the matching fields in the current `texModInfo_t`, uses
   `NameToGenFunc` for `stretch`, and emits the exact missing-parameter and
   unknown-`tcMod` warnings.

That is the exact tcMod parser `ParseTexMod`.

### `sub_455E10`: `ParseStage`

Observed local facts:

1. The helper loops token-by-token until the closing `}` and marks the stage
   active at entry.
2. It dispatches the exact shader stage keywords handled by `ParseStage`,
   including `map`, `clampmap`, `animMap`, `videoMap`, `alphaFunc`,
   `depthfunc`, `detail`, `blendfunc`, `rgbGen`, `alphaGen`, `texgen`/`tcGen`,
   `tcMod`, and `depthwrite`.
3. It calls the newly promoted helpers `ParseVector`, `NameToAFunc`,
   `NameToSrcBlendMode`, `NameToDstBlendMode`, `ParseWaveForm`, and
   `ParseTexMod`, and ends by composing the stage state bits.

That is the exact shader stage parser `ParseStage`.

## Open Follow-Up

This pass closes the last unresolved starts in the old `0x451800-0x456000`
focus band. The next unresolved renderer/parser work now lies beyond that band.
