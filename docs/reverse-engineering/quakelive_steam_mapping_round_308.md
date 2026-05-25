# Quake Live Steam Mapping Round 308

Scope: second-pass chat-area and chat-command wiring, covering qagame
`botSay` / `bchat`, direct `mute` / `unmute`, cgame chat-area server commands,
and engine/server-originated say paths.

## Evidence Walk

- qagame owner: `qagamex86.dll`.
  - `0x10045DD0` (`ClientCommand`) checks `say`, `say_team`, `tell`,
    `botSay`, then voice-chat commands in that order. The `botSay` branch at
    `0x10045EBD -> 0x10045EC8` tailcalls `0x10041CC0`.
  - `0x10041CC0` validates that the sender is a bot, parses argv 1 as the
    target client, argv 2 as a non-negative hold duration, concatenates argv
    3+, logs `botSay: %s for %i seconds to client %i`, and sends the timed
    `bchat "%s%c%c%s" %i` server command to the target.
  - `0x100627C0` / `0x10062890` are direct `mute` / `unmute` handlers. They
    share the retail direct-command target resolver, reject same-or-higher
    privilege targets, flip `client->sess.muted`, and broadcast the exact
    `%s has been muted` / `%s has been unmuted` print payload.
  - The direct command table strings around `0x1008081C` and `0x10080830`
    describe `mute <playerid>` and `unmute <playerid>` as moderator chat
    controls, matching the UI/cgame forwarded command surface.
- cgame owner: `cgamex86.dll`.
  - Existing source already tracks the recovered chat stack: `bchat` routes to
    `CG_ParseBufferedChat`, `clearChat` calls `CG_InitTeamChat`, `chat` honors
    client mute state, and `tchat` pushes through the team-chat writer.
  - `CG_KeyEvent` continues to match the retail overlay intercept for
    `messagemode`, screenshot commands, `+voice`, and `+scores`.
- engine/server owner: `quakelive_steam.exe`.
  - `0x004DEEA0` matches `SV_ConSay_f`: operator `say` strips a wrapping quote
    and sends `chat %d "Server: %s\n"` with the server pseudo-client slot.
  - `0x004B3550`, `0x004B35C0`, `0x004B79B0`, and `0x004B7660` remain the
    engine-side `messagemode`, `messagemode2`, message submit, and console
    bare-text chat anchors from round 306.

## Source Reconstruction

- `src/code/game/g_cmds.c`
  - Added `Cmd_BotSay_f` and wired `ClientCommand` so `botSay` is dispatched
    between `tell` and `vsay`, matching the retail ladder.
  - Reconstructed the retail timed bot-chat payload:
    `botName^7^2message` is emitted as `bchat` with the server-supplied hold
    time, allowing cgame's recovered timed chat stack to render it.
  - Tightened direct `Cmd_Mute_f` / `Cmd_Unmute_f` toward the retail direct
    command behavior by rejecting targets at or above the caller privilege and
    broadcasting the exact all-client status prints.
- `src/code/cgame/cg_main.c`
  - Preserved the scoreboard/team-list social fallback as an explicit
    `row->socialHandle` branch so the recovered identity mute icon path stays
    aligned with the retail-shaped feeder evidence.

## Verification Added

- `tests/test_game_helper_seam_parity.py`
  - Locks the `botSay` command order, bot-only guard, argv target/duration
    parsing, `ConcatArgs(3)`, retail log string, and `bchat` payload.
  - Locks the direct mute/unmute privilege gate, session muted flag flips,
    retail all-client print strings, and the HLIL/symbol-map anchors for
    `0x100627C0` / `0x10062890`.

## Open Edges

- The broader retail direct-command table and help printer are still only
  partially represented in source by the existing `ClientCommand` ladder.
- `G_Say` still keeps this repository's documented muted-chat suppression
  behavior instead of fully adopting retail's `(muted)` per-recipient masking.
