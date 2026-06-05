"""Trace capture and replay harnesses for deterministic regression testing."""

from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_MODULES = {
    "CaptureDiffError": ".capture_diff",
    "CaptureEvidenceError": ".capture_evidence",
    "capture_evidence_capture_plan": ".capture_evidence",
    "capture_evidence_row_contracts": ".capture_evidence",
    "DemoMessageRecord": ".demo_transcript",
    "DemoTranscript": ".demo_transcript",
    "DemoTranscriptError": ".demo_transcript",
    "FragmentTimingError": ".fragment_timing",
    "InvalidLcProbeError": ".invalid_lc_probe",
    "PacketExpectation": ".capture_diff",
    "SnapshotDecodeError": ".snapshot_decode",
    "TraceLauncher": ".launcher",
    "TraceLauncherConfig": ".launcher",
    "TraceLaunchResult": ".launcher",
    "TraceReplayer": ".replay",
    "TraceReplayResult": ".replay",
    "TraceVMDriver": ".replay",
    "capture_evidence_bundle_template": ".capture_evidence",
    "diff_packet_capture": ".capture_diff",
    "hash_capture_evidence_artifacts": ".capture_evidence",
    "packet_expectations_from_huffman_spec": ".capture_diff",
    "packet_expectations_from_xor_spec": ".capture_diff",
    "parse_demo_bytes": ".demo_transcript",
    "parse_demo_file": ".demo_transcript",
    "require_capture_evidence_closure_rows": ".capture_evidence",
    "require_capture_evidence_no_closure_blockers": ".capture_evidence",
    "require_all_capture_evidence_closure_rows": ".capture_evidence",
    "summarize_capture_evidence_closure_blockers": ".capture_evidence",
    "summarize_capture_evidence_closure_status": ".capture_evidence",
    "validate_capture_evidence_bundle_dict": ".capture_evidence",
    "validate_demo_transcript_dict": ".demo_transcript",
    "verify_capture_evidence_artifact_path_policy": ".capture_evidence",
    "verify_capture_evidence_artifact_text_policy": ".capture_evidence",
    "verify_capture_evidence_artifact_uniqueness_policy": ".capture_evidence",
    "validate_fragment_queue_timing_dict": ".fragment_timing",
    "validate_invalid_lc_probe_dict": ".invalid_lc_probe",
    "validate_packet_capture_dict": ".capture_diff",
    "validate_snapshot_field_decode_dict": ".snapshot_decode",
    "verify_capture_evidence_artifact_files": ".capture_evidence",
}


__all__ = sorted(_EXPORT_MODULES)


def __getattr__(name: str) -> Any:
    if name not in _EXPORT_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_EXPORT_MODULES[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
