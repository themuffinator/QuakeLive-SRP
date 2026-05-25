# Quake Live Steam Mapping Round 306

Scope: chat-area input, `messagemode` / `messagemode2`, console-originated
`say`, and qagame `say` / team/tell chat formatting.

## Evidence Walk

- Engine owner: `quakelive_steam.exe`.
  - `0x004B3550` opens public chat: clears the chat field, sets
    `chat_playerNum = -1`, clears reply/team latches, selects width `73` or the
    cgame chat-width export, toggles `KEYCATCH_MESSAGE`, and calls the cgame
    chat-down export.
  - `0x004B35C0` opens team chat with the same setup, sets the team latch, and
    subtracts five visible columns from the cgame/fallback width.
  - `0x004B79B0` owns message submission. Escape clears the catcher and field
    before chat-up. Enter formats `reply`, `tell`, `say_team`, or `say`, then
    calls chat-up before clearing the catcher and field.
  - `0x004B7660` owns console-line entry. With `cl_allowConsoleChat = 0`, bare
    text is prefixed into a command; with it enabled, bare text emits `cmd say`.
- Game owner: `qagamex86.dll`.
  - `0x10041450` is the retail-only chat token expander carried in the symbol
    map as `G_ExpandChatTokens`. It copies spectator text verbatim, but for
    live players expands `##`, `#a`, `#h`, and `#w` in team/tell chat.
  - `0x10041760` is `G_Say`. It emits the retail truncation diagnostic when
    input exceeds `MAX_SAY_TEXT`, runs the token expander for team/tell modes,
    then applies the non-team `say_team` downgrade, logs `say:` / `sayteam:`
    / `tell:` flows, and sends `chat` or `tchat` payloads through `G_SayTo`.

## Source Reconstruction

- `src/code/client/cl_keys.c`
  - Reordered the Enter branch in `Message_Key` so the cgame `CG_CHAT_UP`
    callback fires before the message catcher is cleared, matching the retail
    HLIL ordering at `0x004B7ACF -> 0x004B7AE0`.
- `src/code/game/g_cmds.c`
  - Added `G_ExpandChatTokens` plus bounded append helpers.
  - Reconstructed Quake Live team/tell token expansion:
    - `##` -> literal `#`
    - `#a` -> current armor
    - `#h` -> current health, clamped to `0` below one
    - `#w` -> current weapon name, with ammo count for non-gauntlet weapons
  - Preserved the retail expansion-before-downgrade ordering by keeping the
    original chat mode separate from the delivery mode.
  - Added the retail `G_Say: truncate at %d characters` diagnostic before the
    bounded say-buffer copy.

## Verification Added

- `tests/test_cl_console_cgame_parity.py`
  - Asserts the retail Enter-path chat-up, catcher-clear, field-clear order.
- `tests/test_game_helper_seam_parity.py`
  - Asserts source coverage for `G_ExpandChatTokens`, the `#` token cases,
    weapon/ammo formatting, overflow diagnostic, and the symbol/HLIL evidence
    anchors for `G_ExpandChatTokens` and `G_Say`.

## Open Edges

- The current source still preserves repository-specific muted-chat policy in
  `G_SayTo`/`G_Say`. This round did not attempt to replace that policy because
  the existing `g_allTalk` and `g_teamSpecSayEnable` tests document it as an
  intentional reconstruction layer.
