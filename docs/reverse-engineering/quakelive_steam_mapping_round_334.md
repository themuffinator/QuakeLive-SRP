# Quake Live Steam Mapping Round 334: WebUI Launch Cache and Browser Image Split

Date: 2026-05-28

Scope: Awesomium WebUI launch gating, WebSession cache clear, and the browser
surface shader/image upload path involved in the Campgrounds launch/cache issue.

## Evidence Checked

- `references/analysis/quakelive_symbol_aliases.json` maps the relevant retail
  owners: `sub_4F2A10` to `CL_Web_ClearCache_f`, `sub_4F2A30` to
  `CL_Web_Reload_f`, `sub_4F2590` to `QLWebCore_Update`, `sub_445910` to
  `R_CreateImage`, `sub_458A40` to `R_GetShaderByHandle`, and `sub_4586D0` to
  `RE_RegisterShaderFromImage`.
- Binary Ninja HLIL for `sub_4f2a10` and `sub_4f2a30` shows WebSession slot
  `0x1c` used for `web_clearCache` and before reload.
- Binary Ninja HLIL for the browser bitmap update shows retail creating/updating
  the image named `browser`, then retrieving the retained shader handle and
  replacing the shader-stage image pointer.
- Retail shader registration evidence names the retained browser shader
  `browserShader`.
- `dumpbin /exports` against both the staged rebuilt runtime and the Steam
  Quake Live runtime confirms `_Awe_WebSession_ClearCache@4`,
  `_Awe_WebSession_Release@4`, and `_Awe_WebView_Reload@8`.

## Source Reconstruction

- Added the optional `_Awe_WebSession_ClearCache@4` import and mapped retail
  WebSession slot `0x1c` to `CL_Awesomium_ClearCache`.
- Kept `_Awe_WebSession_Release@4` shutdown-only.
- Split live RGBA shader registration so callers can supply separate shader and
  backing-image names.
- Updated the WebUI surface path to keep the retail shader handle
  `browserShader` while using private image name `*ql_web_browser`, preserving
  the collision fix for unrelated renderer image caching.
- Left existing Steam/avatar image callers on the original one-name wrapper.

## Runtime Verification

- Built `Debug|x86` with the default VS Code task arguments and
  `QL_BUILD_ONLINE_SERVICES=1`; the build completed with the expected warning
  that an external Awesomium SDK path was not supplied for SDK link artifacts.
- Ran the Campgrounds launch-task equivalent from
  `build/win32/Debug/bin` with `+set r_fullscreen 0` and
  `+set ui_browserAwesomium 0`. The log loaded local `qagamex86.dll` and
  `cgamex86.dll`, reached `CL_Shutdown`, and wrote engine screenshot
  `build/win32/Debug/dumps/screenshots/campgrounds_webui_cache_shot0032.jpg`.
- Ran the WebUI-enabled launch-task equivalent from the same cwd with
  `+set ui_browserAwesomium 1 +web_clearCache +web_reload`. The log reached
  `Awesomium startup phase: live WebView ready`, then
  `Awesomium surface became visible`, wrote engine screenshot
  `build/win32/Debug/dumps/screenshots/awesomium_webui_cache_shot0033.jpg`,
  and exited with code `0`.
- A workspace-cwd exploratory launch loaded retail `qagamex86.dll` and
  `cgamex86.dll` from `fs_basepath` before `fs_homepath` and crashed; this is a
  launch-path contamination finding, not the VS Code launch task behavior,
  because the launch task cwd is `build/win32/Debug/bin`.

## Parity Estimate

- Focused WebUI launch/cache/image lane: **88% -> 94%**.
- Overall Awesomium WebUI wiring: **99.0% -> 99.2%**. Native JS handler and
  resource-interceptor objects remain mapped but not fully reconstructed.
- Repo-wide parity remains **98% -> 98%** because online services are still
  intentionally gated behind `QL_BUILD_ONLINE_SERVICES`.
