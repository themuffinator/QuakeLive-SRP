# Quake Live Steam Mapping Round 431

Date: 2026-06-08

## Scope

This round reconstructs the `com_build` launch guard at the top of
`SteamClient_Init`. The focus is preventing build-script/tool launches from
probing Steam or registering the client Steam callback/lobby/voice/rich
presence bootstrap while preserving normal Steam-launched runtime behavior.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_461500` to
  `SteamClient_Init`.
- Binary Ninja HLIL for `sub_461500` starts with
  `sub_4ccd80("com_build")`.
- The `SteamAPI_Init()` call and all later client callback/lobby/voice/stats
  bootstrap work are inside the `result == 0` branch.
- The same HLIL block logs `"Steam API not present.\n"` on failed
  `SteamAPI_Init()` and `"Steam API initialized.\n"` after the successful
  bootstrap path.
- Source registers `com_build` before `SteamClient_Init`, so a literal
  `Cvar_Find("com_build")` test would suppress Steam for every source launch.
  The existing source-side policy already uses `com_buildScript->integer` in
  the common startup guard and persona-name bootstrap.

## Source Reconstruction

- Added a top-level `com_buildScript && com_buildScript->integer` guard in
  `SteamClient_Init` before `SteamClient_CancelAuthTicket()`,
  `QL_RefreshPlatformServices()`, callback registration, lobby bootstrap,
  voice commands, `stats_clear`, and rich-presence writes.
- Kept the existing source-side `com_build` integer interpretation instead of
  the literal retail presence check because source startup owns the cvar earlier
  than retail.
- Added a parity gate that checks the HLIL `com_build`/`SteamAPI_Init` order
  and asserts the source guard runs before platform refresh or any retained
  Steam bootstrap side effects.

## Deferred Notes

- This does not move the entire source startup order to retail's exact
  pre-filesystem `SteamClient_Init()` position. The source still keeps the
  smaller `Com_InitSteamClientForFilesystem()` refresh before filesystem
  startup and the full callback/command bootstrap later.
- Normal Steam launches are unchanged unless `com_build` is explicitly set.

## Parity

Focused Steam `com_build` launch guard confidence moves from 63% to 90%.
The broader Steam launch/runtime integration slice moves from 83% to 84%.
