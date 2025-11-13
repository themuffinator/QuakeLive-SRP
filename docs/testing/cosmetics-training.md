# Cosmetic and Training Override QA

Quake Live's cosmetic helpers extend Quake III with training timers, forced HUD
broadcasts, and scripted scoreboard hints. The new regression fixtures under
`src/game/tests/` capture the server-side vote and configstring behaviour, while
this checklist documents the client observations that still require manual
validation until the HUD harness can drive scripted views.【F:docs/gameplay/cvars.md†L47-L75】【F:src/game/tests/cosmetics_fixtures.c†L94-L176】

## Recommended setup

1. Launch a dedicated server with the cosmetics fixtures compiled in so
   `GT_RunCosmeticTrainingFixtures()` and `GT_RunAllRulesFixtures()` remain
   callable during smoke tests.【F:src/game/tests/cosmetics_fixtures.c†L312-L343】【F:src/game/tests/rules_entry.c†L1-L24】
2. Connect with a stock Quake Live client build so HUD scripts match the retail
   expectations outlined in the cosmetics CVar documentation.【F:docs/gameplay/cvars.md†L47-L75】
3. Enable cheats (`/devmap` or `sv_cheats 1`) to accelerate vote and command
   replay while iterating on HUD reactions.

## Manual validation scenarios

### Item timer vote flow

1. Set `g_training 1` and issue `\callvote itemtimers off`. Confirm the vote
   is rejected with *Voting is not allowed in training.* on both the server
   console and the client chat log.【F:src/game/tests/cosmetics_fixtures.c†L99-L133】
2. Clear training, enable warmup-only mode (`g_warmup 1`, `g_allowVoteMidGame 0`),
   and start a match. Attempt `\callvote itemtimers off` during live play and
   expect *Voting to alter the item timers is only allowed during the warm up
   period.* before the vote is denied.【F:src/game/tests/cosmetics_fixtures.c†L135-L163】
3. Repeat the vote with `\callvote itemtimers on/off` during warmup and verify
   the timers toggle, with the HUD training widgets appearing and disappearing in
   sync with the accepted vote result.【F:docs/gameplay/cvars.md†L47-L64】

### Training command gate

1. Run the scripted training sequence (or set `g_training 1` manually) and issue
   `\addbot visor`. The server should refuse the command with *Addbot not
   allowed during training.* echoed to connected clients.【F:src/game/tests/cosmetics_fixtures.c†L200-L228】
2. Clear `g_training`, retry the command, and confirm bots spawn normally. Note
   the transition point so automated HUD tests can assert when the block lifts.

### Forced configstring broadcast

1. Toggle each force flag (`g_forceSmallScoreboardMessage 1`,
   `g_forceSendConfigstring 1`, `set g_forceAtmosphericEffects rain`,
   `g_forceDmgThroughSurface 1`) and observe the scoreboard tipline and HUD
   flashes that accompany configstring `0x2B3` broadcasts.【F:docs/gameplay/cvars.md†L47-L75】
2. Inspect the server console for `Server: <cvar> changed to <value>` messages
   and confirm `CS_SYSTEMINFO` or HUD payloads refresh without requiring a
   reconnect.【F:src/game/tests/cosmetics_fixtures.c†L230-L268】
3. Reset the flags and ensure the HUD returns to player-selected settings once
   the forced values clear, noting any manual refreshes needed so future client
   automation can replicate them.

## Follow-up automation

- Extend the client regression harness with a scripted scoreboard capture that
  checks for the forced small scoreboard message and HUD timer widgets after the
  relevant configstrings are resent.【F:tools/tests/client_regression/__init__.py†L1-L25】
- Add snapshot archives that cover the training tutorial so the harness can
  assert when command gating lifts and when HUD timers appear or disappear.
- Record the manual observations in the parity ledger once automated coverage is
  landed to keep the documentation map current.【F:docs/gameplay/parity/parity-ledger.md†L27-L36】
