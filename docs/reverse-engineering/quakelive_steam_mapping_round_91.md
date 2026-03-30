# Quake Live Steam Host Mapping Round 91

## Scope

This round closes the next bounded `quakelive_steam.exe` launcher/resource
slice at the retail `QLResourceInterceptor_OnRequest` fallback owner:

- preserve `web.pak` as the first launcher data-source owner
- restore the retail mapped filesystem fallback behind unresolved URI requests
- route launcher-style URI resources through the same cache bridge already used
  for Steam-backed image requests

The evidence stayed inside the committed corpus plus the writable source tree:

- `docs/launcher_awesomium_audit.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- `src/code/qcommon/files.c`
- `src/code/client/cl_webpak.c`
- `src/code/client/cl_steam_resources.c`
- `tests/test_platform_services.py`

## Launcher resource interceptor fallback

Observed facts from the committed evidence before this round:

- the Awesomium audit already documented that retail `QLResourceInterceptor`
  handles unresolved requests by rewriting them against `fs_webpath`, with
  screenshot requests rewritten into `fs_homepath/screenshots/...`
- the shared filesystem layer in `files.c` already contained the retained
  rewrite and open helpers for that exact policy:
  - `FS_RewriteWebPath(...)`
  - `FS_FOpenWebFileRead(...)`
- the client launcher bridge in `cl_webpak.c` still only did:
  - `web.pak` lookup
  - local normalized `FS_ReadFile(...)` fallback
- the URI shader/resource cache bridge in `cl_steam_resources.c` still only
  treated `steam://avatar/...` as a real fetch owner and left other URI-backed
  launcher resources outside the retained cache path

That meant the repo already had the engine-owned rewrite helpers, but the
client-side launcher/resource bridge still stopped short of the retail
interceptor behavior that actually consumed them.

## Retained source changes

The writable source now closes that owner chain explicitly:

- `src/code/client/cl_webpak.c`
  - tightens `CL_WebPak_NormalizePath(...)` so URI-scheme requests do not fall
    into the local-path `web.pak` / plain-filesystem branch
  - adds `CL_WebRequestReadMappedFile(...)` as the retained owner for the
    `fs_webpath` / screenshot fallback path through `FS_FOpenWebFileRead(...)`
  - updates `CL_WebRequestResolve(...)` to follow the retail layering:
    `web.pak` first, mapped interceptor fallback second, plain normalized
    filesystem read last
- `src/code/client/cl_steam_resources.c`
  - adds `CL_SteamResources_IsURIResource(...)` so URI-backed launcher assets
    no longer fall through to direct `RegisterShaderNoMip(...)`
  - keeps Steam-avatar ownership in the Steamworks path
  - routes non-avatar URI requests through `CL_LauncherRequestData(...)`
  - keeps the existing cache-file and shader-registration flow so launcher web,
    screenshot, and Steam-backed resources all reuse one retained cache bridge

This intentionally does not invent a full Awesomium runtime. It only restores
the documented retail filesystem/resource ownership already described by the
committed interceptor notes.

## Verification

Updated coverage landed in:

- `tests/test_platform_services.py`

Command run:

```text
python -m pytest tests/test_steamworks_harness.py tests/test_platform_services.py tests/test_ui_menu_files.py -q
```

Result:

- `85 passed`

## Outcome

This round did not add new address aliases. It consumed already-mapped host
ownership in one concrete way:

- launcher URI resources now follow the same retained ownership chain as the
  retail interceptor notes: `web.pak` first, mapped `fs_webpath` /
  `screenshots` fallback second, then the existing URI cache bridge for shader
  registration

Estimated parity for this round: `91% -> 92%`.
