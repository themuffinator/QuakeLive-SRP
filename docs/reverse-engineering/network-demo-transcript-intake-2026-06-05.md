# Network Demo Transcript Intake - 2026-06-05

## Scope

This pass supports the residual byte-for-byte replay row in
`docs/plans/2026-06-05-outstanding-work-checklist.md` by adding a text
transcript path for protocol-91 demo evidence. It does not claim that a retail
packet capture or retail demo transcript is now committed.

No runtime or game launch was required.

## Demo Envelope

The parser follows the source contract in `src/code/client/cl_main.c`:

- `CL_WriteDemoMessage` writes a little-endian `serverMessageSequence`, then a
  little-endian payload length, then the message payload after netchan packet
  sequencing bytes have been skipped.
- `CL_StopRecord_f` writes the `-1/-1` terminator.
- `CL_ReadDemoMessage` reads the same sequence/length envelope and rejects
  payload lengths larger than `MAX_MSGLEN`.

The transcript tool records each payload as lowercase space-separated hex plus
SHA-256 hashes. That gives future retail `.dm_91` evidence a reviewable text
format, avoiding binary commits.

## Tooling

New helper:

```bash
python -m tools.trace.demo_transcript path/to/demo.dm_91 \
  --provenance source=retail \
  --provenance map=tritoxin \
  -o path/to/transcript.json
```

The output format is `quake_live_demo_message_transcript` schema version `1`.
Retail closure still requires provenance tying the transcript to a real retail
capture/demo source. `validate_demo_transcript_dict` is the follow-up validation
gate for hashes, offsets, terminator sizing, and retail provenance.

## Local Artifact Check

Ignored local `.dm_91` files were found under `build/win32/Debug`, but they are
local generated demos and are not committed retail evidence. They were left out
of the checklist closure claim.

## Checklist Effect

The outstanding checklist now records the transcript-intake tooling as complete.
The byte-for-byte replay fixture row and downstream capture-diff rows remain
unchecked until a retail packet capture, protocol-91 demo transcript, or
equivalent known-good byte fixture with provenance is committed.

Estimated parity movement:

- Overall network-protocol source parity remains `90%` -> `90%`.
- Byte-for-byte capture evidence remains `0%` -> `0%`.
- Repo-wide parity remains `99%` -> `99%`.
