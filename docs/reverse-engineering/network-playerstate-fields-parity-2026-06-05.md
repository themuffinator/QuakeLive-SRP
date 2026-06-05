# Network PlayerState Fields Parity

Date: 2026-06-05

Scope: sixth entry in `docs/plans/2026-06-05-networking-2.md`, reconstructing `playerStateFields` from the committed retail table and using a single machine-readable source of truth for table order, offsets, bit widths, and focused golden vectors.

## Evidence

Retail anchors from the committed `quakelive_steam.exe` HLIL corpus:

| Retail artifact | Address | Parity observation |
|---|---:|---|
| `playerStateFields` | `0x005424D8` | Raw 12-byte entries recover 58 name, offset, and bit-width triples. |
| `MSG_WriteDeltaPlayerstate` | `0x004D5D50` | Scans the 58-entry table, writes `lc` as 8 bits, then serializes scalar fields and four array masks. |
| `MSG_ReadDeltaPlayerstate` | `0x004D66C0` | Copies the 0x250-byte baseline window, reads `lc`, decodes table entries, copies the unchanged tail to `0x3a`, then reads `PS_STATS`, `PS_PERSISTANT`, `PS_AMMO`, and `PS_POWERUPS`. |

The decisive correction is table order. Retail places `jumpTime` and `doubleJumped` after `loopSound`, at zero-based indices `49` and `50`. The source previously placed those fields immediately after `groundEntityNum`, which would have produced too-small `lc` values for jump-timing-only deltas.

## Source Of Truth

The machine-readable source of truth is:

- `docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json`

The JSON records every recovered table entry with:

- retail table address
- field name
- retail `playerState_t` offset
- wire bit width
- C table bit token for generation, including `GENTITYNUM_BITS`
- wire kind, including signed-byte handling for `forwardmove`, `rightmove`, and `upmove`

`src/code/qcommon/msg.c` now matches that source of truth. The existing playerstate replication test reads the JSON rather than carrying a second hardcoded table copy.

## Vectors

Focused logical vectors now cover:

| Vector | Coverage |
|---|---|
| `jump_time_tail_lc` | `jumpTime`-only delta emits retail `lc == 50`, proving the field is at index `49`. |
| `double_jump_tail_lc` | `doubleJumped`-only delta emits retail `lc == 51`. |
| `command_mirror_tail_lc` | `weaponPrimary`, `fov`, and signed command mirrors push `lc` to `58`; signed bytes serialize as unsigned 8-bit payloads and decode back to signed values. |
| `pm_flags_24_bit` | `pm_flags` remains a 24-bit scalar field at index `19`. |
| `origin0_integral_float` | Float fields keep the classic integral-float optimization with `FLOAT_INT_BIAS == 4096` and `FLOAT_INT_BITS == 13`. |

## Completion

Status: `completed_source_patch_retail_table_source_of_truth`

Validation added:

- `tests/test_netcode_parity_manifest.py::test_networking_2_playerstate_fields_source_of_truth_and_roundtrip_contract`
- `tests/test_playerstate_replication.py::test_playerstate_netfield_table_matches_retail_quake_live_scalar_order`

Estimated parity movement for this task: focused `playerStateFields` slice `70%` -> `94%`; overall network-protocol parity `80%` -> `82%`.

Residual risk: full end-to-end snapshot parity still needs at least one byte-for-byte retail snapshot capture or demo-derived replay fixture.
