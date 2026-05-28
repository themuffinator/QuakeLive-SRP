# UI Cvar Mapping Round

Date: 2026-05-28

Scope: `ui_*` cvar ownership, the retail `uix86.dll` cvar table, and related
host wiring. `assets/` and `src/ui/` were treated as read-only.

## Evidence

Primary retail signals:

- `references/reverse-engineering/ghidra/uix86/metadata.txt` identifies
  `uix86.dll` as the owning UI VM binary.
- `references/reverse-engineering/ghidra/uix86/functions.csv` carries the
  relevant function bodies: `FUN_10011730`, `FUN_100118a0`, `FUN_10011240`,
  `FUN_10011630`, `FUN_10011660`, and `FUN_10011690`.
- `references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h` promotes
  the same owners to `UI_RegisterCvars`, `UI_UpdateCvars`,
  `UI_UpdateForceTeamModelSettings`, `UI_UpdateForceEnemyModelSettings`, and
  `UI_UpdateAnnouncer`.
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt:12147`
  shows `UI_RegisterCvars` starting at `data_1002afe0`, iterating `0x82`
  rows, and registering fields `vmCvar`, `name`, `default`, and `flags`.
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt:12202`
  shows `UI_UpdateCvars` starting at `data_1002afd8`, iterating the same
  `0x82` rows, reading the old `vmCvar->modificationCount`, calling
  `trap_Cvar_Update`, and invoking row field `3` when the old count is non-zero
  and changed.
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt:12010`
  shows the shared color callback `sub_10011240` mapping slider-backed UI
  cvars to packed `cg_*Color` cvars through the retail `"0x%08x"` format.
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt:12099`
  and `:12105` show the force-model callbacks bound to
  `cg_forceTeamSkin`/`cg_forceTeamModel` and
  `cg_forceEnemySkin`/`cg_forceEnemyModel`.
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt:12111`
  shows `UI_UpdateAnnouncer` playing the default, evil, or female voice sample
  and writing the selected numeric profile back to `ui_announcer`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  and `part05.txt` show host-side ownership for `ui_recordSPDemo`,
  `ui_singlePlayerActive`, `ui_priv`, and `ui_joyavail`.

## Retail Table Shape

Observed row order is:

| Offset | Meaning | Retail evidence |
| ---: | --- | --- |
| `+0` | `vmCvar_t *` storage | `UI_UpdateCvars` calls `trap_Cvar_Update(*esi)` |
| `+4` | cvar name | `UI_RegisterCvars` passes `esi_1[-1]` |
| `+8` | default string | `UI_RegisterCvars` starts at this field and passes `*esi_1` |
| `+12` | optional update callback | `UI_UpdateCvars` reads `esi[3]` |
| `+16` | flags | `UI_RegisterCvars` passes `esi_1[2]` |

The source table now mirrors that order through `cvarTable_t` and the
`UI_CVAR_TABLE_ENTRY` / `UI_CVAR_TABLE_CALLBACK` initializers.

## Retail Callback Rows

| Retail cvar row | Callback | Reconstructed source behavior |
| --- | --- | --- |
| `cg_announcer` | `sub_10011690` | `UI_UpdateAnnouncer` plays `vo_default`, `vo_evil`, or `vo_female`, then mirrors to `ui_announcer`. |
| `ui_enemyColor` | `sub_10011240` | Writes `cg_enemyUpperColor`, `cg_enemyLowerColor`, then `cg_enemyHeadColor`. |
| `ui_enemyHeadColor` | `sub_10011240` | Writes `cg_enemyHeadColor`. |
| `ui_enemyLowerColor` | `sub_10011240` | Writes `cg_enemyLowerColor`. |
| `ui_enemyUpperColor` | `sub_10011240` | Writes `cg_enemyUpperColor`. |
| `ui_forceEnemyModel` | `sub_10011660` | Resyncs enemy force-model brightness from `cg_forceEnemySkin` / `cg_forceEnemyModel`. |
| `ui_forceEnemySkin` | `sub_10011660` | Same enemy force-model callback. |
| `ui_forceTeamModel` | `sub_10011630` | Resyncs team force-model brightness from `cg_forceTeamSkin` / `cg_forceTeamModel`. |
| `ui_forceTeamSkin` | `sub_10011630` | Same team force-model callback. |
| `ui_screenDamage` | `sub_10011240` | Writes `cg_screenDamage`. |
| `ui_screenDamage_Team` | `sub_10011240` | Writes `cg_screenDamage_Team`. |
| `ui_teamColor` | `sub_10011240` | Writes `cg_teamUpperColor`, `cg_teamLowerColor`, then `cg_teamHeadColor`. |
| `ui_teamHeadColor` | `sub_10011240` | Writes `cg_teamHeadColor`. |
| `ui_teamLowerColor` | `sub_10011240` | Writes `cg_teamLowerColor`. |
| `ui_teamUpperColor` | `sub_10011240` | Writes `cg_teamUpperColor`. |

## Retail Table Inventory

The committed HLIL table contains `0x82` rows:

```text
000 cg_announcer
001 ui_actualNetGametype
002 g_arenasFile
003 ui_bigFont
004 ui_bloomPreset
005 ui_blueteam
006 ui_blueteam1
007 ui_blueteam2
008 ui_blueteam3
009 ui_blueteam4
010 ui_blueteam5
011 g_botsFile
012 cg_brassTime
013 ui_browserGameType
014 ui_browserMaster
015 ui_browserShowEmpty
016 ui_browserShowFull
017 ui_browserSortKey
018 ui_captureLimit
019 ui_cdkeychecked
020 ui_ctf_capturelimit
021 ui_ctf_friendly
022 ui_ctf_timelimit
023 ui_currentMap
024 ui_currentNetMap
025 ui_currentOpponent
026 ui_currentTier
027 ui_cvGameType
028 ui_debug
029 ui_dedicated
030 cg_drawCrosshair
031 cg_enemyCrosshairNames
032 ui_enemyColor
033 ui_enemyHeadColor
034 ui_enemyLowerColor
035 ui_enemyUpperColor
036 ui_findPlayer
037 ui_forceEnemyModel
038 ui_forceEnemyModelBright
039 ui_forceEnemySkin
040 ui_forceTeamModel
041 ui_forceTeamModelBright
042 ui_forceTeamSkin
043 ui_ffa_fraglimit
044 ui_ffa_timelimit
045 ui_fragLimit
046 ui_gametype
047 ui_gibs
048 cg_hudFiles
049 ui_initialized
050 ui_joinGametype
051 ui_lastServerRefresh_0
052 ui_lastServerRefresh_1
053 ui_lastServerRefresh_2
054 ui_lastServerRefresh_3
055 ui_mapIndex
056 cg_marks
057 ui_mainmenu
058 ui_menuFiles
059 ui_netGametype
060 ui_netSource
061 ui_new
062 ui_opponentName
063 ui_priv
064 capturelimit
065 g_warmup
066 ui_recordSPDemo
067 ui_redteam
068 ui_redteam1
069 ui_redteam2
070 ui_redteam3
071 ui_redteam4
072 ui_redteam5
073 ui_scoreAccuracy
074 ui_scoreImpressives
075 ui_scoreExcellents
076 ui_scoreCaptures
077 ui_scoreDefends
078 ui_scoreAssists
079 ui_scoreGauntlets
080 ui_scoreScore
081 ui_scorePerfect
082 ui_scoreTeam
083 ui_scoreBase
084 ui_scoreTime
085 ui_scoreTimeBonus
086 ui_scoreSkillBonus
087 ui_scoreShutoutBonus
088 ui_screenDamage
089 ui_screenDamage_Team
090 cg_selectedPlayer
091 cg_selectedPlayerName
092 server1
093 server2
094 server3
095 server4
096 server5
097 server6
098 server7
099 server8
100 server9
101 server10
102 server11
103 server12
104 server13
105 server14
106 server15
107 server16
108 ui_serverStatusTimeOut
109 ui_singlePlayerActive
110 ui_smallFont
111 g_spAwards
112 ui_spSelection
113 g_spSkill
114 g_spScores1
115 g_spScores2
116 g_spScores3
117 g_spScores4
118 g_spScores5
119 g_spVideos
120 ui_team_fraglimit
121 ui_team_friendly
122 ui_team_timelimit
123 ui_teamColor
124 ui_teamHeadColor
125 ui_teamLowerColor
126 ui_teamName
127 ui_teamUpperColor
128 ui_tourney_fraglimit
129 ui_tourney_timelimit
```

## Host-Owned UI Cvars

These cvars are not only UI-table rows; the retail Windows host also reads or
writes them:

| Cvar | Retail host evidence | Current source owner |
| --- | --- | --- |
| `ui_recordSPDemo` | `quakelive_steam.exe` HLIL `004b85a1` / `004b85b0` reads it before SP demo recording work. | `CL_DemoFilename` and cgame/UI table registration. |
| `ui_singlePlayerActive` | Host writes `0` at `004b8c7f`, `004b8d03`, `004b8d54`, `004cc683`, and `004e401d`; writes `1` at `004de00f`. | Client/server/UI/cgame single-player bridge writes. |
| `ui_priv` | Host writes `3` at `004de01e` when starting the local privileged SP path. | `sv_ccmds.c` and cgame server-command bridge. |
| `ui_joyavail` | Host writes `0` at `004eace3` and `1` at `004eae8b`. | Win32, Unix, and null input joystick availability bridges. |

## Source Reconstruction

This round updated `src/code/ui/ui_main.c` and `src/code/ui/ui_local.h`:

- Restored a retail-shaped callback lane in `cvarTable_t`:
  `vmCvar`, `name`, `default`, `update`, `flags`.
- Added `UI_CVAR_TABLE_ENTRY` and `UI_CVAR_TABLE_CALLBACK` so plain and
  callback rows remain explicit while preserving the retail field order.
- Replaced the previous ad hoc color `modificationCount` globals with the
  retail `UI_UpdateCvars` rule: update the vmCvar, then call the row callback
  when the old count was non-zero and changed.
- Added the missing retail bulk color cvars `ui_teamColor` and
  `ui_enemyColor`.
- Routed all retail color rows through `UI_UpdateRetailSliderColorCvar`,
  including bulk team/enemy color writes in the order shown by HLIL.
- Routed `ui_forceTeamModel`, `ui_forceTeamSkin`, `ui_forceEnemyModel`, and
  `ui_forceEnemySkin` through retail-shaped callback wrappers.
- Reconstructed the `cg_announcer` table row callback and its mirror write to
  `ui_announcer`.

This round also updated the native UI host shim in
`src/code/client/cl_ui.c`: retail passes `7` to the `S_RegisterSound` import
from the announcer callback, so the shim now normalizes any non-zero integer to
`qtrue` instead of treating non-`0`/`1` values as false.

The current source table intentionally still contains compatibility and
inherited GPL-era rows that are not part of the recovered retail `0x82` row
table, such as `ui_browserAwesomium`, `ui_menuFlow`, preset helper cvars,
vote-disabled cvars, and older score/cache helpers. Those are documented as
source compatibility lanes rather than retail table evidence.

## Validation

Focused tests now pin the reconstructed evidence:

- `tests/test_ui_menu_files.py` checks the retail row layout, `0x82` HLIL
  loops, callback entries, slider-color routing, force-model callbacks, and
  announcer callback.
- `tests/test_cgame_hud_parity.py` checks that screen-damage UI cvars use the
  retail callback lane and still feed the packed cgame damage colors.
- `tests/test_platform_services.py` checks that the native UI sound-register
  shim preserves retail non-zero qboolean arguments such as the announcer
  callback's `7`.

No runtime launch was needed for this mapping round.

## Parity Movement

Before this round, focused `ui_*` cvar parity was about `93%`: names, defaults,
and many call sites were present, but the retail callback slot, bulk color
cvars, and `cg_announcer` ownership were still reconstructed as scattered
source-side update logic.

After this round, focused `ui_*` cvar parity is about `98%`. Remaining gaps are
bounded to the broader table-count mismatch caused by retained GPL and
compatibility cvars, read-only `src/ui/` menu text, and online-service fallback
diagnostics. Repo-wide parity remains estimated at `98%`.
