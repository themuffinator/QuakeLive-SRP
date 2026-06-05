"""Validate residual capture evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .capture_diff import validate_packet_capture_dict
from .demo_transcript import (
    RETAIL_CAPTURE_TYPES,
    RETAIL_PROVENANCE_KEYS,
    validate_demo_transcript_dict,
)
from .fragment_timing import validate_fragment_queue_timing_dict
from .invalid_lc_probe import validate_invalid_lc_probe_dict
from .snapshot_decode import validate_snapshot_field_decode_dict


SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
TARGET_STATUSES = frozenset({"submitted_for_closure", "supporting_evidence", "not_claimed"})
TEXT_ARTIFACT_SUFFIXES = frozenset({".json", ".md", ".txt"})
RAW_BINARY_ARTIFACT_SUFFIXES = frozenset({".7z", ".dm_90", ".dm_91", ".dmp", ".pcap", ".pcapng", ".zip"})
ALLOWED_ARTIFACT_PATH_PREFIXES = (
    "docs/reverse-engineering/evidence/",
    "docs/reverse-engineering/fixtures/",
    "tests/netdumps/",
    "tools/tests/client_regression/",
)
REJECTED_ARTIFACT_PATH_PREFIXES = (
    "assets/",
    "references/",
    "src/",
    "src/ui/",
)
ARTIFACT_TYPES = frozenset(
    {
        "capture_diff_report",
        "demo_transcript",
        "fragment_queue_timing_report",
        "invalid_lc_probe_report",
        "packet_capture",
        "snapshot_decode_report",
    }
)
ROW_ALLOWED_FORMATS = {
    "byte_for_byte_replay_fixture": frozenset(
        {
            "quake_live_demo_message_transcript",
            "quake_live_packet_byte_capture",
        }
    ),
    "fragmented_snapshot_queued_followup": frozenset({"quake_live_fragment_queue_timing"}),
    "xor_golden_datagrams": frozenset(
        {
            "quake_live_capture_diff_report",
            "quake_live_packet_byte_capture",
        }
    ),
    "compressed_connect_capture_diff": frozenset(
        {
            "quake_live_capture_diff_report",
            "quake_live_packet_byte_capture",
        }
    ),
    "invalid_lc_retail_probe": frozenset({"quake_live_invalid_lc_probe"}),
    "snapshot_field_capture_decode": frozenset({"quake_live_snapshot_field_decode"}),
}
FORMAT_VALIDATORS: dict[str, Callable[..., Mapping[str, Any]]] = {
    "quake_live_demo_message_transcript": validate_demo_transcript_dict,
    "quake_live_packet_byte_capture": validate_packet_capture_dict,
    "quake_live_fragment_queue_timing": validate_fragment_queue_timing_dict,
    "quake_live_invalid_lc_probe": validate_invalid_lc_probe_dict,
    "quake_live_snapshot_field_decode": validate_snapshot_field_decode_dict,
}
FORMAT_ARTIFACT_TYPES = {
    "quake_live_capture_diff_report": "capture_diff_report",
    "quake_live_demo_message_transcript": "demo_transcript",
    "quake_live_fragment_queue_timing": "fragment_queue_timing_report",
    "quake_live_invalid_lc_probe": "invalid_lc_probe_report",
    "quake_live_packet_byte_capture": "packet_capture",
    "quake_live_snapshot_field_decode": "snapshot_decode_report",
}
ROW_CHECKLIST_TEXT = {
    "byte_for_byte_replay_fixture": (
        "Commit at least one retail packet capture, protocol-91 demo transcript, "
        "or equivalent known-good capture fixture for byte-for-byte replay validation."
    ),
    "fragmented_snapshot_queued_followup": (
        "Validate fragmented snapshot plus queued follow-up timing against a byte-for-byte retail capture."
    ),
    "xor_golden_datagrams": "Capture-diff the XOR golden datagrams against retail packet traces.",
    "compressed_connect_capture_diff": "Capture-diff the compressed connect request path against a retail trace.",
    "invalid_lc_retail_probe": (
        "Probe invalid-lc malicious packet behavior against retail before claiming exact crash/drop equivalence."
    ),
    "snapshot_field_capture_decode": (
        "Verify end-to-end retail snapshot capture/decode parity for playerStateFields and entityStateFields."
    ),
}
ROW_REQUIRED_EVIDENCE = {
    "byte_for_byte_replay_fixture": [
        "retail datagram bytes, protocol-91 demo transcript bytes, or equivalent known-good byte fixture",
        "retail provenance with source, capture_type, capture_date_utc, and retail_build",
        "lowercase SHA-256 for each committed JSON/text artifact",
    ],
    "fragmented_snapshot_queued_followup": [
        "fragmented retail server-message capture from one session",
        "queued follow-up datagram from the same session",
        "timing report proving terminal fragment acceptance and encode-on-pop behavior",
    ],
    "xor_golden_datagrams": [
        "retail packet trace exercising the committed XOR vector windows",
        "capture-diff report with match status for each submitted XOR fixture",
        "packet hashes for the observed retail datagrams",
    ],
    "compressed_connect_capture_diff": [
        "retail compressed connect datagram trace",
        "documented challenge and qport inputs for the trace",
        "capture-diff report matching the committed compressed-connect fixture from offset 12",
    ],
    "invalid_lc_retail_probe": [
        "controlled retail invalid-lc probe report",
        "log, dump, or equivalent artifact classifying retail crash/drop behavior",
        "source comparison against the guarded ERR_DROP path",
    ],
    "snapshot_field_capture_decode": [
        "retail snapshot packet capture or protocol-91 transcript with playerstate and packet entities",
        "decode report covering playerStateFields and entityStateFields",
        "field-level hashes or byte comparisons against the recovered retail field tables",
    ],
}
RESIDUAL_CLOSURE_ROW_IDS = tuple(ROW_ALLOWED_FORMATS)


class CaptureEvidenceError(ValueError):
    """Raised when a residual capture evidence bundle is malformed."""


def _artifact_templates(row_id: str) -> list[dict[str, str]]:
    return [
        {
            "id": f"replace-me-{artifact_format}",
            "type": FORMAT_ARTIFACT_TYPES[artifact_format],
            "format": artifact_format,
            "path": "docs/reverse-engineering/fixtures/replace-me.json",
            "sha256": "replace-with-lowercase-sha256",
            "description": f"replace with retail evidence description for {row_id}",
        }
        for artifact_format in sorted(ROW_ALLOWED_FORMATS[row_id])
    ]


def _template_row_ids(row_ids: Sequence[str] | None) -> list[str]:
    if row_ids is None:
        return list(RESIDUAL_CLOSURE_ROW_IDS)

    unknown = [row_id for row_id in row_ids if row_id not in ROW_ALLOWED_FORMATS]
    if unknown:
        raise CaptureEvidenceError(f"template row_id is not recognized: {', '.join(unknown)}")

    seen: set[str] = set()
    ordered_rows: list[str] = []
    for row_id in row_ids:
        if row_id in seen:
            raise CaptureEvidenceError(f"template row_id repeated: {row_id}")
        seen.add(row_id)
        ordered_rows.append(row_id)
    return ordered_rows


def capture_evidence_bundle_template(row_ids: Sequence[str] | None = None) -> Mapping[str, Any]:
    """Return a non-claiming template for future residual capture submissions."""

    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_bundle",
        "bundle_id": "replace-with-retail-evidence-bundle-id",
        "protocol": 91,
        "provenance": {
            "source": "replace-with-retail-capture-source",
            "capture_type": "retail_packet_capture",
            "capture_date_utc": "replace-with-utc-capture-date",
            "retail_build": "replace-with-steam-build-or-protocol-note",
        },
        "closure_targets": [
            {
                "row_id": row_id,
                "checklist_text": ROW_CHECKLIST_TEXT[row_id],
                "status": "not_claimed",
                "artifacts": [],
                "artifact_templates": _artifact_templates(row_id),
            }
            for row_id in _template_row_ids(row_ids)
        ],
    }


def _contract_row_ids(row_ids: Sequence[str] | None, *, context: str = "row contract") -> list[str]:
    if row_ids is None:
        return list(RESIDUAL_CLOSURE_ROW_IDS)

    unknown = [row_id for row_id in row_ids if row_id not in ROW_ALLOWED_FORMATS]
    if unknown:
        raise CaptureEvidenceError(f"{context} row_id is not recognized: {', '.join(unknown)}")

    seen: set[str] = set()
    ordered_rows: list[str] = []
    for row_id in row_ids:
        if row_id in seen:
            raise CaptureEvidenceError(f"{context} row_id repeated: {row_id}")
        seen.add(row_id)
        ordered_rows.append(row_id)
    return ordered_rows


def capture_evidence_row_contracts(row_ids: Sequence[str] | None = None) -> Mapping[str, Any]:
    """Return residual capture evidence row contracts for submitters and reviewers."""

    rows = []
    for row_id in _contract_row_ids(row_ids):
        allowed_formats = sorted(ROW_ALLOWED_FORMATS[row_id])
        rows.append(
            {
                "row_id": row_id,
                "checklist_text": ROW_CHECKLIST_TEXT[row_id],
                "allowed_formats": allowed_formats,
                "artifact_types": [FORMAT_ARTIFACT_TYPES[artifact_format] for artifact_format in allowed_formats],
                "closure_target_statuses": [
                    "submitted_for_closure",
                    "supporting_evidence",
                    "not_claimed",
                ],
            }
        )

    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_row_contracts",
        "protocol": 91,
        "row_count": len(rows),
        "rows": rows,
    }


def capture_evidence_capture_plan(row_ids: Sequence[str] | None = None) -> Mapping[str, Any]:
    """Return a non-claiming row-scoped capture plan for residual evidence owners."""

    rows = []
    for row_id in _contract_row_ids(row_ids, context="capture plan"):
        allowed_formats = sorted(ROW_ALLOWED_FORMATS[row_id])
        rows.append(
            {
                "row_id": row_id,
                "checklist_text": ROW_CHECKLIST_TEXT[row_id],
                "required_evidence": ROW_REQUIRED_EVIDENCE[row_id],
                "allowed_formats": allowed_formats,
                "artifact_types": [FORMAT_ARTIFACT_TYPES[artifact_format] for artifact_format in allowed_formats],
                "recommended_artifact_prefixes": list(ALLOWED_ARTIFACT_PATH_PREFIXES),
                "reviewed_text_suffixes": sorted(TEXT_ARTIFACT_SUFFIXES),
                "retail_provenance_required_keys": sorted(RETAIL_PROVENANCE_KEYS),
                "bundle_template_command": (
                    f"python -m tools.trace.capture_evidence --print-template --template-row {row_id}"
                ),
                "row_contract_command": (
                    f"python -m tools.trace.capture_evidence --print-row-contracts --row-contract {row_id}"
                ),
                "hash_command": (
                    "python -m tools.trace.capture_evidence --hash-artifact <artifact_path> "
                    "--artifact-root <repo_root>"
                ),
                "final_review_command": (
                    "python -m tools.trace.capture_evidence <bundle.json> "
                    "--strict-final-closure --artifact-root <repo_root>"
                ),
            }
        )

    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_capture_plan",
        "protocol": 91,
        "row_count": len(rows),
        "rows": rows,
        "claims_retail_evidence": False,
    }


def _require_non_empty_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise CaptureEvidenceError(f"{context} must be a non-empty string")
    return value


def _require_sha256(value: object, context: str) -> str:
    if not isinstance(value, str) or not SHA256_HEX_RE.match(value):
        raise CaptureEvidenceError(f"{context} must be a lowercase SHA-256 hex string")
    return value


def _validate_retail_provenance(bundle: Mapping[str, Any]) -> None:
    provenance = bundle.get("provenance")
    if not isinstance(provenance, Mapping):
        raise CaptureEvidenceError("retail capture evidence bundle requires provenance metadata")
    missing = [
        key
        for key in RETAIL_PROVENANCE_KEYS
        if not isinstance(provenance.get(key), str) or not provenance.get(key)
    ]
    if missing:
        raise CaptureEvidenceError(
            f"retail capture evidence bundle provenance missing required keys: {', '.join(missing)}"
        )
    if provenance.get("capture_type") not in RETAIL_CAPTURE_TYPES:
        raise CaptureEvidenceError("retail capture evidence bundle provenance capture_type is not recognized")


def _validate_capture_diff_report(report: Mapping[str, Any], *, require_match: bool) -> Mapping[str, Any]:
    if report.get("schema_version") != 1:
        raise CaptureEvidenceError("capture diff report schema_version must be 1")
    if report.get("format") != "quake_live_capture_diff_report":
        raise CaptureEvidenceError("capture diff report format must be quake_live_capture_diff_report")
    if report.get("status") not in {"match", "missing", "mismatch"}:
        raise CaptureEvidenceError("capture diff report status is not recognized")
    if require_match and report.get("status") != "match":
        raise CaptureEvidenceError("closure capture diff reports must have match status")
    results = report.get("results")
    if not isinstance(results, list) or not results:
        raise CaptureEvidenceError("capture diff report results must be a non-empty list")
    for index, result in enumerate(results):
        if not isinstance(result, Mapping):
            raise CaptureEvidenceError(f"capture diff result {index} must be an object")
        _require_non_empty_string(result.get("fixture_id"), f"capture diff result {index} fixture_id")
        _require_non_empty_string(result.get("lane"), f"capture diff result {index} lane")
        if result.get("status") not in {"match", "missing", "mismatch"}:
            raise CaptureEvidenceError(f"capture diff result {index} status is not recognized")
        if require_match and result.get("status") != "match":
            raise CaptureEvidenceError("closure capture diff results must all match")
        _require_sha256(result.get("expected_sha256"), f"capture diff result {index} expected_sha256")
        observed_hash = result.get("observed_sha256")
        if observed_hash is not None:
            _require_sha256(observed_hash, f"capture diff result {index} observed_sha256")
    return {
        "result_count": len(results),
        "status": report["status"],
    }


def _validate_embedded_report(
    artifact: Mapping[str, Any],
    *,
    target_status: str,
    playerstate_spec: Mapping[str, Any] | None,
    entitystate_spec: Mapping[str, Any] | None,
    require_retail_provenance: bool,
) -> None:
    report = artifact.get("report")
    if report is None:
        if target_status == "submitted_for_closure":
            _require_non_empty_string(artifact.get("validated_by"), "closure artifact validated_by")
        return
    if not isinstance(report, Mapping):
        raise CaptureEvidenceError("artifact report must be an object")

    artifact_format = artifact.get("format")
    try:
        if artifact_format == "quake_live_capture_diff_report":
            _validate_capture_diff_report(report, require_match=target_status == "submitted_for_closure")
            return
        validator = FORMAT_VALIDATORS.get(artifact_format)
        if validator is None:
            raise CaptureEvidenceError(f"artifact format has no embedded report validator: {artifact_format}")
        kwargs: dict[str, Any] = {"require_retail_provenance": require_retail_provenance}
        if artifact_format == "quake_live_snapshot_field_decode":
            kwargs["playerstate_spec"] = playerstate_spec
            kwargs["entitystate_spec"] = entitystate_spec
        validator(report, **kwargs)
    except ValueError as exc:
        raise CaptureEvidenceError(f"embedded report validation failed: {exc}") from exc


def _validate_artifacts(
    target: Mapping[str, Any],
    *,
    target_status: str,
    playerstate_spec: Mapping[str, Any] | None,
    entitystate_spec: Mapping[str, Any] | None,
    require_retail_provenance: bool,
) -> int:
    row_id = target["row_id"]
    artifacts = target.get("artifacts")
    if not isinstance(artifacts, list):
        raise CaptureEvidenceError(f"{row_id} artifacts must be a list")
    if target_status == "submitted_for_closure" and not artifacts:
        raise CaptureEvidenceError(f"{row_id} closure target requires at least one artifact")

    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            raise CaptureEvidenceError(f"{row_id} artifact {index} must be an object")
        artifact_id = _require_non_empty_string(artifact.get("id"), f"{row_id} artifact {index} id")
        if artifact_id in seen:
            raise CaptureEvidenceError(f"{row_id} artifact id repeated: {artifact_id}")
        seen.add(artifact_id)

        artifact_type = artifact.get("type")
        if artifact_type not in ARTIFACT_TYPES:
            raise CaptureEvidenceError(f"{row_id} artifact {artifact_id} type is not recognized")
        artifact_format = artifact.get("format")
        if artifact_format not in ROW_ALLOWED_FORMATS[row_id]:
            raise CaptureEvidenceError(
                f"{row_id} artifact {artifact_id} format is not allowed for this closure row"
            )
        _require_non_empty_string(artifact.get("path"), f"{row_id} artifact {artifact_id} path")
        _require_sha256(artifact.get("sha256"), f"{row_id} artifact {artifact_id} sha256")
        _require_non_empty_string(artifact.get("description"), f"{row_id} artifact {artifact_id} description")
        _validate_embedded_report(
            artifact,
            target_status=target_status,
            playerstate_spec=playerstate_spec,
            entitystate_spec=entitystate_spec,
            require_retail_provenance=require_retail_provenance,
        )
    return len(artifacts)


def validate_capture_evidence_bundle_dict(
    bundle: Mapping[str, Any],
    *,
    playerstate_spec: Mapping[str, Any] | None = None,
    entitystate_spec: Mapping[str, Any] | None = None,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a bundle that maps future capture evidence to residual closure rows."""

    if bundle.get("schema_version") != 1:
        raise CaptureEvidenceError("capture evidence bundle schema_version must be 1")
    if bundle.get("format") != "quake_live_capture_evidence_bundle":
        raise CaptureEvidenceError("capture evidence bundle format must be quake_live_capture_evidence_bundle")

    bundle_id = _require_non_empty_string(bundle.get("bundle_id"), "capture evidence bundle_id")
    protocol = bundle.get("protocol")
    if protocol != 91:
        raise CaptureEvidenceError("capture evidence bundle protocol must be 91")
    if require_retail_provenance:
        _validate_retail_provenance(bundle)

    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    seen_rows: set[str] = set()
    artifact_count = 0
    submitted_count = 0
    for index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {index} must be an object")
        row_id = target.get("row_id")
        if row_id not in ROW_ALLOWED_FORMATS:
            raise CaptureEvidenceError(f"closure target {index} row_id is not recognized")
        if row_id in seen_rows:
            raise CaptureEvidenceError(f"closure target row_id repeated: {row_id}")
        seen_rows.add(row_id)
        target_status = target.get("status")
        if target_status not in TARGET_STATUSES:
            raise CaptureEvidenceError(f"{row_id} status is not recognized")
        if require_retail_provenance and target_status == "not_claimed":
            raise CaptureEvidenceError("retail closure bundles cannot include not_claimed targets")
        if target_status == "submitted_for_closure":
            submitted_count += 1
        artifact_count += _validate_artifacts(
            target,
            target_status=target_status,
            playerstate_spec=playerstate_spec,
            entitystate_spec=entitystate_spec,
            require_retail_provenance=require_retail_provenance,
        )

    if require_retail_provenance and submitted_count == 0:
        raise CaptureEvidenceError("retail closure bundle must submit at least one closure target")

    return {
        "bundle_id": bundle_id,
        "protocol": protocol,
        "closure_target_count": len(targets),
        "submitted_closure_target_count": submitted_count,
        "artifact_count": artifact_count,
    }


def _required_closure_row_ids(row_ids: Sequence[str]) -> list[str]:
    if not row_ids:
        raise CaptureEvidenceError("at least one required closure row_id is needed")

    unknown = [row_id for row_id in row_ids if row_id not in ROW_ALLOWED_FORMATS]
    if unknown:
        raise CaptureEvidenceError(f"required closure row_id is not recognized: {', '.join(unknown)}")

    seen: set[str] = set()
    ordered_rows: list[str] = []
    for row_id in row_ids:
        if row_id in seen:
            raise CaptureEvidenceError(f"required closure row_id repeated: {row_id}")
        seen.add(row_id)
        ordered_rows.append(row_id)
    return ordered_rows


def require_capture_evidence_closure_rows(
    bundle: Mapping[str, Any],
    row_ids: Sequence[str],
) -> Mapping[str, Any]:
    """Require specific residual rows to be submitted for closure in a bundle."""

    required_rows = _required_closure_row_ids(row_ids)
    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    submitted_rows: set[str] = set()
    for index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {index} must be an object")
        row_id = target.get("row_id")
        if row_id in ROW_ALLOWED_FORMATS and target.get("status") == "submitted_for_closure":
            submitted_rows.add(row_id)

    missing_rows = [row_id for row_id in required_rows if row_id not in submitted_rows]
    if missing_rows:
        raise CaptureEvidenceError(
            f"required closure rows are not submitted for closure: {', '.join(missing_rows)}"
        )

    return {
        "required_closure_row_count": len(required_rows),
        "required_closure_rows": required_rows,
    }


def require_all_capture_evidence_closure_rows(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    """Require every residual capture evidence row to be submitted for closure."""

    summary = dict(require_capture_evidence_closure_rows(bundle, RESIDUAL_CLOSURE_ROW_IDS))
    summary["all_closure_rows_required"] = True
    return summary


def _closure_status_for_target(target: Mapping[str, Any] | None) -> tuple[str, int, str | None]:
    if target is None:
        return "missing", 0, "closure target is missing from bundle"

    status = str(target.get("status"))
    artifacts = target.get("artifacts")
    artifact_count = len(artifacts) if isinstance(artifacts, list) else 0
    if status == "submitted_for_closure" and artifact_count > 0:
        return status, artifact_count, None
    if status == "submitted_for_closure":
        return status, artifact_count, "submitted closure target has no artifacts"
    if status == "supporting_evidence":
        return status, artifact_count, "target is supporting evidence only"
    if status == "not_claimed":
        return status, artifact_count, "target is not claimed for closure"
    return status, artifact_count, "target status is not recognized"


def summarize_capture_evidence_closure_status(
    bundle: Mapping[str, Any],
    *,
    required_rows: Sequence[str] | None = None,
) -> Mapping[str, Any]:
    """Summarize per-row closure status for a validated capture evidence bundle."""

    required_row_ids = _required_closure_row_ids(required_rows) if required_rows else []
    targets = bundle.get("closure_targets")
    if not isinstance(targets, list):
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a list")

    targets_by_row: dict[str, Mapping[str, Any]] = {}
    for index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {index} must be an object")
        row_id = target.get("row_id")
        if row_id not in ROW_ALLOWED_FORMATS:
            raise CaptureEvidenceError(f"closure target {index} row_id is not recognized")
        if row_id in targets_by_row:
            raise CaptureEvidenceError(f"closure target row_id repeated: {row_id}")
        targets_by_row[str(row_id)] = target

    rows: list[Mapping[str, Any]] = []
    status_counts = {
        "submitted_for_closure": 0,
        "supporting_evidence": 0,
        "not_claimed": 0,
        "missing": 0,
    }
    artifact_count = 0
    required_ready_count = 0
    for row_id in RESIDUAL_CLOSURE_ROW_IDS:
        status, row_artifact_count, blocker = _closure_status_for_target(targets_by_row.get(row_id))
        if status in status_counts:
            status_counts[status] += 1
        artifact_count += row_artifact_count
        closure_ready = status == "submitted_for_closure" and blocker is None
        required = row_id in required_row_ids
        if required and closure_ready:
            required_ready_count += 1
        rows.append(
            {
                "row_id": row_id,
                "checklist_text": ROW_CHECKLIST_TEXT[row_id],
                "status": status,
                "artifact_count": row_artifact_count,
                "required": required,
                "closure_ready": closure_ready,
                "closure_blocker": blocker,
            }
        )

    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_closure_status",
        "bundle_id": _require_non_empty_string(bundle.get("bundle_id"), "capture evidence bundle_id"),
        "protocol": bundle.get("protocol"),
        "row_count": len(rows),
        "artifact_count": artifact_count,
        "submitted_closure_target_count": status_counts["submitted_for_closure"],
        "supporting_evidence_target_count": status_counts["supporting_evidence"],
        "not_claimed_target_count": status_counts["not_claimed"],
        "missing_target_count": status_counts["missing"],
        "required_closure_row_count": len(required_row_ids),
        "required_closure_rows": required_row_ids,
        "required_closure_rows_ready_count": required_ready_count,
        "rows": rows,
    }


def _closure_blocker_next_action(row: Mapping[str, Any]) -> str:
    status = row["status"]
    if status == "missing":
        return "add a closure target with submitted_for_closure status and at least one retail artifact"
    if status == "not_claimed":
        return "replace the non-claiming template target with submitted retail evidence"
    if status == "supporting_evidence":
        return "promote the target to submitted_for_closure after the artifacts are closure-ready"
    if status == "submitted_for_closure":
        return "attach at least one artifact accepted by this residual row contract"
    return "correct the closure target status"


def summarize_capture_evidence_closure_blockers(
    bundle: Mapping[str, Any],
    *,
    required_rows: Sequence[str] | None = None,
) -> Mapping[str, Any]:
    """Summarize blocked residual rows for a validated capture evidence bundle."""

    required_row_ids = _required_closure_row_ids(required_rows) if required_rows else list(RESIDUAL_CLOSURE_ROW_IDS)
    status_summary = summarize_capture_evidence_closure_status(bundle, required_rows=required_row_ids)

    blocked_rows = []
    for row in status_summary["rows"]:
        row_id = str(row["row_id"])
        if row_id not in required_row_ids or row["closure_ready"]:
            continue
        allowed_formats = sorted(ROW_ALLOWED_FORMATS[row_id])
        blocked_rows.append(
            {
                "row_id": row_id,
                "checklist_text": row["checklist_text"],
                "status": row["status"],
                "artifact_count": row["artifact_count"],
                "closure_blocker": row["closure_blocker"],
                "next_action": _closure_blocker_next_action(row),
                "allowed_formats": allowed_formats,
                "artifact_types": [FORMAT_ARTIFACT_TYPES[artifact_format] for artifact_format in allowed_formats],
            }
        )

    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_closure_blockers",
        "bundle_id": status_summary["bundle_id"],
        "protocol": status_summary["protocol"],
        "required_closure_row_count": len(required_row_ids),
        "blocked_closure_row_count": len(blocked_rows),
        "ready_required_closure_row_count": status_summary["required_closure_rows_ready_count"],
        "required_closure_rows": required_row_ids,
        "blocked_rows": blocked_rows,
    }


def require_capture_evidence_no_closure_blockers(
    bundle: Mapping[str, Any],
    row_ids: Sequence[str] | None = None,
) -> Mapping[str, Any]:
    """Require selected residual rows to have no closure blockers."""

    blocker_summary = summarize_capture_evidence_closure_blockers(bundle, required_rows=row_ids)
    blocked_rows = [row["row_id"] for row in blocker_summary["blocked_rows"]]
    if blocked_rows:
        raise CaptureEvidenceError(f"closure blockers remain: {', '.join(blocked_rows)}")

    return {
        "closure_blocker_gate_passed": True,
        "blocked_closure_row_count": 0,
        "ready_required_closure_row_count": blocker_summary["ready_required_closure_row_count"],
        "required_closure_row_count": blocker_summary["required_closure_row_count"],
        "required_closure_rows": blocker_summary["required_closure_rows"],
    }


def _artifact_file_path(artifact_root: Path, artifact: Mapping[str, Any], context: str) -> Path:
    artifact_path = Path(_require_non_empty_string(artifact.get("path"), f"{context} path"))
    if artifact_path.is_absolute():
        raise CaptureEvidenceError(f"{context} path must be relative to the artifact root")

    resolved_root = artifact_root.resolve()
    resolved_path = (resolved_root / artifact_path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise CaptureEvidenceError(f"{context} path escapes the artifact root") from exc
    return resolved_path


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_input_artifact_path(artifact_root: Path, artifact_path: Path, context: str) -> tuple[Path, str]:
    resolved_root = artifact_root.resolve()
    if artifact_path.is_absolute():
        resolved_path = artifact_path.resolve()
    else:
        resolved_path = (resolved_root / artifact_path).resolve()
    try:
        relative_path = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise CaptureEvidenceError(f"{context} path escapes the artifact root") from exc
    if not resolved_path.is_file():
        raise CaptureEvidenceError(f"{context} file does not exist: {resolved_path}")
    return resolved_path, relative_path.as_posix()


def hash_capture_evidence_artifacts(
    artifact_paths: Sequence[Path],
    *,
    artifact_root: Path,
) -> Mapping[str, Any]:
    """Hash artifact files for future capture evidence bundle entries."""

    if not artifact_paths:
        raise CaptureEvidenceError("at least one artifact path is required")

    artifact_summaries: list[Mapping[str, int | str]] = []
    for index, artifact_path in enumerate(artifact_paths):
        resolved_path, relative_path = _hash_input_artifact_path(
            artifact_root,
            artifact_path,
            f"artifact hash input {index}",
        )
        artifact_summaries.append(
            {
                "path": relative_path,
                "size": resolved_path.stat().st_size,
                "sha256": _file_sha256(resolved_path),
            }
        )

    return {
        "artifact_root": str(artifact_root.resolve()),
        "artifact_count": len(artifact_summaries),
        "artifacts": artifact_summaries,
    }


def verify_capture_evidence_artifact_files(
    bundle: Mapping[str, Any],
    *,
    artifact_root: Path,
) -> Mapping[str, int | str]:
    """Verify bundle artifact paths exist under artifact_root and match SHA-256."""

    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    checked_count = 0
    for target_index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {target_index} must be an object")
        row_id = _require_non_empty_string(target.get("row_id"), f"closure target {target_index} row_id")
        artifacts = target.get("artifacts")
        if not isinstance(artifacts, list):
            raise CaptureEvidenceError(f"{row_id} artifacts must be a list")

        for artifact_index, artifact in enumerate(artifacts):
            if not isinstance(artifact, Mapping):
                raise CaptureEvidenceError(f"{row_id} artifact {artifact_index} must be an object")
            artifact_id = _require_non_empty_string(
                artifact.get("id"),
                f"{row_id} artifact {artifact_index} id",
            )
            expected_sha256 = _require_sha256(
                artifact.get("sha256"),
                f"{row_id} artifact {artifact_id} sha256",
            )
            artifact_path = _artifact_file_path(artifact_root, artifact, f"{row_id} artifact {artifact_id}")
            if not artifact_path.is_file():
                raise CaptureEvidenceError(f"{row_id} artifact {artifact_id} file does not exist: {artifact_path}")

            observed_sha256 = _file_sha256(artifact_path)
            if observed_sha256 != expected_sha256:
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} sha256 mismatch: "
                    f"expected {expected_sha256}, observed {observed_sha256}"
                )
            checked_count += 1

    return {
        "artifact_root": str(artifact_root.resolve()),
        "verified_artifact_file_count": checked_count,
    }


def verify_capture_evidence_artifact_text_policy(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    """Verify artifact paths reference reviewed text fixtures, not raw binary captures."""

    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    checked_count = 0
    for target_index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {target_index} must be an object")
        row_id = _require_non_empty_string(target.get("row_id"), f"closure target {target_index} row_id")
        artifacts = target.get("artifacts")
        if not isinstance(artifacts, list):
            raise CaptureEvidenceError(f"{row_id} artifacts must be a list")

        for artifact_index, artifact in enumerate(artifacts):
            if not isinstance(artifact, Mapping):
                raise CaptureEvidenceError(f"{row_id} artifact {artifact_index} must be an object")
            artifact_id = _require_non_empty_string(
                artifact.get("id"),
                f"{row_id} artifact {artifact_index} id",
            )
            artifact_path = Path(_require_non_empty_string(artifact.get("path"), f"{row_id} artifact {artifact_id} path"))
            suffix = artifact_path.suffix.lower()
            if suffix in RAW_BINARY_ARTIFACT_SUFFIXES:
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} raw binary artifact path is not allowed: {artifact_path}"
                )
            if suffix not in TEXT_ARTIFACT_SUFFIXES:
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} path must use a reviewed text suffix: {artifact_path}"
                )
            checked_count += 1

    return {
        "artifact_text_policy_checked_count": checked_count,
        "artifact_text_policy_allowed_suffixes": sorted(TEXT_ARTIFACT_SUFFIXES),
        "artifact_text_policy_rejected_suffixes": sorted(RAW_BINARY_ARTIFACT_SUFFIXES),
    }


def _artifact_posix_path(artifact: Mapping[str, Any], context: str) -> str:
    artifact_path = Path(_require_non_empty_string(artifact.get("path"), f"{context} path"))
    if artifact_path.is_absolute():
        raise CaptureEvidenceError(f"{context} path must be repository-relative")
    normalized = artifact_path.as_posix()
    if normalized.startswith("../") or "/../" in normalized:
        raise CaptureEvidenceError(f"{context} path must not contain parent directory traversal")
    return normalized


def verify_capture_evidence_artifact_path_policy(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    """Verify artifact paths stay in reviewed evidence directories."""

    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    checked_count = 0
    for target_index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {target_index} must be an object")
        row_id = _require_non_empty_string(target.get("row_id"), f"closure target {target_index} row_id")
        artifacts = target.get("artifacts")
        if not isinstance(artifacts, list):
            raise CaptureEvidenceError(f"{row_id} artifacts must be a list")

        for artifact_index, artifact in enumerate(artifacts):
            if not isinstance(artifact, Mapping):
                raise CaptureEvidenceError(f"{row_id} artifact {artifact_index} must be an object")
            artifact_id = _require_non_empty_string(
                artifact.get("id"),
                f"{row_id} artifact {artifact_index} id",
            )
            normalized_path = _artifact_posix_path(artifact, f"{row_id} artifact {artifact_id}")
            for rejected_prefix in REJECTED_ARTIFACT_PATH_PREFIXES:
                if normalized_path.startswith(rejected_prefix):
                    raise CaptureEvidenceError(
                        f"{row_id} artifact {artifact_id} path uses rejected evidence prefix: {normalized_path}"
                    )
            if not any(normalized_path.startswith(prefix) for prefix in ALLOWED_ARTIFACT_PATH_PREFIXES):
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} path must live under a reviewed evidence directory: "
                    f"{normalized_path}"
                )
            checked_count += 1

    return {
        "artifact_path_policy_checked_count": checked_count,
        "artifact_path_policy_allowed_prefixes": list(ALLOWED_ARTIFACT_PATH_PREFIXES),
        "artifact_path_policy_rejected_prefixes": list(REJECTED_ARTIFACT_PATH_PREFIXES),
    }


def verify_capture_evidence_artifact_uniqueness_policy(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    """Verify artifact IDs and paths are unique across a capture evidence bundle."""

    targets = bundle.get("closure_targets")
    if not isinstance(targets, list) or not targets:
        raise CaptureEvidenceError("capture evidence bundle closure_targets must be a non-empty list")

    seen_ids: dict[str, str] = {}
    seen_paths: dict[str, str] = {}
    checked_count = 0
    for target_index, target in enumerate(targets):
        if not isinstance(target, Mapping):
            raise CaptureEvidenceError(f"closure target {target_index} must be an object")
        row_id = _require_non_empty_string(target.get("row_id"), f"closure target {target_index} row_id")
        artifacts = target.get("artifacts")
        if not isinstance(artifacts, list):
            raise CaptureEvidenceError(f"{row_id} artifacts must be a list")

        for artifact_index, artifact in enumerate(artifacts):
            if not isinstance(artifact, Mapping):
                raise CaptureEvidenceError(f"{row_id} artifact {artifact_index} must be an object")
            artifact_id = _require_non_empty_string(
                artifact.get("id"),
                f"{row_id} artifact {artifact_index} id",
            )
            if artifact_id in seen_ids:
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} id duplicates artifact in {seen_ids[artifact_id]}"
                )
            seen_ids[artifact_id] = row_id

            normalized_path = _artifact_posix_path(artifact, f"{row_id} artifact {artifact_id}")
            if normalized_path in seen_paths:
                raise CaptureEvidenceError(
                    f"{row_id} artifact {artifact_id} path duplicates artifact in {seen_paths[normalized_path]}: "
                    f"{normalized_path}"
                )
            seen_paths[normalized_path] = row_id
            checked_count += 1

    return {
        "artifact_uniqueness_policy_checked_count": checked_count,
        "unique_artifact_id_count": len(seen_ids),
        "unique_artifact_path_count": len(seen_paths),
    }


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, Mapping):
        raise CaptureEvidenceError(f"{path} must contain a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, nargs="?", help="Path to a quake_live_capture_evidence_bundle JSON file")
    parser.add_argument(
        "--playerstate-spec",
        type=Path,
        help="Optional playerStateFields source-of-truth JSON used by embedded snapshot decode reports",
    )
    parser.add_argument(
        "--entitystate-spec",
        type=Path,
        help="Optional entityStateFields source-of-truth JSON used by embedded snapshot decode reports",
    )
    parser.add_argument(
        "--require-retail-provenance",
        action="store_true",
        help="Require retail provenance and closure-ready submitted targets",
    )
    parser.add_argument(
        "--require-closure-row",
        action="append",
        help="Require a residual row_id to be present with submitted_for_closure status; may be repeated",
    )
    parser.add_argument(
        "--require-all-closure-rows",
        action="store_true",
        help="Require every residual capture evidence row to be present with submitted_for_closure status",
    )
    parser.add_argument(
        "--strict-final-closure",
        action="store_true",
        help=(
            "Require retail provenance, every residual row submitted for closure, "
            "and verified artifact files"
        ),
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print a non-claiming bundle template instead of validating a bundle",
    )
    parser.add_argument(
        "--template-row",
        action="append",
        help="Limit --print-template output to a residual row_id; may be provided more than once",
    )
    parser.add_argument(
        "--print-row-contracts",
        action="store_true",
        help="Print residual row IDs and allowed artifact formats instead of validating a bundle",
    )
    parser.add_argument(
        "--row-contract",
        action="append",
        help="Limit --print-row-contracts output to a residual row_id; may be provided more than once",
    )
    parser.add_argument(
        "--print-capture-plan",
        action="store_true",
        help="Print non-claiming residual capture requirements instead of validating a bundle",
    )
    parser.add_argument(
        "--capture-plan-row",
        action="append",
        help="Limit --print-capture-plan output to a residual row_id; may be provided more than once",
    )
    parser.add_argument(
        "--hash-artifact",
        type=Path,
        action="append",
        help="Hash an artifact file under --artifact-root for future bundle entries; may be repeated",
    )
    parser.add_argument(
        "--verify-artifact-files",
        action="store_true",
        help="Verify artifact paths exist under --artifact-root and match declared SHA-256 hashes",
    )
    parser.add_argument(
        "--enforce-artifact-text-policy",
        action="store_true",
        help="Require artifact paths to use reviewed text suffixes and reject raw binary capture suffixes",
    )
    parser.add_argument(
        "--enforce-artifact-path-policy",
        action="store_true",
        help="Require artifact paths to live under reviewed evidence directories",
    )
    parser.add_argument(
        "--enforce-artifact-uniqueness-policy",
        action="store_true",
        help="Require artifact IDs and paths to be unique across the bundle",
    )
    parser.add_argument(
        "--print-closure-status",
        action="store_true",
        help="Print a per-row closure status report for a validated bundle",
    )
    parser.add_argument(
        "--print-closure-blockers",
        action="store_true",
        help="Print residual rows that are not ready for closure in a validated bundle",
    )
    parser.add_argument(
        "--fail-on-closure-blockers",
        action="store_true",
        help="Return non-zero when required residual closure rows have blockers",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path.cwd(),
        help="Root used by --verify-artifact-files for repo-relative artifact paths",
    )
    args = parser.parse_args(argv)

    try:
        utility_modes = (
            int(args.print_template)
            + int(args.print_row_contracts)
            + int(args.print_capture_plan)
            + int(bool(args.hash_artifact))
        )
        if utility_modes > 1:
            raise CaptureEvidenceError(
                "choose only one utility mode: "
                "--print-template, --print-row-contracts, --print-capture-plan, or --hash-artifact"
            )
        if args.print_closure_status and args.print_closure_blockers:
            raise CaptureEvidenceError("choose only one review output: --print-closure-status or --print-closure-blockers")
        if (args.print_closure_status or args.print_closure_blockers) and utility_modes:
            raise CaptureEvidenceError("--print-closure-status and --print-closure-blockers require bundle validation mode")
        if args.fail_on_closure_blockers and utility_modes:
            raise CaptureEvidenceError("--fail-on-closure-blockers requires bundle validation mode")
        if args.strict_final_closure and utility_modes:
            raise CaptureEvidenceError("--strict-final-closure requires bundle validation mode")
        if args.require_all_closure_rows and args.require_closure_row:
            raise CaptureEvidenceError(
                "--require-all-closure-rows cannot be combined with --require-closure-row"
            )
        if args.strict_final_closure and args.require_closure_row:
            raise CaptureEvidenceError(
                "--strict-final-closure cannot be combined with --require-closure-row"
            )
        if args.print_template:
            print(json.dumps(capture_evidence_bundle_template(args.template_row), indent=2, sort_keys=True))
            return 0
        if args.print_row_contracts:
            print(json.dumps(capture_evidence_row_contracts(args.row_contract), indent=2, sort_keys=True))
            return 0
        if args.print_capture_plan:
            print(json.dumps(capture_evidence_capture_plan(args.capture_plan_row), indent=2, sort_keys=True))
            return 0
        if args.hash_artifact:
            print(
                json.dumps(
                    hash_capture_evidence_artifacts(
                        args.hash_artifact,
                        artifact_root=args.artifact_root,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if args.bundle is None:
            parser.error(
                "bundle is required unless --print-template, --print-row-contracts, "
                "--print-capture-plan, or --hash-artifact is used"
            )
        bundle = _load_json(args.bundle)
        summary = dict(
            validate_capture_evidence_bundle_dict(
                bundle,
                playerstate_spec=_load_json(args.playerstate_spec) if args.playerstate_spec else None,
                entitystate_spec=_load_json(args.entitystate_spec) if args.entitystate_spec else None,
                require_retail_provenance=args.require_retail_provenance or args.strict_final_closure,
            )
        )
        if args.require_closure_row:
            summary.update(require_capture_evidence_closure_rows(bundle, args.require_closure_row))
        if args.require_all_closure_rows or args.strict_final_closure:
            summary.update(require_all_capture_evidence_closure_rows(bundle))
        if args.verify_artifact_files or args.strict_final_closure:
            summary.update(
                verify_capture_evidence_artifact_files(
                    bundle,
                    artifact_root=args.artifact_root,
                )
            )
        if args.enforce_artifact_text_policy or args.strict_final_closure:
            summary.update(verify_capture_evidence_artifact_text_policy(bundle))
        if args.enforce_artifact_path_policy or args.strict_final_closure:
            summary.update(verify_capture_evidence_artifact_path_policy(bundle))
        if args.enforce_artifact_uniqueness_policy or args.strict_final_closure:
            summary.update(verify_capture_evidence_artifact_uniqueness_policy(bundle))
        if args.strict_final_closure:
            summary["strict_final_closure"] = True
        if args.print_closure_status:
            status_summary = dict(
                summarize_capture_evidence_closure_status(
                    bundle,
                    required_rows=(
                        RESIDUAL_CLOSURE_ROW_IDS
                        if args.require_all_closure_rows or args.strict_final_closure
                        else args.require_closure_row
                    ),
                )
            )
            status_summary["validation_summary"] = summary
            print(json.dumps(status_summary, indent=2, sort_keys=True))
            return 0
        if args.print_closure_blockers:
            blocker_summary = dict(
                summarize_capture_evidence_closure_blockers(
                    bundle,
                    required_rows=(
                        RESIDUAL_CLOSURE_ROW_IDS
                        if args.require_all_closure_rows or args.strict_final_closure or not args.require_closure_row
                        else args.require_closure_row
                    ),
                )
            )
            blocker_summary["validation_summary"] = summary
            print(json.dumps(blocker_summary, indent=2, sort_keys=True))
            return 1 if args.fail_on_closure_blockers and blocker_summary["blocked_closure_row_count"] else 0
        if args.fail_on_closure_blockers:
            summary.update(
                require_capture_evidence_no_closure_blockers(
                    bundle,
                    RESIDUAL_CLOSURE_ROW_IDS if not args.require_closure_row else args.require_closure_row,
                )
            )
    except (CaptureEvidenceError, OSError, json.JSONDecodeError) as exc:
        print(f"capture evidence validation failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
