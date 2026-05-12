# quakelive_steam.exe Mapping Round 223

Date: 2026-05-11

Scope: the retained client command-wrapper seam in
`src/code/client/cl_main.c`, staying in the engine-owned networking/browser
command surface and avoiding external-library implementation work.

## Summary

This round adds one owner alias and documents a revalidated nearby source lane.
The checked-in `showip` wrapper was already retail-shaped; the useful win here
was promoting its retained retail owner instead of forcing a speculative edit
in the still-unsettled `localservers` / `globalservers` / `ping` /
`serverstatus` registration seam.

Classification mix:

- `1` engine/client command-wrapper alias
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The main win is:

- [`sub_4BB1A0` -> `CL_ShowIP_f`](../../references/analysis/quakelive_symbol_aliases.json)
  is now promoted in the committed alias corpus, matching the retained retail
  `showip` command wrapper used by [`CL_ShowIP_f`](../../src/code/client/cl_main.c).

## Evidence Notes

- In committed HLIL, `CL_Init` registers `showip` through
  `sub_4c81d0("showip", &data_4bb1a0)`.
- The committed HLIL body at `0x004BB1A0` is a jump stub
  (`e9 eb 34 03 00`) rather than a full Ghidra-sized function body, which is
  why this owner promotion improves raw alias coverage but does not change the
  stricter function-row-backed count.
- The jump target is `0x004EE690`, which is already promoted as `Sys_ShowIP`.
- The checked-in source wrapper in
  [`CL_ShowIP_f`](../../src/code/client/cl_main.c) is exactly the retained
  one-line shape:
  1. no argument handling,
  2. no wrapper-side logging or formatting,
  3. a direct `Sys_ShowIP();` tail call.
- I also re-checked the nearby retained browser/status helper lane:
  `CL_ServerStatus`, `CL_GetPing`, `CL_UpdateVisiblePings_f`, and the shared
  `getstatus` / `getinfo xxx` flow still align with the currently promoted
  retail owners, so no engine-source change was justified there this round.
- The larger client command-registration seam remains open:
  the committed retail `CL_Init` evidence still cleanly shows `showip`,
  `setenv`, `connect`, `demo`, and related retained owners, but it does not
  yet give equally stable explicit add-command ownership for the checked-in
  `localservers`, `globalservers`, `ping`, `serverstatus`, and `rcon`
  registration cluster. That should stay in the queue until there is stronger
  address-backed evidence than inherited Quake III text alone.

## Aliases Added

- `sub_4BB1A0` -> `CL_ShowIP_f`

## Verification

Static/source validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- `pytest tests/test_engine_client_command_parity.py -q --tb=no -k "showip or forward_restart_and_info_contracts or cinematic_network_and_browser"`
  passed
- `git diff --check -- references/analysis/quakelive_symbol_aliases.json tests/test_engine_client_command_parity.py docs/reverse-engineering/quakelive_steam_mapping_round_223.md`
  reported only the repo's existing LF -> CRLF normalization warnings on the
  touched text files

Alias accounting for the current dirty worktree:

- before this pass: `2236` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- after this pass: `2237` raw `quakelive_steam` aliases, `2157` strict
  address-backed aliases
- strict Ghidra address-backed coverage after this pass: `39.412%` of `5473`
  committed functions

Parity estimate after this pass:

- strict-retail `showip` command-wrapper lane: `99%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

The next strong nearby pass is still the client command-registration seam
around `localservers`, `globalservers`, `ping`, `serverstatus`, and `rcon`,
but it should wait for stable owner evidence from the committed retail corpus
instead of guessing from GPL-era registration placement.
