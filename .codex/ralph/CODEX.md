# Ralph Codex Instructions

You are running one fresh Ralph iteration for the Quake Live reverse-engineering repository.

Read these files first on every iteration:

1. `AGENTS.md`
2. `.codex/ralph/prd.json`
3. `.codex/ralph/progress.txt`
4. `IMPLEMENTATION_PLAN.md`
5. `AUDIT.md`

Then read only the extra evidence and source files needed for the selected story.

## Iteration Contract

You must do exactly one of these outcomes:

1. Complete the selected story end-to-end.
2. If the story is too large or too ambiguous for one clean iteration, split it into smaller stories in `.codex/ralph/prd.json`, update `.codex/ralph/progress.txt` with the rationale, and stop.
3. If the story is blocked by missing evidence or an unsafe assumption, leave it incomplete, record the blocker in `.codex/ralph/progress.txt`, and stop.

Do not silently drift into unrelated work.

## Repo Rules That Matter Here

- Use the committed HLIL and Ghidra corpora before making new assumptions.
- Build claims from at least two signals when possible.
- Keep observed facts separate from inferred meaning.
- Never edit `assets/` or `src/ui/`.
- In C/C++ code, indent with tabs and preserve the repository's required commented function-header format.
- Never launch the game in fullscreen; any launch command must include `+set r_fullscreen 0`.
- If you commit, generate the required PR message only if the current runtime exposes that tool. If it does not, record the limitation in `.codex/ralph/progress.txt` instead of inventing output.

## Verification Rules

- Run the smallest meaningful verification for the story you touched.
- When code changes can affect startup/runtime stability, follow the AGENTS debugging process as far as the current environment and tooling allow.
- If a required runtime artifact cannot be captured in the current environment, say so explicitly in `.codex/ralph/progress.txt` and in your final response.

## Required Updates Before You Finish

If you completed the story:

- Update `.codex/ralph/prd.json` so the selected story has `"passes": true`.
- Append an entry to `.codex/ralph/progress.txt` that includes:
  - date/time
  - story id
  - what changed
  - verification run
  - before/after parity estimate
  - open questions or follow-ups

If you split the story:

- Replace the oversized story with smaller stories or add child stories beneath it.
- Mark the original story as passed only if its only purpose became "decompose this work into smaller executable slices".
- Record the decomposition in `.codex/ralph/progress.txt`.

If you are blocked:

- Keep the story incomplete.
- Record the blocker, missing evidence, and the safest next step in `.codex/ralph/progress.txt`.

## Final Response Contract

- Keep the final response concise.
- State whether the story was completed, split, or blocked.
- Include verification performed.
- Only emit `<promise>COMPLETE</promise>` as a separate final line if there are no remaining `passes: false` stories in `.codex/ralph/prd.json`.
