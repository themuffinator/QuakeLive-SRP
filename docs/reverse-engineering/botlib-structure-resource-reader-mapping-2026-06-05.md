# Botlib Structure Resource Reader Mapping - 2026-06-05

## Scope

This pass identifies `src/code/botlib/l_struct.c` as the next botlib section
worth working on going forward. The section owns bot resource structure parsing:
field lookup, numeric bounds coercion, string/literal handling, nested structure
reads, and the direct item/weapon/projectile readers that feed bot gameplay
data.

This was a static reverse-engineering and source-confirmation round. No runtime
launch was needed because the committed HLIL and Ghidra references expose the
relevant control flow, diagnostics, and caller wiring directly.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/l_struct.c`
- `src/code/botlib/be_ai_goal.c`
- `src/code/botlib/be_ai_weap.c`

## Why This Section

The parser slice is a good forward botlib work area because it is small enough
to map accurately and important enough to affect real bot behavior:

- `ReadStructure` parses bot item, weapon, and projectile structures.
- `ReadNumber` enforces signed, unsigned, float, bounded, char, and int
  coercion rules that determine whether bot resource files are accepted.
- `FindField` gives the field-table dispatch used by every structure reader.
- The adjacent `l_precomp.c` token wrappers are already mapped enough to make
  `l_struct.c` evidence actionable instead of speculative.

## Retail Evidence

Observed facts:

- Ghidra metadata identifies `quakelive_steam.exe` as the owning x86 retail
  binary with `5473` functions, `351` imports, and `2` exports.
- Ghidra `functions.csv` still lists the relevant functions as raw unknowns:
  `FUN_004AE830` size `104`, `FUN_004AE8A0` size `1062`, and
  `FUN_004AECD0` size `851`.
- The alias map already promotes:
  - `sub_4AE830 -> FindField`
  - `sub_4AE8A0 -> ReadNumber`
  - `sub_4AECD0 -> ReadStructure`
- Binary Ninja HLIL for `0x004AE830` walks a field table in `0x1c`-byte
  records and returns `&arg1[esi * 7]`, matching `fielddef_t`.
- Binary Ninja HLIL for `0x004AE8A0` preserves the source-reader numeric
  contract: unsigned-minus rejection, unexpected punctuation, expected-number
  diagnostics, float-only acceptance for `FT_FLOAT`, bounded float checks,
  default char/int min/max ranges, bounded integer overrides, and final storage
  into char/int/float destinations.
- Binary Ninja HLIL for `0x004AECD0` calls `FindField`, reports unknown
  structure fields, handles array braces and comma separators, dispatches by
  field type, strips string quotes through `StripDoubleQuotes`, recursively
  reads nested structures, and emits the exact `BUG: no sub structure defined`
  diagnostic.
- Ghidra companion call sites route `ReadStructure` through the bot item and
  weapon/projectile resource parsers, matching `be_ai_goal.c` and
  `be_ai_weap.c`.

## Source Confirmation

The checked-in source matches the recovered retail shape:

- `FindField` performs exact `strcmp` field-name matching and returns the
  address of the matching `fielddef_t`.
- `ReadNumber` preserves the retail signed/unsigned and bounded conversion
  behavior. The source uses the same diagnostic strings observed in HLIL:
  `unexpected float`, `float out of range [%f, %f]`,
  `value %d out of range [%f, %f]`, and
  `value %d out of range [%d, %d]`.
- `ReadChar` and `ReadString` remain source-level helpers, but retail folds
  their behavior into the larger `ReadStructure` body. That means they are
  source-confirmed behavior, not stable standalone retail aliases in this pass.
- `ReadStructure` intentionally keeps the recursive nested-structure call
  without checking its return value, matching the observed retail body. This is
  a parity behavior, not a style recommendation.
- `be_ai_goal.c` consumes `ReadStructure` through `iteminfo_struct`.
- `be_ai_weap.c` consumes `ReadStructure` through `weaponinfo_struct` and
  `projectileinfo_struct`.

## Consumer Resource Tables

Second-pass source reconstruction extended the selected section from
`l_struct.c` internals into the concrete resource tables that feed it.

Observed facts:

- `be_ai_goal.c::iteminfo_fields` maps the retail `iteminfo` resource body
  through `name`, `model`, `modelindex`, `type`, `index`, `respawntime`,
  `mins[3]`, and `maxs[3]`.
- Retail HLIL at `0x0049CD80` reads `max_iteminfo` with default `256`, accepts
  only `iteminfo` top-level definitions, reads a quoted classname into the
  first `0x1f` bytes of the `iteminfo_t` entry, calls `ReadStructure` with
  `data_563f9c`, and writes the item number at entry offset `0xe8`.
- The retail item allocation formula `esi * 0xec + 8` matches a config header
  plus `max_iteminfo * sizeof(iteminfo_t)`.
- `be_ai_weap.c::weaponinfo_fields` maps the retail `weaponinfo` resource body
  through weapon number/name/level/model/index/flags/projectile controls,
  spread/speed/acceleration values, three-vector recoil/offset/angleoffset
  values, ammo fields, and activation/reload/spin timing fields.
- `be_ai_weap.c::projectileinfo_fields` maps the retail `projectileinfo`
  resource body through name/model/flags/gravity/damage/radius/visdamage,
  damage type, owner health increment, push, detonation, bounce, bounce
  friction, and bounce-stop values.
- Retail HLIL at `0x004A5A90` reads `max_weaponinfo` and
  `max_projectileinfo` with default `32`, allocates
  `max_projectileinfo * 0xd0 + max_weaponinfo * 0x228 + 0x10`, calls
  `ReadStructure` with `data_5643d4` for temporary weapon entries and
  `data_5643dc` for projectile entries, then copies valid weapons into the
  indexed weapon table and resolves each weapon's projectile name.
- Ghidra corroborates the same weapon/projectile table addresses and allocation
  sizes in `FUN_004A5A90`.

Inference:

- The source field-table layout is already close to retail for this selected
  slice. Remaining uncertainty is mostly data-symbol naming, not parser
  behavior.

## Writer Path Status

The adjacent write helpers in `l_struct.c` are source-real but not yet
retail-promoted:

- `WriteIndent` and `WriteFloat` are used by `be_ai_weight.c` when writing
  fuzzy weight configs.
- `WriteStructure` and `WriteStructWithIndent` are only directly called from
  `be_ai_weap.c::DumpWeaponConfig`, which is guarded by `DEBUG_AI_WEAP`.
- Nearby retail `0x004AF0xx` functions in the committed HLIL do not provide
  enough string, call-site, or control-flow evidence to safely alias them as
  the structure writer helpers.

Open question:

- If a future pass needs write-side parity, start from `be_ai_weight.c` writer
  call sites and fprintf/format-string evidence, not from address adjacency
  after `ReadStructure`.

## Characteristic Parser Sibling

A follow-on pass mapped `be_ai_char.c` as a related parser sibling. It does not
call `ReadStructure`, but it uses the same precompiler/token layer and owns bot
character resource loading.

Observed facts:

- `BotLoadCharacterFromFile` is promoted as `sub_496B40` in the alias map.
- Retail HLIL allocates `0x2cc` bytes for a loaded character, matching
  `filename[64]`, `skill`, and `80` characteristic entries with one byte of
  type plus a four-byte union payload per entry after compiler padding.
- The source and retail both accept only top-level `skill` definitions, expect
  a number plus `{`, and either parse the matching skill block or skip an
  unmatched skill block with brace-depth tracking.
- The index check remains `index > MAX_CHARACTERISTICS`, not `>=`; HLIL
  preserves the same upper-bound shape as `var_30 s> 0x50`. This is a retail
  parity quirk to preserve.
- Characteristic values remain split by token type: integer, float, or quoted
  string after double-quote stripping.
- `BotLoadCachedCharacter` and `BotLoadCharacterSkill` preserve the default
  fallback chain through `bots/default_c.c`, cached exact skill, integer skill
  load, any-skill load, and default any-skill fallback.

## Weight Parser Sibling

The same follow-on pass mapped `be_ai_weight.c` as the other close parser
sibling for this selected area.

Observed facts:

- Alias map promotions cover `ReadValue`, `ReadFuzzyWeight`,
  `FreeFuzzySeperators_r`, `ReadFuzzySeperators_r`, `ReadWeightConfig`, and
  `FindFuzzyWeight`.
- Retail HLIL confirms the `ReadValue` negative-value warning path and invalid
  return-value diagnostic.
- `ReadFuzzyWeight` matches the source split between `balance(a,b,c);` and a
  plain `return value;` weight.
- `ReadFuzzySeperators_r` matches the recursive `switch(index) { case/default
  ... }` grammar, duplicate-default rejection, and missing-default warning that
  synthesizes a `MAX_INVENTORYVALUE` fallback separator.
- `ReadWeightConfig` matches the `MAX_WEIGHT_FILES == 128` cache scan gated by
  `bot_reloadcharacters`, the retail `0x444` allocation, the filename copy at
  offset `0x404`, the `weight` top-level token, the `too many fuzzy weights`
  warning, and the recursive `switch` or flat `return` branch.
- The source writer helpers in `be_ai_weight.c` are inside `#if 0`. This
  strengthens the prior conclusion that write-side structure/weight dumping is
  source-real but not part of the active retail parser surface for this pass.

Inference:

- The selected parser corridor now has strong coverage for three resource
  families: structure-table resources, character resources, and fuzzy-weight
  resources.

## Changes

- Strengthened `tests/test_botlib_internal_parity.py` so the existing
  precompiler/script alias test now also pins `ReadNumber` and `ReadStructure`
  against HLIL starts and Ghidra `functions.csv` rows.
- Added a focused source-shape test for `l_struct.c` that connects:
  - source helper bodies,
  - retail HLIL diagnostic/control-flow anchors,
  - Ghidra caller evidence, and
  - item/weapon/projectile consumer wiring.
- Added a second source-shape test that pins the selected reader's concrete
  `iteminfo`, `weaponinfo`, and `projectileinfo` field tables against retail
  allocation sizes, table addresses, top-level tokens, diagnostics, and alias
  map entries.
- Added parser-sibling tests for bot character and fuzzy-weight resources,
  including aliases, Ghidra `functions.csv` rows, retail HLIL control-flow
  anchors, Ghidra source-shape anchors, and the compiled-out weight writer
  block.
- Added this mapping note as the forward botlib work section.
- No C source body change was needed.

## Follow-On Work

Good next slices inside this same section:

- The `l_precomp.c` handle wrappers that feed bot resource loading from qagame
  and host imports.
- `l_script.c::PS_ReadNumber` and punctuation handling, especially where
  Quake Live resource files rely on permissive legacy token behavior.
- Write-side structure/weight config dumping, but only after identifying stable
  retail call sites and format strings.
- Resource-level executable fixtures for tiny synthetic item/weapon structures,
  if a future source change touches parser semantics.

## Validation

Targeted validation for this pass:

- `python -m pytest tests/test_botlib_internal_parity.py -k "structure_resource_reader or structure_reader_consumers or character_resource_parser or weight_resource_parser or precompiler_and_script_internal_aliases" -q`
- `python -m pytest tests/test_botlib_internal_parity.py -q`
- `python -m pytest tests/test_bot_resource_loading.py -q`

Observed result:

- focused parser selection after the character/weight parser extension:
  `5 passed, 25 deselected`
- full botlib internal parity file after the extension: `30 passed`
- adjacent bot resource loading: `3 passed`

No game launch was performed. Static source, HLIL, Ghidra, and pytest coverage
fully answer this mapping question.

## Parity Estimate

- Focused `l_struct.c` resource-reader mapping: `72% -> 94%`. Before this
  round, aliases existed but the source-level contract and bot resource
  consumers were not pinned together.
- Focused `l_struct.c` plus item/weapon/projectile consumer-table mapping:
  `94% -> 97%` after the second pass.
- Focused parser-corridor mapping after characteristic and fuzzy-weight
  siblings: `97% -> 98%`.
- Overall botlib plus related parser wiring: approximately `67% -> 68%`.
- Strict-retail Windows replacement target: unchanged at `100%`; this pass
  reduces future botlib-parser uncertainty rather than changing an active gate.
