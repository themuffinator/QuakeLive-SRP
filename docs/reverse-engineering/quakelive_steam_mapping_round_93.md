# Quake Live Steam Host Mapping Round 93

## Scope

This round closes the next clean client-owned Steamworks lifetime seam in
`quakelive_steam.exe`:

1. the missing retained wrapper for `SteamUser()->CancelAuthTicket`
2. the discarded client auth-ticket handle in the writable Steam credential
   request path
3. the absent disconnect and error cleanup owner for that ticket handle

The evidence base stayed the same:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- earlier auth/browser notes in
  [Round 02](./quakelive_steam_mapping_round_02.md) and
  [Round 03](./quakelive_steam_mapping_round_03.md)

## Retail evidence recap

Round 03 already bounded the small Steam client auth helpers:

- `sub_4605c0` -> `SteamClient_GetAuthSessionTicket`
- `sub_4605f0` -> `SteamClient_CancelAuthTicket`

The key retail observation from that pass was stable:

- `SteamClient_CancelAuthTicket` cancels the cached auth-ticket handle in
  `data_e2c208`
- the common disconnect/error path calls that helper before the browser-facing
  `game.end` publish

The writable source base still had only half of that lifetime:

- [platform_steamworks.c](../../src/common/platform/platform_steamworks.c)
  already reconstructed `GetAuthSessionTicket`
- [ql_auth.c](../../src/code/client/ql_auth.c) requested Steam tickets for the
  auth dispatcher, but it passed `NULL` for the out-handle slot and discarded
  the retail lifetime owner completely
- [cl_main.c](../../src/code/client/cl_main.c) had no retained disconnect owner
  for the client Steam ticket at all

## Source reconstruction

This round restores that lifetime end-to-end in writable source:

- [platform_steamworks.h](../../src/common/platform/platform_steamworks.h) and
  [platform_steamworks.c](../../src/common/platform/platform_steamworks.c) now
  expose `QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle )`
- [ql_auth.c](../../src/code/client/ql_auth.c) now retains the most recent
  client Steam auth-ticket handle through a dedicated
  `cl_clientAuthSteamTicketHandle` owner instead of throwing the handle away
- [ql_auth.c](../../src/code/client/ql_auth.c) now exposes
  `QL_ClientAuth_CancelSteamTicket()` so the client host has a single retained
  teardown point for disconnect and error cleanup
- [cl_main.c](../../src/code/client/cl_main.c) now calls that teardown owner
  from `CL_Disconnect`

This stays deliberately scoped to the evidence-backed client lifetime seam. It
does **not** invent extra auth bookkeeping beyond the single retained ticket
handle that retail clearly owns.

## Practical result

After this round:

- the Steam auth-ticket request path no longer discards the issued handle
- disconnect and error cleanup now tear down the retained client Steam ticket
  instead of leaving the retail `CancelAuthTicket` lifetime owner absent
- the platform layer now exposes the same small ticket-cancel wrapper family as
  the already reconstructed ticket-request wrapper

The adjacent unresolved piece in the original retail note remains the
browser-side `game.end` event publication itself. This pass only restores the
client Steam lifetime owner that occurs immediately before it.

## Verification

I added:

- static parity assertions in
  [tests/test_platform_services.py](../../tests/test_platform_services.py)
- harness coverage for the cancel wrapper in
  [tests/steamworks_harness.c](../../tests/steamworks_harness.c) and
  [tests/test_steamworks_harness.py](../../tests/test_steamworks_harness.py)

Validation command:

- `python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q`

Result:

- `89 passed`

## Completion stats after Round 93

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `944` raw alias entries, `943` address-backed
  aliases
- Address-backed coverage: `17.230%` of `5473` functions
- Alias delta this round: `0`; this pass consumed already-mapped ownership as
  source reconstruction
- Estimated parity for this round: `93% -> 94%`
