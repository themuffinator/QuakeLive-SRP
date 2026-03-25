# Cgame Mapping Ledger

This ledger records the current reverse-engineered mapping pass for the retail
`cgamex86.dll` against `src/code/cgame/`. All claims below were checked against
the committed Ghidra corpus in `references/reverse-engineering/ghidra/cgamex86/`
and the Binary Ninja HLIL dump in `references/hlil/quakelive/cgamex86.dll/`.

Observed facts come from exports, function inventories, strings, and call flow.
Inferred names are only used where the retail behavior and the Quake Live source
analogue line up cleanly enough to support a stable mapping.

## Recovered Function Map

| Retail address | Recovered name | Closest source analogue | Evidence summary | Confidence |
| --- | --- | --- | --- | --- |
| `0x10020A70` | `dllEntry` | `cg_syscalls.c::dllEntry` | Named export in HLIL and Ghidra; installs the syscall table. | High |
| `0x10020A90` | `Com_Printf` | `cg_main.c::Com_Printf` | Varargs print wrapper wired into the retail `cgDC.Print` slot; HLIL forwards directly to `trap_Print`, which matches the narrower `Com_Printf` role better than source `CG_Printf` with its extra `cg_chatbeep` side path. | High |
| `0x10020AF0` | `Com_Error` | `cg_main.c::Com_Error` | Varargs error wrapper used across retail `cgame`, frequently called with Quake error levels, and assigned into `cgDC.Error` as the HUD/menu error callback. | High |
| `0x10020BB0` | `CG_RegisterCvars` | `cg_main.c::CG_RegisterCvars` | Iterates the retail cvar table, registers `model`, `headmodel`, and `cg_version`, then clears `ui_voteactive`; also appears as slot 1 in the native `cgame` entry table. | High |
| `0x10020CA0` | `CG_UpdateCvars` | `cg_main.c::CG_UpdateCvars` | Walks the retail cvar table with `trap_Cvar_Update`, checks tracked values, and triggers the refresh path used before `CG_DrawActiveFrame` continues. | High |
| `0x10020D60` | `CG_CrosshairPlayer` | `cg_main.c::CG_CrosshairPlayer` | Tiny native API-table helper returning the crosshair client index while the one-second timeout is still live. | High |
| `0x10020D80` | `CG_LastAttacker` | `cg_main.c::CG_LastAttacker` | Tiny native API-table helper returning the attacker persistent field while `cg.attackerTime` is active, otherwise `-1`. | High |
| `0x10007F00` | `CG_ConsoleCommand` | `cg_consolecmds.c::CG_ConsoleCommand` | Reads `Argv(0)`, scans the static console-command table, dispatches the matching handler, and returns `qtrue` or `qfalse`; HLIL also shows it exposed through the native entry table. | High |
| `0x10029820` | `CG_Init` | `cg_main.c::CG_Init` | HLIL-only function boundary with the retail startup sequence: version mismatch check, loading strings for `collision map`, `sounds`, `graphics`, `clients`, then the expected init calls, including the late `AdvertisementBridge_InitCGame` host import before the final looping-sound clear. Not present in committed `functions.csv`. | High |
| `0x10029FC0` | `CG_Shutdown` | `cg_main.c::CG_Shutdown` | Native entry-table slot that performs the retail teardown path, issues the shutdown-side advertisement-bridge syscall, and restores `ui_mainmenu` before returning. | High |
| `0x1003C6F0` | `CG_KeyEvent` | `cg_newdraw.c::CG_KeyEvent` | Two-argument input handler in the native entry table; HLIL fetches the bound command string and directly intercepts `messagemode`, `screenshot`, `screenshotJPEG`, `+voice`, and `+scores`, which is the retail key-input path for the spectator/HUD overlay. | High |
| `0x10020E70` | `CG_RegisterSounds` | `cg_main.c::CG_RegisterSounds` | Called from `CG_Init` after the retail loading string switches to `sounds`; body registers announcer, feedback, and weapon sounds. | High |
| `0x10022F40` | `CG_RegisterGraphics` | `cg_main.c::CG_RegisterGraphics` | Called from `CG_Init` after the retail loading string switches to `graphics`; body registers game media, shaders, and models. | High |
| `0x10025260` | `CG_RegisterClients` | `cg_main.c::CG_RegisterClients` | Called from `CG_Init` after the retail loading string switches to `clients`; loops player configstrings and registers client info. | High |
| `0x100252F0` | `CG_ConfigString` | `cg_main.c::CG_ConfigString` | Small bounds-checked accessor returning `gameState` string data. | High |
| `0x10025320` | `CG_StartMusic` | `cg_main.c::CG_StartMusic` | Reads the music configstring, parses two tokens, and starts the background track pair. | High |
| `0x10025CA0` | `CG_LoadMenus` | `cg_main.c::CG_LoadMenus` | Uses the menu-file fallback path, `ui/hud.txt`, size guards, `Menu_Reset`, `loadmenu`, and the UI menu load-time print. | High |
| `0x10029120` | `CG_LoadHudMenu` | `cg_main.c::CG_LoadHudMenu` | Reads `cg_hudFiles`, falls back to `ui/hud.txt`, calls `CG_LoadMenus`, and performs the loading half of the HUD bootstrap. | High |
| `0x10029210` | `CG_InitDisplayContext` | `synthetic retail cgDC bootstrap helper` | Deliberate synthetic retail name for the split HUD-display bootstrap. The committed Ghidra boundary and HLIL body both match the source-side `cgDC` callback assignment block from `CG_LoadHudMenu`, and the helper finishes by publishing `&cgDC` through the `ui_shared.c::Init_Display` context pointer. | High |
| `0x10029420` | `CG_AssetCache` | `cg_main.c::CG_AssetCache` | Registers gradient bar, scrollbar, and slider assets used by the HUD/menu path. | High |
| `0x10019EB0` | `CG_EntityEvent` | `cg_event.c::CG_EntityEvent` | Large event switch with obituary, item, footstep, and unknown-event handling. | High |
| `0x100446E0` | `CG_PredictPlayerState` | `cg_predict.c::CG_PredictPlayerState` | Prediction error, dropped-event, and double-event strings match the prediction loop and transition logic. | High |
| `0x10049980` | `CG_ConfigStringModified` | `cg_servercmds.c::CG_ConfigStringModified` | Reads `Argv(1)`, parses the changed configstring index, and switches over update handlers. This is not the plain `CG_ConfigString` accessor. | High |
| `0x1004A2E0` | `CG_MapRestart` | `cg_servercmds.c::CG_MapRestart` | Matches the map-restart reset path and the `CG_MapRestart` debug print. | High |
| `0x1004ADC0` | `CG_ServerCommand` | `cg_servercmds.c::CG_ServerCommand` | Main server-command dispatcher with `map_restart`, `clientLevelShot`, vote UI toggles, race commands, and the unknown-command print. | High |
| `0x1004C020` | `CG_TransitionSnapshot` | `cg_snapshot.c::CG_TransitionSnapshot` | Snapshot handoff with `NULL cg.snap` and `NULL cg.nextSnap` fatal paths. | High |
| `0x1004C4D0` | `CG_ProcessSnapshots` | `cg_snapshot.c::CG_ProcessSnapshots` | Snapshot pump with `latestSnapshotNum`, server-time ordering checks, and the handoff into `CG_TransitionSnapshot`. | High |
| `0x1004E4D0` | `CG_GetPhysicsTime` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the one-word time getter. The host uses slot `data_146cc38 + 0x38` when formatting `[m:ss.mmm]` notify/chat prefixes, falling back to host `serverTime`; the retail body itself returns `cg.physicsTime`. | High |
| `0x1004E4E0` | `CG_DrawActiveFrame` | `cg_view.c::CG_DrawActiveFrame` | Top-level frame loop that updates cvars, clears scene state, calls `CG_ProcessSnapshots`, runs prediction, and builds the view. | High |

## Additional Recoveries This Round

| Retail address | Recovered name | Closest source analogue | Evidence summary | Confidence |
| --- | --- | --- | --- | --- |
| `0x100068E0` | `CG_InitTeamChat` | `cg_newdraw.c::CG_InitTeamChat` | Retail buffered-chat reset helper used during `CG_Init` and again by the `clearChat` server command; closest source analogue is `CG_InitTeamChat`, but retail clears a timed chat ring instead of three flat strings. | High |
| `0x10006910` | `CG_PushPrintString` | `synthetic retail buffered chat helper` | Deliberate synthetic name for the timed print/chat writer: HLIL measures the incoming line, rotates the live entry into the 24-slot history ring when needed, timestamps the active slot, trims a trailing newline, and copies the text into the live buffered-chat record. | High |
| `0x10006A10` | `CG_DrawNewChatArea` | `cg_newdraw.c::CG_DrawNewChatArea` | Retail timed chat-stack renderer reached from ownerdraw case `CG_AREA_NEW_CHAT`; HLIL only exposes the scale float directly because the ownerdraw call frame carries the rect/color context. | High |
| `0x10007BC0` | `CG_StartOrbit_f` | `cg_consolecmds.c::CG_StartOrbit_f` | Exact command-table match for `startOrbit`; HLIL reads `developer` and toggles `cg_cameraOrbit`, `cg_thirdPerson`, `cg_thirdPersonAngle`, and `cg_thirdPersonRange` exactly like the public-source handler. | High |
| `0x10007CD0` | `CG_ChatDown_f` | `retail-only console command handler` | Command-table string `+chat` points here; the body simply raises the chat-history latch consumed by the buffered chat ownerdraw path. | High |
| `0x10007CF0` | `CG_ChatUp_f` | `retail-only console command handler` | Command-table string `-chat` points here; the body clears the same chat-history latch used by `CG_ChatDown_f`. | High |
| `0x10007D10` | `CG_ToggleChatHistory_f` | `retail-only console command handler` | Command-table string `togglechathistory` points here; the body flips the same chat-history latch used by `+chat` and `-chat`. | High |
| `0x10007D30` | `CG_Print_f` | `cg_newdraw.c::CG_SetPrintString` | Command-table string `print` points here; HLIL joins `Argv(1..)` into one line and forwards it to the retail buffered print/chat writer at `0x10006910`. | High |
| `0x10007E90` | `CG_ClientMute_f` | `retail-only console command handler` | Command-table string `clientmute` points here; HLIL parses a client slot, reads two identity words from the per-client block, and forwards them through a private native mute/social import. | High |
| `0x10007F80` | `CG_InitConsoleCommands` | `cg_consolecmds.c::CG_InitConsoleCommands` | Walks the same console-command table as `CG_ConsoleCommand` and registers each name through `trap_AddCommand` during `CG_Init`. | High |
| `0x100122B0` | `CG_AdjustFrom640` | `cg_drawtools.c::CG_AdjustFrom640` | HLIL shows the shared 640-space scaler that every adjacent retail rect/pic helper calls. The retail body null-guards each coordinate pointer, scales Y/H by the cached 480-space factor, and only takes the default centered widescreen path while `Key_GetCatcher()` reports `KEYCATCH_CGAME`, with explicit left/center/right overrides coming from the local mode setter. | High |
| `0x100123C0` | `CG_SetAdjustFrom640Mode` | `cg_drawtools.c::CG_SetAdjustFrom640Mode` | Tiny local setter for the shared widescreen translation mode consumed by `CG_AdjustFrom640`; retail HUD menu paint paths feed it from `itemDef_t.widescreen` / `menuDef_t.widescreen` before restoring the parent mode. | High |
| `0x100123D0` | `CG_FillRect` | `cg_drawtools.c::CG_FillRect` | Small wrapper around `CG_AdjustFrom640`: sets the draw color, scales the rect, draws the white shader with zeroed UVs, and clears the color state. | High |
| `0x10012460` | `CG_DrawSides` | `cg_drawtools.c::CG_DrawSides` | Uses `CG_AdjustFrom640`, multiplies the border thickness by the horizontal scale, and draws the left/right white-shader strips. | High |
| `0x10012540` | `CG_DrawTopBottom` | `cg_drawtools.c::CG_DrawTopBottom` | Uses `CG_AdjustFrom640`, multiplies the border thickness by the vertical scale, and draws the top/bottom white-shader strips. | High |
| `0x10012620` | `CG_DrawRect` | `cg_drawtools.c::CG_DrawRect` | Sets the color, calls the recovered `CG_DrawTopBottom` and `CG_DrawSides` pair, then restores the default color state. | High |
| `0x100126A0` | `CG_DrawPic` | `cg_drawtools.c::CG_DrawPic` | Calls `CG_AdjustFrom640` and forwards the scaled quad to the renderer with full-image UVs, matching the source-side `CG_DrawPic` helper. | High |
| `0x10018E60` | `CG_PlaceString` | `cg_event.c::CG_PlaceString` | Retail rank/place formatter used by obituary and scoreboard text; HLIL preserves the tied-rank mask handling plus the ordinal-suffix selection from the source helper even though the recovered calling convention carries extra register noise. | High |
| `0x10019130` | `CG_Obituary` | `cg_event.c::CG_Obituary` | Large obituary helper anchored by `CG_Obituary: target out of range`, the local `You fragged %s.` / `You thawed %s.` strings, the frozen/thawed obituary verbs, and the delayed follow-killer side effect. | High |
| `0x10019AF0` | `CG_UseItem` | `cg_event.c::CG_UseItem` | Retail use-item event helper with the invalid-item guard, local `No item to use` / `Use %s` centerprints, medkit timestamp update, and the expected holdable-use sound dispatch. | High |
| `0x10019CA0` | `CG_PainEvent` | `cg_event.c::CG_PainEvent` | Reached from `EV_PAIN`; HLIL shows the same 500 ms debounce, painTime update, painDirection toggle, and player pain-sound dispatch as the source helper. | High |
| `0x10019D20` | `CG_TryAutoFollowPowerup` | `synthetic retail spectator auto-follow helper` | Deliberate synthetic retail name. The only HLIL callsites are the global powerup-pickup path plus `GTS_RED_TAKEN` / `GTS_BLUE_TAKEN`; the helper then applies spectator/follow-mode gates and emits `follow %d%s`, using the `" pw"` suffix only on the direct powerup-pickup path. | High |
| `0x100208F0` | `CG_MouseEvent` | `cg_newdraw.c::CG_MouseEvent` | Native export slot at `data_100769C8`; the raw wrapper copies the live cursor globals into the retail `cgDC` cursor fields and then tail-jumps into the shared HUD mouse path, matching the source `CG_MOUSE_EVENT` vmMain case. | High |
| `0x10020910` | `CG_CopyClientIdentity` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the client-identity marshaller: it validates the client slot, copies the sidecar words at `0x10A42400` / `0x10A42418` / `0x10A4241C`, and copies two `0x27`-byte identity strings into the caller buffer. | High |
| `0x100209E0` | `CG_GetChatFieldY` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the 640-space chat-line Y selector. The host chat-input draw path at `0x004B4100` calls slot `data_146cc38 + 0x44` before its `SCR_AdjustFrom640`-style scaler, and the retail body returns `413` or `455` depending on `data_10a9c214`. | High |
| `0x10020A00` | `CG_GetChatFieldPixelWidth` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the 640-space chat-line width selector. The same host draw path calls slot `data_146cc38 + 0x48`, and the retail body returns `640` or `300`, matching the full-width versus compact native chat-overlay families. | High |
| `0x10020A20` | `CG_GetChatFieldWidthInChars` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the chat `field_t.widthInChars` selector. Host `say` / `say_team` openers store slot `data_146cc38 + 0x4C` directly into `data_1648C88`, the `widthInChars` member of the live `field_t` at `data_1648C80`; the fallback values are `73` and `68`, while retail returns `73` or `30` depending on `data_10a9c214`. | High |
| `0x10020A40` | `CG_SetClientSpeakingState` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the speaking-state setter: it writes the per-client speaking flag at `0x10A4240C`, timestamps `0x10A42410` with `cg.time`, and returns the client block pointer for chaining. | High |
| `0x10029FF0` | `CG_Show1stTrackedPlayer` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the first tracked-slot notifier: HLIL arms a 3000 ms timer later consumed by `CG_SHOW_IF_1ST_PLYR_TRACKED`, reloads `cg_lastmsg`, and replays that text through `CG_PushPrintString`. | High |
| `0x1002A060` | `CG_Show2ndTrackedPlayer` | `synthetic retail native export helper` | Deliberate synthetic native-export name for the second tracked-slot notifier: HLIL arms a 3000 ms timer later consumed by `CG_SHOW_IF_2ND_PLYR_TRACKED`, reloads `cg_lastmsg`, and replays that text through `CG_PushPrintString`. | High |
| `0x10025E60` | `CG_OwnerDrawHandleKey` | `cg_main.c::CG_OwnerDrawHandleKey` | Assigned into `cgDC.ownerDrawHandleKey`; the retail body is a pure `qfalse` stub, which cleanly matches the source analogue. | High |
| `0x10025E70` | `CG_FeederCount` | `cg_main.c::CG_FeederCount` | Assigned into `cgDC.feederCount`; HLIL counts the same scoreboard and team-list feeder families keyed by ids such as `5f`, `17f`, and `18f`. | High |
| `0x10028830` | `CG_FeederItemImage` | `cg_main.c::CG_FeederItemImage` | Assigned into `cgDC.feederItemImage`; the retail body dispatches across scoreboard/team feeder variants and is richer than the older public-source stub that simply returned `0`. | High |
| `0x10028B10` | `CG_FeederItemText` | `cg_main.c::CG_FeederItemText` | Assigned into `cgDC.feederItemText`; formats retail scoreboard/team-list text columns including names, scores, ping, ready, and spectator state. | High |
| `0x10028C30` | `CG_Cvar_Get` | `cg_main.c::CG_Cvar_Get` | Assigned into `cgDC.getCVarValue`; reads the current cvar string, runs `atof`, and falls back to `trap_Cvar_VariableStringBuffer` when the retail token helper is empty. | High |
| `0x10028CE0` | `CG_Cvar_GetString` | `synthetic retail cgDC adapter name` | Assigned into `cgDC.getCVarString`; HLIL first checks the native token helper used by the retail client and otherwise falls back to `trap_Cvar_VariableStringBuffer`, so the role is stable even though the exact public-source symbol does not exist. | High |
| `0x10028D30` | `CG_Text_PaintWithCursor` | `cg_main.c::CG_Text_PaintWithCursor` | Assigned into `cgDC.drawTextWithCursor`; thin wrapper around the shared text painter using the cursor-aware HUD callback signature. | High |
| `0x10028D80` | `CG_OwnerDrawWidth` | `cg_main.c::CG_OwnerDrawWidth` | Assigned into `cgDC.ownerDrawWidth`; computes the text widths for retail ownerdraw labels including `Unknown Gametype` and `Fragged by %s`. | High |
| `0x10028E80` | `CG_PlayCinematic` | `cg_main.c::CG_PlayCinematic` | Assigned into `cgDC.playCinematic`; wraps `trap_CIN_PlayCinematic` with integer extents and the retail looping mode. | High |
| `0x10028EC0` | `CG_StopCinematic` | `cg_main.c::CG_StopCinematic` | Assigned into `cgDC.stopCinematic`; HLIL tail-jumps directly into the stop-cinematic syscall slot. | High |
| `0x10028ED0` | `CG_DrawCinematic` | `cg_main.c::CG_DrawCinematic` | Direct slot assignment at `data_10a256E0`; the HLIL-only wrapper converts float extents, calls `trap_CIN_SetExtents`, and then calls `trap_CIN_DrawCinematic`, which is enough to recover the retail draw-cinematic callback despite the split boundary. | High |
| `0x10028F20` | `CG_RunCinematicFrame` | `cg_main.c::CG_RunCinematicFrame` | Assigned into `cgDC.runCinematicFrame`; HLIL tail-jumps directly into the run-cinematic syscall slot. | High |
| `0x10030C00` | `CG_DrawLevelTimer` | `cg_newdraw.c::CG_DrawLevelTimer` | Retail `CG_LEVELTIMER` ownerdraw that formats the live clock as `%i:%i%i` and then routes it through the standard centered text path. | High |
| `0x10031610` | `CG_GetValue` | `cg_newdraw.c::CG_GetValue` | Assigned into the `cgDC` callback table at `0x10029210`; HLIL body returns score, stat, and selected-player values keyed by ownerdraw IDs. | High |
| `0x10031790` | `CG_OwnerDrawVisible` | `cg_newdraw.c::CG_OwnerDrawVisible` | Assigned into `cgDC.ownerDrawVisible`; HLIL evaluates the same broad ownerdraw visibility bitmask family used by the HUD/menu bridge. | High |
| `0x10032110` | `CG_DrawKiller` | `cg_newdraw.c::CG_DrawKiller` | Centered HUD obituary line using `cg.killerName` and the `Fragged by %s` format that `CG_OwnerDrawWidth` already references. | High |
| `0x10032240` | `CG_GetScoreboardTimerSeconds` | `cg_event.c::CG_GetScoreboardTimerSeconds` | Small helper returning the rounded scoreboard stopwatch seconds from the retail match clock; HLIL preserves the same non-negative clamp and `+500` ms rounding bias as the source helper. | High |
| `0x10032260` | `CG_DrawCapFragLimit` | `cg_newdraw.c::CG_DrawCapFragLimit` | Draws frag, capture, or score limits from the same gametype buckets as the source helper and prints the chosen numeric limit through the HUD text path. | High |
| `0x100335F0` | `CG_DrawClanArenaPlayers` | `cg_newdraw.c::CG_DrawClanArenaPlayers` | Ownerdraw cases `CG_RED_CLAN_PLYRS` / `CG_BLUE_CLAN_PLYRS` land here; HLIL selects the round-based team count slot and paints it through the shared numeric HUD text path. | High |
| `0x10033650` | `CG_DrawPlayerCount` | `cg_newdraw.c::CG_DrawPlayerCount` | Ownerdraw cases `CG_TEAM_PLYR_COUNT` / `CG_ENEMY_PLYR_COUNT` land here; HLIL flips the local team when the enemy slot is requested and draws the centered living-player count. | High |
| `0x100336E0` | `CG_DrawRoundLabel` | `cg_newdraw.c::CG_DrawRoundLabel` | Emits `Warmup` or `Round %d` via the ownerdraw text path; narrower than the newer source helper but clearly the same round-label slot. | High |
| `0x100337A0` | `CG_DrawDominationOwnedFlags` | `cg_newdraw.c::CG_DrawDominationOwnedFlags` | Ownerdraw cases `CG_RED_OWNED_FLAGS` / `CG_BLUE_OWNED_FLAGS` land here; HLIL selects the per-team Domination ownership counter and paints it through the shared numeric text path. | High |
| `0x10033800` | `CG_DrawGameLimit` | `cg_newdraw.c::CG_DrawGameLimit` | Retail legacy `CG_GAME_LIMIT` ownerdraw that selects one of the exact `Cap Limit` / `Frag Limit` / `Round Limit` / `Score Limit` strings. The current source helper now mirrors those labels, so the slot and behavior line up cleanly. | High |
| `0x10033910` | `CG_DrawStartingWeapons` | `cg_newdraw.c::CG_DrawStartingWeapons` | Retail `CG_STARTING_WEAPONS` ownerdraw that walks the starting-weapon mask and renders the configured loadout through the intro-panel draw path. The current source helper now mirrors that icon-strip path with `CS_LOADOUT_MASK` preference and queued-primary preview fallback. | High |
| `0x10033D80` | `CG_DrawLocalTime` | `cg_newdraw.c::CG_DrawLocalTime` | Retail `CG_LOCALTIME` ownerdraw that prints a richer local time/date label (`HH:MM (Mon DD, YYYY)`), which the current source helper now matches. | High |
| `0x10034280` | `CG_DrawMatchEndCondition` | `cg_newdraw.c::CG_DrawMatchEndCondition` | Retail `CG_MATCH_END_CONDITION` ownerdraw that chooses the appropriate race / time / mercy / round / score / capture end-condition string family and draws it directly. | High |
| `0x100343D0` | `CG_DrawMapName` | `cg_newdraw.c::CG_DrawMapName` | Retail `CG_MAP_NAME` ownerdraw that paints the prebuilt current-map label buffer directly through the text path. | High |
| `0x10034420` | `CG_DrawMatchDetails` | `cg_newdraw.c::CG_DrawMatchDetails` | Retail `CG_MATCH_DETAILS` ownerdraw that formats the phase label, gametype, and prebuilt panel string via `%s - %s - %s`. The current source helper now follows that narrower retail shape. | High |
| `0x100344B0` | `CG_DrawGameTypeMap` | `cg_newdraw.c::CG_DrawGameTypeMap` | Retail `CG_GAME_TYPE_MAP` ownerdraw that formats the gametype label plus the same prebuilt panel string through `%s - %s`; the current source helper now matches that retail shape. | High |
| `0x10034590` | `CG_DrawSelectedPlayerAccuracy` | `cg_newdraw.c::CG_DrawSelectedPlayerAccuracy` | Retail `CG_SELECTED_PLYR_ACCURACY` ownerdraw; HLIL formats the tracked scoreboard client's accuracy as `%d%%` and paints it through the standard text path. | High |
| `0x100345F0` | `CG_DrawSelectedPlayerBestWeapon` | `cg_newdraw.c::CG_DrawSelectedPlayerBestWeapon` | Retail `CG_PLYR_BEST_WEAPON_NAME` ownerdraw; HLIL maps the tracked weapon index to the same human-readable weapon-name family used by the source helper. | High |
| `0x100346E0` | `CG_DrawEndGameScore` | `cg_newdraw.c::CG_DrawEndGameScore` | Retail `CG_PLYR_END_GAME_SCORE` ownerdraw that emits the richer local endgame summary family for placement, score, assists, defends, captures, skulls, and forfeits before drawing the selected line. | High |
| `0x10034840` | `CG_DrawGameTypeIcon` | `cg_newdraw.c::CG_DrawGameTypeIcon` | Selects the pre-registered retail gametype HUD shader (`ffa` / `duel` / `race` / `tdm` / ...) and draws it into the supplied rect. | High |
| `0x10034900` | `CG_DrawFirstPlaceModel` | `cg_newdraw.c::CG_DrawFirstPlaceModel` | Ownerdraw case `CG_1STPLACE_PLYR_MODEL` forwards the first-place client slot through the shared profile/model draw helper and matches the non-active scoreboard role of the source analogue. | High |
| `0x10034980` | `CG_DrawPlayerModel` | `synthetic retail ownerdraw helper` | Deliberate synthetic retail name for the old `CG_PLAYERMODEL` ownerdraw wrapper. HLIL lands here from ownerdraw case `0x1A`, selects either the tracked client slot or the live local client slot, and forwards that client through the same shared profile/model draw helper used by `CG_DrawFirstPlaceModel`. | High |
| `0x10034A00` | `CG_GetMatchStatusText` | `synthetic retail HUD helper` | Deliberate synthetic name: retail composes the match-phase label (`MATCH WARMUP` / `MATCH IN PROGRESS` / `MATCH SUMMARY`) plus the game-status suffix here instead of building the string inline inside `CG_DrawMatchStatus`. | High |
| `0x10034B30` | `CG_GetGameStatusText` | `cg_newdraw.c::CG_GetGameStatusText` | Returns the same FFA placement or team-score lead text family used by the ownerdraw width and match-status path. | High |
| `0x10034BD0` | `CG_DrawGameStatus` | `cg_newdraw.c::CG_DrawGameStatus` | Thin draw wrapper that paints the retail `CG_GetGameStatusText` result at the ownerdraw baseline. | High |
| `0x10034C20` | `CG_DrawGameType` | `cg_newdraw.c::CG_DrawGameType` | Draws the current gametype label from the same static gametype string table used by `CG_OwnerDrawWidth`. | High |
| `0x10034CC0` | `CG_DrawMatchStatus` | `cg_newdraw.c::CG_DrawMatchStatus` | Retail draw wrapper that consumes the already-composed match-status text from `0x10034A00` and paints it with the standard HUD alignment rules. | High |
| `0x10034D70` | `CG_DrawSpectatorMessages` | `cg_newdraw.c::CG_DrawSpectatorMessages` | Ownerdraw case `CG_SPEC_MESSAGES` draws the older retail spectator/pregame copy: `Round In Progress`, `SPECTATOR MODE`, `waiting to play`, the join-button fallback, and the mouse-cycle hint inside the same HUD slot used by the source helper. | High |
| `0x1003B0F0` | `CG_OwnerDraw` | `cg_newdraw.c::CG_OwnerDraw` | Assigned into `cgDC.ownerDrawItem`; large switch over ownerdraw IDs dispatches to draw helpers matching the retail HUD bridge shape. | High |
| `0x1003C620` | `CG_EventHandling` | `cg_newdraw.c::CG_EventHandling` | Single-argument native entry-table slot that updates the retail HUD interaction mode; the retail event ids appear extended relative to the public-source enum, but the state-setting behavior still matches. | High |
| `0x1003C870` | `CG_RunMenuScript` | `cg_newdraw.c::CG_RunMenuScript` | Assigned into `cgDC.runScript`; HLIL parses script tokens and handles retail `setFullScreen`, `setWindowed`, and `toggleFullscreen` commands before `vid_restart fast`. | High |
| `0x1003C9A0` | `CG_GetTeamColor` | `cg_newdraw.c::CG_GetTeamColor` | Assigned into `cgDC.getTeamColor`; writes the expected red, blue, or neutral HUD tint vector based on the local team. | High |
| `0x1004A460` | `CG_ParseStopRecord` | `cg_servercmds.c::CG_ParseStopRecord` | Tiny helper under `CG_ServerCommand`; HLIL emits `stoprecord; wait\n`, which is the retail command-buffer variant of the stop-record path. | High |
| `0x1004A4A0` | `CG_ParseRecord` | `cg_servercmds.c::CG_ParseRecord` | Pulls `Argv(1)` when present and issues `record "%s"\n`; otherwise falls back to the nameless record path. | High |
| `0x1004A500` | `CG_ParseScreenshot` | `cg_servercmds.c::CG_ParseScreenshot` | Pulls `Argv(1)` when present and issues `screenshotJPEG "%s"\n`; otherwise falls back to the nameless screenshot path. | High |
| `0x1004A560` | `CG_HeadModelVoiceChats` | `cg_servercmds.c::CG_HeadModelVoiceChats` | Opens a voice-chat file, checks the `MAX_VOICEFILESIZE` guard, parses the list header, and returns a cached voice-chat index or `-1`. | High |
| `0x1004A6A0` | `CG_GetVoiceChat` | `cg_servercmds.c::CG_GetVoiceChat` | Walks a loaded voice-chat list, compares the chat id, and picks a random sound/chat pair from the matching entry. | High |
| `0x1004A740` | `CG_VoiceChatListForClient` | `cg_servercmds.c::CG_VoiceChatListForClient` | Normalizes the client index, builds the head-model path, checks the cache, tries `scripts/%s.vc`, and falls back by gender. | High |
| `0x1004AAC0` | `CG_PlayVoiceChat` | `cg_servercmds.c::CG_PlayVoiceChat` | Starts the local voice sound, opens `voiceMenu` for order prompts, updates accept-order state, and echoes text when allowed. | High |
| `0x1004ABC0` | `CG_PlayBufferedVoiceChats` | `cg_servercmds.c::CG_PlayBufferedVoiceChats` | Checks `cg.voiceChatTime < cg.time`, drains the buffered ring, and delays the next playback by one second. | High |
| `0x1004AC30` | `CG_AddBufferedVoiceChat` | `cg_servercmds.c::CG_AddBufferedVoiceChat` | Copies the chat into the voice ring buffer and forces playback of the oldest buffered entry when the ring wraps. | High |
| `0x1004AC90` | `CG_VoiceChatLocal` | `cg_servercmds.c::CG_VoiceChatLocal` | Normalizes the client index, resolves the voice-chat list, formats the colored chat line, and queues the buffered local voice chat. | High |
| `0x1004AD90` | `CG_RemoveChatEscapeChar` | `cg_servercmds.c::CG_RemoveChatEscapeChar` | Tiny in-place filter that strips `0x19` chat-escape bytes before text is printed or added to team chat. | High |

### Retail Event Helper Sweep

- The event-side tranche now includes `CG_PlaceString`, `CG_Obituary`, `CG_UseItem`, `CG_PainEvent`, and the synthetic retail helper `CG_TryAutoFollowPowerup`. That closes the most distinctive standalone helpers under `CG_EntityEvent` without forcing unstable names onto the smaller retail-only sidecars in the same region.
- `CG_Obituary` is now closer to the retail feed shape as well as the retail event behavior: the current source caches expanded obituary rows with target/attacker strings, per-name color ids, icon handles, row-cap trimming through `cg_obituaryRowSize`, and expiry compaction instead of rebuilding every line from only `(attacker, target, mod, time)` at draw time.
- `CG_TryAutoFollowPowerup` is intentionally documented as a synthetic retail name rather than being flattened onto a GPL helper. The current source split still keeps the newer tracked-player overlay state, but it now mirrors the retail direct follow-command shape: `cg_event.c` still feeds powerup/flag spectator tracking through `CG_TrackFlagCarrierForEvent` and `CG_SpectatorTrackEvent`, and the follow path now emits `follow %d%s` with the optional `" pw"` suffix on the direct powerup-pickup path.

### Retail HUD Status/Text Sweep

- The ownerdraw text/status sweep now covers the broader `0x10032110-0x10034D70` cluster: `CG_DrawKiller`, `CG_GetScoreboardTimerSeconds`, `CG_DrawCapFragLimit`, `CG_DrawClanArenaPlayers`, `CG_DrawPlayerCount`, `CG_DrawRoundLabel`, `CG_DrawDominationOwnedFlags`, `CG_DrawGameLimit`, `CG_DrawGameTypeIcon`, `CG_DrawFirstPlaceModel`, the synthetic retail `CG_DrawPlayerModel`, `CG_GetGameStatusText`, `CG_DrawGameStatus`, `CG_DrawGameType`, `CG_DrawMatchStatus`, and `CG_DrawSpectatorMessages`.
- `0x10034A00` is intentionally normalized as the synthetic `CG_GetMatchStatusText` rather than forced onto a GPL symbol. Retail composes the uppercase match-phase label plus the status suffix there, and the current source tree now mirrors that split instead of building the buffer inline inside `CG_DrawMatchStatus`.
- `CG_GetGameStatusText` now also follows the narrower retail status family: Race returns no status suffix, Red Rover stays on the placement path, and team modes use the colorized `^1Red^7` / `^4Blue^7` lead strings instead of the older plain-text wording.
- The tranche also explains the earlier `Fragged by %s` width anchor: `0x10032110` is the actual `CG_DrawKiller` ownerdraw, while both the draw helper and `CG_OwnerDrawWidth` inline the killer-text formatting instead of calling a standalone `CG_GetKillerText`.
- `CG_DrawGameTypeIcon` now stays source-aligned at the asset-path level too: retail draws pre-registered `.tga` handles from `CG_RegisterGraphics`, and the current source now mirrors that registration path instead of lazily registering `.png` assets on demand.
- `CG_DrawGameLimit` is still worth calling out because HLIL preserves the exact `Cap Limit` / `Frag Limit` / `Round Limit` / `Score Limit` string family behind ownerdraw case `CG_GAME_LIMIT`; the current source helper now mirrors that narrower retail label set instead of the earlier broader summary text.
- `CG_DrawSpectatorMessages` is now source-aligned to the older retail copy family: `Round In Progress`, `SPECTATOR MODE`, `waiting to play`, the join-button fallback, and the mouse-cycle hint all ride the same HUD slot.
- `0x10034900` and `0x10034980` now form a stable paired profile-image recovery. `CG_DrawFirstPlaceModel` stays aligned to `CG_1STPLACE_PLYR_MODEL`, while the synthetic `CG_DrawPlayerModel` keeps the separate retail `CG_PLAYERMODEL` slot explicit instead of pretending the current source tree still exposes a matching standalone helper.

### Retail Intro / Endgame Ownerdraw Sweep

- The intro/endgame panel tranche now also covers `CG_DrawLevelTimer`, `CG_DrawStartingWeapons`, `CG_DrawLocalTime`, `CG_DrawMatchEndCondition`, `CG_DrawMapName`, `CG_DrawMatchDetails`, `CG_DrawGameTypeMap`, `CG_DrawSelectedPlayerAccuracy`, `CG_DrawSelectedPlayerBestWeapon`, and `CG_DrawEndGameScore`.
- `CG_DrawStartingWeapons` is now source-aligned to the retail intro panel path: the helper prefers `CS_LOADOUT_MASK`, renders the icon strip in retail weapon order, and appends the queued-primary preview after the `+` separator.
- `CG_DrawLocalTime` is likewise source-aligned now that the public helper prints the full local date/time label with month/day/year instead of the older `HH:MM` output.
- `CG_DrawMatchDetails` and `CG_DrawGameTypeMap` both reuse the same prebuilt panel string in retail, and the current source helpers now follow those shorter retail format shapes.
- `CG_DrawEndGameScore` is now source-aligned to the richer retail summary family behind `CG_PLYR_END_GAME_SCORE`: the current helper follows the `You finished ...`, `You had %d assist%s.`, `You had %d defend%s.`, `You had %d flag capture%s.`, `You captured %d skull%s.`, and forfeit branches instead of the older generic score strings.
- `CG_MATCH_WINNER` also stays closer to retail now on the intermission/forfeit edge: the current helper preserves the retail `...^7 WINS by forfeit` wording instead of flattening every winner line into `Winner: ...`.
- The team pickup/time-held ownerdraws now stay on the retail telemetry path too: current source consumes the parsed `scorestats_team` payload directly, preserves the published field count, and no longer synthesizes `CG_TEAMSTAT_MAP_PICKUPS` from scoreboard-side capture/assist/defend proxies when that payload is absent.

### HUD Callback Bridge At `0x10029210`

- `0x10029210` is now stable enough to promote as the synthetic retail helper `CG_InitDisplayContext`. The committed Ghidra corpus already carries a standalone function boundary there, HLIL shows the full `cgDC` callback slab being wired at that address, and the tail write to `data_1074ccf8` matches the source-side `Init_Display(&cgDC)` handoff from `ui_shared.c`.
- The front drawtools tranche is now explicit too: retail `0x100122B0`, `0x100123C0`, `0x100123D0`, `0x10012460`, `0x10012540`, `0x10012620`, and `0x100126A0` line up cleanly with `CG_AdjustFrom640`, `CG_SetAdjustFrom640Mode`, `CG_FillRect`, `CG_DrawSides`, `CG_DrawTopBottom`, `CG_DrawRect`, and `CG_DrawPic`. The recovered `cgDC` tail and the shared menu callsites show the same helper pair the current source now exposes through `adjustFrom640` and `setAdjustFrom640Mode`.
- This pass keeps the paired print/error hooks explicit in the bridge notes: `0x10020A90` is now normalized as `Com_Printf` because source `cg_main.c` wires `cgDC.Print = &Com_Printf`, and retail HLIL shows a direct `trap_Print` wrapper with no `cg_chatbeep` branch; `0x10020AF0` remains `Com_Error` because retail call sites preserve the leading Quake error-level parameter before forwarding through `cgDC.Error`.
- The bridge coverage now includes the remaining high-confidence value/text/feeder/cinematic targets: `CG_Cvar_Get`, the deliberately named `CG_Cvar_GetString` adaptor, `CG_Text_PaintWithCursor`, `CG_OwnerDrawHandleKey`, `CG_FeederCount`, `CG_FeederItemImage`, `CG_FeederItemText`, `CG_OwnerDrawWidth`, `CG_PlayCinematic`, `CG_StopCinematic`, `CG_DrawCinematic`, and `CG_RunCinematicFrame`, alongside the already-mapped `CG_OwnerDraw`, `CG_GetValue`, `CG_OwnerDrawVisible`, `CG_RunMenuScript`, and `CG_GetTeamColor`.
- `CG_Cvar_GetString` is intentionally documented as a synthetic retail adapter name rather than a public-source symbol. The stable part is the callback contract: token-helper fast path first, `trap_Cvar_VariableStringBuffer` fallback otherwise.
- `CG_DrawCinematic` is also a slightly unusual recovery: the committed corpus still does not expose a clean standalone function start, but the direct `cgDC.drawCinematic` slot assignment plus the extents-then-draw syscall sequence make the callback role itself stable enough to normalize.
- `CG_InitDisplayContext` is intentionally documented as a synthetic retail name rather than being flattened onto a source symbol. Current source still inlines that bootstrap inside `CG_LoadHudMenu`, while retail split it into a dedicated helper before the HUD file load runs.

### Retail Buffered Chat Stack

- HLIL exposes a small retail-only chat-stack cluster around `data_10079840`: `0x100068E0` clears the active slot plus the 24-entry history ring, `CG_PushPrintString` at `0x10006910` pushes a timed entry into that ring, and `0x10006A10` renders the stack from ownerdraw case `CG_AREA_NEW_CHAT`.
- The retail command-table tail now makes the latch explicit: `0x10007CD0` (`+chat`) sets `data_10a9c9b4`, `0x10007CF0` (`-chat`) clears it, and `0x10007D10` (`togglechathistory`) flips it. `0x10006A10` checks that same latch to decide whether the full buffered history should stay visible.
- `0x10007D30` is the retail `print` front-end into that stack, while `CG_PushPrintString` is the underlying timed-buffer writer used by `print`, `chat`, `tchat`, `bchat`, and the tracked-slot notifier pair.
- `CG_Show1stTrackedPlayer` and `CG_Show2ndTrackedPlayer` are intentionally synthetic names for that notifier pair: both read `cg_lastmsg` into the chat ring, but they also arm the tracked-slot timers later consumed by `CG_SHOW_IF_1ST_PLYR_TRACKED` and `CG_SHOW_IF_2ND_PLYR_TRACKED`.
- `CG_PushPrintString` is intentionally documented as a synthetic retail helper rather than flattened into the public-source `CG_SetPrintString`: the stable behavior is the timed history-ring push, not the older flat-string contract.
- Current source now mirrors the public-facing part of that retail stack: `cg_consolecmds.c` exposes `+chat`, `-chat`, `togglechathistory`, and `print`; `cg_newdraw.c::CG_DrawNewChatArea` obeys the same history latch instead of always painting the full ring; `cg_main.c::CG_PushPrintString` feeds `print`, `chat`, `tchat`, voice-text replay, and `cg_lastmsg` persistence through the shared timed chat buffer; and `cg_servercmds.c` now consumes the retail `bchat` and `clearChat` server commands instead of dropping them.

### Command Table Sweep At `data_10078DC0`

- The static command table now yields a large source-identical recovery set instead of just the earlier tail cluster: `CG_TargetCommand_f`, `CG_SizeUp_f`, `CG_SizeDown_f`, `CG_Viewpos_f`, `CG_ScoresDown_f`, `CG_ScoresUp_f`, `CG_TellTarget_f`, `CG_TellAttacker_f`, `CG_VoiceTellTarget_f`, `CG_VoiceTellAttacker_f`, the `nextTeamMember` / `prevTeamMember` pair, the order-confirm / deny flow, and the full task / taunt family through `CG_TaskSuicide_f`.
- `0x10006E40` is no longer treated as an anonymous loader clone. The command-table slot, `cg_hudFiles` / `ui/hud.txt` reads, parser reset, and `CG_LoadMenus` replay make it stable as the retail `CG_LoadHud_f` wrapper.
- Cross-file command targets are now also stable from the same table: `CG_LoadDeferredPlayers`, `CG_ZoomDown_f`, `CG_ZoomUp_f`, `CG_NextWeapon_f`, `CG_PrevWeapon_f`, and `CG_Weapon_f`. The weapon path is source-aligned but retail extends it with a `toggle` argument.
- Retail-only wrappers recovered from the same sweep now include `CG_DropFlag_f`, `CG_DropPowerup_f`, `CG_DropRune_f`, `CG_DropWeapon_f`, `CG_ReadyUp_f`, `CG_Team_f`, `CG_Forfeit_f`, `CG_RageQuit_f`, `CG_SetTeamColor_f`, and `CG_SetEnemyColor_f`.
- The command-table tail findings still stand: `CG_StartOrbit_f`, the three chat-history handlers, the buffered `CG_Print_f` front-end, and `CG_ClientMute_f` remain stable, while the private native mute/social callback stays an observed import-table extension rather than a forced public enum slot.
- Current source now mirrors that narrower retail local console surface: `CG_ConsoleCommand` keeps `nextTeamMember` / `prevTeamMember`, while spectator follow or camera actions stay on the `CG_RunMenuScript` path instead of extra dedicated console strings.
- Current source now mirrors the retail local wrapper cluster for the drop and concession tail too: `cg_consolecmds.c` handles `dropflag`, `droppowerup`, `droprune`, `dropweapon`, `forfeit`, and `ragequit` locally with the same gametype and InstaGib gates before forwarding to the server, and `ragequit` now arms the existing `cg.rageQuitTime` countdown latch instead of bypassing it.
- Current source now mirrors the retail local color-wrapper pair too: `setteamcolor` and `setenemycolor` live in `cg_consolecmds.c`, preserve the raw 1-3 character token through `cg_teamColors` / `cg_enemyColors`, and apply the recovered retail 26-entry palette onto the per-part head/upper/lower override cvars in the same upper/lower/head token order observed in HLIL.
- Current source now mirrors the retail local `team` and `readyup` wrappers too: `cg_consolecmds.c` formats `team %s`, forwards it through `trap_SendClientCommand`, and then dismisses the cgame-owned capture state by clearing `CGAME_EVENT_TEAMMENU` / `CGAME_EVENT_EDITHUD` and dropping `KEYCATCH_CGAME`; `readyup` now also stays local, requiring an active warmup or ready-up deadline and blocking spectators before forwarding to the server.
- Retail `0x10007840` still carries one unresolved special-case bypass through the same match-phase discriminator used by the native chat-field geometry and match-status helpers. Current source uses the strongest local proxy available for that branch instead of inventing a false public-source enum name: non-empty tutorial configstrings or `g_training` in serverinfo enable the same spectator and no-snapshot bypass for the tutorial/training pregame path.
- `CG_InitConsoleCommands` now also registers the missing retail forwarded-command tail instead of the older shorter GPL-era set, including `abort`, `ban`, `dropflag`, `dropweapon`, `forfeit`, `listaccess`, `lock`, `mute`, `put`, `ragequit`, `reload_access`, `setmatchtime`, `spec`, `tempban`, `timein`, `timeout`, `unlock`, `unmute`, and `unpause`.
- The taunt sweep also clarifies one small retail/source divergence: retail dispatches `kill_gauntlet`, not the public-source typo `kill_guantlet`.

### Native Import Extensions Used By `cgDC`

- Retail `cgDC` setup does more than the current public-source `cg_main.c` block: HLIL wires additional binding and command callbacks into the display context, including key-name / binding / execute-text style hooks adjacent to `cgDC.feederSelection`, `cgDC.Error`, and `cgDC.Print`.
- Current source now mirrors the retail key/binding command bridge on the legacy syscall seam too: `cg_main.c` wires `cgDC.keynumToStringBuf`, `getBindingBuf`, `setBinding`, `getOverstrikeMode`, `setOverstrikeMode`, and `executeText`, while `cg_public.h`, `cg_syscalls.c`, and `cl_cgame.c` expose matching host opcodes for those callbacks under the old `vmMain` interface.
- The retail command-table tail also reaches beyond the public import enum: `CG_ClientMute_f` at `0x10007E90` forwards per-client identity words through a private native mute/social callback near import-table offset `0x1F8`.
- Current mapping policy: treat those retail import-table callbacks as observed interface facts until the native cgame import contract is refreshed, rather than inventing a false source-identical import enum.

### Retail Social / Spectator Sidecar State

- `CG_RegisterCvars` now has an explicit retail anchor for `cg_trackPlayer`, which lines up with the reconstructed spectator-tracking flow already present in `cg_newdraw.c`.
- `CG_RegisterGraphics` now also has explicit retail anchors for the tracked-slot HUD assets and the voice overlay window: `ui/assets/score/1st_plyr_ready`, `1st_plyr_notready`, `1st_plyr_leads`, `1st_plyr_tied`, `1st_plyr_trails`, the matching `2nd_plyr_*` set, and `ui/assets/voiceWindow`.
- The scoreboard/team-list feeder family around `0x10026294`, `0x10026A08`, `0x10027398`, `0x10027CF4`, and `0x10027F8C` shares a stable social-overlay branch: the private import at `data_1074cccc + 0x1F4` checks the per-client identity words at `0x10a42418` / `0x10a4241C` and selects `ui/assets/score/muted`; otherwise the per-client flag at `0x10a4240C` selects `ui/assets/score/speaking`.
- `CG_SetClientSpeakingState` at `0x10020A40` is now stable enough to normalize as a synthetic native-export name: it stores the caller-provided state to `0x10a4240C`, timestamps `0x10a42410` with `cg.time`, and returns the client block pointer.
- `CG_CopyClientIdentity` at `0x10020910` is likewise stable enough to normalize as a synthetic native-export name: it validates the client slot, copies the retail sidecar words at `0x10a42400`, `0x10a42418`, and `0x10a4241C`, and copies two `0x27`-byte identity strings out of the client block into the caller buffer.
- `CG_ClientMute_f` and the `ui_priv` server-command path both reinforce that retail `cgame` talks to additional native social callbacks that are absent from the current public import enum: `+0x1F8` mutates mute state, while `ui_priv` remains an observed bridge rather than a normalized server-command analogue.
- Current source now reconstructs the UI-visible side of that retail path without inventing new import slots: `CG_ClientMute_f` toggles a local `cg.clientMuted[clientNum]` bit, the scoreboard/team-list feeders reuse the retail `ui/assets/score/muted` / `ui/assets/score/speaking` assets through the existing `cgDC.feederItemText` and `cgDC.feederItemImage` callbacks, and `cg_servercmds.c` now mirrors the retail `ui_priv` bridge by publishing `Argv(1)` through the `ui_priv` cvar. This is intentionally client-slot keyed until the native identity-based mute callback is rebuilt.
- `CG_GetChatFieldY` at `0x100209E0` and `CG_GetChatFieldPixelWidth` at `0x10020A00` are now stable enough to normalize as synthetic native-export names: the host chat-input draw path at `0x004B4100` calls slots `data_146cc38 + 0x44` and `+ 0x48` before its `SCR_AdjustFrom640`-style scaler, while retail returns `413 / 455` and `640 / 300` depending on `data_10a9c214`.
- `CG_GetChatFieldWidthInChars` at `0x10020A20` is also now stable enough to normalize: the host `say` / `say_team` openers store slot `data_146cc38 + 0x4C` directly into `data_1648C88`, which is the `widthInChars` member of the live `field_t` rooted at `data_1648C80`.
- `CG_GetPhysicsTime` at `0x1004E4D0` closes the last unnamed native-export getter in this sidecar cluster. The host timestamp-prefix path uses slot `data_146cc38 + 0x38` and falls back to host `serverTime`, while the retail body itself is the one-word read of `cg.physicsTime`.

### Native Entry Table At `data_100769A8`

- HLIL shows `dllEntry(void ***exports, void *imports, int *apiVersion)` returning a function table rooted at `data_100769A8`, caching the syscall/import table, and writing native API version `8` through `*apiVersion`.
- That matters because the retail native export array follows the Quake Live `dllEntryQL` / `VM_CallNativeExports` contract, while the current source tree still exposes the older `cgameExport_t` enum in `cg_public.h`. Table slots should therefore be named from observed behavior, not assumed enum order.
- Stable recovered slots in that table now include `CG_Init`, `CG_RegisterCvars`, `CG_Shutdown`, `CG_ConsoleCommand`, `CG_DrawActiveFrame`, `CG_CrosshairPlayer`, `CG_LastAttacker`, `CG_KeyEvent`, `CG_MouseEvent`, `CG_EventHandling`, `CG_ChatDown_f`, `CG_ChatUp_f`, `CG_Show1stTrackedPlayer`, `CG_Show2ndTrackedPlayer`, `CG_CopyClientIdentity`, `CG_GetChatFieldY`, `CG_GetChatFieldPixelWidth`, `CG_GetChatFieldWidthInChars`, `CG_SetClientSpeakingState`, and `CG_GetPhysicsTime`.
- Host `quakelive_steam.exe` HLIL now closes the native export tail directly through `data_146cc38`: slot `+0x38` is the timestamp-prefix getter (`CG_GetPhysicsTime`), slots `+0x44` / `+0x48` / `+0x4C` feed the native chat-input overlay (`CG_GetChatFieldY`, `CG_GetChatFieldPixelWidth`, `CG_GetChatFieldWidthInChars`), and slot `+0x40` remains a literal null entry.
- Current mapping policy: keep that deliberate null slot as an observed table fact rather than inventing a public-source callback name for it.

## Important Disagreements And Split Paths

### Export disagreement: `dllEntry` vs `entry`

- Ghidra `exports.txt` lists both `0x10020A70 dllEntry` and `0x10063D56 entry`.
- HLIL shows the PE export table naming only `dllEntry` at `0x10020A70`.
- HLIL also shows `addressOfEntryPoint = 0x63D56`, which makes `0x10063D56`
  the PE entrypoint / CRT startup rather than a named export.
- Current working assumption: treat `dllEntry` as the only named export and
  record `entry` as a Ghidra corpus disagreement, not as a normalized symbol.

### HLIL-only `CG_Init` boundary at `0x10029820`

- HLIL presents a clean function boundary at `0x10029820`.
- The committed Ghidra `functions.csv` and `analysis_symbols.txt` do not contain
  a function start at `0x10029820`.
- The internal flow still matches `CG_Init` strongly enough to map it, but the
  discrepancy should be preserved until the corpus is refreshed.

### Native API version / slot-order mismatch

- The current source path in `win_main.c::Sys_LoadDll` and `vm.c::VM_CallNativeExports`
  supports native game DLLs returning an export array plus an API version instead
  of the old `vmMain`-only contract.
- Retail `cgame` uses that path: HLIL `dllEntry` stores `&data_100769A8` into the
  export pointer and writes `8` to the caller-provided `apiVersion`.
- `src/code/cgame/cg_public.h` still describes the legacy `cgameExport_t` order.
- Current mapping policy: do not force `data_100769A8` into a source-identical slot
  order until each retail slot is revalidated against direct behavior.

### Split HUD bootstrap

- The source-level `CG_LoadHudMenu` is not monolithic in retail.
- `0x10029120` performs the shared menu-selection and load phase used during init.
- `0x10029210` now resolves as the synthetic retail helper `CG_InitDisplayContext`, which wires the `cgDC` callbacks and then publishes the display context through the same `Init_Display(&cgDC)` step that current source still keeps inline.
- `0x10006E40`, referenced via `data_10078E5C`, now resolves as the retail
  `CG_LoadHud_f` console wrapper that replays that same HUD load path on demand.
- Current mapping policy: normalize `0x10029120` as `CG_LoadHudMenu`,
  `0x10029210` as the synthetic `CG_InitDisplayContext`, and `0x10006E40`
  as `CG_LoadHud_f`, while still avoiding false public-source symbol claims
  for the retail split itself.

## Open Questions

- Refresh the committed Ghidra corpus to see whether `CG_Init` at `0x10029820`
  can be promoted into `functions.csv` and `analysis_symbols.txt`.
- Revalidate the deliberate null export slot at `data_100769E8` if a later
  retail host trace or refreshed corpus ever shows a callback there; current
  host and cgame HLIL both leave that slot null.
