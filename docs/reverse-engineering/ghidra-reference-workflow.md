# Quake Live Ghidra Reference Workflow

## Scope

This repository now keeps an OpenAlice-style Ghidra reference corpus alongside the
existing Binary Ninja HLIL dumps so reverse-engineering work has both:

- the retail Quake Live binaries as the primary evidence base
- committed, structured Ghidra exports for fast triage and repeatable analysis

Reference binaries:

- `assets/quakelive/quakelive_steam.exe`
- `assets/quakelive/baseq3/cgamex86.dll`
- `assets/quakelive/baseq3/qagamex86.dll`
- `assets/quakelive/baseq3/uix86.dll`

## Canonical Reference Location

Generated outputs are committed under:

- `references/reverse-engineering/ghidra/quakelive_steam/`
- `references/reverse-engineering/ghidra/cgamex86/`
- `references/reverse-engineering/ghidra/qagamex86/`
- `references/reverse-engineering/ghidra/uix86/`

Each folder contains:

- `metadata.txt`
- `functions.csv`
- `imports.txt`
- `exports.txt`
- `analysis_symbols.txt`
- `decompile_top_functions.c`

## Companion Binary Ninja / Mapping Material

Use the committed Ghidra corpus with the existing Binary Ninja material rather than
instead of it:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/hlil/quakelive/cgamex86.dll/`
- `references/hlil/quakelive/qagamex86.dll/`
- `references/hlil/quakelive/uix86.all/`
- `references/symbol-maps/`
- `docs/reverse-engineering/ghidra-module-mapping.md`

Precedence rule:

- Treat retail binaries in `assets/quakelive/` plus the committed HLIL dumps under
  `references/hlil/` as canonical for parity claims.
- Treat the committed Ghidra corpus under `references/reverse-engineering/ghidra/`
  as the primary structured companion corpus for day-to-day recovery work.
- Treat live MCP output and ad-hoc decompiler sessions as advisory until they are
  revalidated against committed corpus files and, when needed, the HLIL dumps.

## Tooling

- Headless exporter script: `scripts/ghidra/ExportQuakeLiveReference.java`
- Runner wrapper: `scripts/ghidra/run_quakelive_reference.ps1`
- Optional GhidrAssistMCP bootstrap: `scripts/ghidra/setup_ghidrassist_mcp.ps1`
- Default Ghidra install path used by the wrapper:
  - `C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC`

## Optional Live MCP Analysis

Quake Live can use GhidrAssistMCP as an interactive analysis aid while keeping the
committed exports and HLIL corpus as the evidence base.

Quick setup:

```powershell
scripts\ghidra\setup_ghidrassist_mcp.ps1 -Mode release
```

Full setup and usage details:

- `docs/reverse-engineering/ghidrassist-mcp.md`

## Regeneration

Run from repository root:

```powershell
scripts\ghidra\run_quakelive_reference.ps1
```

Optional parameters:

- `-GhidraHome` to point at another Ghidra install
- `-QuakeLiveRoot` to point at another retail binary snapshot
- `-OutputRoot` to write to a different output directory
- `-MaxDecompFunctions` to change how many large functions are exported

## Fingerprints

Reference binary MD5 values:

- `quakelive_steam.exe`: `B8E404E377AB33E482DF9D6063F67DA5`
- `cgamex86.dll`: `375A1CC258A7432DF35EBBE0A5215B9B`
- `qagamex86.dll`: `005D0C49D4190FE82F325E4FB6437AD0`
- `uix86.dll`: `64321E7C6357A59063AE8900E2A20732`

## Reconstruction Guidelines

These guidelines are intentionally imported from the OpenAlice workflow and adapted
to Quake Live:

- Treat the artifacts as evidence for behavior and interfaces, not as drop-in
  source code.
- Start with `metadata.txt`, `imports.txt`, `exports.txt`, and `functions.csv`
  before reading large decompile output.
- Treat `decompile_top_functions.c` as a hint set, not ground truth.
- Build each semantic claim from at least two signals when possible:
  - call relationships and symbol context
  - strings, imports, exports, and constants
  - repeated offsets and data access patterns
- Separate observed facts from inferred meaning in notes and reviews.
- Track confidence and open questions instead of forcing unstable names.
- Validate engine-facing assumptions against the Binary Ninja HLIL dumps whenever
  there is disagreement or uncertainty.
- Do not claim certainty without direct evidence from the retail corpus.
