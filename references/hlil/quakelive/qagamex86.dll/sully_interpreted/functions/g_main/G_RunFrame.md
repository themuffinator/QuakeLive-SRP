# `G_RunFrame` (`sub_100594d0`)

**Signature:** `void G_RunFrame(int levelTime)`  
**Address:** `0x100594D0`

The stripped Quake Live routine at `0x100594D0` follows the Quake III Arena
`G_RunFrame` contract with a handful of Live-specific extensions.

1. **Time bookkeeping** – When the server is not shutting down
   (`data_105dce80 == 0`), the function copies the incoming `levelTime` into the
   global clock (`data_105dce5c`) and stores the frame delta in
   `data_105dce60`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L64480-L64483】  The previous frame time lives in
   `data_105dce64`, matching Quake III’s `level.previousTime`.
2. **Command queue maintenance** – The warmup/vote subsystem walks every active
   client (`for` loop over `data_105dce58`) and issues UI enables when the
   per-client vote timeout (`client->pers.voteDelay` at `0x33C`) elapses.  This
   mirrors `CheckVote` in Quake III but adds the Live-specific UI hook at
   `"enable_vote_ui"`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L64497-L64513】
3. **Respawn delay feedback** – When the ruleset enables extended respawns
   (`data_1059f1ac` minutes), the HLIL computes the remaining delay, clamps it to
   the configured maximum (`data_105e1b0c`), and prints a centre message using the
   engine callback at `data_104b13ac + 0x60`—exactly how Quake III’s
   `CheckIntermissionExit` broadcasts countdowns, but with the Quake Live
   seconds-based presentation.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L64514-L64536】
4. **Tournament & backend hooks** – After the base frame logic runs, the HLIL
   calls the same helper chain as Quake III (`sub_10054dd0`, `sub_10057f10`, etc.)
   to process game rules, but now with extra guards for backend throttles such as
   `data_105de9d4`/`data_105de9d8` (matchmaker-driven locks) and
   `data_105df41c` (respawn timer).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L64482-L64538】
5. **Inline client stepping** – The entity loop does not appear to preserve a
   standalone `G_RunClient` wrapper in this retail build. Non-client entities
   dispatch through `sub_10059370` (`G_RunThink`), while client entities branch
   directly to `sub_10034c90` (`ClientThink_real`) inside the same loop, leaving
   the classic thin wrapper effectively inlined or absent.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L64552-L64581】

The remainder of the function therefore fans out to the usual Quake III helper
families (`G_RunThink`, `ClientThink_real`, the vote/match-state chain, and the
adjacent team-count refresh) rather than a clean standalone `G_RunClient`
boundary.
