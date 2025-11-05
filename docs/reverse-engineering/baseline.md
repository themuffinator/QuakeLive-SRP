# Reverse Engineering Baseline

The initial symbol export covers the retail Quake Live client, dedicated server,
and UI modules. Data comes from the automated Ghidra workflow in
`ghidra_scripts/ExportSymbolMap.py`, normalized with
`references/analysis/quakelive_symbol_aliases.json` and captured in
`references/symbol-maps/`.

## Coverage snapshot

| Binary | Functions resolved | Strings resolved | Relocations captured |
| ------ | ------------------ | ---------------- | -------------------- |
| Client | 4 / 5 | 4 / 5 | 4 |
| Server | 4 / 5 | 4 / 6 | 5 |
| UI     | 4 / 5 | 4 / 5 | 4 |

Key metrics come directly from the `stats` nodes in the exported JSON manifests
(`client.json`, `server.json`, `ui.json`).

## High-priority unknowns

### Client
- `UNRESOLVED_CLIENT_func_00445AB0` at `0x00445AB0` references the unresolved
  string `UNRESOLVED_CLIENT_str_0068C5D0`. This block appears inside the renderer
  call chain and should be triaged alongside the draw backend bootstrap.

### Server
- `UNRESOLVED_SERVER_func_00412190` at `0x00412190` is tied to scoring text and
  relocates `teamScores`. Confirm whether this houses the team scoring logic for
  Capture the Flag and Duel variations.
- Strings `UNRESOLVED_SERVER_str_0069F210` and `UNRESOLVED_SERVER_str_0069F250`
  share that same function and may expose additional team messaging formats.

### UI
- `UNRESOLVED_UI_func_0030F8A0` at `0x0030F8A0` references
  `UNRESOLVED_UI_str_0058F200` (“challenge hub update pending”). Investigate this
  dispatcher to uncover the new challenge/changelog systems.

## Next steps

1. Feed the JSON manifests into the documentation build so that unresolved
   prefixes surface on dashboards.
2. Expand the alias map with additional leak/debug symbol data to raise the
   resolution beyond ~80% for strings.
3. Re-run the exporter once the alias map grows to verify normalization remains
   stable across binaries.
