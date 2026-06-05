"""Validate snapshot field decode parity reports."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .demo_transcript import RETAIL_CAPTURE_TYPES, RETAIL_PROVENANCE_KEYS


SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
FIELD_TABLE_NAMES = ("playerStateFields", "entityStateFields")
EXPECTED_FIELD_COUNT = 58


class SnapshotDecodeError(ValueError):
    """Raised when a snapshot decode report is malformed."""


def _require_non_empty_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise SnapshotDecodeError(f"{context} must be a non-empty string")
    return value


def _require_int(value: object, context: str) -> int:
    if not isinstance(value, int):
        raise SnapshotDecodeError(f"{context} must be an integer")
    return value


def _require_non_negative_int(value: object, context: str) -> int:
    value = _require_int(value, context)
    if value < 0:
        raise SnapshotDecodeError(f"{context} must be a non-negative integer")
    return value


def _require_sha256(value: object, context: str) -> str:
    if not isinstance(value, str) or not SHA256_HEX_RE.match(value):
        raise SnapshotDecodeError(f"{context} must be a lowercase SHA-256 hex string")
    return value


def _validate_retail_provenance(report: Mapping[str, Any]) -> None:
    provenance = report.get("provenance")
    if not isinstance(provenance, Mapping):
        raise SnapshotDecodeError("retail snapshot decode report requires provenance metadata")
    missing = [
        key
        for key in RETAIL_PROVENANCE_KEYS
        if not isinstance(provenance.get(key), str) or not provenance.get(key)
    ]
    if missing:
        raise SnapshotDecodeError(
            f"retail snapshot decode provenance missing required keys: {', '.join(missing)}"
        )
    if provenance.get("capture_type") not in RETAIL_CAPTURE_TYPES:
        raise SnapshotDecodeError("retail snapshot decode provenance capture_type is not recognized")


def _field_index_from_spec(spec: Mapping[str, Any] | None, table_name: str) -> dict[str, Mapping[str, Any]]:
    if spec is None:
        return {}
    source_of_truth = spec.get("source_of_truth")
    if not isinstance(source_of_truth, Mapping):
        raise SnapshotDecodeError(f"{table_name} spec source_of_truth must be an object")
    entries = source_of_truth.get("entries")
    if not isinstance(entries, list):
        raise SnapshotDecodeError(f"{table_name} spec source_of_truth entries must be a list")

    index: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise SnapshotDecodeError(f"{table_name} spec entry must be an object")
        field = entry.get("field")
        if not isinstance(field, str) or not field:
            raise SnapshotDecodeError(f"{table_name} spec entry field must be a non-empty string")
        index[field] = entry
        alias = entry.get("source_alias")
        if isinstance(alias, str) and alias:
            index[alias] = entry
    return index


def _validate_observed_fields(
    table: Mapping[str, Any],
    *,
    table_name: str,
    spec_entries: Mapping[str, Mapping[str, Any]],
) -> int:
    observed_fields = table.get("observed_fields")
    if not isinstance(observed_fields, list):
        raise SnapshotDecodeError(f"{table_name} observed_fields must be a list")
    if not observed_fields:
        raise SnapshotDecodeError(f"{table_name} observed_fields must not be empty")

    seen: set[str] = set()
    for index, field in enumerate(observed_fields):
        if not isinstance(field, Mapping):
            raise SnapshotDecodeError(f"{table_name} observed field {index} must be an object")
        field_name = _require_non_empty_string(
            field.get("field"),
            f"{table_name} observed field {index} field",
        )
        if field_name in seen:
            raise SnapshotDecodeError(f"{table_name} observed field repeated: {field_name}")
        seen.add(field_name)

        observed_index = _require_non_negative_int(
            field.get("index"),
            f"{table_name} observed field {field_name} index",
        )
        if observed_index >= EXPECTED_FIELD_COUNT:
            raise SnapshotDecodeError(f"{table_name} observed field {field_name} index is out of range")
        observed_bits = _require_int(field.get("bits"), f"{table_name} observed field {field_name} bits")
        _require_non_empty_string(
            field.get("wire_kind"),
            f"{table_name} observed field {field_name} wire_kind",
        )
        _require_sha256(field.get("value_hash"), f"{table_name} observed field {field_name} value_hash")

        spec_entry = spec_entries.get(field_name)
        if spec_entry is not None:
            if spec_entry.get("index") != observed_index:
                raise SnapshotDecodeError(f"{table_name} observed field {field_name} index does not match spec")
            if spec_entry.get("bits") != observed_bits:
                raise SnapshotDecodeError(f"{table_name} observed field {field_name} bits do not match spec")
            if spec_entry.get("wire_kind") != field.get("wire_kind"):
                raise SnapshotDecodeError(
                    f"{table_name} observed field {field_name} wire_kind does not match spec"
                )
        elif spec_entries:
            raise SnapshotDecodeError(f"{table_name} observed field {field_name} is not in the retail spec")

    return len(observed_fields)


def _validate_field_tables(
    report: Mapping[str, Any],
    *,
    playerstate_spec: Mapping[str, Any] | None,
    entitystate_spec: Mapping[str, Any] | None,
) -> tuple[int, int]:
    field_tables = report.get("field_tables")
    if not isinstance(field_tables, list):
        raise SnapshotDecodeError("snapshot decode field_tables must be a list")

    tables_by_name: dict[str, Mapping[str, Any]] = {}
    for index, table in enumerate(field_tables):
        if not isinstance(table, Mapping):
            raise SnapshotDecodeError(f"snapshot decode field table {index} must be an object")
        table_name = table.get("name")
        if table_name not in FIELD_TABLE_NAMES:
            raise SnapshotDecodeError(f"snapshot decode field table {index} name is not recognized")
        if table_name in tables_by_name:
            raise SnapshotDecodeError(f"snapshot decode field table repeated: {table_name}")
        tables_by_name[table_name] = table

    missing = [name for name in FIELD_TABLE_NAMES if name not in tables_by_name]
    if missing:
        raise SnapshotDecodeError(f"snapshot decode field_tables missing: {', '.join(missing)}")

    observed_total = 0
    for table_name, spec in (
        ("playerStateFields", playerstate_spec),
        ("entityStateFields", entitystate_spec),
    ):
        table = tables_by_name[table_name]
        if table.get("field_count") != EXPECTED_FIELD_COUNT:
            raise SnapshotDecodeError(f"{table_name} field_count must be {EXPECTED_FIELD_COUNT}")
        _require_sha256(table.get("decode_hash"), f"{table_name} decode_hash")
        observed_total += _validate_observed_fields(
            table,
            table_name=table_name,
            spec_entries=_field_index_from_spec(spec, table_name),
        )

    return len(field_tables), observed_total


def _validate_snapshot_frames(report: Mapping[str, Any]) -> int:
    snapshots = report.get("snapshots")
    if not isinstance(snapshots, list):
        raise SnapshotDecodeError("snapshot decode snapshots must be a list")
    if not snapshots:
        raise SnapshotDecodeError("snapshot decode snapshots must not be empty")

    for index, snapshot in enumerate(snapshots):
        if not isinstance(snapshot, Mapping):
            raise SnapshotDecodeError(f"snapshot {index} must be an object")
        _require_non_negative_int(snapshot.get("messageNum"), f"snapshot {index} messageNum")
        _require_int(snapshot.get("serverTime"), f"snapshot {index} serverTime")
        _require_int(snapshot.get("deltaNum"), f"snapshot {index} deltaNum")
        _require_non_negative_int(snapshot.get("packetEntityCount"), f"snapshot {index} packetEntityCount")
        _require_sha256(snapshot.get("playerStateHash"), f"snapshot {index} playerStateHash")
        _require_sha256(snapshot.get("entityStateHash"), f"snapshot {index} entityStateHash")
        _require_sha256(snapshot.get("packetEntitiesHash"), f"snapshot {index} packetEntitiesHash")

    return len(snapshots)


def validate_snapshot_field_decode_dict(
    report: Mapping[str, Any],
    *,
    playerstate_spec: Mapping[str, Any] | None = None,
    entitystate_spec: Mapping[str, Any] | None = None,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a retail snapshot player/entity field decode report."""

    if report.get("schema_version") != 1:
        raise SnapshotDecodeError("snapshot decode schema_version must be 1")
    if report.get("format") != "quake_live_snapshot_field_decode":
        raise SnapshotDecodeError("snapshot decode format must be quake_live_snapshot_field_decode")

    capture_id = _require_non_empty_string(report.get("capture_id"), "snapshot decode capture_id")
    protocol = _require_int(report.get("protocol"), "snapshot decode protocol")
    if protocol != 91:
        raise SnapshotDecodeError("snapshot decode protocol must be 91")

    if require_retail_provenance:
        _validate_retail_provenance(report)

    table_count, observed_field_count = _validate_field_tables(
        report,
        playerstate_spec=playerstate_spec,
        entitystate_spec=entitystate_spec,
    )
    snapshot_count = _validate_snapshot_frames(report)

    return {
        "capture_id": capture_id,
        "protocol": protocol,
        "field_table_count": table_count,
        "observed_field_count": observed_field_count,
        "snapshot_count": snapshot_count,
    }
