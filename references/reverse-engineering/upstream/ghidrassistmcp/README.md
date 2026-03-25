# GhidrAssistMCP Cache

This directory is reserved for assets fetched by
`scripts/ghidra/setup_ghidrassist_mcp.ps1`.

Expected subdirectories:

- `releases/<tag>/` for downloaded extension zip files
- `source/<tag>/` for source checkouts used by `-Mode source`

Do not treat contents fetched here as canonical reverse-engineering evidence. They
are tooling dependencies only; durable findings must be revalidated against the
committed Ghidra corpus and HLIL dumps.
