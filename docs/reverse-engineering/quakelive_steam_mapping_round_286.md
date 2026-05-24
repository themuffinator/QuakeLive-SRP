# Quake Live Steam Host Mapping Round 286

## Scope

- Continued the Awesomium/browser-host reconstruction pass around the native
  cgame import slab and the web comm-notice bridge.
- Resolved the source-side mismatch left open by round 275: native cgame slot
  `116` is a tagged info-string publisher, not a cvar-string buffer helper.
- Rechecked the retail `sub_4BF5D0 -> sub_4EC6D0 -> sub_4F2950` path against
  source wiring, tests, and the static Awesomium browser-host verifier.

## Evidence

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  shows the host-side publisher:
  - `0x004B03B0` tailcalls `sub_4BF5D0`.
  - `0x004BF5D0` constructs a message object, writes key `MSG_TYPE`, walks the
    supplied info string through `sub_4D9380`, serializes the object, and calls
    `sub_4EC6D0`.
  - `0x004EC6D0` is a tail thunk to `sub_4F2950`.
  - `0x004F2950` pushes a single serialized string argument and invokes the
    bound browser object method named `OnCommNotice`.
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` confirms the
  caller side:
  - `0x10048931` calls import offset `0x1D0` with `"serverinfo"` and the
    current serverinfo info string.
  - `0x10049440` repeats the same call during the later config-value refresh.
- `references/analysis/quakelive_symbol_aliases.json` already carries the
  address-backed ownership names:
  - `sub_4B03B0` -> `QLCGImport_PublishTaggedInfoString`
  - `sub_4BF5D0` -> `QLWebView_PublishTaggedInfoString`
  - `sub_4EC6D0` -> `QLWebView_InvokeCommNoticeThunk`
  - `sub_4F2950` -> `QLWebView_InvokeCommNotice`

## Source Reconstruction

- Renamed cgame native import slot `116` from the compatibility-only
  `CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER` to
  `CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING`.
- Replaced `QL_CG_trap_TaggedCvarStringBuffer` in the client host import table
  with `QL_CG_trap_PublishTaggedInfoString`, which forwards to the browser host
  publisher.
- Added `CL_WebView_PublishTaggedInfoString` in `cl_main.c`:
  - starts a JSON object with `MSG_TYPE`;
  - iterates the incoming info string with `Info_NextPair`;
  - appends each key/value pair using the retained browser JSON escaping helper;
  - forwards the serialized object to `CL_WebView_InvokeCommNotice`.
- Narrowed `CL_WebView_InvokeCommNotice` to the retail one-argument shape and
  kept the source-owned fallback event lane as the transport for the serialized
  `OnCommNotice` payload.
- Updated cgame syscall declarations and null-client stubs so QVM and
  portability lanes remain explicit no-ops rather than resurrecting the old
  cvar-buffer behavior.

## Source Files

| File | Change |
| --- | --- |
| `src/code/cgame/cg_public.h` | Slot `116` now names the publish-tagged-info-string import. |
| `src/code/cgame/cg_syscalls.c` | Adds `trap_QL_PublishTaggedInfoString` over the renamed native import. |
| `src/code/cgame/cg_local.h` | Provides a QVM-side no-op fallback for the retail-only browser publish lane. |
| `src/code/client/client.h` | Declares the one-argument comm-notice invoker and tagged info-string publisher. |
| `src/code/client/cl_cgame.c` | Wires native cgame slot `116` to `QL_CG_trap_PublishTaggedInfoString`. |
| `src/code/client/cl_main.c` | Reconstructs the info-string-to-comm-notice serialization path. |
| `src/code/null/null_client.c` | Keeps null-host behavior explicit with matching no-op stubs. |
| `tools/ci/verify-awesomium-browser-host-parity.ps1` | Extends static Awesomium verification to this source-owned lane. |

## Guardrails

- Extended
  `tests/test_engine_client_command_parity.py::test_client_cgame_native_bridge_mapping_round_275_promotes_hlil_backed_symbols`
  so the original retail address evidence now requires the reconstructed source
  owner names and one-argument comm-notice signature.
- Added a focused Awesomium browser parity guard for the tagged info-string
  lane in `tests/test_awesomium_browser_parity.py`.
- Extended `tools/ci/verify-awesomium-browser-host-parity.ps1` with source,
  alias, and round-286 mapping anchors.

## Parity Estimate

- Before this round, the address mapping was high-confidence, but the writable
  source still modeled slot `116` as a cvar read. I estimate the focused native
  cgame-to-Awesomium comm-notice lane at roughly `70%` source parity and `95%`
  mapping parity.
- After this round, the source behavior, names, and static guards align with
  the retail HLIL evidence. I estimate this focused lane at `96%` source parity
  and `97%` mapping parity; the remaining uncertainty is the exact Awesomium
  JS object/string ABI beneath the repository's compatibility event queue.
- The broader Awesomium source-owned Windows parity estimate remains effectively
  closed for the repository target. Literal retail ABI parity is still bounded
  by the documented C-export Awesomium adapter and default-off online services.
