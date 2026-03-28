# Quake Live Steam Host Mapping Round 53

## Scope

This round closes the remaining random-map and factory-management tranche that
follows the arena/map-pool loader work from round 52.

The promoted slice covers:

- factory-list printing used by the host `map` command
- random map-pool selection and the `startRandomMap` / `nextmap` helpers
- factory JSON/object parsing, single-file loading, bulk loading, and reload

Primary evidence for this round:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/game/g_factory.c`
- `src/code/game/g_main.c`
- `src/code/game/g_cmds.c`

## Random Map And Factory Helper Closures

### `sub_45E7D0`: `Factory_PrintValidList`

The helper prints the exact header `Valid factories: `, walks the loaded
factory table, skips entries whose ids begin with `_`, and prints each
remaining id. Call-site evidence shows the host `map` command invoking this
helper immediately after printing the `%s (map) (factory)\n` usage line. The
current source tree does not expose a standalone equivalent, so this promotion
uses a descriptive host-side name.

### `sub_45E830`: `MapPool_SelectRandomEntry`

Observed facts:

1. The helper returns a `0x1000`-byte map-pool record, not just a map name.
2. When the map pool is empty, it seeds the output with `campgrounds`.
3. Otherwise it selects a random loaded entry using the map-pool count and
   copies the chosen `0x1000`-byte record into the caller buffer.

That is a clean host-side random map-pool selector, promoted as
`MapPool_SelectRandomEntry`.

### `sub_45E8B0`: `StartRandomMap_f`

The command registration block wires `startRandomMap` directly to this helper.
Its body selects a random map-pool entry through `sub_45E830` and executes the
exact command format `map %s %s`. That is exactly the console command
`StartRandomMap_f`.

### `sub_45E940`: `MapPool_UpdateNextMap`

The helper is called during dedicated-server startup immediately after the map
pool is loaded and again from other server control flow. When the pool is
empty, it sets `nextmap` to `map_restart 0`; otherwise it selects a random
entry via `sub_45E830` and writes `nextmap = "map %s %s"`. The current source
tree does not expose this as a standalone helper, so this promotion uses the
descriptive name `MapPool_UpdateNextMap`.

## Factory Parsing And Loading Closures

### `sub_45F380`: `Factory_ParseDefinition`

Observed facts:

1. The helper insists that each incoming JSON element is an object and requires
   string keys for `id`, `basegt`, and `title`, plus an object-valued `cvars`
   member.
2. It validates `basegt` against the same Quake Live gametype token set used by
   the reconstructed source and rejects duplicates with the exact string
   `^1Factory with id %s already exists.\n`.
3. It duplicates strings for the id/title/author/description fields, parses the
   optional tag array, and copies the cvar override pairs into the loaded
   factory record.

This emitted helper corresponds to the `Factory_ParseDefinition` stage, with
the later registration/dedup bookkeeping fused into the same body rather than
split into a separate `Factory_RegisterDefinition` call.

### `sub_45F800`: `Factory_LoadFile`

The helper opens a single factories file, enforces the host-side `file not
found` and `file too large` guardrails, parses the buffer as JSON, accepts both
singleton objects and arrays, forwards each definition to `sub_45F380`, and
logs `loaded factories from %s, total %i\n`. That is exactly the host-side
`Factory_LoadFile`.

### `sub_45FA50`: `Factory_LoadAllDefinitions`

The helper loads the base factories file first, enumerates `scripts/*.factories`
via `trap_FS_GetFileList`, prefixes each name with `scripts/`, and feeds every
path to `sub_45F800`. This corresponds to the current source's
`Factory_LoadAllDefinitions` phase, even though the host implementation does not
emit a separate tiny `Factory_LoadSupplementalFiles` helper.

### `sub_45FB40`: `Factory_Reload_f`

The command registration block wires `reload_factories` directly to this
helper. Its body frees the previously loaded factory records, explicitly skips
freeing the currently loaded factory while printing the exact diagnostic
`not clearing currently loaded factory id %s, continuing\n`, resets the loaded
count, and then reloads the base plus supplemental factories via the same
`Factory_LoadFile` path. That is exactly the host-side reload command
`Factory_Reload_f`.

## Completion Summary

This round promotes:

- `Factory_PrintValidList`
- `MapPool_SelectRandomEntry`
- `StartRandomMap_f`
- `MapPool_UpdateNextMap`
- `Factory_ParseDefinition`
- `Factory_LoadFile`
- `Factory_LoadAllDefinitions`
- `Factory_Reload_f`
- `SteamAPI_Shutdown`

Remaining nearby standalone gaps after this pass are now concentrated in:

- `0x004607A0`
- `0x00460750`
- `0x004606D0`
- `0x004606B0`
- `0x00460710`
- `0x00460730`

These are short helper functions in the adjacent Steam/utility band rather than
part of the world/map-pool/factory block that this round targeted.
