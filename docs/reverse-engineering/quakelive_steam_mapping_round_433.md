# Quake Live Steam Mapping Round 433

Date: 2026-06-08

## Scope

This round reconstructs the Steam auth-ticket cleanup edge in the common error
path. The focus is `Com_Error` runtime teardown, not normal quit shutdown.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4605f0` to
  `SteamClient_CancelAuthTicket`.
- Binary Ninja HLIL for `sub_4605f0` calls `SteamUser()` and, when present,
  dispatches vtable slot `0x40` with the retained ticket handle.
- Binary Ninja HLIL for retail `Com_Error` at `0x004c9b60` stores
  `com_errorMessage`, writes the error-log ring, then calls `sub_4605f0()` at
  `0x004c9d1d` before branching on the error code.
- The source already routes disconnect and explicit ticket cancellation through
  `SteamClient_CancelAuthTicket`, but the common error path did not own the
  retail pre-branch cleanup point.

## Source Reconstruction

- Added `SteamClient_CancelAuthTicket()` to `Com_Error` immediately after
  `Cvar_Set("com_errorMessage", com_errorMessage)`.
- Kept existing disconnect, shutdown-callback, and quit-path cancellation
  owners intact; this new call is idempotent because the retained ticket handle
  is cleared by `SteamClient_CancelAuthTicket`.
- Added parity assertions that bind the source placement to the HLIL
  `004c9d1d sub_4605f0()` evidence and require the call before
  `ERR_SERVERDISCONNECT`, `ERR_DROP`, `ERR_DISCONNECT`, `ERR_NEED_CD`, and
  fatal handling diverge.

## Deferred Notes

- Retail writes the circular error log before the cancel call. The source error
  path still uses the existing qconsole/profile logging pipeline, so this round
  reconstructs the Steam cleanup placement relative to `com_errorMessage` and
  branch selection rather than the full retail error-log writer.

## Parity

Focused Steam auth-ticket error-cleanup confidence moves from 78% to 92%.
The broader Steam launch/runtime integration slice moves from 85% to 86%.
