# Ralph Loop

This repo now has a Windows-first Ralph loop for Codex under `.codex/ralph/`.

The setup is intentionally repo-specific:

- It reads the current work queue from `.codex/ralph/prd.json`, which is seeded from `IMPLEMENTATION_PLAN.md`.
- It reminds Codex to obey [`AGENTS.md`](../../AGENTS.md), especially the reverse-engineering evidence workflow and the read-only `assets/` / `src/ui/` trees.
- It defaults to safer manual review mode. Use `-AutoCommit` only when you want Ralph to create commits as part of the loop.

## Files

- `ralph.ps1`: the loop runner
- `CODEX.md`: repo-specific Codex instructions for each iteration
- `prd.json`: the current Ralph backlog
- `progress.txt`: append-only notes and parity estimates between iterations
- `events.log`: high-level iteration log
- `run.log`: full Codex output

## Usage

From the repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/ralph/ralph.ps1
```

Useful variants:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/ralph/ralph.ps1 -MaxIterations 3
pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/ralph/ralph.ps1 -StoryId QLR-021 -AllowDirtyWorktree
pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/ralph/ralph.ps1 -AutoCommit
pwsh -NoProfile -ExecutionPolicy Bypass -File .codex/ralph/ralph.ps1 -DryRun -AllowDirtyWorktree
```

## Safety Notes

- The runner refuses to switch/create the target branch on a dirty worktree unless `-AllowDirtyWorktree` is passed.
- `workspace-write` is the default Codex sandbox. Use `-Sandbox danger-full-access` only when you really need it.
- The seeded stories are intentionally broad. Ralph is allowed to split an oversized story into smaller child stories in `prd.json` before attempting implementation.
- Runtime artifacts are ignored through the root `.gitignore`, but `prd.json` and `progress.txt` are meant to persist as the loop memory.
