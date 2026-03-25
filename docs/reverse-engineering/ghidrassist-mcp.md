# GhidrAssistMCP Integration

## Purpose

GhidrAssistMCP provides a live MCP bridge for interactive analysis inside Ghidra.
In this repository it is an optional reverse-engineering aid.

Canonical evidence remains:

- retail Quake Live binaries under `assets/quakelive/`
- committed Binary Ninja HLIL dumps under `references/hlil/`
- committed Ghidra exports under `references/reverse-engineering/ghidra/`

Use GhidrAssistMCP to accelerate investigation, then persist conclusions back into
committed corpus-backed notes.

## Setup Paths

Bootstrap script:

- `scripts/ghidra/setup_ghidrassist_mcp.ps1`

Default upstream cache location used by the script:

- `references/reverse-engineering/upstream/ghidrassistmcp/`

### Release package download

```powershell
scripts\ghidra\setup_ghidrassist_mcp.ps1 -Mode release
```

Options:

- `-Version <tag>` to pin a specific release tag instead of `latest`
- `-Force` to re-download an existing zip
- `-DryRun` to preview paths and assets without writing files

After download, install from Ghidra UI:

1. `File -> Install Extensions...`
2. Select the downloaded `*GhidrAssistMCP.zip`
3. Restart Ghidra

### Source install path

```powershell
scripts\ghidra\setup_ghidrassist_mcp.ps1 -Mode source -GhidraHome "C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC"
```

This clones the tagged source under
`references/reverse-engineering/upstream/ghidrassistmcp/source/<tag>/` and runs:

- `gradlew(.bat) -PGHIDRA_INSTALL_DIR=<GhidraHome> installExtension`

## MCP Server Configuration

Inside Ghidra, configure GhidrAssist and enable MCP server mode.

Default endpoint modes:

- SSE: `http://127.0.0.1:8080/sse`
- Streamable HTTP: `http://127.0.0.1:8080/mcp`

Auth modes supported by GhidrAssistMCP:

- `none`
- `api_key`
- `jwt`

Client-side MCP configuration must match the endpoint mode and auth mode selected
in GhidrAssist.

## Workflow Policy

1. Use GhidrAssistMCP for interactive exploration and hypothesis generation.
2. Re-validate conclusions against committed corpus files in
   `references/reverse-engineering/ghidra/*`.
3. Cross-check parity-sensitive claims against the matching HLIL dumps in
   `references/hlil/quakelive/*`.
4. Record durable findings in:
   - `docs/reverse-engineering/ghidra-module-mapping.md`
   - `docs/reference-mapping.md`
   - subsystem notes under `docs/reverse-engineering/` or `docs/gameplay/parity/`
5. Refresh committed corpus exports when needed:
   - `scripts\ghidra\run_quakelive_reference.ps1`

Do not treat live MCP output as canonical without committed corpus-backed evidence.
