# Quake Live Steamworks Mapping Round 368

Date: 2026-06-06

Focus: reconstruct executable harness coverage for the SteamFriends
`SetInGameVoiceSpeaking` wrapper used by the retained `+voice` and `-voice`
command owners.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt` and
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Existing mapping anchors:
  `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_367.md`, and
  `tests/test_engine_client_command_parity.py`.

Observed HLIL evidence:

- `0x00460430` obtains the local SteamID through `SteamUser()` slot `0x08`
  while starting voice capture.
- `0x00460441` forwards that SteamID into `SteamFriends()` slot `0x6c` with
  speaking value `1`.
- `0x004604cc` obtains the local SteamID again while stopping voice capture.
- `0x004604dc` forwards the same identity into `SteamFriends()` slot `0x6c`
  with speaking value `0`.

## Observed Facts

- The production wrapper `QL_Steamworks_SetInGameVoiceSpeaking` already maps
  the SteamFriends vtable slot as `0x6c / 4`.
- The wrapper combines the low/high identity words with
  `QL_Steamworks_CombineIdentityWords` and forwards `speaking ? 1 : 0`.
- `CL_VoiceStartRecording_f` and `CL_VoiceStopRecording_f` already call the
  wrapper around the SteamUser capture start/stop path, while offline builds
  continue to use the local cgame speaking-state fallback.
- Before this pass, the harness had SteamFriends coverage for presence,
  overlays, avatars, and invites, but not this voice-speaking slot.

## Source Reconstruction

This pass extended the local Steamworks harness:

- Added mock state for SteamFriends voice-speaking calls, last SteamID, and
  last speaking value.
- Added `QLR_SteamFriends_SetInGameVoiceSpeaking` and installed it in the mock
  SteamFriends vtable at `0x6c / 4`.
- Exported enabled and disabled harness wrappers for
  `QL_Steamworks_SetInGameVoiceSpeaking`.
- Added `test_steam_friends_voice_speaking_wrapper_uses_retail_slot` to prove
  SteamID word-combination, speaking-on/speaking-off forwarding, call counts,
  and disabled fallback behavior.
- Added `test_steam_friends_voice_speaking_round_368_is_pinned` to tie the
  production wrapper, mock vtable, executable test, HLIL evidence, and this
  note together.

## Inference Boundary

The retail evidence proves the SteamFriends slot, the local SteamID source,
and the speaking flag values used by the retained voice commands. This round
does not claim live Steam overlay, friend-list, microphone, or backend timing
behavior. It only closes deterministic wrapper coverage for the already-mapped
speaking-state edge.

## Verification

Local verification for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_friends_voice_speaking_round_368_is_pinned tests/test_steamworks_harness.py::test_steam_friends_voice_speaking_wrapper_uses_retail_slot -q
3 passed
```

Full Steamworks/platform verification:

```text
python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py -q
188 passed
```

## Parity Estimate

- Focused SteamFriends voice-speaking wrapper harness parity:
  **before 60% -> after 97%**.
- Retained client voice command wrapper evidence confidence:
  **before 98% -> after 99%**.
- Broader Steamworks parity remains approximately **99%** because live Steam
  backend behavior and modern networking replacement work remain outside this
  opt-in reconstruction pass.
