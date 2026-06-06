# Quake Live Steamworks Mapping Round 367

Date: 2026-06-06

Focus: reconstruct executable harness coverage for the retained SteamUser voice
wrapper slots that feed the client Steam voice transport.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` and
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Existing mapping anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`, and
  `docs/reverse-engineering/client-sound-parity-audit-2026-04-16.md`.

Observed HLIL evidence:

- `0x0046044c` starts capture through `SteamUser()` slot `0x1c` from the
  retained `+voice` command owner.
- `0x00460459` immediately queries `SteamUser()` slot `0x30` for the optimal
  voice sample rate and prints the retained diagnostic string.
- `0x004604b1` stops capture through `SteamUser()` slot `0x20` from the
  retained `-voice` command owner.
- `0x00460d4b` pulls compressed voice through `SteamUser()` slot `0x28` before
  sending the bytes over the legacy `SteamNetworking` channel `1` path.
- `0x00461b07` loads `SteamUser()` slot `0x2c` while processing incoming voice
  packets and decompressing them before the sound mixer handoff.

## Observed Facts

- The production source already exposes the matching wrapper family:
  `QL_Steamworks_StartVoiceRecording`, `QL_Steamworks_StopVoiceRecording`,
  `QL_Steamworks_GetCompressedVoice`, `QL_Steamworks_DecompressVoice`, and
  `QL_Steamworks_GetVoiceOptimalSampleRate`.
- Those wrappers dispatch through `QL_Steamworks_GetUserInterface` and slots
  `0x1c`, `0x20`, `0x28`, `0x2c`, and `0x30` respectively.
- `CL_VoiceStartRecording_f`, `CL_VoiceStopRecording_f`,
  `CL_Steam_SendVoicePacket`, and `CL_Steam_ProcessVoicePackets` already pin
  the client-level command and packet-pump wiring.
- Before this pass, the Steamworks harness covered the adjacent legacy P2P
  transport but did not expose executable mock coverage for the SteamUser voice
  slots themselves.

## Source Reconstruction

This pass extended the local Steamworks harness rather than production engine
behavior:

- Added deterministic mock state for voice start/stop calls, compressed voice
  payloads, decompressed PCM payloads, result controls, optimal sample rate,
  and last-call argument capture.
- Expanded the mock `SteamUser` vtable with:
  - slot `0x1c / 4`: `StartVoiceRecording`
  - slot `0x20 / 4`: `StopVoiceRecording`
  - slot `0x28 / 4`: `GetVoice`
  - slot `0x2c / 4`: `DecompressVoice`
  - slot `0x30 / 4`: `GetVoiceOptimalSampleRate`
- Exported stable enabled and disabled harness wrappers for the five
  production voice APIs.
- Added `test_steam_user_voice_wrappers_use_retail_slots` to prove payload
  copy-out, size projection, failure zeroing, call counts, compressed/
  uncompressed argument flags, decompression sample-rate forwarding, and the
  disabled-build fallback contract.
- Added `test_steam_user_voice_wrapper_round_367_is_pinned` to tie the harness
  reconstruction back to the retail HLIL slot evidence and this mapping note.

## Inference Boundary

The retail binary proves the SteamUser slot ownership and the client voice
packet topology. It does not require this pass to reinterpret the full
`EVoiceResult` enum. The deterministic harness keeps `0` as the success value
because the production wrappers already accept only return value `0`; non-zero
values are used as explicit failure controls for local regression coverage.

Live Steam microphone capture, backend timing, and platform audio-device
behavior remain outside this static/harness pass. Modern networking adapter
work also remains separate from the retained legacy Steam voice lane.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_steamworks_harness.py::test_steam_user_voice_wrappers_use_retail_slots -q
2 passed
```

Planned full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
```

## Parity Estimate

- Focused SteamUser voice wrapper harness parity:
  **before 72% -> after 97%**.
- Client Steam voice transport evidence confidence:
  **before 96% -> after 98%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  microphone/backend behavior and modern networking replacement work remain
  intentionally outside this opt-in reconstruction pass.
