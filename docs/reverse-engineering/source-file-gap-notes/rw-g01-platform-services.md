# `src/common/platform/platform_services.c` Divergence Note

Last updated: 2026-05-24

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Permanent bounded divergence for default builds; strict-retail Windows closure intentionally excludes this compatibility-only build lane unless a documented open replacement path is adopted.

## Why this file remains a documented divergence

This file publishes build-disabled, externally-disabled, Steamworks, open-adapter, and hybrid descriptors, plus explicit parity-scope and parity-reason labels. That keeps the repo honest and makes the bounded compatibility story machine-visible instead of pretending the checked-in tree has a retail-equivalent live-service surface.

## Observed facts

- Default builds return `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` provider labels for auth, matchmaking, workshop, overlay, and stats.
- Runtime environment variables can also force the descriptor table into a disabled external-ecosystem mode.
- Hybrid and open-adapter provider labels remain explicit compatibility descriptors, not evidence of a retail live-service implementation.
- `QL_GetOnlineServicesParityScopeLabel()` returns `permanent-bounded-divergence` for default builds, and `QL_GetOnlineServicesParityReasonLabel()` explains that online services stay disabled until a documented open replacement exists.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_StringRepresentsTrue` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |
| `QL_PlatformExternalEcosystemsDisabled` | `bounded compatibility` | Runtime kill-switch for the non-retail external ecosystem lane. |
| `QL_FinaliseDescriptor` | `bounded compatibility` | Normalises fallback labels for compatibility descriptors. |
| `QL_DescribePlatformFeaturePolicy` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |
| `QL_GetOnlineServicesModeLabel` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |
| `QL_GetOnlineServicesPolicyLabel` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |
| `QL_GetOnlineServicesParityScopeLabel` | `bounded divergence classifier` | Makes the default build's permanent bounded divergence explicit to client and test surfaces. |
| `QL_GetOnlineServicesParityReasonLabel` | `bounded divergence classifier` | Publishes the stable reason string for default-disabled and opt-in compatibility lanes. |
| `QL_PlatformSteamworks_InitOnce` | `bounded compatibility` | Caches wrapper initialisation, but still sits under the bounded online-service policy. |
| `QL_BuildServiceTable` | `divergence owner` | Builds the service descriptor table that explicitly advertises build-disabled and compatibility-only providers. |
| `QL_GetPlatformServices` | `helper closed` | Helper-only function; not the primary remaining parity blocker by itself. |

## Maintenance expectations

- Keep the current explicit compatibility and parity-scope labels while this lane remains a permanent bounded divergence.
- If a real open implementation is pursued later, refresh the descriptor table, auth, workshop, and runtime evidence together so the policy story stays consistent.
