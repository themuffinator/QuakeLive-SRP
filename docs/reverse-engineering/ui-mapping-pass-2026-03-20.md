# UI Mapping Pass 2026-03-20

## Scope

This pass expands the committed `ui` reverse-engineering map from a synthetic five-function sample into a curated high-confidence subset tied to the retail `uix86.dll` binary. The goal was to land names that are directly supported by the committed Ghidra corpus and cross-checked against the HLIL dump plus the reconstructed UI source.

## Sources Used

- `references/reverse-engineering/ghidra/uix86/metadata.txt`
- `references/reverse-engineering/ghidra/uix86/imports.txt`
- `references/reverse-engineering/ghidra/uix86/exports.txt`
- `references/reverse-engineering/ghidra/uix86/functions.csv`
- `references/reverse-engineering/ghidra/uix86/analysis_symbols.txt`
- `references/reverse-engineering/ghidra/uix86/decompile_top_functions.c`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/ui/ui_atoms.c`
- `src/code/ui/ui_gameinfo.c`
- `src/code/ui/ui_main.c`
- `src/code/ui/ui_players.c`
- `src/code/ui/ui_shared.c`

## Canonical Observations

- `metadata.txt` reports 348 functions, 50 imports, 2 exports, 510 promoted analysis symbols, and 180 decompiled functions for `uix86.dll`.
- `exports.txt` exposes `dllEntry` at `0x10003970` and `entry` at `0x10020d66`.
- The HLIL dump shows `0x10020d66` as the module start routine. This pass does not rename it to `vmMain`.
- The prior `references/symbol-maps/ui.json` file did not describe the retail binary. It was a placeholder sample that used synthetic addresses, strings, and relocations.
- The new curated map points at `assets/quakelive/baseq3/uix86.dll`, which is the committed retail UI binary for this repository.

## Landed Ghidra-Backed Mappings

The following names were added because the committed Ghidra function index already exposes stable raw names for them and the behavior can be cross-checked against HLIL plus the reconstructed source:

- `FUN_10001f70` -> `UI_SetBestScores`
- `FUN_10002350` -> `UI_LoadBestScores`
- `FUN_10002550` -> `UI_CalcPostGameStats`
- `FUN_10002bf0` -> `UI_AdjustFrom640`
- `FUN_10002c50` -> `UI_DrawHandlePic`
- `FUN_10002d60` -> `UI_FillRect`
- `FUN_10002e20` -> `UI_LoadArenasFromFile`
- `FUN_10003190` -> `UI_LoadArenas`
- `FUN_10003640` -> `UI_LoadBotsFromFile`
- `FUN_10003770` -> `UI_LoadBots`
- `dllEntry` -> `dllEntry`
- `FUN_10003990` -> `AssetCache`
- `FUN_10003b30` -> `_UI_DrawSides`
- `FUN_10003c20` -> `_UI_DrawTopBottom`
- `FUN_10003ec0` -> `Text_Paint`
- `FUN_10004070` -> `Text_PaintWithCursor`
- `FUN_100044f0` -> `GetMenuBuffer`
- `FUN_100045b0` -> `Asset_Parse`
- `FUN_10004b20` -> `UI_ParseMenu`
- `FUN_10004e10` -> `UI_LoadMenus`
- `FUN_10004fc0` -> `UI_Load`
- `FUN_100097b0` -> `UI_OwnerDraw`
- `FUN_1000b0e0` -> `UI_RunMenuScript`
- `FUN_1000f340` -> `GameType_Parse`
- `FUN_1000f4c0` -> `MapList_Parse`
- `FUN_1000f6d0` -> `UI_ParseGameInfo`
- `FUN_1000fab0` -> `_UI_Init`
- `FUN_10010080` -> `UI_LoadNonIngame`
- `FUN_10010380` -> `_UI_IsFullscreen`
- `FUN_100103f0` -> `UI_ReadableSize`
- `FUN_10010540` -> `UI_PrintTime`
- `FUN_100105f0` -> `Text_PaintCenter`
- `FUN_10010660` -> `Text_PaintCenter_AutoWrapped`
- `FUN_100108d0` -> `UI_DisplayDownloadInfo`
- `FUN_10010e30` -> `UI_DrawConnectScreen`
- `FUN_10011730` -> `UI_RegisterCvars`
- `FUN_100118a0` -> `UI_UpdateCvars`
- `FUN_100118f0` -> `UI_StopServerRefresh`
- `FUN_10011970` -> `UI_DoServerRefresh`
- `FUN_10011a30` -> `UI_StartServerRefresh`
- `FUN_10011c50` -> `UI_PlayerInfo_SetWeapon`
- `FUN_10013850` -> `UI_FindClientHeadFile`
- `FUN_100139a0` -> `UI_RegisterClientSkin`
- `FUN_10013ba0` -> `UI_ParseAnimationFile`
- `FUN_10013e70` -> `UI_RegisterClientModelname`

Representative evidence:

- `FUN_10003990` registers `ui/assets/gradientbar2.tga`, FX art, scrollbar art, slider art, and `gfx/2d/crosshair%d`, matching `AssetCache`.
- `FUN_100044f0`, `FUN_100045b0`, `FUN_10004b20`, `FUN_10004e10`, and `FUN_10004fc0` line up with the menu loading and parsing pipeline seen in `ui_shared.c`.
- `FUN_10002e20`, `FUN_10003190`, `FUN_10003640`, `FUN_10003770`, `FUN_1000f340`, `FUN_1000f4c0`, and `FUN_1000f6d0` line up with arena, bot, gametype, and map parsing in `ui_gameinfo.c`.
- `FUN_10011c50`, `FUN_10013850`, `FUN_100139a0`, `FUN_10013ba0`, and `FUN_10013e70` line up with the player model, skin, and animation helpers in `ui_players.c`.
- `_UI_Init` assigns `UI_DrawHandlePic`, `UI_FillRect`, `Text_Paint`, `_UI_DrawSides`, `_UI_DrawTopBottom`, and `UI_OwnerDraw` into `uiDC`, which matches the existing UI renderer architecture.

## Second-Pass Additions

This follow-up pass focused on the connect-screen formatting path, centered text helpers, and the UI cvar refresh worker:

- `FUN_100103f0` formats `bytes`, `KB`, `MB`, and `GB` strings, matching `UI_ReadableSize` in `ui_main.c`.
- `FUN_10010540` formats `sec`, `min/sec`, and `hr/min` strings, matching `UI_PrintTime`.
- `FUN_100105f0` measures text width through the shared text-metrics helper and then calls `Text_Paint` at an adjusted x coordinate, matching `Text_PaintCenter`.
- `FUN_10010660` copies and wraps long strings on spaces before repeatedly calling the centered painter, matching `Text_PaintCenter_AutoWrapped`.
- `FUN_10004070` is assigned into `uiDC.drawTextWithCursor` during `_UI_Init` and draws the blink-mode cursor glyph over text, matching `Text_PaintWithCursor`.
- `FUN_100118a0` iterates the UI vmCvar table, updates each entry through the trap layer, and fires optional handlers, matching `UI_UpdateCvars`.

## Third-Pass Additions

This follow-up pass landed the contiguous player-preview helper chain from `ui_players.c`, where source order, call relationships, and HLIL state offsets all line up:

- `FUN_10011f40` -> `UI_ForceLegsAnim`
- `FUN_10011f70` -> `UI_SetLegsAnim`
- `FUN_10011fc0` -> `UI_ForceTorsoAnim`
- `FUN_10012000` -> `UI_SetTorsoAnim`
- `FUN_10012060` -> `UI_TorsoSequencing`
- `FUN_10012100` -> `UI_LegsSequencing`
- `FUN_10012190` -> `UI_PositionEntityOnTag`
- `FUN_10012290` -> `UI_PositionRotatedEntityOnTag`
- `FUN_10012390` -> `UI_SetLerpFrameAnimation`
- `FUN_10012490` -> `UI_RunLerpFrame`
- `FUN_10012550` -> `UI_SwingAngles`
- `FUN_10012760` -> `UI_MovedirAdjustment`
- `FUN_10012900` -> `UI_PlayerAngles`
- `FUN_10012c00` -> `UI_PlayerFloatSprite`
- `FUN_10012ca0` -> `UI_MachinegunSpinAngle`
- `FUN_10012d90` -> `UI_DrawPlayer`
- `FUN_10014250` -> `UI_PlayerInfo_SetModel`
- `FUN_100142e0` -> `UI_PlayerInfo_SetInfo`

Representative evidence:

- `FUN_10011f40`, `FUN_10011f70`, `FUN_10011fc0`, `FUN_10012000`, `FUN_10012060`, and `FUN_10012100` manipulate the same legs and torso animation state slots used by the source `playerInfo_t` sequencing helpers, including the jump, gesture, attack, and weapon-switch timers.
- `FUN_10012190` and `FUN_10012290` both call the tag-lerp trap and then build child origins from the parent axes; the rotated variant additionally composes entity axes, matching `UI_PositionRotatedEntityOnTag`.
- `FUN_10012390` validates animation bounds and selects an animation record, while `FUN_10012490` advances frame timing and computes backlerp, matching the `lerpFrame_t` pipeline in `ui_players.c`.
- `FUN_10012550`, `FUN_10012760`, and `FUN_10012900` use the same angle-subtract, swing tolerance, strafe adjustment, and axis-build logic as `UI_SwingAngles`, `UI_MovedirAdjustment`, and `UI_PlayerAngles`.
- `FUN_10012c00` builds a zeroed `refEntity_t`, offsets `origin[2]` by `48`, sets `RT_SPRITE`, and submits it to the renderer, matching `UI_PlayerFloatSprite`.
- `FUN_10012ca0` updates the barrel spin/coast state from realtime and torso attack animation state, matching `UI_MachinegunSpinAngle`.
- `FUN_10012d90` clears the scene, calls the player angle and lerp-frame helpers, adds legs, torso, head, gun, barrel, muzzle flash, chat sprite, and accent lights, then renders the preview scene, matching `UI_DrawPlayer`.
- `FUN_10014250` zeroes a `playerInfo_t`, registers the requested model set, seeds the default machinegun state, and calls `UI_PlayerInfo_SetWeapon`, matching `UI_PlayerInfo_SetModel`.
- `FUN_100142e0` updates view and move angles, handles weapon transition state, resets new-model initialization, and routes through the torso and legs animation helpers, matching `UI_PlayerInfo_SetInfo`.

## Fourth-Pass Additions

This follow-up pass landed the shared parser, memory, and base window-paint layer from `ui_shared.c`:

- `FUN_100144c0` -> `UI_Alloc`
- `FUN_10014510` -> `hashForString`
- `FUN_10014560` -> `String_Alloc`
- `FUN_10014670` -> `String_Report`
- `FUN_10014710` -> `PC_SourceError`
- `FUN_100147a0` -> `LerpColor`
- `FUN_100148a0` -> `Float_Parse`
- `FUN_100148d0` -> `PC_Float_Parse`
- `FUN_10014990` -> `Color_Parse`
- `FUN_100149d0` -> `PC_Color_Parse`
- `FUN_10014ab0` -> `Int_Parse`
- `FUN_10014ae0` -> `PC_Int_Parse`
- `FUN_10014ba0` -> `Rect_Parse`
- `FUN_10014c30` -> `String_Parse`
- `FUN_10014c60` -> `PC_String_Parse`
- `FUN_10014cf0` -> `PC_Script_Parse`
- `FUN_10014e50` -> `GradientBar_Paint`
- `FUN_10014ea0` -> `Fade`
- `FUN_10014f00` -> `Window_Paint`
- `FUN_10015410` -> `Item_SetScreenCoords`
- `FUN_10015470` -> `Item_UpdatePosition`

Representative evidence:

- `FUN_100144c0` allocates from the fixed UI pool, aligns sizes to 16 bytes, and emits the literal `UI_Alloc: Failure. Out of memory!` failure path, matching `UI_Alloc`.
- `FUN_10014510`, `FUN_10014560`, and `FUN_10014670` implement the 2048-slot hashed string interning path and the string/memory pool usage report, matching `hashForString`, `String_Alloc`, and `String_Report`.
- `FUN_10014710` calls the parser source-file-and-line trap and prints the `ERROR`-formatted message, matching `PC_SourceError`.
- `FUN_100148a0`, `FUN_100148d0`, `FUN_10014990`, `FUN_100149d0`, `FUN_10014ab0`, `FUN_10014ae0`, `FUN_10014ba0`, `FUN_10014c30`, `FUN_10014c60`, and `FUN_10014cf0` line up with the `Float_Parse`/`PC_Float_Parse`, color, integer, rectangle, string, and script parser helpers by token-reading behavior and error strings.
- `FUN_10014e50` sets the color, draws the shared gradient bar shader, and clears the color, matching `GradientBar_Paint`.
- `FUN_10014ea0` checks the fade flags, `realTime`, `nextTime`, clamp, and fade amount to drive fade-in and fade-out alpha transitions, matching `Fade`.
- `FUN_10014f00` dispatches the filled, gradient, shader, team-color, and cinematic window styles and then draws the border variants, matching `Window_Paint`.
- `FUN_10015410` and `FUN_10015470` rebuild item screen rectangles from rect-client offsets and parent menu position, matching `Item_SetScreenCoords` and `Item_UpdatePosition`.

## Fifth-Pass Additions

This follow-up pass landed the first raw-name-backed menu and script-command tranche from `ui_shared.c`:

- `FUN_10015c50` -> `Menu_ItemsMatchingGroup`
- `FUN_10015cc0` -> `Menu_GetMatchingItemByNumber`
- `FUN_10015d50` -> `Script_SetColor`
- `FUN_10015ea0` -> `Menu_FindItemByName`
- `FUN_10015f10` -> `Script_SetTeamColor`
- `FUN_10015f90` -> `Script_SetItemColor`
- `FUN_100160f0` -> `Menu_ShowItemByName`
- `FUN_10016340` -> `Script_FadeIn`
- `FUN_10016450` -> `Script_ConditionalOpen`
- `FUN_100167b0` -> `Script_Transition`
- `FUN_100169d0` -> `Script_Orbit`
- `FUN_10016c20` -> `Script_SetCvar`

Representative evidence:

- `FUN_10015c50` and `FUN_10015cc0` walk the menu item array, compare against both `window.name` and `window.group`, count matches, and return the indexed match, lining up with `Menu_ItemsMatchingGroup` and `Menu_GetMatchingItemByNumber`.
- `FUN_10015d50` parses `backcolor`, `forecolor`, or `bordercolor` and then reads four float tokens into the selected output vector, matching `Script_SetColor`.
- `FUN_10015ea0` checks only `window.name` slots and returns the first exact match, matching `Menu_FindItemByName`.
- `FUN_10015f10` calls the display-context team-color callback and copies the resulting vec4 into the current item's background color, matching `Script_SetTeamColor`.
- `FUN_10015f90` parses an item/group selector, a color field selector, and a vec4, then iterates the matching item set through `FUN_10015c50` and `FUN_10015cc0`, matching `Script_SetItemColor`.
- `FUN_100160f0` loops the matching item set, toggles the visible flag, and stops active cinematics on the hide path, matching `Menu_ShowItemByName`.
- The HLIL command table at `0x1002a018` binds `"fadein"` to `sub_10016340`, `"conditionalopen"` to `sub_10016450`, `"transition"` to `sub_100167b0`, `"setcvar"` to `sub_10016c20`, and `"orbit"` to `sub_100169d0`, while each function's parser shape matches the corresponding `Script_*` helper in `src/code/ui/ui_shared.c`.
- `FUN_10016340` parses one token and then marks the matching items visible plus fading-in, matching `Script_FadeIn`.
- `FUN_10016450` reads one cvar name and two menu names, branches on the `getCVarValue` result, and opens the selected menu, matching `Script_ConditionalOpen`.
- `FUN_100167b0` parses two rectangles, a transition time, and a float amount before calling the item-transition worker, matching `Script_Transition`.
- `FUN_100169d0` parses an orbit target name, x/y origin, orbit center, and time before calling the orbit worker, matching `Script_Orbit`.
- `FUN_10016c20` parses a cvar name/value pair and forwards them through the display-context `setCVar` callback, matching `Script_SetCvar`.

## Sixth-Pass Additions

This follow-up pass extends the same `ui_shared.c` region in two ways: additional Ghidra-backed menu helpers with stable `FUN_...` raw names, and a larger batch of HLIL `sub_...` handlers whose identities are fixed by the retail script command table at `0x1002a018`.

Landed helper names:

- `FUN_10015a80` -> `Menu_ClearFocus`
- `FUN_10016160` -> `Menus_FindByName`
- `FUN_100161b0` -> `Menus_CloseByName`
- `FUN_10016220` -> `Menus_CloseAll`
- `FUN_10016d70` -> `Item_RunScript`

Landed command-table-backed handlers:

- `sub_10015e30` -> `Script_SetAsset`
- `sub_10015e60` -> `Script_SetBackground`
- `sub_100162c0` -> `Script_Show`
- `sub_10016300` -> `Script_Hide`
- `sub_100163b0` -> `Script_FadeOut`
- `sub_10016420` -> `Script_Open`
- `sub_100164f0` -> `Script_Close`
- `sub_10016580` -> `Script_Toggle`
- `sub_10016ad0` -> `Script_ActivateAdvert`
- `sub_10016b10` -> `Script_SetFocus`
- `sub_10016ba0` -> `Script_SetPlayerModel`
- `sub_10016be0` -> `Script_SetPlayerHead`
- `sub_10016c80` -> `Script_Exec`
- `sub_10016cd0` -> `Script_Play`
- `sub_10016d20` -> `Script_playLooped`

Representative evidence:

- `FUN_10015a80` walks all menu items, captures the currently focused item, clears the focus bit on each, and runs any `leaveFocus` script, matching `Menu_ClearFocus`.
- `FUN_10016160` iterates the global menu array and compares `window.name` strings, matching `Menus_FindByName`.
- `FUN_100161b0` and `FUN_10016220` layer the retail close-script path on top of `FUN_10016160` and the global menu array traversal, matching `Menus_CloseByName` and `Menus_CloseAll`.
- `FUN_10016d70` tokenizes a semicolon-delimited script string, interns command tokens, dispatches through the retail command table rooted at `0x1002a018`, and falls back to the execute-text callback for unknown commands, matching `Item_RunScript`.
- The table at `0x1002a018` binds `"show"` to `sub_100162c0`, `"hide"` to `sub_10016300`, `"fadeout"` to `sub_100163b0`, `"open"` to `sub_10016420`, `"close"` to `sub_100164f0`, `"toggle"` to `sub_10016580`, `"setasset"` to `sub_10015e30`, `"setbackground"` to `sub_10015e60`, `"setfocus"` to `sub_10016b10`, `"setplayermodel"` to `sub_10016ba0`, `"setplayerhead"` to `sub_10016be0`, `"exec"` to `sub_10016c80`, `"play"` to `sub_10016cd0`, `"playlooped"` to `sub_10016d20`, and `"activateAdvert"` to `sub_10016ad0`.
- `sub_100162c0`, `sub_10016300`, and `sub_100163b0` all parse one token and tail-call or mirror the already landed visibility and fade helpers, matching `Script_Show`, `Script_Hide`, and `Script_FadeOut`.
- `sub_10016420`, `sub_100164f0`, and `sub_10016580` parse a menu name and route through the retail open, close, and toggle flows for named menus, matching `Script_Open`, `Script_Close`, and `Script_Toggle`.
- `sub_10015e30` is a retail no-op-style stub that only parses and interns the asset token, matching the behavior of `Script_SetAsset`; `sub_10015e60` registers the parsed shader and stores it into `item->window.background`, matching `Script_SetBackground`.
- `sub_10016b10` parses a target item name, finds it in the parent menu, clears prior focus, runs the new `onFocus` script, and plays the focus sound, matching `Script_SetFocus`.
- `sub_10016ba0` and `sub_10016be0` parse one token and forward it through the display-context `setCVar` callback as `"model"` and `"headmodel"` respectively, matching the retail `setplayermodel` and `setplayerhead` handlers.
- `sub_10016c80`, `sub_10016cd0`, and `sub_10016d20` match the exec, local sound, and looping background-track script helpers by parser shape and callback usage.
- `sub_10016ad0` is Quake Live specific: it parses an integer advert token, calls the advert activation callback, and clears the current item's focus bit, so the command-string anchor is the primary naming signal for `Script_ActivateAdvert`.

## Seventh-Pass Additions

This follow-up pass targeted the listbox, slider, hover, capture, and cursor-navigation block in `ui_shared.c`, where the retail control flow is especially dense but the call relationships are unusually strong.

Landed names:

- `FUN_10016e70` -> `Item_EnableShowViaCvar`
- `FUN_10016fc0` -> `Item_SetFocus`
- `FUN_10017190` -> `Item_ListBox_MaxScroll`
- `FUN_100171f0` -> `Item_ListBox_ThumbPosition`
- `FUN_10017310` -> `Item_ListBox_ThumbDrawPosition`
- `FUN_10017410` -> `Item_Slider_ThumbPosition`
- `FUN_10017500` -> `Item_Slider_OverSlider`
- `FUN_10017570` -> `Item_ListBox_OverLB`
- `FUN_10017880` -> `Item_ListBox_MouseEnter`
- `FUN_100179d0` -> `Item_MouseEnter`
- `FUN_10017b50` -> `Item_MouseLeave`
- `FUN_10017b90` -> `Item_ListBox_HandleKey`
- `sub_10018c50` -> `Scroll_ListBox_AutoFunc`
- `FUN_10018cb0` -> `Scroll_ListBox_ThumbFunc`
- `FUN_10018e60` -> `Scroll_Slider_ThumbFunc`
- `FUN_10019000` -> `Item_StartCapture`
- `FUN_100194b0` -> `Menu_SetPrevCursorItem`
- `FUN_100195b0` -> `Menu_SetNextCursorItem`

Representative evidence:

- `FUN_10016e70` iterates the item's four cvar-test slots, pulls the current cvar string through the display context, tokenizes the semicolon-delimited test list, and returns the retail enable/show decision based on `item->cvarFlags & flag`, matching `Item_EnableShowViaCvar`.
- `FUN_10016fc0` rejects decorative and cvar-gated items, clears prior focus through `FUN_10015a80`, uses the corrected text-rect path for text items, runs the `onFocus` script and focus sound, and updates `parent->cursorItem`, matching `Item_SetFocus`.
- `FUN_10017190` and `FUN_100171f0` call the feeder-count callback, divide by listbox element width or height depending on `WINDOW_HORIZONTAL`, and apply the retail scrollbar constants, matching `Item_ListBox_MaxScroll` and `Item_ListBox_ThumbPosition`.
- `FUN_10017310` falls back to `FUN_100171f0` unless the current capture item matches, in which case it clamps the thumb draw position against the live cursor and scrollbar bounds, matching `Item_ListBox_ThumbDrawPosition`.
- `FUN_10017410` and `FUN_10017500` implement the slider-thumb x-position and thumb hit-test path through the cvar value callback, min/max clamps, the 96-pixel slider width, and the 12-pixel thumb envelope, matching `Item_Slider_ThumbPosition` and `Item_Slider_OverSlider`.
- `FUN_10017570`, `FUN_10017880`, and `FUN_10017b90` line up with the listbox arrow/page/thumb bitmask flow: the first returns the `WINDOW_LB_*` hover flags, the second refreshes those flags and updates `cursorPos`, and the third consumes them to drive keyboard, paging, click, feeder-selection, and double-click behavior, matching `Item_ListBox_OverLB`, `Item_ListBox_MouseEnter`, and `Item_ListBox_HandleKey`.
- `FUN_100179d0` and `FUN_10017b50` match the retail mouse-over state machine: they gate on cvar visibility, distinguish text-rect hover from full-window hover, run `mouseEnter` / `mouseEnterText` / `mouseExit` / `mouseExitText`, and delegate the listbox-specialized path when appropriate, matching `Item_MouseEnter` and `Item_MouseLeave`.
- `FUN_10018cb0`, `FUN_10018e60`, and `FUN_10019000` form the capture path seen in the GPL source: thumb-drag capture for listboxes and sliders, plus auto-repeat capture for listbox arrows, matching `Scroll_ListBox_ThumbFunc`, `Scroll_Slider_ThumbFunc`, and `Item_StartCapture`.
- `sub_10018c50` is the matching listbox auto-scroll callback, identified from its `Item_ListBox_HandleKey` repeat loop, timer tightening, and direct linkage from `FUN_10019000`; it is landed with the HLIL `sub_...` raw name because the committed `functions.csv` does not expose a `FUN_...` anchor for `0x10018c50`.
- `FUN_100194b0` and `FUN_100195b0` decrement or increment `menu->cursorItem` with wraparound, test candidates through `FUN_10016fc0`, and then call `Menu_HandleMouseMove` on the newly focused item's top-left corner plus one pixel, matching `Menu_SetPrevCursorItem` and `Menu_SetNextCursorItem`.

## Eighth-Pass Additions

This follow-up pass stayed in `ui_shared.c` and moved one block later into the retail item-key, popup-routing, corrected-text-rect, menu-mouse, and display-cache helpers.

Landed names:

- `FUN_10019180` -> `Item_Slider_HandleKey`
- `FUN_10019350` -> `Item_HandleKey`
- `FUN_100196b0` -> `Display_CloseCinematics`
- `FUN_10019790` -> `Menus_HandleOOBClick`
- `FUN_10019970` -> `Item_CorrectedTextRect`
- `FUN_1001d600` -> `Menu_HandleMouseMove`
- `FUN_100207f0` -> `Display_CacheAll`
- `FUN_100208f0` -> `Menu_OverActiveItem`

Representative evidence:

- `FUN_10019180` checks `WINDOW_HASFOCUS`, `item->cvar`, and a slider-local hit rectangle, uses the same `SLIDER_WIDTH`-style `96.0` constant and half-thumb offset math as the GPL `Item_Slider_HandleKey`, and prints the literal `slider handle key exit\n` on the failure path.
- `FUN_10019350` first clears the active capture globals or starts capture on mouse-down, rejects key-up events, and then switches by `item->type` into the retail listbox, ownerdraw, yes/no, multi, bind, and slider key handlers, matching `Item_HandleKey`.
- `FUN_100196b0` walks the global menu array and stops menu-window cinematics, item-window cinematics, and ownerdraw cinematics directly through the display-context stop callback, matching `Display_CloseCinematics`.
- `FUN_10019790` mirrors `Menus_HandleOOBClick`: it conditionally runs the current menu close script on OOB click, searches the global menu array through `FUN_100208f0`, activates the newly hit menu, calls `FUN_1001d600`, forwards the key through the downstream menu handler, checks whether any visible menus remain for the pause callback, and closes cinematics again on exit.
- `FUN_10019970` copies the item text rectangle into a shared static rect, runs the text-width/text-height callback, and subtracts the height from `y` when the rect is populated, matching `Item_CorrectedTextRect`.
- `FUN_1001d600` performs the same two-pass menu-item sweep as the source `Menu_HandleMouseMove`, including cvar enable/show gating, corrected text-rect hit testing for text items, `Item_MouseEnter`, `Item_MouseLeave`, and the first successful `Item_SetFocus`.
- `FUN_100207f0` is the direct target of the retail `ui_cache` console command in `0x10002ac0`, loops all menus, runs the play-then-stop cinematic cache path for menu and item windows, and registers menu sounds, matching `Display_CacheAll`.
- `FUN_100208f0` checks menu visibility and menu-rect containment, then scans active non-decoration items with corrected text-rect hit testing and cvar visibility gating, matching `Menu_OverActiveItem`.

## Ninth-Pass Additions

This follow-up pass moved into the retail parser keyword layer in `ui_shared.c`: item and menu keyword-hash setup, parser entrypoints, selected source-backed parse handlers with stable `FUN_...` raw names, and the adjacent retail-only cvar-preset keyword block.

Landed names:

- `FUN_1001da70` -> `Item_ValidateTypeData`
- `FUN_1001db60` -> `Parse_name`
- `FUN_1001dc00` -> `ItemParse_focusSound`
- `FUN_1001dcb0` -> `ItemParse_group`
- `FUN_1001dd50` -> `ItemParse_asset_model`
- `FUN_1001de60` -> `ItemParse_asset_shader`
- `FUN_1001df70` -> `Parse_model_fovx_or_elementwidth`
- `FUN_1001e190` -> `ItemParse_columns`
- `FUN_1001ed80` -> `ItemParse_cvar`
- `FUN_1001efa0` -> `ItemParse_cvarFloat`
- `FUN_1001f010` -> `ItemParse_cvarFloatList`
- `FUN_1001f150` -> `ItemParse_cvarInt`
- `FUN_1001f1d0` -> `ItemParse_cvarPreset`
- `FUN_1001f370` -> `ItemParse_cvarStrList`
- `FUN_1001f4c0` -> `ItemParse_addColorRange`
- `FUN_1001f5e0` -> `ItemParse_enableCvar`
- `FUN_1001f610` -> `ItemParse_disableCvar`
- `FUN_1001f650` -> `ItemParse_showCvar`
- `FUN_1001f690` -> `ItemParse_hideCvar`
- `FUN_1001f730` -> `Item_SetupKeywordHash`
- `FUN_1001f7c0` -> `Item_Parse`
- `FUN_1001f9d0` -> `MenuParse_font`
- `FUN_1001fc20` -> `MenuParse_focuscolor`
- `FUN_1001fd10` -> `MenuParse_disablecolor`
- `FUN_1001fed0` -> `Parse_text_or_soundLoop`
- `FUN_10020100` -> `Menu_SetupKeywordHash`
- `FUN_10020190` -> `Menu_Parse`
- `FUN_100203a0` -> `Menu_PaintAll`

Representative evidence:

- The retail item keyword table rooted at `0x1002a868` and the retail menu keyword table rooted at `0x1002ac70` bind exact parser keywords to exact handler addresses, providing direct naming anchors for `FUN_1001dcb0`, `FUN_1001dc00`, `FUN_1001dd50`, `FUN_1001de60`, `FUN_1001df70`, `FUN_1001e190`, `FUN_1001ed80`, `FUN_1001efa0`, `FUN_1001f010`, `FUN_1001f150`, `FUN_1001f1d0`, `FUN_1001f370`, `FUN_1001f4c0`, `FUN_1001f5e0`, `FUN_1001f610`, `FUN_1001f650`, `FUN_1001f690`, `FUN_1001f9d0`, `FUN_1001fc20`, `FUN_1001fd10`, and `FUN_1001fed0`.
- `FUN_1001f730` and `FUN_10020100` both clear an `0x800`-byte hash table and then walk the three-field keyword records, hashing the keyword text and linking each record into the per-bucket chain, matching `Item_SetupKeywordHash` and `Menu_SetupKeywordHash`.
- `FUN_1001f7c0` and `FUN_10020190` both read a leading `{`, iterate tokens, resolve them through the corresponding keyword hash, call the handler callback, and emit the same parser errors seen in source such as `end of file inside menu item\n`, `couldn't parse menu item keyword %s`, `end of file inside menu\n`, and `couldn't parse menu keyword %s`, matching `Item_Parse` and `Menu_Parse`.
- `FUN_100203a0` runs the active capture callback, iterates every menu through the paint worker, and prints the debug `fps: %f` overlay when debug mode is enabled, matching `Menu_PaintAll` rather than the parse-time `Menu_New` helper.
- `FUN_1001da70` allocates and zeroes the same typeData blocks described in `Item_ValidateTypeData`: listbox, edit-style, multi, and model data, including the default edit-field max-paint-char seed.
- `FUN_1001dd50`, `FUN_1001de60`, `FUN_1001df70`, and `FUN_1001e190` line up with the source parser shapes for model asset registration, shader registration, the shared retail `model_fovx` or `elementwidth` float parser, and listbox columns, including the `rand() % 360` angle seed and the per-column triple loop.
- `FUN_1001ed80`, `FUN_1001efa0`, `FUN_1001f010`, `FUN_1001f4c0`, `FUN_1001f5e0`, `FUN_1001f610`, `FUN_1001f650`, and `FUN_1001f690` follow the exact source parser behavior for `cvar`, `cvarFloat`, `cvarFloatList`, `addColorRange`, and the enable/disable/show/hide cvar gating scripts.
- The retail-only keyword strings `cvarInt`, `cvarPreset`, and `cvarPresetList` are present in the item parser table and point at `FUN_1001f150`, `FUN_1001f1d0`, and `FUN_1001f370`; HLIL shows the first parsing a cvar plus range and then setting integer mode, the second parsing brace-delimited preset labels plus numeric values, and the third parsing alternating string-pair lists that retail reuses for `cvarPresetList`.
- `FUN_1001f9d0`, `FUN_1001fc20`, `FUN_1001fd10`, and `FUN_1001fed0` align with the retail parser layer by parser shape and field targets: menu font normalization and registration, focus color, disable color, and the shared `text` or `soundLoop` string slot.

## Tenth-Pass Additions

This pass widened coverage across the rest of the retail item and menu parser tables and resolved the earlier shared-helper question by standardizing `Parse_*` names wherever the same retail implementation clearly serves both item and menu keywords. It also corrected a few earlier source-biased aliases once the full table cross-check showed the real retail slot identities.

Corrected earlier names:

- `FUN_1001db60`: `MenuParse_name` -> `Parse_name`
- `FUN_1001dcb0`: `ItemParse_name` -> `ItemParse_group`
- `FUN_1001df70`: `ItemParse_elementwidth` -> `Parse_model_fovx_or_elementwidth`
- `FUN_1001fed0`: `MenuParse_soundLoop` -> `Parse_text_or_soundLoop`

Newly landed names:

- `sub_1001de20` -> `ItemParse_widescreen`
- `sub_1001df10` -> `ItemParse_model_origin`
- `sub_1001dfa0` -> `Parse_model_fovy_or_elementheight`
- `sub_1001dfd0` -> `ItemParse_model_rotation`
- `sub_1001e000` -> `ItemParse_model_angle`
- `sub_1001e030` -> `ItemParse_rect`
- `sub_1001e090` -> `ItemParse_decoration`
- `sub_1001e0a0` -> `ItemParse_notselectable`
- `sub_1001e0d0` -> `ItemParse_wrapped`
- `sub_1001e0f0` -> `ItemParse_autowrapped`
- `sub_1001e110` -> `ItemParse_horizontalscroll`
- `sub_1001e130` -> `ItemParse_type`
- `sub_1001e160` -> `ItemParse_elementtype`
- `sub_1001e260` -> `Parse_visible`
- `sub_1001e290` -> `ItemParse_ownerdraw`
- `sub_1001e2c0` -> `ItemParse_align`
- `sub_1001e2e0` -> `Parse_textalign_or_fadeCycle`
- `sub_1001e300` -> `Parse_textaligny_or_fadeAmount`
- `sub_1001e320` -> `ItemParse_font`
- `sub_1001e340` -> `ItemParse_textscale`
- `sub_1001e360` -> `ItemParse_textstyle`
- `FUN_1001e380` -> `Parse_backcolor`
- `FUN_1001e470` -> `Parse_forecolor`
- `FUN_1001e570` -> `Parse_bordercolor`
- `sub_1001e660` -> `Parse_outlinecolor`
- `sub_1001e680` -> `ItemParse_altrowcolor`
- `sub_1001e6a0` -> `ItemParse_elementcolor`
- `sub_1001e6c0` -> `ItemParse_selectedcolor`
- `FUN_1001e6e0` -> `ItemParse_outlineimage`
- `FUN_1001e790` -> `Parse_background`
- `FUN_1001e840` -> `Parse_cinematic`
- `FUN_1001e940` -> `ItemParse_defaultContent`
- `FUN_1001eb00` -> `ItemParse_cvarTest`
- `FUN_1001eba0` -> `ItemParse_cvarTest2`
- `FUN_1001ec40` -> `ItemParse_cvarTest3`
- `FUN_1001ece0` -> `ItemParse_cvarTest4`
- `sub_1001faa0` -> `MenuParse_fullscreen`
- `sub_1001fac0` -> `MenuParse_widescreen`
- `FUN_1001fb00` -> `MenuParse_rect`
- `sub_1001fb60` -> `Parse_style`
- `sub_1001fb80` -> `MenuParse_onOpen`
- `sub_1001fba0` -> `MenuParse_onClose`
- `sub_1001fbc0` -> `MenuParse_onESC`
- `sub_1001fbe0` -> `Parse_border`
- `sub_1001fc00` -> `Parse_borderSize`
- `FUN_1001fe00` -> `MenuParse_backgroundSize`
- `sub_1001fe70` -> `MenuParse_ownerdraw`
- `sub_1001fe90` -> `MenuParse_popup`
- `sub_1001feb0` -> `MenuParse_outOfBounds`
- `sub_1001ff70` -> `Parse_textalignx_or_fadeClamp`
- `sub_1001ff90` -> `MenuParse_itemDef`

Representative evidence:

- The item keyword table at `0x1002a868` and the menu keyword table at `0x1002ac70` both point the same addresses at exact shared keywords such as `name`, `visible`, `style`, `backcolor`, `forecolor`, `bordercolor`, `outlinecolor`, `background`, `cinematic`, `border`, and `borderSize`, which gives direct evidence for the merged `Parse_*` naming scheme.
- The same table walk also shows several cross-keyword retail merges: `model_fovx` and `elementwidth` both call `FUN_1001df70`, `model_fovy` and `elementheight` both call `sub_1001dfa0`, `text` and `soundLoop` both call `FUN_1001fed0`, `textalign` and `fadeCycle` both call `sub_1001e2e0`, `textaligny` and `fadeAmount` both call `sub_1001e300`, and `textalignx` and `fadeClamp` both call `sub_1001ff70`.
- The item-only helpers from `sub_1001de20` through `sub_1001e360` line up with the source parser shapes in `ui_shared.c` for widescreen, model preview fields, item rect, decoration and wrapping flags, type validation, alignment, and text attributes.
- The retail-only item keyword strings `altrowcolor`, `selectedcolor`, `elementcolor`, `outlineimage`, `defaultContent`, `cvarTest2`, `cvarTest3`, and `cvarTest4` all appear directly in the item table and point at the handlers landed here; HLIL confirms the expected color, shader-string, or string-slot parse shape in each case.
- The menu-only parser block from `sub_1001faa0` through `sub_1001ff90` matches the source `MenuParse_fullscreen`, `MenuParse_widescreen`, `MenuParse_rect`, `MenuParse_onOpen`, `MenuParse_onClose`, `MenuParse_onESC`, `MenuParse_ownerdraw`, `MenuParse_popup`, `MenuParse_outOfBounds`, and `MenuParse_itemDef` shapes, and also exposes the retail-only `backgroundSize` keyword at `FUN_1001fe00`.

## Eleventh-Pass Additions

This pass closes out the remaining parser-table handlers that were still missing after the merged-parser cleanup: the item event-script parsers, the retail-only `cellId`, `precision`, `cvara`, `maxChars`, and `maxPaintChars` handlers, the shared `feeder` or `special` float parser, the shared `ownerdrawFlag` or `ownerdrawFlag2` helpers, and the repeated `showCvar[2-4]` or `hideCvar[2-4]` visibility-script slots.

Landed names:

- `sub_1001e8e0` -> `ItemParse_doubleClick`
- `sub_1001e920` -> `ItemParse_cellId`
- `sub_1001e9e0` -> `ItemParse_precision`
- `sub_1001ea00` -> `ItemParse_onFocus`
- `sub_1001ea20` -> `ItemParse_leaveFocus`
- `sub_1001ea40` -> `ItemParse_mouseEnter`
- `sub_1001ea60` -> `ItemParse_mouseExit`
- `sub_1001ea80` -> `ItemParse_mouseEnterText`
- `sub_1001eaa0` -> `ItemParse_mouseExitText`
- `sub_1001eac0` -> `ItemParse_action`
- `sub_1001eae0` -> `Parse_feeder_or_special`
- `sub_1001ee70` -> `ItemParse_cvara`
- `sub_1001eec0` -> `ItemParse_maxChars`
- `sub_1001ef30` -> `ItemParse_maxPaintChars`
- `sub_1001f580` -> `Parse_ownerdrawFlag`
- `sub_1001f5b0` -> `Parse_ownerdrawFlag2`
- `sub_1001f6d0` -> `Parse_showCvar2_or_hideCvar2`
- `sub_1001f6f0` -> `Parse_showCvar3_or_hideCvar3`
- `sub_1001f710` -> `Parse_showCvar4_or_hideCvar4`

Representative evidence:

- The retail item keyword table continues to provide exact anchors for `doubleclick`, `cellId`, `precision`, `onFocus`, `leaveFocus`, `mouseEnter`, `mouseExit`, `mouseEnterText`, `mouseExitText`, `action`, `cvara`, `maxChars`, and `maxPaintChars`; the corresponding HLIL bodies match the source `PC_Script_Parse`, `PC_Int_Parse`, or `PC_String_Parse` shapes and offsets.
- `sub_1001eae0` is bound by the table to both `feeder` and `special`, and its HLIL body is just the shared float parser that stores into the same `item->special` slot used by both source helpers.
- `sub_1001f580` is shared by item and menu `ownerdrawFlag`, while `sub_1001f5b0` is shared by item and menu `ownerdrawFlag2`; both parse an integer and OR it into the corresponding ownerdraw-flag field.
- `sub_1001f6d0`, `sub_1001f6f0`, and `sub_1001f710` are each reused by a paired `showCvarN` and `hideCvarN` keyword block, and HLIL shows each one parsing a script into a distinct auxiliary cvar-script slot.
- `sub_1001ee70` first executes the same path as `ItemParse_cvar` and then immediately calls the display-context setter with the parsed cvar name and the empty-string global `data_100239ab`, which matches a retail-only `cvara` helper layered on top of `cvar`.

## Twelfth-Pass Additions

This pass moves beyond the now-complete static parser tables and lands the first clean runtime menu-layer tranche: focused-menu lookup, feeder selection, named-menu activation, and the single-menu paint worker. All four landed names are backed by stable `FUN_...` anchors in `functions.csv`, direct source-shape matches in `ui_shared.c`, and corroborating HLIL or Ghidra call relationships.

Landed names:

- `FUN_1001d390` -> `Menu_GetFocused`
- `FUN_1001d3d0` -> `Menu_SetFeederSelection`
- `FUN_1001d4a0` -> `Menus_ActivateByName`
- `FUN_1001d7b0` -> `Menu_Paint`

Representative evidence:

- `FUN_1001d390` walks the global retail menu array, tests the same paired visible and focus bits seen in `ui_shared.c`, and returns the first matching menu pointer, which is an exact structural match for `Menu_GetFocused`.
- `FUN_1001d3d0` chooses either `FUN_1001d390` or the already-landed `FUN_10016160` (`Menus_FindByName`) depending on whether the caller supplied a name, scans `menu->items` for a matching `special` feeder id, zeroes the listbox cursor and start state when the target index is zero, writes `item->cursorPos`, and invokes the display-context feeder-selection callback. That matches `Menu_SetFeederSelection` rather than the simpler `Menu_ScrollFeeder`.
- `FUN_1001d4a0` first snapshots the currently focused visible menu, then walks the full menu array clearing focus on non-matches while activating the named target. Its body runs the menu `onOpen` script through the already-landed `Item_RunScript` path, starts the menu background track when present, pushes the previous focus into the open-menu stack when space remains, and closes cinematics. This is the exact source shape of `Menus_ActivateByName`.
- `FUN_1001d7b0` is the per-menu paint worker mirrored inside the already-landed `Menu_PaintAll` loop: it enforces visible and force-paint gating, checks the ownerdraw-visible callback, handles fullscreen background drawing, routes through the already-landed `Window_Paint` and per-item paint worker chain, and draws the debug rectangle when the retail debug flag is enabled.
- `FUN_10020740` still remains documented-only. Its committed HLIL cleanly proves the `menu == NULL` branch of `Display_MouseMove` by routing a popup-focused menu or all menus into the already-landed `Menu_HandleMouseMove`, but it still does not expose the source drag branch that mutates `menu->window.rectClient` and calls `Menu_UpdatePosition`.

## Thirteenth-Pass Additions

This pass moves deeper into the `ui_shared.c` runtime layer and lands the next clean helper chain: top-level display key routing, text metrics and wrapped-text paint, edit and bind capture, the retail multi-choice and preset-list helpers, model and listbox paint, ownerdraw paint, and the main per-item paint dispatcher. All landed names are backed by stable `FUN_...` anchors in `functions.csv`, retail callsite shapes in the already-landed `Item_HandleKey` and `Item_Paint` jump tables, and direct HLIL or source correspondence in `ui_shared.c`.

Landed names:

- `FUN_100180a0` -> `Item_YesNo_HandleKey`
- `FUN_100181a0` -> `Item_Multi_FindCvarByValue`
- `FUN_10018280` -> `Item_Multi_Setting`
- `FUN_10018370` -> `Item_Multi_HandleKey`
- `FUN_10018510` -> `Item_PresetList_Setting`
- `FUN_100185d0` -> `Item_PresetList_FindCvarByValue`
- `FUN_10018680` -> `Item_PresetList_HandleKey`
- `FUN_10018870` -> `Item_TextField_HandleKey`
- `FUN_10019a10` -> `Display_HandleKey`
- `FUN_10019f10` -> `Item_SetTextExtents`
- `FUN_1001a150` -> `Item_TextColor`
- `FUN_1001a3d0` -> `Item_Text_AutoWrapped_Paint`
- `FUN_1001a630` -> `Item_Text_Wrapped_Paint`
- `FUN_1001a7e0` -> `Item_Text_Paint`
- `FUN_1001a8e0` -> `Item_TextField_Paint`
- `FUN_1001ad40` -> `Item_Multi_Paint`
- `FUN_1001af00` -> `Item_PresetList_Paint`
- `FUN_1001b3d0` -> `Item_Slider_Paint`
- `FUN_1001b7c0` -> `Item_Bind_Paint`
- `FUN_1001b9e0` -> `Item_Bind_HandleKey`
- `FUN_1001bc30` -> `Item_Model_Paint`
- `FUN_1001bfb0` -> `Item_ListBox_Paint`
- `FUN_1001ca50` -> `Item_OwnerDraw_Paint`
- `FUN_1001ced0` -> `Item_Paint`

Representative evidence:

- `FUN_10019a10` owns the retail top-level key router. Its body first resolves the bind-capture and edit-capture globals, falls back to focused-menu routing, handles popup out-of-bounds clicks through the already-landed `FUN_10019790`, and delegates per-item key handling through the already-landed `FUN_10019350`. That is the exact `Display_HandleKey` role in the reconstructed source.
- `FUN_10019f10` through `FUN_1001a8e0` form a contiguous text-paint chain. The extents helper updates `item->textRect`; the color helper applies fade, focus pulse, blink, and disabled-color logic; the wrapped and auto-wrapped painters split the text by width or carriage returns; and the textfield painter reuses the base text paint before drawing the editable cvar string with cursor and paint-offset handling. The call graph and struct offsets line up directly with `Item_SetTextExtents`, `Item_TextColor`, `Item_Text_AutoWrapped_Paint`, `Item_Text_Wrapped_Paint`, `Item_Text_Paint`, and `Item_TextField_Paint`.
- `FUN_100181a0`, `FUN_10018280`, and `FUN_10018370` match the retail multi-choice helper chain. `FUN_100181a0` returns the current numeric-or-string-backed multi index with a retail default of zero, `FUN_10018280` returns the matching display label or the empty-string global, and `FUN_10018370` advances the current selection and writes back the next string or numeric cvar value when the item is focused and activated.
- `FUN_10018510`, `FUN_100185d0`, and `FUN_10018680` are the corresponding preset-list helpers. The first returns the current preset-list label or the retail `"Custom"` fallback, the second returns the matching preset index or `-1`, and the third advances the preset-list selection while applying the linked hidden preset item's cvar set.
- The already-landed `FUN_1001ced0` dispatch table gives stable type-slot anchors for the paint helpers around it. Inside that dispatcher, `case 0x0c` calls `FUN_1001ad40`, whose body immediately resolves the current label through `FUN_10018280`, making `Item_Multi_Paint` exact; `case 0x10` calls `FUN_1001af00`, whose body resolves the current label through `FUN_10018510`, making `Item_PresetList_Paint` exact; and `case 0x0a` calls `FUN_1001b3d0`, whose body uses the already-landed `FUN_10017410` slider-thumb helper, making `Item_Slider_Paint` exact.
- `FUN_1001b7c0`, `FUN_1001b9e0`, `FUN_1001bfb0`, and `FUN_1001ca50` match the retail bind, listbox, and ownerdraw layer by their direct use of binding-string helpers, key-capture globals, feeder callbacks, selection-scroll state, ownerdraw value callbacks, and the already-landed text-paint helper chain. The neighboring `FUN_1001bc30` is instead the model-preview refdef and scene path, which makes it the true `Item_Model_Paint`.
- `FUN_100180a0` is a direct match for `Item_YesNo_HandleKey` because it uses the same focused hit-test and mouse or enter toggle path as the GPL helper.

## Fourteenth-Pass Additions

This pass lands the next clean `ui_shared.c` runtime tranche around hit testing, yes-no and slider-color paint, and the controls binding-table maintenance helpers. All seven names are backed by stable `FUN_...` anchors in `functions.csv`, direct source matches in `ui_shared.c`, and corroborating retail callsite evidence from the already-landed item paint and bind handling paths.

Landed names:

- `FUN_10015c00` -> `Rect_ContainsPoint`
- `FUN_1001ab30` -> `Item_YesNo_Paint`
- `FUN_1001b0c0` -> `Controls_GetConfig`
- `FUN_1001b1e0` -> `Controls_SetConfig`
- `FUN_1001b250` -> `BindingIDFromName`
- `FUN_1001b2a0` -> `BindingFromName`
- `FUN_1001b5c0` -> `Item_SliderColor_Paint`

Representative evidence:

- `FUN_10015c00` is the tiny rect hit-test helper reused by the already-landed `Item_YesNo_HandleKey`, `Menu_HandleMouseMove`, `Display_CaptureItem`, `Display_CursorType`, and `Menu_OverActiveItem` paths. Its null-rect guard and strict `x` and `y` bound tests are an exact match for `Rect_ContainsPoint`.
- `FUN_1001ab30` reads the bound cvar value through the retail display context, selects between the two adjacent string literals used for the yes-no labels, applies the same focus-pulse color path seen in other item text painters, and draws the result beside the item label. That is a direct structural match for `Item_YesNo_Paint`.
- `FUN_1001b0c0`, `FUN_1001b1e0`, `FUN_1001b250`, and `FUN_1001b2a0` form the full controls-binding maintenance cluster from `ui_shared.c`. The first refreshes `g_bindings` from live key assignments, the second writes both slots back through the retail binding callback and appends `in_restart`, the third resolves a command name to its binding-table index, and the fourth formats the uppercase `bind1 or bind2` display string with the retail `???` fallback.
- `FUN_1001b5c0` is the Quake Live specific slider-color painter rather than the older GPL model-preview path. The retail `Item_Paint` dispatcher routes type `0x0e` (`ITEM_TYPE_SLIDER_COLOR`) to this body, and the body itself mirrors the slider painter by drawing the bar first, reusing the already-landed `Item_Slider_ThumbPosition`, and then colorizing the thumb through the same focus-color pulse path used by adjacent text items.
- `FUN_10020740` still remains documented-only. The committed HLIL continues to prove only the `menu == NULL` routing branch of `Display_MouseMove`, not the source drag branch that mutates `menu->window.rectClient` and calls `Menu_UpdatePosition`.

## Fifteenth-Pass Additions

This pass lands the next source-backed layout and animation helper slice in `ui_shared.c`: the menu child-position refresh helper plus the two named item-animation setup helpers behind the already-landed `transition` and `orbit` script handlers.

Landed names:

- `FUN_100159a0` -> `Menu_UpdatePosition`
- `FUN_100165e0` -> `Menu_TransitionItemByName`
- `FUN_100168a0` -> `Menu_OrbitItemByName`

Representative evidence:

- `FUN_100159a0` is called immediately after successful retail menu parse in the same path that already inlines the fullscreen post-parse rect initialization. Its body computes the menu border-adjusted origin, walks `menu->items`, and rebuilds each child item's screen rect from the child `rectClient` fields while clearing cached text extents. That is the core `Menu_UpdatePosition` behavior from `ui_shared.c`, even though the fullscreen branch is inlined in the retail caller rather than kept in a separate `Menu_PostParse` wrapper.
- `FUN_100165e0` is an exact structural match for `Menu_TransitionItemByName`. It uses the already-landed `Menu_ItemsMatchingGroup` and `Menu_GetMatchingItemByNumber` helpers, marks matching items with the retail visible and in-transition flags, writes `offsetTime`, seeds both source and destination rect state, computes the per-axis step amounts from the transition delta over `amt`, and finishes by calling the already-landed `Item_UpdatePosition`.
- `FUN_100168a0` is the matching orbit helper. It again walks the matching item set, marks each item visible plus orbiting, writes `offsetTime`, stores the orbit center in `rectEffects`, stores the starting `x` and `y` in `rectClient`, and refreshes screen coordinates through `Item_UpdatePosition`. That is a direct match for `Menu_OrbitItemByName`.
- `FUN_10020740` still remains documented-only. The committed HLIL continues to prove only the null-menu routing branch of `Display_MouseMove`, so the separate drag-path callsite that would strengthen `Menu_UpdatePosition` even further is still not committed in a stable raw-name form.

## Sixteenth-Pass Additions

This pass reanchors the previously landed runtime widget tranche against the committed retail `menudef.h` item-type extensions and lands the remaining menu-level preset synchronization helper. The key retail evidence is that `ITEM_TYPE_SLIDER_COLOR`, `ITEM_TYPE_PRESET`, and `ITEM_TYPE_PRESETLIST` are present in both committed `menudef.h` copies, `FUN_10019350` dispatches on `item->type - 1`, and `FUN_1001ced0` dispatches directly on `item->type`, which together pin the nearby helper bodies to their true retail slots.

Landed and corrected names:

- `FUN_100156b0` -> `Menu_UpdatePresetLists`
- `FUN_100181a0` -> `Item_Multi_FindCvarByValue`
- `FUN_10018280` -> `Item_Multi_Setting`
- `FUN_10018510` -> `Item_PresetList_Setting`
- `FUN_100185d0` -> `Item_PresetList_FindCvarByValue`
- `FUN_10018680` -> `Item_PresetList_HandleKey`
- `FUN_1001ad40` -> `Item_Multi_Paint`
- `FUN_1001af00` -> `Item_PresetList_Paint`
- `FUN_1001b5c0` -> `Item_SliderColor_Paint`
- `FUN_1001bc30` -> `Item_Model_Paint`
- `FUN_1001bfb0` -> `Item_ListBox_Paint`

Representative evidence:

- The committed retail headers in `src/ui/menudef.h` and `assets/quakelive/baseq3/ui/menudef.h` expose the otherwise absent GPL item types `14`, `15`, and `16` as `ITEM_TYPE_SLIDER_COLOR`, `ITEM_TYPE_PRESET`, and `ITEM_TYPE_PRESETLIST`. That closes the earlier source-biased gap that had pulled several nearby runtime helpers onto the wrong labels.
- `FUN_10019350` subtracts one from `item->type` before switching, which makes `case 0x0a` the yes-no handler, `case 0x0b` the multi handler, `case 0x0c` the bind handler, and `case 0x0f` the preset-list handler. That validates `FUN_100180a0` as yes-no, keeps `FUN_10018370` as multi, and anchors `FUN_10018680` as the retail preset-list key path rather than a generalized multi helper.
- `FUN_1001ced0` switches directly on `item->type`, so `case 0x0c` is the multi painter, `case 0x0e` is the slider-color painter, `case 0x10` is the preset-list painter, `case 7` is the model painter, and `case 6` is the listbox painter. The neighboring bodies agree: `FUN_1001bc30` builds the refdef and scene for a preview model, while the much larger `FUN_1001bfb0` walks feeder rows, scrollbars, and selection state exactly like the retail listbox layer.
- `FUN_100156b0` scans each menu item for retail type `0x10` (`ITEM_TYPE_PRESETLIST`), resolves the currently selected linked preset by name through the already-landed `Menu_FindItemByName`, compares each linked preset cvar against the live display-context value, and writes the retail `"Custom"` fallback when no linked preset still matches. That makes it a menu-level preset-list synchronization helper rather than a generic paint or parse routine.
- `FUN_100154e0` and `FUN_100155a0` remain held back. They clearly sit beside this same retail-only runtime band, but the committed evidence still only proves that they manage a specific ownerdraw or cinematic-style item path, not yet a clean public-facing helper name.

## Seventeenth-Pass Additions

This pass promotes the first native export-table tranche from documented inference into the committed UI symbol set. The key retail anchor is `dllEntry` at `0x10003970`, which returns `&data_1002aea4` and reports API version `8`; the table entries at `0x1002aea4` through `0x1002aec8` line up with the expected UI entry surface from `ui_main.c`, so the slot identity is stable even though `functions.csv` does not expose these addresses as `FUN_...` rows.

Landed names:

- `sub_10002ac0` -> `UI_ConsoleCommand`
- `sub_10003910` -> `UI_HasUniqueCDKey`
- `sub_10004390` -> `_UI_Refresh`
- `sub_100044e0` -> `_UI_Shutdown`
- `sub_1000ff40` -> `_UI_KeyEvent`
- `sub_10010000` -> `_UI_MouseEvent`
- `sub_100100d0` -> `_UI_SetActiveMenu`

Representative evidence:

- `dllEntry` stores `&data_1002aea4` in the caller-provided export-table pointer and writes API version `8`. The first nine table slots are `sub_1000fab0`, `0x100044e0`, `sub_1000ff40`, `sub_10010000`, `sub_10004390`, `sub_10010380`, `sub_100100d0`, `sub_10002ac0`, and `sub_10010e30`, which align exactly with the native UI entry order `_UI_Init`, `_UI_Shutdown`, `_UI_KeyEvent`, `_UI_MouseEvent`, `_UI_Refresh`, `_UI_IsFullscreen`, `_UI_SetActiveMenu`, `UI_ConsoleCommand`, and `UI_DrawConnectScreen`.
- `sub_100044e0` is a tail jump through the syscall table slot used by `trap_LAN_SaveCachedServers`, and the committed source body of `_UI_Shutdown` is nothing more than that syscall. This is stronger than a shape-only match.
- `sub_1000ff40` follows the focused-menu key path from `ui_shared.c`: it queries `Menu_GetFocused`, routes keys into `Menu_HandleKey`, special-cases `ESC` with the `Menus_AnyFullScreenVisible` check, and otherwise clears `KEYCATCH_UI`, key states, and `cl_paused` when no focused menu remains.
- `sub_10010000` accumulates cursor deltas into the cached display context, clamps them to `0..640` and `0..480`, and calls the already-documented `Display_MouseMove` wrapper when menus are present. That is the native `_UI_MouseEvent` behavior.
- `sub_100100d0` is the `UIMENU_*` dispatcher. Its switch covers the close path, the `main`, `team`, `postgame`, `ingame`, and `joingame_menu` activations, the `cl_paused` updates, the non-ingame menu reload path, and the retail `error_popmenu` branch, which matches `_UI_SetActiveMenu`.
- `sub_10004390` advances `realtime`, updates rolling FPS history, calls the already-landed `UI_UpdateCvars`, paints menus through `Menu_PaintAll`, kicks `UI_DoServerRefresh` and the browser status builders, and finally draws the cursor. That is the full `_UI_Refresh` entrypoint.
- `sub_10002ac0` reads the first console token and dispatches the retail UI command set `listPlayerModels`, `ui_report`, `ui_load`, `postgame`, `ui_cache`, `menu_close`, and `menu_open`, matching `UI_ConsoleCommand`.
- `sub_10003910` simply returns `1` from the export-table slot immediately following `UI_DrawConnectScreen`, which matches the old `UI_HASUNIQUECDKEY` behavior preserved in the source export enum.

## Eighteenth-Pass Additions

This pass extends the committed UI map through the core server-browser and player-list runtime slice in `ui_main.c`, using exact source matches cross-checked against the retail HLIL. The landed functions are stable because each one has either distinctive string anchors, a unique control-flow shape, or both.

Landed names:

- `FUN_100038c0` -> `UI_GetBotNameByNumber`
- `FUN_10008b60` -> `UI_BuildPlayerList`
- `FUN_10008e90` -> `UI_DrawSelectedPlayer`
- `FUN_10008f20` -> `UI_DrawServerRefreshDate`
- `FUN_10009080` -> `UI_DrawServerMOTD`
- `FUN_1000d630` -> `UI_InsertServerIntoDisplayList`
- `FUN_1000d670` -> `UI_RemoveServerFromDisplayList`
- `FUN_1000d6c0` -> `UI_BinaryServerInsertion`
- `FUN_1000d740` -> `UI_BuildServerDisplayList`
- `FUN_1000da60` -> `UI_SortServerStatusInfo`
- `FUN_1000db60` -> `UI_GetServerStatusInfo`
- `FUN_1000deb0` -> `UI_BuildFindPlayerList`
- `FUN_1000e3b0` -> `UI_BuildServerStatus`

Representative evidence:

- `FUN_100038c0` prints `^1Invalid bot number: %i\n`, looks up bot info through the existing bot-info helpers, and falls back to `"Sarge"` when no valid record is present. That is an exact match for `UI_GetBotNameByNumber` from `ui_gameinfo.c`.
- `FUN_10008b60` iterates player configstrings, records player and team names, updates `cg_selectedPlayerName`, and is also called from the `_UI_SetActiveMenu` ingame path. The control flow matches `UI_BuildPlayerList`.
- `FUN_10008e90` refreshes the cached player list every 3000 ms and paints either `"cg_selectedPlayerName"` or `"name"`, which uniquely identifies `UI_DrawSelectedPlayer`.
- `FUN_10008f20` switches between the pulsing `"Getting info for %d servers (ESC to cancel)"` status and the formatted `"Refresh Time: %s"` string, matching `UI_DrawServerRefreshDate`.
- `FUN_10009080` scrolls `cl_motdString` across the destination rect, falls back to `"Welcome to Team Arena!"`, and performs the dual draw needed for wraparound. That is `UI_DrawServerMOTD`.
- `FUN_1000d630`, `FUN_1000d670`, and `FUN_1000d6c0` are the three contiguous display-list helpers: insert at position by shifting entries, remove a matching server and compact the array, then binary-search the sorted list through `trap_LAN_CompareServers` before inserting. Their bodies match `UI_InsertServerIntoDisplayList`, `UI_RemoveServerFromDisplayList`, and `UI_BinaryServerInsertion` exactly.
- `FUN_1000d740` loads `cl_motdString`, installs the `"Welcome to Team Arena!"` fallback, resets the visible counters on force, calls `Menu_SetFeederSelection(NULL, FEEDER_SERVERS, 0, NULL)`, marks server visibility through the LAN trap table, filters empty/full/gametype/basedir rows, deduplicates favorites, and inserts visible servers into the display list. This is a direct match for `UI_BuildServerDisplayList`.
- `FUN_1000da60` walks the static promoted server-status cvar table, swaps named lines to the front, and remaps `g_gametype` numbers through the Quake Live gametype-name array, matching `UI_SortServerStatusInfo`.
- `FUN_1000db60` zeroes the destination struct, calls the server-status trap, seeds the `"Address"` line, tokenizes the cvar and player rows in-place, appends the `"num" / "score" / "ping" / "name"` header, and then calls the sort helper. That is the full `UI_GetServerStatusInfo` body.
- `FUN_1000deb0` is the asynchronous find-player worker: it reads and cleans `ui_findPlayer`, sets `cl_serverStatusResendTime`, resets outstanding status probes, scans returned server-status lines for matching player names, updates the `"searching %d/%d..."` progress line, and finishes with either `"no servers found"` or the `%d server%s found with player %s` summary. This matches `UI_BuildFindPlayerList`.
- `FUN_1000e3b0` is the selected-server status refresh path. It early-outs while a find-player refresh is active, resets the feeder and pending requests on force, calls `FUN_1000db60` for the current server address, and either clears or schedules the next refresh. That is `UI_BuildServerStatus`.

## Nineteenth-Pass Additions

This pass extends the committed UI map through the low-address shared string and infostring helpers plus the native callback block installed by `_UI_Init`. Every landed name in this tranche is backed by at least two strong signals: either exact shared-source string matches plus control-flow parity, or exact callback-slot identity in the `_UI_Init` table plus a matching reconstructed source body.

Landed names:

- `FUN_10001750` -> `Q_strncpyz`
- `FUN_10001830` -> `Com_sprintf`
- `FUN_10001900` -> `va`
- `FUN_10001940` -> `Info_ValueForKey`
- `FUN_10001a60` -> `Info_RemoveKey`
- `FUN_10001b80` -> `Info_SetValueForKey`
- `FUN_10001e70` -> `Com_Error`
- `FUN_10001ee0` -> `Com_Printf`
- `FUN_10001f50` -> `UI_Cvar_VariableString`
- `FUN_10003070` -> `UI_ParseInfos`
- `sub_10006950` -> `UI_OwnerDrawWidth`
- `FUN_10009d30` -> `UI_OwnerDrawVisible`
- `FUN_1000a820` -> `UI_OwnerDrawHandleKey`
- `sub_1000a980` -> `UI_GetValue`
- `sub_1000d2f0` -> `UI_GetTeamColor`
- `sub_1000e470` -> `UI_FeederCount`
- `sub_1000e640` -> `UI_FeederItemImage`
- `sub_1000ea80` -> `UI_FeederItemText`
- `FUN_1000eba0` -> `UI_FeederSelection`
- `sub_1000f7b0` -> `UI_Pause`

Representative evidence:

- The low-address helper cluster matches `src/code/game/q_shared.c` exactly. `FUN_10001750` carries the same `Q_strncpyz: NULL dest`, `Q_strncpyz: NULL src`, and `Q_strncpyz: destsize < 1` fatal strings before doing the bounded copy and forced terminator write, which is a direct match for `Q_strncpyz`. `FUN_10001830` uses `vsprintf` into the same oversized temporary buffer and reports `Com_sprintf: overflowed bigbuffer`, which pins `Com_sprintf`. `FUN_10001900` alternates the same two fixed scratch buffers as `va`.
- The three infostring helpers are equally explicit. `FUN_10001940` parses `\\key\\value` pairs with alternating static return buffers and carries the same oversize-string diagnostic path as `Info_ValueForKey`. `FUN_10001a60` emits `Info_RemoveKey: oversize infostring`, and `FUN_10001b80` rejects `'\\'`, `';'`, and `'"'`, removes any existing key, and appends the new `\\key\\value` pair exactly like `Info_SetValueForKey`.
- `FUN_10001e70` and `FUN_10001ee0` format through the same shared varargs helper and then dispatch through the UI syscall table's error and print slots. That matches the native `Com_Error` and `Com_Printf` wrappers used by the UI DLL.
- `FUN_10001f50` is the retail `UI_Cvar_VariableString` helper from `ui_atoms.c`: it calls the cvar-string syscall with the shared `0x400`-byte scratch buffer at `data_10042f38` and returns that buffer.
- `FUN_10003070` is a direct source match for `UI_ParseInfos` from `ui_gameinfo.c`. The HLIL carries the exact `Missing { in info file\n`, `Max infos exceeded\n`, and `Unexpected end of info file\n` parse guards, then allocates and stores each completed info-string record with the appended `\\num\\` field.
- `_UI_Init` provides stable callback identity for the runtime helper tranche. The committed HLIL stores `sub_1000a980`, `FUN_10009d30`, `sub_1000d2f0`, `FUN_1000a820`, `sub_1000e470`, `sub_1000e640`, `sub_1000ea80`, `FUN_1000eba0`, `sub_1000f7b0`, and `sub_10006950` into the `uiInfo.uiDC` callback block in the exact slots used by `UI_GetValue`, `UI_OwnerDrawVisible`, `UI_GetTeamColor`, `UI_OwnerDrawHandleKey`, `UI_FeederCount`, `UI_FeederItemImage`, `UI_FeederItemText`, `UI_FeederSelection`, `UI_Pause`, and `UI_OwnerDrawWidth`.
- The reconstructed source then corroborates those slot assignments. `UI_OwnerDrawVisible`, `UI_OwnerDrawHandleKey`, `UI_FeederCount`, `UI_FeederItemImage`, `UI_FeederItemText`, `UI_FeederSelection`, `UI_OwnerDrawWidth`, and `UI_Pause` all have matching bodies in `src/code/ui/ui_main.c`, while `UI_GetValue` and `UI_GetTeamColor` are both deliberate stubs in the source and in the native retail code.

## Twentieth-Pass Additions

This pass clears the remaining high-confidence ownerdraw control band around `FUN_1000a040` through `FUN_1000acf0` and promotes the retail crosshair widgets from the draw-side dispatcher. The new names come from three converging signals: exact `UI_OwnerDrawHandleKey` slot identity for the control handlers, exact `UI_OwnerDraw` slot identity for the crosshair widgets, and direct body matches against the reconstructed `ui_main.c` loaders and handlers.

Landed names:

- `FUN_10006c60` -> `UI_DrawCrosshair`
- `FUN_10009660` -> `UI_DrawCrosshairColor`
- `FUN_1000a040` -> `UI_Handicap_HandleKey`
- `FUN_1000a110` -> `UI_GameType_HandleKey`
- `FUN_1000a210` -> `UI_NetGameType_HandleKey`
- `FUN_1000a300` -> `UI_JoinGameType_HandleKey`
- `FUN_1000a390` -> `UI_Skill_HandleKey`
- `FUN_1000a420` -> `UI_NetSource_HandleKey`
- `FUN_1000a4f0` -> `UI_NetFilter_HandleKey`
- `FUN_1000a570` -> `UI_BotName_HandleKey`
- `FUN_1000a5d0` -> `UI_BotSkill_HandleKey`
- `FUN_1000a640` -> `UI_Crosshair_HandleKey`
- `FUN_1000a6c0` -> `UI_SelectedPlayer_HandleKey`
- `FUN_1000a790` -> `UI_CrosshairColor_HandleKey`
- `FUN_1000a9d0` -> `UI_LoadMods`
- `FUN_1000ac00` -> `UI_LoadMovies`
- `FUN_1000acf0` -> `UI_LoadDemos`

Representative evidence:

- `FUN_1000a820`, already landed as `UI_OwnerDrawHandleKey`, is the primary control anchor. Its switch dispatches ownerdraw `513`, `515`, `517`, `518`, `520`, `531`, `532`, `534`, `535`, `537`, `545`, and `550` to `FUN_1000a040`, `FUN_1000a110`, `FUN_1000a390`, `FUN_1000a420`, `FUN_1000a4f0`, `FUN_1000a570`, `FUN_1000a5d0`, `FUN_1000a640`, `FUN_1000a6c0`, `FUN_1000a210`, `FUN_1000a300`, and `FUN_1000a790`. Those numeric ids match `UI_HANDICAP`, `UI_GAMETYPE`, `UI_SKILL`, `UI_NETSOURCE`, `UI_NETFILTER`, `UI_BOTNAME`, `UI_BOTSKILL`, `UI_CROSSHAIR`, `UI_SELECTEDPLAYER`, `UI_NETGAMETYPE`, `UI_JOINGAMETYPE`, and the retail-only `UI_CROSSHAIR_COLOR` in the committed Quake Live `menudef.h`.
- The handler bodies then match the source exactly. `FUN_1000a040` clamps and wraps `"handicap"` in 5-point steps. `FUN_1000a110` advances `ui_gameType`, skips the old hole at index `2`, refreshes limits and best scores, and resets the map feeder when the visible map count changes. `FUN_1000a210` advances `ui_netGameType` while skipping actual gametype enums `6`, `7`, and `8`, updates both `ui_netGameType` and `ui_actualnetGameType`, resets `ui_currentNetMap`, and refreshes the feeder. `FUN_1000a300`, `FUN_1000a390`, `FUN_1000a420`, and `FUN_1000a4f0` are direct matches for the join-gametype, single-player skill, net-source, and net-filter handlers from `ui_main.c`.
- `FUN_1000a570`, `FUN_1000a5d0`, `FUN_1000a640`, and `FUN_1000a6c0` likewise have exact control-flow matches for the bot-name, bot-skill, crosshair, and selected-player handlers. `FUN_1000a6c0` is especially strong because it calls the already-landed `UI_BuildPlayerList`, checks the team-leader flag, writes `"Everyone"` into `cg_selectedPlayerName` for the terminal slot, and updates both selected-player cvars exactly like `UI_SelectedPlayer_HandleKey`.
- `FUN_1000a790` is a retail-only addition. The committed source does not yet expose a separate `UI_CrosshairColor_HandleKey`, but the evidence is still high confidence: `FUN_1000a820` routes ownerdraw `550` (`UI_CROSSHAIR_COLOR`) into `FUN_1000a790`, and that body only reads, wraps, and rewrites `cg_crosshairColor` over the Quake Live numbered palette range.
- On the draw side, `FUN_100097b0` dispatches ownerdraw `534` directly to `FUN_10006c60` and ownerdraw `550` directly to `FUN_10009660`. `FUN_10006c60` draws the selected crosshair shader after applying retail `cg_crosshairSize`, `cg_crosshairBrightness`, `cg_crosshairHealth`, and `cg_crosshairColor` handling, so it is the stronger retail form of `UI_DrawCrosshair`. `FUN_10009660` paints the horizontal color bar and selection swatch keyed off `cg_crosshairColor`, making `UI_DrawCrosshairColor` the stable retail-facing name.
- `FUN_1000a9d0`, `FUN_1000ac00`, and `FUN_1000acf0` are exact source matches for `UI_LoadMods`, `UI_LoadMovies`, and `UI_LoadDemos`. The native bodies enumerate `$modlist`, `"video" / ".roq"`, and `"demos" / ".dm_%d"` respectively, then strip or split names, uppercase the movie and demo entries, and intern the resulting feeder strings just like the committed `ui_main.c` implementations.
- One retail delta remains intentionally undocumented-only as a separate function name: there is still no standalone `UI_RedBlue_HandleKey` body in the committed Ghidra function index. The native `UI_OwnerDrawHandleKey` inlines the `uiInfo.redBlue ^= 1` toggle for ownerdraw `533` and then falls through into the crosshair handler path, so only the standalone helper bodies with stable addresses were landed in this pass.

## Twenty-First-Pass Additions

This pass clears a text-centric ownerdraw tranche directly under `FUN_100097b0`. The new names are all backed by the same two primary signals: exact ownerdraw slot identity from the retail `UI_OwnerDraw` switch and exact or near-exact body matches against the reconstructed `ui_main.c` draw helpers.

Landed names:

- `FUN_10005100` -> `UI_DrawHandicap`
- `FUN_10005220` -> `UI_DrawGameType`
- `FUN_10005260` -> `UI_DrawNetGameType`
- `FUN_100052e0` -> `UI_DrawJoinGameType`
- `FUN_10005350` -> `UI_DrawSkill`
- `FUN_10006550` -> `UI_DrawNetSource`
- `FUN_100066d0` -> `UI_DrawNetFilter`
- `FUN_100068f0` -> `UI_DrawOpponentName`
- `FUN_10006b30` -> `UI_DrawBotName`
- `FUN_10006bc0` -> `UI_DrawBotSkill`
- `FUN_10006c10` -> `UI_DrawRedBlue`

Representative evidence:

- The already-landed `FUN_100097b0` / `UI_OwnerDraw` is the primary anchor. Its switch routes ownerdraw `513`, `515`, `517`, `518`, `520`, `529`, `531`, `532`, `533`, `537`, and `545` to `FUN_10005100`, `FUN_10005220`, `FUN_10005350`, `FUN_10006550`, `FUN_100066d0`, `FUN_100068f0`, `FUN_10006b30`, `FUN_10006bc0`, `FUN_10006c10`, `FUN_10005260`, and `FUN_100052e0`. Those numeric ids line up with `UI_HANDICAP`, `UI_GAMETYPE`, `UI_SKILL`, `UI_NETSOURCE`, `UI_NETFILTER`, `UI_OPPONENT_NAME`, `UI_BOTNAME`, `UI_BOTSKILL`, `UI_REDBLUE`, `UI_NETGAMETYPE`, and `UI_JOINGAMETYPE` in the committed Quake Live `menudef.h`.
- `FUN_10005100` is an exact retail `UI_DrawHandicap` match: it reads `"handicap"`, clamps the value into the same `5..100` range, indexes the static handicap label table, and then paints the selected string through `Text_Paint`.
- `FUN_10005220`, `FUN_10005260`, `FUN_100052e0`, and `FUN_10005350` are the same compact table-backed draw helpers visible in `src/code/ui/ui_main.c`. The net and join variants preserve the same out-of-range cvar reset paths for `ui_netGameType`, `ui_actualNetGameType`, and `ui_joinGameType`, while the skill helper clamps `g_spSkill` into the same `1..5` band before indexing the skill-level string table.
- `FUN_10006550` and `FUN_100066d0` are pinned by their format strings as well as their slot ids: the bodies build `"Source: %s"` and `"Filter: %s"` through the retail `va` helper before painting them, which exactly matches `UI_DrawNetSource` and `UI_DrawNetFilter`.
- `FUN_100068f0`, `FUN_10006b30`, `FUN_10006bc0`, and `FUN_10006c10` line up cleanly with the remaining text helpers. `FUN_100068f0` fetches `"ui_opponentName"` into the shared UI cvar buffer and paints it directly. `FUN_10006b30` preserves the same invalid-bot fallback path to `"Sarge"` while resolving the current bot label. `FUN_10006bc0` indexes the retail skill-level table from the current bot-skill selection. `FUN_10006c10` chooses between the same `"Red"` and `"Blue"` strings used by `UI_DrawRedBlue`.
- This pass intentionally leaves the adjacent image, cinematic, and multi-line ownerdraw helpers for follow-up work. The next strongest nearby candidates are `FUN_100065b0`, `FUN_100092f0`, `FUN_100093b0`, `FUN_10006ea0`, `FUN_10006f30`, `FUN_10005850`, `FUN_10005c20`, `FUN_10005ff0`, `FUN_100062a0`, `FUN_10007030`, and `FUN_10008730`.

## Twenty-Second-Pass Additions

This pass lands the remaining highest-confidence display-information helper from the ownerdraw layer: the retail GL diagnostics painter behind ownerdraw `541`.

Landed names:

- `FUN_100093b0` -> `UI_DrawGLInfo`

Representative evidence:

- The already-landed `FUN_100097b0` / `UI_OwnerDraw` is again the primary anchor. Its switch routes ownerdraw `541` directly to `FUN_100093b0`, which matches `UI_GLINFO` in the committed `menudef.h` and the `UI_OwnerDraw` switch in `src/code/ui/ui_main.c`.
- The native body is an exact behavioral match for `UI_DrawGLInfo`. It formats and paints the same `VENDOR: %s`, `VERSION: %s: %s`, and `PIXELFORMAT: color(%d-bits) Z(%d-bits) stencil(%d-bits)` lines, then copies the GL extensions string into a local buffer, splits it on spaces, and repaints wrapped extension lines inside the available rect exactly like the reconstructed source.
- This saturated the old `348`-function counter previously carried by `ui.json`, but it did not exhaust the broader HLIL and runtime-helper backlog. The next pass rebases that accounting against the full committed Ghidra-plus-HLIL address union.

## Twenty-Third-Pass Additions

This pass lands the remaining high-confidence ownerdraw preview and status tranche while correcting the `ui.json` coverage accounting to match the actual committed corpus. The new percentage baseline is now the combined address union of the committed `functions.csv` index plus the already-promoted HLIL-only raw anchors.

Landed names:

- `FUN_100053c0` -> `UI_DrawMapPreview`
- `FUN_100054a0` -> `UI_DrawMapTimeToBeat`
- `FUN_10005560` -> `UI_DrawMapCinematic`
- `FUN_10005690` -> `UI_DrawPlayerModel`
- `FUN_10005850` -> `UI_DrawTeamPlayerModel`
- `FUN_10005c20` -> `UI_DrawEnemyPlayerModel`
- `FUN_10005ff0` -> `UI_DrawRedTeamModel`
- `FUN_100062a0` -> `UI_DrawBlueTeamModel`
- `FUN_100065b0` -> `UI_DrawNetMapPreview`
- `FUN_10006600` -> `UI_DrawNetMapCinematic`
- `FUN_10006730` -> `UI_DrawOpponent`
- `FUN_10006ea0` -> `UI_DrawNextMap`
- `FUN_10006f30` -> `UI_DrawVoteString`
- `FUN_10007030` -> `UI_DrawServerSettings`
- `FUN_10008730` -> `UI_DrawStartingWeapons`
- `FUN_100092f0` -> `UI_DrawKeyBindStatus`

Representative evidence:

- `FUN_100097b0` / `UI_OwnerDraw` remains the primary slot anchor. Its switch routes ownerdraw `516`, `536`, `519`, `538`, `522`, `551`, `552`, `553`, `554`, `555`, `556`, `557`, and `558` directly into `FUN_100053c0`, `FUN_10005560`, `FUN_100065b0`, `FUN_10006600`, `FUN_10006730`, `FUN_10006ea0`, `FUN_10006f30`, `FUN_10005850`, `FUN_10005c20`, `FUN_10005ff0`, `FUN_100062a0`, `FUN_10007030`, and `FUN_10008730`. Those ids line up with `UI_MAPPREVIEW`, `UI_MAPCINEMATIC`, `UI_NETMAPPREVIEW`, `UI_NETMAPCINEMATIC`, `UI_OPPONENTMODEL`, `UI_NEXTMAP`, `UI_VOTESTRING`, `UI_TEAMPLAYERMODEL`, `UI_ENEMYPLAYERMODEL`, `UI_REDTEAMMODEL`, `UI_BLUETEAMMODEL`, `UI_SERVER_SETTINGS`, and `UI_STARTING_WEAPONS` in the committed Quake Live `menudef.h`.
- `FUN_100054a0`, `FUN_10005690`, `FUN_100065b0`, `FUN_10006600`, `FUN_10006730`, and `FUN_100092f0` are exact source matches. They carry the same `%02i:%02i` time-to-beat format, the same model/headmodel player preview rebuild, the same unknown-map fallback, the same net-map cinematic fallback path, the same opponent-model preview rebuild, and the same keybind status strings visible in `src/code/ui/ui_main.c`.
- The team and enemy preview quartet is pinned by both slot identity and cvar usage. `FUN_10005850`, `FUN_10005c20`, `FUN_10005ff0`, and `FUN_100062a0` each read the exact model/skin/color cvar families implied by their ownerdraw ids: `cg_forceTeamModel` plus team colors, `cg_forceEnemyModel` plus enemy colors, `cg_forceRedTeamModel`, and `cg_forceBlueTeamModel`.
- The retail-only status widgets are equally explicit. `FUN_10006f30` reads `ui_votestring`, measures its width, centers it, and paints it, which cleanly lands `UI_DrawVoteString`. `FUN_10007030` renders the settings panel used by `UI_SERVER_SETTINGS`, including `Unknown Gametype`, `Time Limit: %i`, `Frag Limit: %i`, `Capture Limit: %i`, `Air Control`, `Ramp Jumping`, `Tiered Armor`, `Weapon Switching`, `Physics`, `Gravity %i`, `Regen Health`, `Drop Health`, `Vampiric Damage`, `Item Spawning`, `Headshots`, `Rail Jumping`, `Default Settings`, and `MODIFIED WEAPONS:`. `FUN_10008730` then paints the starting-weapon icon strip and queued-primary label used by `UI_STARTING_WEAPONS`.
- `FUN_10006ea0` is a slot-first landing: ownerdraw `551` is publicly exposed as `UI_NEXTMAP`, and the body fetches a localized string-table entry before painting it into the rect. That is sufficient for the stable public-facing name even though the current committed source does not yet expose a matching GPL-era helper.
- Two map-display helpers retain a documented retail/source delta in their comments but are still stable names. `FUN_100053c0` and `FUN_10005560` are clearly the preview and cinematic drawers for the same ownerdraw family, but the observed retail boolean pathing around `UI_MAPPREVIEW`, `UI_MAPCINEMATIC`, and `UI_STARTMAPCINEMATIC` does not align perfectly with the current reconstructed source's parameter meaning. The public-facing function names are still exact enough to land.
- The `ui.json` coverage block is now normalized to the real committed corpus. Before this rebase, the artifact misleadingly reported `348 / 348` despite still leaving `90` `functions.csv` entries unmapped because the function list already contained `90` HLIL-only `sub_...` anchors. After the rebase, the committed corpus baseline is `438` total anchors: `348` Ghidra-indexed functions plus `90` HLIL-only anchors. This pass moves the curated corpus mapping from `348 / 438` (`79.5%`) to `364 / 438` (`83.1%`), and the Ghidra-indexed subset from `258 / 348` (`74.1%`) to `274 / 348` (`78.7%`).

## Twenty-Fourth-Pass Additions

This pass lands the next clean runtime-helper tranche around the gametype-count logic, the display-scale refresh helper, and the retail per-cvar callback block for force-model brightness and announcer selection.

Landed names:

- `FUN_100051b0` -> `UI_SetCapFragLimits`
- `FUN_1000d300` -> `UI_CVMapCountByGameType`
- `FUN_1000d3c0` -> `UI_MapCountByGameType`
- `FUN_1000f9f0` -> `UI_RefreshDisplayContextScale`
- `FUN_10011510` -> `UI_UpdateForceModelBrightness`
- `FUN_10011630` -> `UI_UpdateForceTeamModelSettings`
- `FUN_10011660` -> `UI_UpdateForceEnemyModelSettings`
- `FUN_10011690` -> `UI_UpdateAnnouncer`

Representative evidence:

- `FUN_100051b0` is an exact retail `UI_SetCapFragLimits` match. The body carries the same default `cap = 5` / `frag = 10` setup, the same `GT_OBELISK -> 4` and `GT_HARVESTER -> 15` overrides, and the same `uiVars` branch that writes either `ui_captureLimit` and `ui_fragLimit` or the live `capturelimit` and `fraglimit` cvars visible in `src/code/ui/ui_main.c`.
- `FUN_1000d3c0` is an exact `UI_MapCountByGameType` match. It clears each map's active flag, tests the current gametype bit, and on the single-player path requires the extra `GT_SINGLE_PLAYER` bit before reactivating the slot and incrementing the visible-map count. The already-landed `UI_GameType_HandleKey` calls it after writing `ui_gameType`, and the already-landed `sub_1000e470` / `UI_FeederCount` routes feeder ids `1` and `4` to this helper, which lines up with `FEEDER_MAPS` and `FEEDER_ALLMAPS`.
- `FUN_1000d300` is the retail sibling for the callvote-map feed. The same `UI_FeederCount` dispatcher routes decimal feeder id `19` to it, which matches `FEEDER_CVMAPS` in the committed Quake Live `menudef.h`. The function toggles the same `mapList[].active` field used by `FUN_1000d3c0`, but it uses the selected or forced callvote gametype state instead of the skirmish/browser gametype. That same override state is later consumed by the `callvote map %s %s\n` script path, which justifies the stable retail-only name `UI_CVMapCountByGameType`.
- `FUN_1000f9f0` is the display-scale refresh helper used during `_UI_Init` and by the still-doc-only `0x10003920` wrapper. It calls the renderer glconfig syscall and then rebuilds the same 640x480 virtual-screen bias and scale values (`bias`, `yscale`, and `xscale`) that are currently computed inline near the top of `_UI_Init` in `src/code/ui/ui_main.c`.
- `FUN_10011510` lowercases two cvar strings, searches both for the token `"bright"`, and writes the resulting `0` or `1` into the caller-selected UI bright-model cvar. The wrappers `FUN_10011630` and `FUN_10011660` bind that shared helper to the exact retail cvar pairs `"cg_forceTeamSkin"` / `"cg_forceTeamModel"` and `"cg_forceEnemySkin"` / `"cg_forceEnemyModel"`, then mark the corresponding preset-dirty globals.
- The retail cvar callback table provides the second anchor for that trio. The table at `0x1002b2bc` through `0x1002b32c` wires `FUN_10011630` to `ui_forceTeamModel` and `ui_forceTeamSkin`, and wires `FUN_10011660` to `ui_forceEnemyModel` and `ui_forceEnemySkin`, while the adjacent entries expose the paired retail toggle cvars `ui_forceTeamModelBright` and `ui_forceEnemyModelBright`.
- `FUN_10011690` is pinned by both strings and callback ownership. The cvar callback table at `0x1002afd8` binds it to `cg_announcer`, and the body plays `sound/misc/vo_default.wav`, `sound/misc/vo_evil.wav`, or `sound/misc/vo_female.wav` based on the selected profile before mirroring the current numeric selection into `ui_announcer`.
- This pass deliberately leaves the older player-model-list helpers around `FUN_1000d490`, `FUN_1000d530`, `FUN_1000f140`, and `FUN_1000f2b0` in the doc-only bucket. Their retail model/skin catalog shape no longer aligns cleanly enough with the current reconstructed source to justify stable public-facing names without a separate dedicated pass.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `364 / 438` (`83.1%`) to `372 / 438` (`84.9%`), and the Ghidra-indexed subset from `274 / 348` (`78.7%`) to `282 / 348` (`81.0%`).

## Twenty-Fifth-Pass Additions

This pass lands a compact but exact shared utility tranche plus the retail helper that converts a selected gametype into the short factory token used by the `callvote map` command path.

Landed names:

- `FUN_10001000` -> `UI_GetCallvoteGametypeToken`
- `FUN_10001400` -> `COM_Compress`
- `FUN_10001500` -> `COM_ParseExt`
- `FUN_100016c0` -> `Q_stricmpn`
- `FUN_10001730` -> `Q_stricmp`

Representative evidence:

- `FUN_10001000` is a stable retail-only callvote helper. HLIL shows a direct switch over gametype values returning the short token strings `"duel"`, `"race"`, `"oneflag"`, and the other factory ids used by Quake Live. The same helper feeds straight into the `callvote map %s %s\n` formatting path at `0x1000c34a`, which anchors the descriptive name `UI_GetCallvoteGametypeToken` without borrowing a misleading GPL-era symbol.
- `FUN_10001400` is an exact `COM_Compress` match against `src/code/game/q_shared.c`. The retail body strips both `//` and `/* */` comments in place, tracks pending newline and whitespace state, emits compressed separators, and copies quoted strings without modification before terminating the destination buffer and returning the new length.
- `FUN_10001500` is an exact `COM_ParseExt` match. Both the Ghidra decompilation and the committed HLIL show the same `allowLineBreaks` gate, the same newline accounting through the shared parse-line counter, the same comment skipping, the same quoted-string path, and the same global token-buffer writeback visible in the current shared game layer.
- `FUN_100016c0` is an exact `Q_stricmpn` match. HLIL shows the same Quake-style null handling, the same decrementing bounded compare, the same lowercase-to-uppercase folding over `a..z`, and the same `-1 / 0 / 1` style return when the first differing character is found.
- `FUN_10001730` is the thin `Q_stricmp` wrapper over `FUN_100016c0`. The retail body returns `Q_stricmpn(arg1, arg3, 99999)` when both input strings are non-null and `-1` otherwise, which matches the current shared implementation exactly.
- This pass intentionally leaves the nearby text-measurement helpers in the doc-only bucket. `FUN_10003d90` is a lower-level retail text-bounds helper that writes width and height through out-parameters, while the committed source exposes split `Text_Width` and `Text_Height` wrappers instead. The adjacent HLIL-only shims at `0x10003e60` and `0x10003e90` likely correspond to those public wrappers, but they are not yet carried by the committed `functions.csv`.
- `FUN_10004280` also stays unlanded. Its renderer state and coordinate adjustment pattern place it in the retail text/icon draw path, but the committed current-source surface is not yet close enough to justify a stable public-facing name without another focused pass.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `372 / 438` (`84.9%`) to `377 / 438` (`86.1%`), and the Ghidra-indexed subset from `282 / 348` (`81.0%`) to `287 / 348` (`82.5%`).

## Twenty-Sixth-Pass Additions

This pass lands an exact shared math-and-string tranche plus the two HLIL-only text-metric wrappers that are assigned into `uiDC` during `_UI_Init`.

Landed names:

- `FUN_10001140` -> `AngleSubtract`
- `FUN_100011c0` -> `MatrixMultiply`
- `FUN_100012a0` -> `AngleVectors`
- `FUN_100017e0` -> `Q_CleanStr`
- `sub_10003e60` -> `Text_Width`
- `sub_10003e90` -> `Text_Height`

Representative evidence:

- `FUN_10001140` is an exact `AngleSubtract` match against `src/code/game/q_math.c`. The retail body computes `a1 - a2`, repeatedly subtracts `360` while the delta is above `180`, repeatedly adds `360` while it is below `-180`, and returns the normalized result. The already-landed player-preview helpers use it in the same animation swing and orientation paths that the current source routes through `AngleSubtract`.
- `FUN_100011c0` is an exact `MatrixMultiply` match. HLIL shows the full nine-output 3x3 multiply, and the same helper is called from the already-landed `UI_PositionEntityOnTag` and `UI_PositionRotatedEntityOnTag` paths in `src/code/ui/ui_players.c`, which use `MatrixMultiply` twice during tag attachment and rotated child-axis composition.
- `FUN_100012a0` is an exact `AngleVectors` match. The retail helper converts Euler angles from degrees to radians, computes `sin` and `cos` for yaw, pitch, and roll, and then conditionally writes the forward, right, and up vectors through the same three optional pointer outputs used by the shared `AngleVectors` implementation in `src/code/game/q_math.c`.
- `FUN_100017e0` is an exact `Q_CleanStr` match against `src/code/game/q_shared.c`. HLIL shows the same in-place walk over the source string, the same `'^'` plus `0..7` color-sequence skip, the same printable-ASCII gate `>= 0x20`, and the same terminating zero writeback. The retail UI uses it in the same player-name, team-name, and server-browser cleanup paths visible in `src/code/ui/ui_main.c`.
- `sub_10003e60` and `sub_10003e90` are exact HLIL-only wrappers over the still-unlanded retail text-bounds helper at `FUN_10003d90`. The first wrapper passes a width out-parameter and returns it, while the second passes a height out-parameter and returns it. `_UI_Init` then stores those two wrapper addresses into `data_10746354` and `data_10746358`, which line up directly with `uiInfo.uiDC.textWidth = &Text_Width` and `uiInfo.uiDC.textHeight = &Text_Height` in the current `src/code/ui/ui_main.c`.
- `FUN_10003d90` itself remains deliberately unlanded. It is a lower-level retail text-bounds helper that writes width and height through out-parameters rather than the split public `Text_Width` and `Text_Height` surface used by the committed source.
- The still-open nearby helpers remain separate work: `FUN_10001090` is clearly the retail weapon-token lookup used by the starting-weapons ownerdraw path, and `FUN_10001670` is clearly a short numeric-string validator, but neither has a strong enough current-source naming anchor yet to justify a stable public alias.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `377 / 438` (`86.1%`) to `383 / 438` (`87.4%`), and the Ghidra-indexed subset from `287 / 348` (`82.5%`) to `291 / 348` (`83.6%`).

## Twenty-Seventh-Pass Additions

This pass lands a small high-confidence runtime-helper tranche: one exact shared math helper, one exact UI-main string helper, one retail text-bounds helper below the already-landed HLIL wrappers, and the two retail-only console-command wrappers behind `menu_open` and `menu_close`.

Landed names:

- `FUN_100010f0` -> `AnglesToAxis`
- `FUN_10002490` -> `UI_ConsoleCommand_MenuClose`
- `FUN_10002520` -> `UI_ConsoleCommand_MenuOpen`
- `FUN_10003d90` -> `Text_GetDimensions`
- `FUN_1000de40` -> `stristr`

Representative evidence:

- `FUN_100010f0` is an exact `AnglesToAxis` match against `src/code/game/q_math.c`. Retail HLIL calls the already-landed `AngleVectors`, writes the forward vector to `axis[0]`, writes the up vector to `axis[2]`, and negates the intermediate right vector into `axis[1]`, exactly matching the shared implementation used by the current player-preview renderer in `src/code/ui/ui_players.c`.
- `FUN_10002490` is the retail-only console-command helper behind `menu_close`. `UI_ConsoleCommand` compares the first token against `"menu_close"` and dispatches here; the helper pulls `argv(1)` into the command scratch buffer, resolves the target through the already-landed `Menus_FindByName`, clears the menu-open state, and then runs the close path through the still-unresolved nearby runtime helper at `FUN_100155a0`.
- `FUN_10002520` is the retail-only console-command helper behind `menu_open`. `UI_ConsoleCommand` dispatches it from the `"menu_open"` string branch, and the helper reads `argv(1)` into the same scratch buffer before forwarding the requested menu name to the already-landed `Menus_ActivateByName`.
- `FUN_10003d90` is the lower retail text-bounds helper that sits underneath the committed `Text_Width` and `Text_Height` surface. Its body refreshes cached text scale when needed, routes through the renderer text-bounds syscall, and writes integer width and height results through out-parameters; the already-landed HLIL-only wrappers at `0x10003e60` and `0x10003e90` each call this helper and return one of those two outputs.
- `FUN_1000de40` is an exact `stristr` match against the static helper in `src/code/ui/ui_main.c`. Retail HLIL walks the haystack one character at a time, compares case-insensitively with `toupper`, and returns the first matching substring pointer or null. The already-landed `UI_BuildFindPlayerList` then uses it in the same find-player browser path as the current source.
- This pass still holds back the nearby low-address unresolved helpers. `FUN_10001090` remains the weapon-token lookup used by the starting-weapons ownerdraw path, and `FUN_10001670` remains the short numeric-string validator used around retail list parsing, but the committed source still does not provide a stable enough public naming anchor for either helper.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `383 / 438` (`87.4%`) to `388 / 438` (`88.6%`), and the Ghidra-indexed subset from `291 / 348` (`83.6%`) to `296 / 348` (`85.1%`).

## Twenty-Eighth-Pass Additions

This pass lands a focused retail runtime tranche around map-selection ownerdraws, the advert ownerdraw, and the teaminfo or player-model parsing path used during UI startup and the `listPlayerModels` console command.

Landed names:

- `FUN_10006890` -> `UI_DrawAllMapsSelection`
- `FUN_10009340` -> `UI_DrawAdvert`
- `FUN_1000e600` -> `UI_SelectedMap`
- `FUN_1000f140` -> `Character_Parse`
- `FUN_1000f2b0` -> `UI_ParseTeamInfo`
- `FUN_1000f960` -> `UI_ListPlayerModels`

Representative evidence:

- `FUN_10006890` is an exact `UI_DrawAllMapsSelection` match from the retail ownerdraw switch. The already-landed `UI_OwnerDraw` routes ownerdraw ids `0x210` and `0x224` to the shared map-selection path; those ids are `UI_ALLMAPS_SELECTION` and `UI_MAPS_SELECTION` in the committed `src/ui/menudef.h`, and the current `src/code/ui/ui_main.c` uses the same shared public helper with the final boolean selecting between the two active selection slots.
- `FUN_10009340` is the retail-only ownerdraw helper behind `UI_ADVERT`. The retail ownerdraw switch dispatches ownerdraw `0x225` here, matching `UI_ADVERT` in the committed `menudef.h`. HLIL shows the helper setting render color, drawing the advert surface through the already-landed picture helper, invoking the advert-update callback in the display context, and then restoring a null render color.
- `FUN_1000e600` is an exact `UI_SelectedMap` match against the current feeder path in `src/code/ui/ui_main.c`. Retail HLIL walks the active map list, translates a visible row index into the backing active-map index through an out-parameter, and returns the selected map name pointer. The already-landed `UI_FeederItemText`, `UI_FeederItemImage`, and `UI_FeederSelection` use the same helper shape and row-to-actual-index conversion.
- `FUN_1000f140` is the retail `Character_Parse` helper for the `characters` section in `teaminfo.txt`. HLIL parses repeated `{ "model" "skin" }` pairs, stores them in the startup character table, forces the cached head image handle to `-1`, and formats `models/players/%s/icon_%s.tga` for each entry. The committed `src/ui/teaminfo.txt` still begins with the same `characters { ... }` section containing model and skin pairs.
- `FUN_1000f2b0` is the retail `UI_ParseTeamInfo` entry point. It loads the menu buffer through the already-landed `GetMenuBuffer`, scans top-level tokens, and dispatches the `characters` block to `FUN_1000f140`. The current source still exposes that public entry point as `UI_ParseTeamInfo`, although the retail helper currently only proves the `characters` branch directly rather than the full modern `teams` and `aliases` handling.
- `FUN_1000f960` is the retail-only helper behind the `listPlayerModels` console command. `UI_ConsoleCommand` compares the command string against `"listPlayerModels"` and dispatches here; the helper refreshes the retail player-model list and prints the currently loaded `model/skin` pairs.
- This pass still holds back the nearby retail player-model filtering helpers at `FUN_1000d490` and `FUN_1000d530`, plus the adjacent advert runtime helpers at `FUN_100154e0` and `FUN_100155a0`. Their roles are clearer now, but the committed source still does not provide stable enough public naming anchors to land them without overcommitting.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `388 / 438` (`88.6%`) to `394 / 438` (`90.0%`), and the Ghidra-indexed subset from `296 / 348` (`85.1%`) to `302 / 348` (`86.8%`).

## Twenty-Ninth-Pass Additions

This pass lands a mixed exact-plus-descriptive runtime tranche around the low-address UI script helpers and the Quake Live advertisement extension seam.

Landed names:

- `FUN_10001090` -> `UI_StartingWeaponIndexFromToken`
- `FUN_10001670` -> `String_IsNumeric`
- `FUN_1000ae50` -> `UI_Update`
- `FUN_100154e0` -> `Menu_SetupAdvertCellShaders`
- `FUN_100155a0` -> `Menu_RefreshAdvertCellShaders`

Representative evidence:

- `FUN_1000ae50` is an exact `UI_Update` match against `src/code/ui/ui_main.c`. Retail HLIL compares the incoming script token against `"ui_SetName"`, `"ui_setRate"`, `"ui_GetName"`, `"r_colorBits"`, and `"ui_mousePitch"`, then performs the same `name` or `ui_Name`, `cl_maxpackets`, `cl_packetdup`, `r_depthBits`, `r_stencilBits`, and `m_pitch` writes as the current helper. The retail caller shape also matches the `update <name>` UI script command path in `UI_RunMenuScript`.
- `FUN_100154e0` is now stable enough as `Menu_SetupAdvertCellShaders`. The retail menu parser finishes building each menu, runs `Menu_UpdatePosition`, and then immediately calls `FUN_100154e0`. That helper walks the menu item list, filters on item type `0x225`, computes a live rect for each advert item, and calls the already-mapped display-context extension callback `QLUIImport_SetupAdvertCellShader(defaultContent, &rect, cellId)` before storing the returned shader handle into the item background slot.
- `FUN_100155a0` is the runtime counterpart, now landed as `Menu_RefreshAdvertCellShaders`. Retail `menu_close`, activation, and refresh paths repeatedly dispatch it after menu state changes. HLIL shows the same advert-item walk, but it routes through `QLUIImport_RefreshAdvertCellShader(defaultContent, bounds_or_sentinel, cellId)` instead of the setup slot, which is the exact setup-versus-refresh split already documented in `quakelive_steam_mapping_round_15.md`.
- `FUN_10001090` is a bounded retail-only helper used by `UI_DrawStartingWeapons`. The ownerdraw first pulls the `cg_weaponPrimaryQueued` cvar into a buffer, then passes it here; the helper tokenizes the string with the already-landed `COM_ParseExt`, walks the static weapon table at `data_1002c1dc`, and returns a 1-based table index. The ownerdraw then clamps the result into its icon table before rendering the queued weapon, so `UI_StartingWeaponIndexFromToken` is the narrowest accurate public-facing name.
- `FUN_10001670` is a descriptive retail-only helper used by the corrected choice-list paint path around `FUN_10018700`. HLIL shows it scanning a caller-supplied substring and returning true only when every character is a decimal digit except for at most one `'.'`. The caller uses that boolean to decide whether to format a list entry through the numeric-value format string or to print the raw label text, so `String_IsNumeric` fits the observed role without overclaiming a GPL source match.
- `FUN_10020740` still remains documented-only. The committed HLIL continues to prove only the `menu == NULL` popup-focused-or-all-menus routing branch of `Display_MouseMove`, not the source drag branch that mutates `menu->window.rectClient` and calls `Menu_UpdatePosition`.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `394 / 438` (`90.0%`) to `399 / 438` (`91.1%`), and the Ghidra-indexed subset from `302 / 348` (`86.8%`) to `307 / 348` (`88.2%`).

## Thirtieth-Pass Additions

This pass lands the exact compiler-runtime support tranche at the tail of `uix86.dll`. Unlike the earlier descriptive retail-only passes, these names come directly from committed CRT symbols or from HLIL bodies that expose the standard helper identity unambiguously.

Landed names:

- `__security_check_cookie`
- `__CRT_INIT@12`
- `___DllMainCRTStartup`
- `___report_gsfailure`
- `__onexit`
- `_atexit`
- `__ValidateImageBase`
- `__FindPESection`
- `__IsNonwritableInCurrentImage`
- `initterm`
- `initterm_e`
- `_amsg_exit`
- `_DllMain@12`
- `__SEH_prolog4`
- `__SEH_epilog4`
- `FUN_10021189` -> `__except_handler4`
- `___security_init_cookie`
- `FUN_10021270` -> `__ftol2_sse`
- `FUN_100212a6` -> `__ftol2`
- `_crt_debugger_hook`
- `_unlock`
- `__dllonexit`
- `_lock`
- `except_handler4_common`
- `memset`
- `_CIcos`
- `_CIsin`
- `__alloca_probe`
- `_CIatan2`
- `_CItan`
- `__aulldiv`
- `__allmul`

Representative evidence:

- `FUN_10021189` is an exact `__except_handler4` match. Committed HLIL labels the body directly and shows it forwarding into `_except_handler4_common(&__security_cookie, sub_100209e9, ...)`, which is the canonical MSVC EH4 wrapper shape.
- `FUN_10021270` and `FUN_100212a6` are exact float-conversion helpers. HLIL labels `0x100212a6` directly as `__ftol2`, while `0x10021270` returns `__ftol2(arg1)` when SSE conversion is disabled and otherwise performs the inline fast-path integer conversion, which is the standard `__ftol2_sse` split.
- `___security_init_cookie` at `0x100211ae` is exact. The retail body seeds `__security_cookie` and its complement from `GetSystemTimeAsFileTime`, `GetCurrentProcessId`, `GetCurrentThreadId`, `GetTickCount`, and `QueryPerformanceCounter`, matching the standard MSVC GS initializer.
- `__ValidateImageBase`, `__FindPESection`, and `__IsNonwritableInCurrentImage` are exact committed CRT helpers. HLIL shows the PE signature checks, section-table walk, and non-writable-section predicate in the same startup slab used by `__onexit` and the CRT initialization paths.
- `__CRT_INIT@12` and `___DllMainCRTStartup` are exact startup helpers. The retail startup flow runs `___security_init_cookie` on process attach, enters `___DllMainCRTStartup`, and then dispatches through `__CRT_INIT@12` and `_DllMain@12`, which matches the standard DLL CRT bootstrap chain.
- The tiny tail thunks are exact because both `functions.csv` and HLIL preserve their standard identities: `_crt_debugger_hook`, `_lock`, `_unlock`, `__dllonexit`, `except_handler4_common`, `memset`, `_CIcos`, `_CIsin`, `_CIatan2`, `_CItan`, `__alloca_probe`, `__aulldiv`, and `__allmul` all tail-call the expected runtime helper or implement the standard compiler helper body.
- This pass intentionally still leaves `entry`, `FUN_10020d5b`, and `FUN_10020f33` out of the alias set. Their committed bodies are only strong enough to prove module-startup reset and lock-cleanup roles, not a final stable public-facing symbol name beyond the raw `entry` label already carried by `functions.csv`.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `399 / 438` (`91.1%`) to `431 / 438` (`98.4%`), and the Ghidra-indexed subset from `307 / 348` (`88.2%`) to `339 / 348` (`97.4%`).

## Thirty-First-Pass Additions

This pass closes the last remaining committed `functions.csv` gaps in `uix86.dll` and corrects the combined-corpus accounting. The earlier `438`-anchor total understated the extra-address HLIL slab by `2`; the current curated map carries `92` additional HLIL-only addresses, plus two address-overlap helpers still represented by HLIL `sub_...` raw names, so the committed corpus total is now `440`.

Landed names:

- `FUN_10001d60` -> `Color_LerpBytesToPacked`
- `FUN_10001e20` -> `Color_PackedToScaledRGBA`
- `FUN_10004280` -> `Text_Paint_Limit`
- `FUN_1000d490` -> `UI_PlayerModelEntryHasSkin`
- `FUN_1000d530` -> `UI_CountPlayerModelEntries`
- `FUN_10020740` -> `Display_MouseMove`
- `FUN_10020d5b` -> `CRT_ResetNativeDllMainReason`
- `entry` -> `_start`
- `FUN_10020f33` -> `CRT_UnlockOnExitTable`

Representative evidence:

- `FUN_10004280` is an exact `Text_Paint_Limit` match against `src/code/ui/ui_main.c`. The retail helper takes an optional `maxX` out-parameter, projects both the drawing coordinates and that out-parameter through the already-landed 640x480 scale state, sets the render color, and then dispatches through the same Quake Live text syscall slot used by the committed `QL_UI_trap_Import94` wrapper. The already-landed `UI_DrawServerMOTD` is the direct callsite match: it maintains two scrolling X positions and repeatedly calls `Text_Paint_Limit(&maxX, motdPaintX, ..., text, 0, limit)`.
- `FUN_1000d490` and `FUN_1000d530` are now stable enough to land as descriptive retail-only player-model helpers. HLIL shows `FUN_1000d490` formatting `models/players/%s/lower_%s.skin` from the retail model table and probing the file through the filesystem import, while `FUN_1000d530` walks that same table, caches successful probes, and skips the retail team-color alias skins `"blue"`, `"bright"`, `"red"`, `"sport"`, `"sport_blue"`, and `"sport_red"` when called in the `FEEDER_Q3HEADS`-style mode. The already-landed `UI_FeederCount` and `UI_ListPlayerModels` are the key caller anchors.
- `FUN_10020740` is now landed as `Display_MouseMove`. The committed `_UI_MouseEvent` still clamps cursor motion and forwards directly into this helper, and the retail body cleanly matches the `menu == NULL` branch of the current `Display_MouseMove` by resolving the focused menu, prioritizing popup routing, and then falling back to `Menu_HandleMouseMove` across all menus. The current GPL-derived source still carries an additional `menu != NULL` drag path that is not present in this retail helper, so the landed comment keeps that divergence explicit instead of treating the implementations as byte-for-byte identical.
- `FUN_10001d60` and `FUN_10001e20` remain descriptive but high-confidence color helpers. `FUN_10001d60` linearly blends two RGB byte triplets with a fractional weight, applies a final brightness scale, clamps to `0xff`, and returns a packed `0xRRGGBBFF` word; `FUN_10001e20` performs the inverse direction used by the retail player-preview path by unpacking a packed color into destination bytes, scaling RGB by an integer factor, and preserving the low-byte alpha channel.
- `entry` is now strong enough to promote to the exact `_start` name because the committed HLIL labels the symbol directly and shows the standard process-attach cookie initialization before tail-calling the already-landed `___DllMainCRTStartup`. The adjacent `FUN_10020d5b` and `FUN_10020f33` still need descriptive names rather than exact CRT exports, but their roles are narrow and stable: the first resets the cached DLL reason to `-1` after startup work completes, and the second is the tiny `_unlock(8)` cleanup stub on the `__onexit` / `__dllonexit` path.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `431 / 440` (`98.0%`) to `440 / 440` (`100.0%`), and the Ghidra-indexed subset from `339 / 348` (`97.4%`) to `348 / 348` (`100.0%`).

## Thirty-Second-Pass Additions

This pass closes the remaining extended export-table wrapper seam that sat outside the committed `functions.csv` index. These helpers were already documented from HLIL, but the accumulated evidence is now strong enough to promote them into the curated map as descriptive retail-only names.

Landed names:

- `sub_10003920` -> `UI_RefreshDisplayContext`
- `sub_10003930` -> `UI_ForEachArenaName`
- `sub_100103c0` -> `Menus_AnyVisible`
- `sub_10011130` -> `UI_DrawAdvertisementWaitScreen`

Representative evidence:

- `sub_10003920` is the display-context refresh wrapper at the first post-`UI_HasUniqueCDKey` export-table slot. Its whole body is `UI_RefreshDisplayContextScale(); data_106b40d0 = &data_10746340; return ...`, which makes the synthetic `UI_RefreshDisplayContext` name narrower and more accurate than the earlier doc-only description.
- `sub_10003930` is an arena-name visitor helper, not a generic map-table iterator. HLIL first ensures arenas are loaded through the already-landed `UI_LoadArenas`, then walks the `mapInfo` array at `data_1075add8` with the known `0x64` stride and calls the supplied callback with the first field of each live entry, which the current documented layout identifies as `mapName`. `UI_ForEachArenaName` therefore matches the observed callback contract.
- `sub_100103c0` is a clean `Menus_AnyVisible` predicate. It walks the retail menu array with the known `menuDef_t` stride and returns true when any menu's `window.flags` contain `WINDOW_VISIBLE`; unlike the already-landed `_UI_IsFullscreen` path, it does not test the `fullScreen` member.
- `sub_10011130` is the advertisement wait-screen drawer exposed through the final extended export-table slot. It optionally resolves and paints a named menu via `Menus_FindByName` and `Menu_Paint`, then centers the literal strings `"Waiting on Advertisement"` and `"Press ESC to cancel"` using the already-landed text measurement and paint helpers. `UI_DrawAdvertisementWaitScreen` is the narrowest stable public-facing name for that behavior.
- On the corrected corpus baseline, this pass moves the curated corpus mapping from `440 / 444` (`99.1%`) to `444 / 444` (`100.0%`). The Ghidra-indexed subset remains `348 / 348` (`100.0%`) because these four additions sit outside the committed Ghidra function index.

## HLIL-Only Wrapper Observations

The committed Ghidra index and the currently curated extended export-table wrapper seam are now both fully mapped. The remaining documented-only work now sits outside that closed committed function corpus, such as parser support routines and future HLIL-only helpers that still lack stable raw anchors.

## Thirty-Third-Pass Additions

This pass does not add new semantic `ui` names. It closes the last raw-anchor normalization debt inside the committed Ghidra function index by reconciling two parser helpers that were still carried under HLIL `sub_...` names even though `functions.csv` already exposes stable `FUN_...` anchors for their exact addresses.

Reconciled raw anchors:

- `sub_1001df10` -> `FUN_1001df10` for `ItemParse_model_origin`
- `sub_1001e030` -> `FUN_1001e030` for `ItemParse_rect`

Representative evidence:

- `functions.csv` already carries both rows as `FUN_1001df10` at `0x1001df10` and `FUN_1001e030` at `0x1001e030`.
- The committed HLIL continues to match the already-landed behaviors exactly: the first validates model `typeData` and parses the preview-model origin vector, while the second parses four floats into `item->window.rectClient`.
- This cleanup leaves semantic coverage unchanged at `348 / 348` Ghidra-indexed functions and `444 / 444` combined committed anchors, but it closes the last raw-name drift between the curated map and the committed Ghidra function index.

## Open Questions

- `String_Init` and `PC_SourceWarning` were not landed in this round because the committed Ghidra function index does not yet expose an equally clean raw-name anchor for them.
- Several handlers landed across these passes with HLIL `sub_...` raw names because the retail command table or caller shape gives them exact slot identity even though `functions.csv` does not expose stable `FUN_...` names for those addresses. A later Ghidra re-export may let these be reconciled to `FUN_...` names; the newest examples are `sub_10018c50`, `sub_10006950`, `sub_1000a980`, `sub_1000d2f0`, `sub_1000e470`, `sub_1000e640`, `sub_1000ea80`, and `sub_1000f7b0`.
- The committed `uix86.dll` function index and the currently curated extended export-table wrapper seam are now fully covered at `348 / 348` Ghidra functions and `444 / 444` combined committed anchors. The next useful UI mapping passes now sit entirely outside that closed set: parser support routines such as `String_Init` or `PC_SourceWarning`, plus any future HLIL-only helpers that become stable enough to promote into the curated map.
- `FUN_100156b0` is committed under the descriptive retail-only name `Menu_UpdatePresetLists` because the committed source does not expose an older GPL helper with the same behavior; a future stronger naming source could still refine that label.
- `FUN_10001090`, `FUN_10001670`, `FUN_1000d490`, `FUN_1000d530`, `FUN_10001d60`, `FUN_10001e20`, `FUN_10020d5b`, and `FUN_10020f33` are committed under descriptive retail-only names because the committed GPL-derived tree does not expose equally stable public helper names for those recovered behaviors.
- The retail `setplayermodel` and `setplayerhead` handlers write `"model"` and `"headmodel"` through the UI display context, while the current reconstructed `src/code/ui/ui_shared.c` still uses `"team_model"` and `"team_headmodel"`. That source-level parity difference should be resolved separately from the symbol-map work.
- Retail `toggle` and `activateAdvert` script commands are present in the command table but are not mirrored by equivalent GPL-era helpers in the current reconstructed `src/code/ui/ui_shared.c`.
