# Quake Live Steam Host Mapping Round 19

## Scope

This round revisits the native `cgamex86.dll` host tail immediately after the Round 18 cinematic/parser band.

The main goal was to correct the offset alignment in the retail callback slab at `data_565B18..data_565B54` and then promote only the stable pieces. A fresh pass through the host HLIL, the retail `cgamex86.dll` HLIL, and the local reconstruction now splits that band into:

- shared cursor helpers already closed from the native UI slab
- a tagged info-string dispatch seam used by native cgame `serverinfo` refresh
- shared text draw/measure helpers already closed from the native UI slab
- the Steam voice mute-state / toggle seam
- the Steam avatar-image handle import used by native scoreboards and player cards

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`

## Corrected Native Cgame Tail Alignment At `0x1C0..0x1FC`

This pass corrects the shifted read from the unfinished exploratory notes.

Observed local facts:

1. The owning host slab resolves as:
   - `data_565B18 = sub_4B0340`
   - `data_565B1C = sub_4BEF20`
   - `data_565B20 = sub_4B0350`
   - `data_565B24 = 0x4B0360`
   - `data_565B28 = sub_4B03B0`
   - `data_565B2C = sub_4B0370`
   - `data_565B30 = 0`
   - `data_565B34 = 0`
   - `data_565B38 = sub_4B03C0`
   - `data_565B3C = sub_4B03D0`
   - `data_565B40 = sub_4BF2E0`
   - `data_565B44 = sub_4B03E0`
   - `data_565B48 = sub_4BF310`
   - `data_565B4C = sub_4BF340`
   - `data_565B50 = sub_4B0420`
   - `data_565B54 = sub_4B0440`
2. The two literal null slots at `0x1D8` and `0x1DC` are real. They explain why the shared text helpers land at `0x1EC` and `0x1F0`, not at the earlier tentative offsets from the exploratory pass.
3. `sub_4B0340` and `sub_4BEF20` were already closed earlier as the shared cursor shims over `Win32_SetCursorPos` / `Win32_GetCursorPos`.
4. `sub_4B03E0` and `sub_4BF310` were already closed earlier as the shared scaled-text draw and text-measure helpers.

So the new work in this round is not to rename those shared helpers again, but to document that native cgame reuses them and then promote the remaining Steam-specific band safely.

## `sub_4B03B0` / `sub_4BF5D0`: Tagged `serverinfo` Dispatch

The `0x1D0` slot is now semantically constrained even though I am not promoting a final alias for it yet.

Observed local facts:

1. Native cgame calls `(*(data_1074CCCC + 0x1D0))("serverinfo", data_10A38420 + 0x10A39420)` in both `sub_10048910` and `sub_10049420` before it starts pulling values back through the local token/value helpers.
2. `sub_4B03B0` is a pure tailcall to `sub_4BF5D0`.
3. `sub_4BF5D0` creates a message object, writes `MSG_TYPE = arg1`, tokenizes `arg2` into repeated key/value pairs through `sub_4D9380`, and then hands the finished object to `sub_4EC6D0()`.
4. The only observed retail cgame caller passes the literal `"serverinfo"` tag.

That is enough to document this seam as a tagged info-string dispatcher feeding host-side message publication, but not enough yet to lock an exact stable name for the generic host helper.

## Shared Text Reuse At `0x1EC` And `0x1F0`

The corrected alignment also closes the ownership of the native cgame text helpers without requiring new aliases.

Observed local facts:

1. Native cgame UI/layout paths call:
   - `(*(data_1074CCCC + 0x1EC))(x, y, fontOrStyle, flags, scale, color, cursor, ...)`
   - `(*(data_1074CCCC + 0x1F0))(text, 0, fontOrStyle, scale, flags, &outHeight)`
2. `sub_4B03E0` forwards eight arguments through `data_146CCF0`; that wrapper was already promoted earlier as `QLUIImport_DrawScaledText`.
3. `sub_4BF310` forwards six arguments through `data_146CCF4`; that wrapper was already promoted earlier as `QLUIImport_MeasureText`.

So this round just records that native cgame reuses the same shared text helpers previously mapped from the native UI slab.

## Steam Voice Mute Seam At `0x1F4` And `0x1F8`

The final unresolved Steam-specific pair in this band is now high-confidence.

### `sub_4BF340` And `sub_461990`

Observed local facts:

1. `sub_4BF340` is a pure wrapper over `sub_461990(arg1, arg2)`.
2. `sub_461990` performs a keyed lookup in the `data_E30224` tree using the two 32-bit halves of a `CSteamID`-shaped key and returns whether the entry already exists.
3. Native cgame scoreboard/player-card paths use `(*(data_1074CCCC + 0x1F4))(steamIDLow, steamIDHigh)` to decide whether to show `ui/assets/score/muted`; otherwise they fall back to `ui/assets/score/speaking` when the speaker flag is set.
4. The Steam voice receive path in `sub_461A60` calls `sub_461990(var_8060, var_805C)` before starting voice playback for an incoming sender.

This is the native cgame mute-state query wrapper and the exact host-side Steam voice mute-set membership test behind it.

### `sub_4B0420` And `sub_461C00`

Observed local facts:

1. `sub_4B0420` is a pure wrapper over `sub_461C00(arg1, arg2)`.
2. The native cgame console command table binds `"clientmute"` to `sub_10007E90`.
3. `sub_10007E90` parses the target client number, reads that client’s two-word SteamID from `data_10A42418`, and returns `(*(data_1074CCCC + 0x1F8))(steamIDLow, steamIDHigh)`.
4. `sub_461C00` searches the same `data_E30224` mute tree. If the SteamID is already present it removes the entry through `sub_4615E0(...)` and returns `0`; otherwise it inserts a new node through `sub_461880(...)` and returns `1`.

That is exact toggle behavior, not a one-way insert helper.

## Steam Avatar Handle Import At `0x1FC`

The final slot in this band is now straightforward.

Observed local facts:

1. `sub_4B0440` is a pure wrapper over `sub_460F30(arg1, arg2)`.
2. `sub_460F30` was already promoted earlier as `SteamClient_GetAvatarImageHandle`.
3. Native cgame caches `(*(data_1074CCCC + 0x1FC))(steamIDLow, steamIDHigh)` into the per-player avatar field during the scoreboard/player-card refresh path around `sub_1003EDD0`.

That makes `sub_4B0440` the native cgame avatar-handle import wrapper over the already-closed Steam client helper.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BF340` (`0x004BF340`) | `QLCGImport_IsClientMuted` | Observed | Native cgame import wrapper for Steam voice mute-state queries by client SteamID. |
| `sub_4B0420` (`0x004B0420`) | `QLCGImport_ToggleClientMute` | Observed | Native cgame import wrapper behind the `clientmute` command. |
| `sub_4B0440` (`0x004B0440`) | `QLCGImport_GetAvatarImageHandle` | Observed | Native cgame import wrapper for the Steam avatar image-handle lookup. |
| `sub_461990` (`0x00461990`) | `SteamVoice_IsClientMuted` | Observed | Exact host-side Steam voice mute-set membership test over the `CSteamID` key tree. |
| `sub_461C00` (`0x00461C00`) | `SteamVoice_ToggleClientMute` | Observed | Exact host-side Steam voice mute-set toggle helper over the same `CSteamID` key tree. |

## Open Questions

1. `sub_4B0330`, `sub_4B0350`, and the literal thunk at `0x4B0360` remain intentionally unnamed. The current retail cgame evidence only constrains `0x1C8` / `0x1CC` as a paired no-arg utility seam wrapped around the stereo-view camera offset path in `sub_10011490`.
2. `sub_4B0370` is still only a generic five-float forwarder through `data_146CCE4`, and I do not yet have a direct native cgame caller proving whether it belongs to additive light, sound, or another helper family.
3. `sub_4B03C0` and `sub_4B03D0` are a paired three-vector seam used together in the world-indicator draw path around `sub_10011680`, but their exact math ownership is not pinned tightly enough yet for promotion.
4. `sub_4BF2E0` remains the shared `IsSubscribedApp` wrapper already mapped from the native UI slab. I did not find a stable native cgame caller for `0x1E8` in this pass, so I am leaving that reuse documented but unpromoted.
