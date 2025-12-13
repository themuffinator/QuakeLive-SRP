# Match state and readiness configstring audit

## HLIL coverage
- Quake Live's qagame updates configstring `0x295` (CS_MATCH_STATE) with the round time, number, turn, state, and assorted per-team flags during round transitions. The HLIL shows `trap_SetConfigstring(0x295, "\time\%d\round\%d\turn\%d\state\…")` when moving into a new match state, immediately after resetting per-client timers and toggling the round controller state machine.【51aeaf†L19-L31】【e52fe0†L9-L18】
- While entering overtime/sudden-death branches the server also sends configstring `0x296` (CS_SUDDENDEATH_STATUS) with a payload derived from `data_1007dd18`, and follows with a state `\turn\%d\state\2` update on CS_MATCH_STATE.【3020db†L1-L9】
- Additional lifecycle hooks broadcast `0x297` and `0x298` with the same placeholder payload (`sub_10070cb0(&data_1007dd18)`) when ready-up/timeout bookkeeping transitions occur, suggesting clients expect separate readiness snapshots alongside the match-state string.【52a1b7†L10-L16】
- The cgame configstring dispatcher has dedicated cases for `0x295`–`0x298` and `0x2c4`, calling parsing helpers instead of treating them as generic strings. Case `0x295` feeds `sub_10048c80` (multiple `atoi` pulls), `0x296`/`0x297`/`0x298` each read an integer into distinct client globals, and `0x2c4` ingests another integer deadline used by the ready-up UI.【16a56b†L9-L36】

## Current server assembly vs HLIL
- `G_UpdateMatchStateConfigString` currently assembles `CS_MATCH_STATE` with all timeout, overtime, turn/state, respawn, shuffle, and factory fields that mirror the HLIL match-state payload keys (`time`, `round`, `turn`, `state`, `ot*`, `to*`, `team*`, `resp*`, `shuffle*`, `sd*`).【cdfa05†L52-L136】【b0fd33†L1-L32】
- The server publishes the ready-up deadline through `G_UpdateReadyUpConfigstring`, but the configstring ID used is `CS_READYUP_STATUS` (0x2C4) instead of a distinct HLIL slot in the 0x297/0x298 range. The timeout pause handler also rebroadcasts this deadline when warmup time is adjusted.【5c0be4†L2820-L2833】
- Warmup readiness snapshots are emitted from the server side via `SV_CheckWarmupReadiness`, which encodes `pct`, `ready`, and `eligible` into `CS_WARMUP_READY`.【c818ff†L730-L754】
- No server code currently sets `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS` beyond the warmup deadline, or the 0x297/0x298 configstrings seen in HLIL, leaving several HLIL-observed lifecycle updates unrepresented.【bddfe1†L117-L154】

## Client parsing vs HLIL
- The client’s `CG_ParseMatchState` fully consumes every key emitted by `G_UpdateMatchStateConfigString`, including overtime, timeout, respawn, shuffle, and factory sudden-death fields, so the CS_MATCH_STATE payload aligns with HLIL expectations.【928330†L975-L1055】
- There is no client handler for `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS` (0x2C4), or `CS_WARMUP_READY` despite HLIL showing configstring dispatch cases for 0x295–0x298 and 0x2C4. HUD readiness timers and sudden-death toggles therefore miss updates that the retail client parsed via those configstrings.【16a56b†L9-L36】【bddfe1†L117-L154】

## Gaps and proposed adjustments
- Reintroduce the missing configstring publishers on the server: emit `CS_SUDDENDEATH_STATUS` alongside `CS_MATCH_STATE` during overtime entry/exit, and add discrete readiness configstrings matching the HLIL slots (0x297/0x298) so clients can mirror the retail ready-up sequencing.【3020db†L1-L9】【52a1b7†L10-L16】
- Wire up cgame parsing for `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY`, updating HUD timers and sudden-death flags the same way HLIL’s configstring switch fed dedicated consumer routines. This would let the ready-check UI and overtime indicators track server state without relying solely on the `CS_MATCH_STATE` payload.【16a56b†L9-L36】【c818ff†L730-L754】
- Align the timing of `trap_SetConfigstring` calls with the HLIL sequence by firing ready/sudden-death configstrings during the same round transitions that already call `G_UpdateMatchStateConfigString`, ensuring clients receive synchronized snapshots for both match flow and readiness gating.【51aeaf†L19-L31】【e52fe0†L9-L18】
