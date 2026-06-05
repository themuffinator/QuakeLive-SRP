# Network EntityState Fields Parity

Date: 2026-06-05

Scope: seventh entry in `docs/plans/2026-06-05-networking-2.md`, reconstructing `entityStateFields` from the committed retail table and updating the source layout/table so entity deltas use the retail field count, offsets, and terminal fields.

## Evidence

Retail anchors from the committed `quakelive_steam.exe` HLIL corpus:

| Retail artifact | Address | Parity observation |
|---|---:|---|
| `entityStateFields` | `0x00542220` | Raw 12-byte entries recover 58 name, offset, and bit-width triples. |
| `MSG_WriteDeltaEntity` | `0x004D5780` | Scans the 58-entry table, writes `lc` as 8 bits, and emits field change records. |
| `MSG_ReadDeltaEntity` | `0x004D5AC0` | Copies `0xec` bytes for no-delta entities, decodes table entries from `data_542220`, and copies unchanged tail fields up to `0x3a`. |

The raw table resolves the previous ledger gap. Source had 52 table entries and ended with a source-only `retailEventData` row. Retail has 58 entries, including:

- `pos.gravity` at index `9`
- `apos.gravity` at index `46`
- `jumpTime` at index `53`
- `doubleJumped` at index `54`
- `health` at index `55`
- `armor` at index `56`
- `location` at index `57`

Retail names the `0xE0` entity slot `generic1`. Existing source code uses that same recovered slot as `retailEventData` for temp-event readability, so the source now keeps `retailEventData` as an alias of the retail `generic1` storage slot instead of serializing it as a separate terminal field.

## Source Of Truth

The machine-readable source of truth is:

- `docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json`

The JSON records each recovered table entry with retail address, field name, offset, bit width, C token, and wire kind. `src/code/qcommon/msg.c` now matches that order, and `src/code/game/q_shared.h` carries the matching `0xec` replicated entity layout:

- `trajectory_t` now includes the retail gravity/acceleration dword after `trDelta`.
- `entityState_t` now includes `health`, `armor`, `location`, `jumpTime`, and `doubleJumped`.
- `generic1` and `retailEventData` share the retail `0xE0` slot.

## Vectors

Focused logical vectors now cover:

| Vector | Coverage |
|---|---|
| `terminal_location_lc` | `location`-only delta emits retail `lc == 58`. |
| `health_armor_tail_lc` | Health and armor tail fields use 16-bit payloads and push `lc` to `57`. |
| `jump_state_tail_lc` | Jump timing fields use indices `53` and `54`, with `doubleJumped` as a 1-bit payload. |
| `trajectory_gravity_lc` | `pos.gravity` and `apos.gravity` are raw 32-bit trajectory scalars at indices `9` and `46`. |
| `generic1_alias_event_payload` | Source `retailEventData` event payloads serialize through the retail `generic1` row at index `33`. |

## Completion

Status: `completed_source_patch_retail_table_source_of_truth`

Validation added:

- `tests/test_netcode_parity_manifest.py::test_networking_2_entitystate_fields_source_of_truth_and_delta_contract`
- `tests/test_cgame_event_transport_parity.py::test_shared_entity_state_restores_retail_event_data_slot`
- `tests/test_bg_playerstate_bridge_parity.py::test_playerstate_bridge_body_stays_on_the_interpolating_retail_path`

Estimated parity movement for this task: focused `entityStateFields` slice `48%` -> `92%`; overall network-protocol parity `82%` -> `84%`.

Residual risk: full end-to-end entity snapshot parity still needs byte-for-byte retail snapshot replay or demo-derived capture comparison.
