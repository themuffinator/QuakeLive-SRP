# Quake Live Steam Mapping Round 289

Date: 2026-05-24

Scope: Awesomium `SteamDataSource` vtable, callback, and lifecycle wiring
source reconstruction in `src/code/client/cl_steam_resources.c`.

## Evidence

Primary retail signals:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  exposes `SteamDataSource::vftable` at `0x00532B80`.
- The same vtable has slot `0x00 -> sub_464510` and
  slot `0x04 -> sub_4640C0`, matching the recovered
  `SteamDataSource_Destroy` and `SteamDataSource_OnRequest` aliases.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  contains RTTI and complete-object-locator evidence for `SteamDataSource`,
  `Awesomium::DataSource`, and
  `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>`.
- The embedded Steam callback vtable is visible at `0x00532B68`.
- `sub_464300` constructs the data source, installs
  `SteamDataSource::vftable`, initializes the two retained STL tree owners,
  installs the `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>`
  vtable, writes the callback owner pointer, writes the callback target
  `sub_464290`, and registers Steam callback id `0x14e`.
- `sub_464440` restores the same vtable/callback-vtable owners, unregisters
  the callback when the registration flag is set, erases both retained tree
  owners, and calls the `Awesomium::DataSource` destructor.
- `sub_464290` handles `AvatarImageLoaded_t` by looking up the pending avatar
  request in the `arg1 + 0xc` SteamID-value tree, erasing that pending owner,
  and forwarding the stored request id/image handle to
  `SteamDataSource_StartResponseThread`.

Companion alias anchors:

| Address | Alias | Evidence role |
|---|---|---|
| `0x00463550` | `SteamDataSource_StartResponseThread` | Starts the retail response worker named `request_%i`. |
| `0x004640C0` | `SteamDataSource_OnRequest` | `Awesomium::DataSource` vtable slot `0x04`. |
| `0x00464290` | `SteamDataSource_OnAvatarImageLoaded` | `AvatarImageLoaded_t` callback target. |
| `0x00464300` | `SteamDataSource_Init` | Constructor/lifecycle owner and callback registration site. |
| `0x00464440` | `SteamDataSource_Shutdown` | Callback unregister and tree teardown. |
| `0x00464510` | `SteamDataSource_Destroy` | `Awesomium::DataSource` vtable slot `0x00`. |

## Source Reconstruction

`src/code/client/cl_steam_resources.c` now records the recovered data-source
wiring through `clSteamDataSourceRetailMapping_t` and
`cl_steamDataSourceRetailMappings[]`.

Each row captures:

- retail owner or embedded callback owner
- retail member or callback role
- vtable address when the retail evidence is vtable-backed
- vtable slot or object/member offset when that offset is meaningful
- retail function address
- current source owner
- the source parity scope for the row

The mapping covers:

| Retail owner | Vtable | Recovered wiring |
|---|---|---|
| `SteamDataSource` | `0x00532B80` | deleting destructor at slot `0x00`, `OnRequest` at slot `0x04`. |
| `SteamDataSource` lifecycle | constructor body | `Init`, `Shutdown`, and the bounded `StartResponseThread` owner. |
| `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>` | `0x00532B68` | callback target at embedded object offset `0x10`, callback id `0x14e`. |

`CL_CountSteamDataSourceRetailMappings()` counts the recovered rows, and
`CL_RefreshSteamResourceBridgeCvars()` now publishes that count through
`ui_resourceBridgeSteamDataSourceMappings`. This keeps the source-visible
diagnostic state aligned with the retail wiring evidence instead of treating
`SteamDataSource` as only a broad compatibility label.

## Guardrails

Observed:

- The `SteamDataSource` vtable and the callback vtable are direct HLIL/Ghidra
  evidence.
- Slot `0x00` is the deleting destructor and slot `0x04` is `OnRequest`.
- `sub_464300` registers `AvatarImageLoaded_t` callback id `0x14e`.
- The callback target is `sub_464290`.
- `sub_464290` erases the pending request and forwards to
  `SteamDataSource_StartResponseThread`.

Inferred:

- The source owner `CL_SteamResources_OnAvatarImageLoaded` is the repository's
  bounded open replacement for the retail callback target: it clears pending
  avatar state and allows retry, but it does not hold a live Awesomium delayed
  response object.
- `CL_SteamResources_RequestAvatarRGBA` is the closest source owner for the
  retail `StartResponseThread` role because default builds avoid recreating the
  C++ `ResponseThread`/`Awesomium::DataSource::SendResponse` path.

Still bounded:

- The source does not recreate the exact retail C++ `SteamDataSource` object
  layout or its STL tree node layout.
- The source does not launch the retail `ResponseThread` or call
  `Awesomium::DataSource::SendResponse` asynchronously in default builds.
- Default builds continue to keep live Steam/Awesomium services behind
  `QL_BUILD_ONLINE_SERVICES`.

## Validation

New and updated static coverage:

- `tests/test_awesomium_browser_parity.py` checks the
  `cl_steamDataSourceRetailMappings[]` table, vtable addresses, callback
  target, lifecycle rows, and diagnostic cvar.
- `tests/test_platform_services.py` checks that the recovered mapping survives
  the default online-service-disabled resource bridge policy.
- `tools/ci/verify-awesomium-browser-host-parity.ps1` now checks source,
  alias, and mapping anchors for this round.

No game/runtime launch was performed. This round is static source
reconstruction and mapping documentation.

## Parity Movement

Before this round, the `SteamDataSource` resource bridge was about 84%
source-visible for the data-source wiring seam: request handling, avatar
fallbacks, and callback retry state existed, but the retail vtable and embedded
callback wiring remained mostly in docs and aliases.

After this round, the seam is about 93% source-visible and 98% mapped. The
remaining delta is the documented live-service boundary: exact C++ object
allocation, async response-thread lifetime, and `Awesomium::DataSource`
`SendResponse` ownership remain bounded rather than recreated in the default
offline-safe build.
