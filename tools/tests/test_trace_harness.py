"""Tests for the trace capture and replay harness."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest

from tools.trace import (
    CaptureDiffError,
    CaptureEvidenceError,
    DemoTranscriptError,
    FragmentTimingError,
    InvalidLcProbeError,
    SnapshotDecodeError,
    TraceLaunchResult,
    TraceLauncher,
    TraceLauncherConfig,
    TraceReplayer,
    TraceVMDriver,
    capture_evidence_capture_plan,
    capture_evidence_bundle_template,
    capture_evidence_row_contracts,
    diff_packet_capture,
    hash_capture_evidence_artifacts,
    packet_expectations_from_huffman_spec,
    packet_expectations_from_xor_spec,
    parse_demo_bytes,
    require_all_capture_evidence_closure_rows,
    require_capture_evidence_closure_rows,
    require_capture_evidence_no_closure_blockers,
    summarize_capture_evidence_closure_blockers,
    summarize_capture_evidence_closure_status,
    validate_packet_capture_dict,
    validate_demo_transcript_dict,
    validate_capture_evidence_bundle_dict,
    validate_fragment_queue_timing_dict,
    validate_invalid_lc_probe_dict,
    validate_snapshot_field_decode_dict,
    verify_capture_evidence_artifact_path_policy,
    verify_capture_evidence_artifact_text_policy,
    verify_capture_evidence_artifact_uniqueness_policy,
    verify_capture_evidence_artifact_files,
)


@pytest.fixture()
def trace_fixture(tmp_path_factory: pytest.TempPathFactory) -> TraceLaunchResult:
    output_dir = tmp_path_factory.mktemp("trace")
    producer = Path(__file__).parent / "match_sim" / "mock_trace_producer.py"
    config = TraceLauncherConfig(
        command=[sys.executable, str(producer)],
        output_dir=output_dir,
        match_duration=0.2,
    )
    launcher = TraceLauncher(config)
    return launcher.launch()


def test_launcher_captures_expected_streams(trace_fixture: TraceLaunchResult) -> None:
    result = trace_fixture

    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert manifest["counts"]["SYS"] == 2
    assert manifest["counts"]["RNG"] == 1
    assert manifest["counts"]["ENT"] == 2
    assert manifest["metadata"]["map"] == "qztourney7"

    syscalls = (result.output_dir / "syscalls.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(syscalls) == 2
    assert "trap_Print" in syscalls[0]


def test_replay_confirms_determinism(trace_fixture: TraceLaunchResult) -> None:
    class RecordingDriver(TraceVMDriver):
        def __init__(self) -> None:
            self.syscalls: list[Mapping[str, Any]] = []
            self.rng: list[Mapping[str, Any]] = []
            self.entities: list[Mapping[str, Any]] = []

        def apply_syscall(self, event: Mapping[str, Any]) -> None:
            self.syscalls.append(event)

        def apply_rng_seed(self, event: Mapping[str, Any]) -> None:
            self.rng.append(event)

        def apply_entity_state(self, event: Mapping[str, Any]) -> None:
            self.entities.append(event)

    driver = RecordingDriver()
    replayer = TraceReplayer(trace_fixture.output_dir, driver)
    replay_result = replayer.replay()

    assert replay_result.digests == json.loads(
        trace_fixture.manifest_path.read_text(encoding="utf-8")
    )["digests"]

    assert len(driver.syscalls) == 2
    assert driver.syscalls[0]["name"] == "trap_Print"
    assert len(driver.rng) == 1
    assert driver.rng[0]["seed"] == 123456
    assert len(driver.entities) == 2
    assert driver.entities[-1]["entities"][0]["health"] == 100


def _demo_record(sequence: int, payload: bytes) -> bytes:
    return (
        sequence.to_bytes(4, "little", signed=True)
        + len(payload).to_bytes(4, "little", signed=True)
        + payload
    )


def _demo_terminator() -> bytes:
    return (-1).to_bytes(4, "little", signed=True) * 2


def test_demo_transcript_parses_quake_live_demo_envelope() -> None:
    payload_a = b"\x03snapshot"
    payload_b = b"\x07"
    demo = _demo_record(41, payload_a) + _demo_record(42, payload_b) + _demo_terminator()

    transcript = parse_demo_bytes(demo)
    data = transcript.to_dict({"source": "unit-test"})

    assert data["format"] == "quake_live_demo_message_transcript"
    assert data["protocol"] == 91
    assert data["message_count"] == 2
    assert data["terminator_offset"] == len(_demo_record(41, payload_a) + _demo_record(42, payload_b))
    assert data["provenance"] == {"source": "unit-test"}
    assert data["messages"][0]["sequence"] == 41
    assert data["messages"][0]["length"] == len(payload_a)
    assert data["messages"][0]["payload_hex"] == "03 73 6e 61 70 73 68 6f 74"
    assert data["messages"][0]["first_byte"] == 3
    assert data["messages"][1]["sequence"] == 42
    assert data["messages"][1]["first_byte"] == 7
    assert validate_demo_transcript_dict(data)["message_count"] == 2


def test_demo_transcript_validator_requires_retail_provenance_for_closure() -> None:
    demo = _demo_record(41, b"\x03snapshot") + _demo_terminator()
    transcript = parse_demo_bytes(demo)
    valid_retail = transcript.to_dict(
        {
            "source": "retail-qzdm6",
            "capture_type": "protocol91_demo_transcript",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "Steam protocol 91",
        }
    )

    summary = validate_demo_transcript_dict(valid_retail, require_retail_provenance=True)

    assert summary["protocol"] == 91
    assert summary["message_count"] == 1

    missing_provenance = transcript.to_dict()
    with pytest.raises(DemoTranscriptError, match="requires provenance metadata"):
        validate_demo_transcript_dict(missing_provenance, require_retail_provenance=True)

    bad_type = transcript.to_dict(
        {
            "source": "unit-test",
            "capture_type": "local_generated_demo",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "not retail",
        }
    )
    with pytest.raises(DemoTranscriptError, match="capture_type is not recognized"):
        validate_demo_transcript_dict(bad_type, require_retail_provenance=True)


def test_demo_transcript_validator_rejects_corrupt_hashes_and_offsets() -> None:
    demo = _demo_record(41, b"\x03snapshot") + _demo_terminator()
    transcript = parse_demo_bytes(demo)

    corrupt_hash = transcript.to_dict()
    corrupt_hash["messages"][0]["payload_sha256"] = "0" * 64
    with pytest.raises(DemoTranscriptError, match="payload_sha256 mismatch"):
        validate_demo_transcript_dict(corrupt_hash)

    corrupt_offset = transcript.to_dict()
    corrupt_offset["messages"][0]["offset"] = 4
    with pytest.raises(DemoTranscriptError, match="offset mismatch"):
        validate_demo_transcript_dict(corrupt_offset)


def test_packet_capture_diff_matches_xor_and_huffman_fixture_bytes() -> None:
    xor_spec = {
        "golden_vectors": [
            {
                "id": "client_to_server_sideband_move",
                "encoded_datagram_hex": "10 00 00 00 96 27 04 03",
            }
        ]
    }
    huffman_spec = {
        "fixtures": [
            {
                "id": "compressed_connect_profile91_numeric_challenge",
                "encoded_datagram_hex": "ff ff ff ff 63 6f 6e 6e",
            }
        ]
    }
    expectations = (
        *packet_expectations_from_xor_spec(xor_spec),
        *packet_expectations_from_huffman_spec(huffman_spec),
    )
    capture = {
        "schema_version": 1,
        "format": "quake_live_packet_byte_capture",
        "provenance": {
            "source": "retail-qzdm6",
            "capture_type": "retail_packet_capture",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "Steam protocol 91",
        },
        "packets": [
            {
                "id": "client_to_server_sideband_move",
                "bytes_hex": "10 00 00 00 96 27 04 03",
            },
            {
                "id": "compressed_connect_profile91_numeric_challenge",
                "bytes_hex": "ff ff ff ff 63 6f 6e 6e",
            },
        ],
    }

    report = diff_packet_capture(capture, expectations, require_retail_provenance=True)

    assert report["format"] == "quake_live_capture_diff_report"
    assert report["status"] == "match"
    assert report["packet_count"] == 2
    assert [result["status"] for result in report["results"]] == ["match", "match"]
    assert report["results"][0]["lane"] == "xor_golden_datagram"
    assert report["results"][1]["lane"] == "adaptive_huffman_datagram"


def test_packet_capture_diff_reports_missing_and_mismatched_fixture_bytes() -> None:
    expectations = packet_expectations_from_xor_spec(
        {
            "golden_vectors": [
                {"id": "expected_a", "encoded_datagram_hex": "01 02 03"},
                {"id": "expected_b", "encoded_datagram_hex": "04 05"},
            ]
        }
    )
    capture = {
        "schema_version": 1,
        "format": "quake_live_packet_byte_capture",
        "packets": [
            {"id": "expected_a", "bytes_hex": "01 ff 03"},
        ],
    }

    report = diff_packet_capture(capture, expectations)

    assert report["status"] == "mismatch"
    assert report["results"][0]["status"] == "mismatch"
    assert report["results"][0]["first_mismatch_offset"] == 1
    assert report["results"][1]["status"] == "missing"
    assert report["results"][1]["observed_size"] is None


def test_packet_capture_validator_rejects_bad_hashes_and_repeated_ids() -> None:
    repeated = {
        "schema_version": 1,
        "format": "quake_live_packet_byte_capture",
        "packets": [
            {"id": "packet", "bytes_hex": "01"},
            {"id": "packet", "bytes_hex": "02"},
        ],
    }
    with pytest.raises(CaptureDiffError, match="packet id repeated"):
        validate_packet_capture_dict(repeated)

    bad_hash = {
        "schema_version": 1,
        "format": "quake_live_packet_byte_capture",
        "packets": [
            {"id": "packet", "bytes_hex": "01", "sha256": "0" * 64},
        ],
    }
    with pytest.raises(CaptureDiffError, match="sha256 does not match"):
        validate_packet_capture_dict(bad_hash)


def _capture_diff_report(status: str = "match") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "format": "quake_live_capture_diff_report",
        "status": status,
        "packet_count": 1,
        "aggregate_payload_sha256": "e" * 64,
        "results": [
            {
                "fixture_id": "client_to_server_sideband_move",
                "lane": "xor_golden_datagram",
                "source": "network-xor-codec-parity-2026-06-05.json",
                "status": status,
                "expected_size": 8,
                "observed_size": 8 if status == "match" else 7,
                "expected_sha256": "f" * 64,
                "observed_sha256": "f" * 64 if status == "match" else "0" * 64,
                "first_mismatch_offset": None if status == "match" else 7,
            }
        ],
    }


def _capture_evidence_bundle() -> dict[str, Any]:
    transcript = parse_demo_bytes(_demo_record(41, b"\x03snapshot") + _demo_terminator())
    provenance = {
        "source": "retail-qzdm6",
        "capture_type": "protocol91_demo_transcript",
        "capture_date_utc": "2026-06-05T00:00:00Z",
        "retail_build": "Steam protocol 91",
    }
    return {
        "schema_version": 1,
        "format": "quake_live_capture_evidence_bundle",
        "bundle_id": "retail-evidence-bundle-unit",
        "protocol": 91,
        "provenance": provenance,
        "closure_targets": [
            {
                "row_id": "byte_for_byte_replay_fixture",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "retail-demo-transcript",
                        "type": "demo_transcript",
                        "format": "quake_live_demo_message_transcript",
                        "path": "docs/reverse-engineering/fixtures/retail-demo-transcript.json",
                        "sha256": "1" * 64,
                        "description": "protocol-91 retail demo transcript JSON",
                        "report": transcript.to_dict(provenance),
                    }
                ],
            },
            {
                "row_id": "xor_golden_datagrams",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "xor-capture-diff",
                        "type": "capture_diff_report",
                        "format": "quake_live_capture_diff_report",
                        "path": "docs/reverse-engineering/fixtures/xor-capture-diff.json",
                        "sha256": "2" * 64,
                        "description": "retail XOR datagram capture diff report",
                        "report": _capture_diff_report(),
                    }
                ],
            },
        ],
    }


def _capture_evidence_complete_bundle() -> dict[str, Any]:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"].extend(
        [
            {
                "row_id": "fragmented_snapshot_queued_followup",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "fragment-queue-timing-report",
                        "type": "fragment_queue_timing_report",
                        "format": "quake_live_fragment_queue_timing",
                        "path": "docs/reverse-engineering/fixtures/fragment-queue-timing.json",
                        "sha256": "3" * 64,
                        "description": "retail fragment queue timing report",
                        "validated_by": "tools.trace.fragment_timing",
                    }
                ],
            },
            {
                "row_id": "compressed_connect_capture_diff",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "compressed-connect-capture-diff",
                        "type": "capture_diff_report",
                        "format": "quake_live_capture_diff_report",
                        "path": "docs/reverse-engineering/fixtures/compressed-connect-capture-diff.json",
                        "sha256": "4" * 64,
                        "description": "retail compressed connect capture diff report",
                        "validated_by": "tools.trace.capture_diff",
                    }
                ],
            },
            {
                "row_id": "invalid_lc_retail_probe",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "invalid-lc-retail-probe",
                        "type": "invalid_lc_probe_report",
                        "format": "quake_live_invalid_lc_probe",
                        "path": "docs/reverse-engineering/fixtures/invalid-lc-retail-probe.json",
                        "sha256": "5" * 64,
                        "description": "controlled retail invalid-lc probe report",
                        "validated_by": "tools.trace.invalid_lc_probe",
                    }
                ],
            },
            {
                "row_id": "snapshot_field_capture_decode",
                "status": "submitted_for_closure",
                "artifacts": [
                    {
                        "id": "snapshot-field-decode-report",
                        "type": "snapshot_decode_report",
                        "format": "quake_live_snapshot_field_decode",
                        "path": "docs/reverse-engineering/fixtures/snapshot-field-decode.json",
                        "sha256": "6" * 64,
                        "description": "retail snapshot field decode report",
                        "validated_by": "tools.trace.snapshot_decode",
                    }
                ],
            },
        ]
    )
    return bundle


def test_capture_evidence_bundle_validator_accepts_embedded_retail_reports() -> None:
    summary = validate_capture_evidence_bundle_dict(
        _capture_evidence_bundle(),
        require_retail_provenance=True,
    )

    assert summary["bundle_id"] == "retail-evidence-bundle-unit"
    assert summary["protocol"] == 91
    assert summary["closure_target_count"] == 2
    assert summary["submitted_closure_target_count"] == 2
    assert summary["artifact_count"] == 2


def test_capture_evidence_bundle_validator_rejects_wrong_row_format_and_diff_failures() -> None:
    wrong_format = _capture_evidence_bundle()
    wrong_format["closure_targets"][0]["artifacts"][0]["format"] = "quake_live_snapshot_field_decode"
    with pytest.raises(CaptureEvidenceError, match="format is not allowed"):
        validate_capture_evidence_bundle_dict(wrong_format)

    mismatch_diff = _capture_evidence_bundle()
    mismatch_diff["closure_targets"][1]["artifacts"][0]["report"] = _capture_diff_report("mismatch")
    with pytest.raises(CaptureEvidenceError, match="must have match status"):
        validate_capture_evidence_bundle_dict(mismatch_diff, require_retail_provenance=True)

    repeated_row = _capture_evidence_bundle()
    repeated_row["closure_targets"][1]["row_id"] = "byte_for_byte_replay_fixture"
    with pytest.raises(CaptureEvidenceError, match="row_id repeated"):
        validate_capture_evidence_bundle_dict(repeated_row)


def test_capture_evidence_bundle_validator_requires_retail_provenance_for_closure() -> None:
    missing_provenance = _capture_evidence_bundle()
    missing_provenance.pop("provenance")
    with pytest.raises(CaptureEvidenceError, match="requires provenance metadata"):
        validate_capture_evidence_bundle_dict(missing_provenance, require_retail_provenance=True)

    not_claimed = _capture_evidence_bundle()
    not_claimed["closure_targets"][0]["status"] = "not_claimed"
    with pytest.raises(CaptureEvidenceError, match="cannot include not_claimed targets"):
        validate_capture_evidence_bundle_dict(not_claimed, require_retail_provenance=True)


def test_capture_evidence_bundle_cli_validates_json_file(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["bundle_id"] == "retail-evidence-bundle-unit"
    assert summary["submitted_closure_target_count"] == 2
    assert "capture evidence validation failed" not in result.stderr


def test_capture_evidence_bundle_cli_reports_validation_errors(tmp_path: Path) -> None:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][1]["artifacts"][0]["report"] = _capture_diff_report("mismatch")
    bundle_path = tmp_path / "bad_bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "must have match status" in result.stderr


def test_capture_evidence_bundle_cli_requires_specific_closure_rows(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--require-closure-row",
            "xor_golden_datagrams",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["required_closure_row_count"] == 1
    assert summary["required_closure_rows"] == ["xor_golden_datagrams"]


def test_capture_evidence_bundle_cli_requires_all_closure_rows(tmp_path: Path) -> None:
    bundle_path = tmp_path / "complete_bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_complete_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--require-all-closure-rows",
            "--print-closure-status",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["required_closure_row_count"] == 6
    assert status["required_closure_rows_ready_count"] == 6
    assert status["missing_target_count"] == 0
    assert status["validation_summary"]["all_closure_rows_required"] is True
    assert status["validation_summary"]["required_closure_row_count"] == 6


def test_capture_evidence_all_closure_row_requirement_rejects_missing_rows() -> None:
    with pytest.raises(CaptureEvidenceError, match="required closure rows are not submitted for closure"):
        require_all_capture_evidence_closure_rows(_capture_evidence_bundle())


def test_capture_evidence_closure_row_requirement_rejects_supporting_only_rows() -> None:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][1]["status"] = "supporting_evidence"

    with pytest.raises(CaptureEvidenceError, match="not submitted for closure"):
        require_capture_evidence_closure_rows(bundle, ["xor_golden_datagrams"])


def test_capture_evidence_closure_status_summarizes_all_residual_rows() -> None:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][1]["status"] = "supporting_evidence"

    status = summarize_capture_evidence_closure_status(
        bundle,
        required_rows=["byte_for_byte_replay_fixture", "xor_golden_datagrams"],
    )

    assert status["format"] == "quake_live_capture_evidence_closure_status"
    assert status["bundle_id"] == "retail-evidence-bundle-unit"
    assert status["row_count"] == 6
    assert status["artifact_count"] == 2
    assert status["submitted_closure_target_count"] == 1
    assert status["supporting_evidence_target_count"] == 1
    assert status["not_claimed_target_count"] == 0
    assert status["missing_target_count"] == 4
    assert status["required_closure_row_count"] == 2
    assert status["required_closure_rows_ready_count"] == 1

    rows = {row["row_id"]: row for row in status["rows"]}
    assert rows["byte_for_byte_replay_fixture"]["closure_ready"] is True
    assert rows["byte_for_byte_replay_fixture"]["required"] is True
    assert rows["byte_for_byte_replay_fixture"]["closure_blocker"] is None
    assert rows["xor_golden_datagrams"]["status"] == "supporting_evidence"
    assert rows["xor_golden_datagrams"]["required"] is True
    assert rows["xor_golden_datagrams"]["closure_ready"] is False
    assert rows["xor_golden_datagrams"]["closure_blocker"] == "target is supporting evidence only"
    assert rows["snapshot_field_capture_decode"]["status"] == "missing"
    assert rows["snapshot_field_capture_decode"]["closure_blocker"] == "closure target is missing from bundle"


def test_capture_evidence_closure_blockers_summarize_blocked_residual_rows() -> None:
    blockers = summarize_capture_evidence_closure_blockers(_capture_evidence_bundle())

    assert blockers["format"] == "quake_live_capture_evidence_closure_blockers"
    assert blockers["bundle_id"] == "retail-evidence-bundle-unit"
    assert blockers["required_closure_row_count"] == 6
    assert blockers["ready_required_closure_row_count"] == 2
    assert blockers["blocked_closure_row_count"] == 4
    blocked_rows = {row["row_id"]: row for row in blockers["blocked_rows"]}
    assert blocked_rows["fragmented_snapshot_queued_followup"]["closure_blocker"] == (
        "closure target is missing from bundle"
    )
    assert blocked_rows["fragmented_snapshot_queued_followup"]["next_action"] == (
        "add a closure target with submitted_for_closure status and at least one retail artifact"
    )
    assert blocked_rows["fragmented_snapshot_queued_followup"]["allowed_formats"] == [
        "quake_live_fragment_queue_timing"
    ]
    assert blocked_rows["invalid_lc_retail_probe"]["artifact_types"] == ["invalid_lc_probe_report"]


def test_capture_evidence_no_closure_blockers_rejects_blocked_rows() -> None:
    with pytest.raises(CaptureEvidenceError, match="closure blockers remain"):
        require_capture_evidence_no_closure_blockers(_capture_evidence_bundle())

    summary = require_capture_evidence_no_closure_blockers(
        _capture_evidence_complete_bundle(),
        ["byte_for_byte_replay_fixture", "xor_golden_datagrams"],
    )
    assert summary["closure_blocker_gate_passed"] is True
    assert summary["blocked_closure_row_count"] == 0
    assert summary["required_closure_rows"] == ["byte_for_byte_replay_fixture", "xor_golden_datagrams"]


def test_capture_evidence_bundle_cli_prints_closure_status(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--require-closure-row",
            "xor_golden_datagrams",
            "--print-closure-status",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["format"] == "quake_live_capture_evidence_closure_status"
    assert status["required_closure_rows"] == ["xor_golden_datagrams"]
    assert status["required_closure_rows_ready_count"] == 1
    assert status["validation_summary"]["required_closure_rows"] == ["xor_golden_datagrams"]
    assert status["validation_summary"]["submitted_closure_target_count"] == 2
    assert "capture evidence validation failed" not in result.stderr


def test_capture_evidence_bundle_cli_prints_closure_blockers(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--print-closure-blockers",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    blockers = json.loads(result.stdout)
    assert blockers["format"] == "quake_live_capture_evidence_closure_blockers"
    assert blockers["required_closure_row_count"] == 6
    assert blockers["ready_required_closure_row_count"] == 2
    assert blockers["blocked_closure_row_count"] == 4
    assert {row["row_id"] for row in blockers["blocked_rows"]} == {
        "fragmented_snapshot_queued_followup",
        "compressed_connect_capture_diff",
        "invalid_lc_retail_probe",
        "snapshot_field_capture_decode",
    }
    assert blockers["validation_summary"]["submitted_closure_target_count"] == 2
    assert "capture evidence validation failed" not in result.stderr


def test_capture_evidence_bundle_cli_fails_on_closure_blockers_after_printing_report(
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--print-closure-blockers",
            "--fail-on-closure-blockers",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    blockers = json.loads(result.stdout)
    assert blockers["format"] == "quake_live_capture_evidence_closure_blockers"
    assert blockers["blocked_closure_row_count"] == 4
    assert "capture evidence validation failed" not in result.stderr


def test_capture_evidence_artifact_text_policy_accepts_reviewed_text_paths() -> None:
    summary = verify_capture_evidence_artifact_text_policy(_capture_evidence_complete_bundle())

    assert summary["artifact_text_policy_checked_count"] == 6
    assert summary["artifact_text_policy_allowed_suffixes"] == [".json", ".md", ".txt"]
    assert ".dm_91" in summary["artifact_text_policy_rejected_suffixes"]
    assert ".pcap" in summary["artifact_text_policy_rejected_suffixes"]


def test_capture_evidence_artifact_path_policy_accepts_reviewed_evidence_paths() -> None:
    summary = verify_capture_evidence_artifact_path_policy(_capture_evidence_complete_bundle())

    assert summary["artifact_path_policy_checked_count"] == 6
    assert "docs/reverse-engineering/fixtures/" in summary["artifact_path_policy_allowed_prefixes"]
    assert "tests/netdumps/" in summary["artifact_path_policy_allowed_prefixes"]
    assert "assets/" in summary["artifact_path_policy_rejected_prefixes"]
    assert "src/ui/" in summary["artifact_path_policy_rejected_prefixes"]


def test_capture_evidence_bundle_cli_enforces_artifact_path_policy(tmp_path: Path) -> None:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][0]["artifacts"][0]["path"] = "assets/quakelive/retail-demo-transcript.json"
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--enforce-artifact-path-policy",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "path uses rejected evidence prefix" in result.stderr


def test_capture_evidence_artifact_uniqueness_policy_accepts_unique_artifacts() -> None:
    summary = verify_capture_evidence_artifact_uniqueness_policy(_capture_evidence_complete_bundle())

    assert summary["artifact_uniqueness_policy_checked_count"] == 6
    assert summary["unique_artifact_id_count"] == 6
    assert summary["unique_artifact_path_count"] == 6


def test_capture_evidence_bundle_cli_enforces_artifact_uniqueness_policy(tmp_path: Path) -> None:
    bundle = _capture_evidence_complete_bundle()
    duplicate_path = bundle["closure_targets"][0]["artifacts"][0]["path"]
    bundle["closure_targets"][1]["artifacts"][0]["path"] = duplicate_path
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--enforce-artifact-uniqueness-policy",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "path duplicates artifact" in result.stderr


def test_capture_evidence_bundle_cli_enforces_artifact_text_policy(tmp_path: Path) -> None:
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][0]["artifacts"][0]["path"] = "docs/reverse-engineering/fixtures/retail-match.dm_91"
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--enforce-artifact-text-policy",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "raw binary artifact path is not allowed" in result.stderr


def test_capture_evidence_bundle_cli_prints_row_contracts() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            "--print-row-contracts",
            "--row-contract",
            "invalid_lc_retail_probe",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    contracts = json.loads(result.stdout)
    assert contracts["format"] == "quake_live_capture_evidence_row_contracts"
    assert contracts["protocol"] == 91
    assert contracts["row_count"] == 1
    row = contracts["rows"][0]
    assert row["row_id"] == "invalid_lc_retail_probe"
    assert row["allowed_formats"] == ["quake_live_invalid_lc_probe"]
    assert row["artifact_types"] == ["invalid_lc_probe_report"]
    assert row["closure_target_statuses"] == [
        "submitted_for_closure",
        "supporting_evidence",
        "not_claimed",
    ]


def test_capture_evidence_row_contracts_reject_unknown_rows() -> None:
    with pytest.raises(CaptureEvidenceError, match="row contract row_id is not recognized"):
        capture_evidence_row_contracts(["not_a_residual_row"])


def test_capture_evidence_capture_plan_lists_row_scoped_collection_requirements() -> None:
    plan = capture_evidence_capture_plan(["compressed_connect_capture_diff"])

    assert plan["format"] == "quake_live_capture_evidence_capture_plan"
    assert plan["protocol"] == 91
    assert plan["claims_retail_evidence"] is False
    assert plan["row_count"] == 1
    row = plan["rows"][0]
    assert row["row_id"] == "compressed_connect_capture_diff"
    assert row["allowed_formats"] == [
        "quake_live_capture_diff_report",
        "quake_live_packet_byte_capture",
    ]
    assert "retail compressed connect datagram trace" in row["required_evidence"]
    assert "capture_date_utc" in row["retail_provenance_required_keys"]
    assert "docs/reverse-engineering/fixtures/" in row["recommended_artifact_prefixes"]
    assert row["bundle_template_command"].endswith("--template-row compressed_connect_capture_diff")
    assert "--strict-final-closure" in row["final_review_command"]


def test_capture_evidence_bundle_cli_prints_row_scoped_capture_plan() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            "--print-capture-plan",
            "--capture-plan-row",
            "invalid_lc_retail_probe",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    plan = json.loads(result.stdout)
    assert plan["format"] == "quake_live_capture_evidence_capture_plan"
    assert plan["rows"][0]["row_id"] == "invalid_lc_retail_probe"
    assert plan["rows"][0]["artifact_types"] == ["invalid_lc_probe_report"]
    assert "controlled retail invalid-lc probe report" in plan["rows"][0]["required_evidence"]


def test_capture_evidence_capture_plan_rejects_unknown_rows() -> None:
    with pytest.raises(CaptureEvidenceError, match="capture plan row_id is not recognized"):
        capture_evidence_capture_plan(["not_a_residual_row"])


def _write_artifact(root: Path, relative_path: str, payload: bytes) -> str:
    artifact_path = root / relative_path
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _write_capture_evidence_bundle_artifacts(root: Path, bundle: dict[str, Any]) -> None:
    for target in bundle["closure_targets"]:
        for artifact in target["artifacts"]:
            artifact["sha256"] = _write_artifact(
                root,
                artifact["path"],
                artifact["id"].encode("ascii"),
            )


def test_capture_evidence_bundle_cli_verifies_artifact_files(tmp_path: Path) -> None:
    artifact_root = tmp_path / "repo"
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][0]["artifacts"][0]["sha256"] = _write_artifact(
        artifact_root,
        "docs/reverse-engineering/fixtures/retail-demo-transcript.json",
        b'{"format":"quake_live_demo_message_transcript"}',
    )
    bundle["closure_targets"][1]["artifacts"][0]["sha256"] = _write_artifact(
        artifact_root,
        "docs/reverse-engineering/fixtures/xor-capture-diff.json",
        b'{"format":"quake_live_capture_diff_report"}',
    )
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--require-retail-provenance",
            "--verify-artifact-files",
            "--artifact-root",
            str(artifact_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["artifact_count"] == 2
    assert summary["verified_artifact_file_count"] == 2
    assert summary["artifact_root"] == str(artifact_root.resolve())


def test_capture_evidence_bundle_cli_strict_final_closure_requires_all_rows_and_artifacts(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "repo"
    bundle = _capture_evidence_complete_bundle()
    _write_capture_evidence_bundle_artifacts(artifact_root, bundle)
    bundle_path = tmp_path / "complete_bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--strict-final-closure",
            "--artifact-root",
            str(artifact_root),
            "--print-closure-status",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["required_closure_row_count"] == 6
    assert status["required_closure_rows_ready_count"] == 6
    assert status["missing_target_count"] == 0
    assert status["validation_summary"]["strict_final_closure"] is True
    assert status["validation_summary"]["all_closure_rows_required"] is True
    assert status["validation_summary"]["submitted_closure_target_count"] == 6
    assert status["validation_summary"]["verified_artifact_file_count"] == 6
    assert "capture evidence validation failed" not in result.stderr


def test_capture_evidence_bundle_cli_strict_final_closure_rejects_missing_artifact_files(
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "complete_bundle.json"
    bundle_path.write_text(json.dumps(_capture_evidence_complete_bundle()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            str(bundle_path),
            "--strict-final-closure",
            "--artifact-root",
            str(tmp_path / "repo"),
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "file does not exist" in result.stderr


def test_capture_evidence_bundle_artifact_file_verification_rejects_hash_mismatch(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "repo"
    bundle = _capture_evidence_bundle()
    bundle["closure_targets"][0]["artifacts"][0]["path"] = "docs/reverse-engineering/fixtures/demo.json"
    bundle["closure_targets"][0]["artifacts"][0]["sha256"] = "0" * 64
    _write_artifact(artifact_root, "docs/reverse-engineering/fixtures/demo.json", b"retail demo transcript")

    with pytest.raises(CaptureEvidenceError, match="sha256 mismatch"):
        verify_capture_evidence_artifact_files(bundle, artifact_root=artifact_root)


def test_capture_evidence_bundle_cli_hashes_artifacts_for_bundle_population(tmp_path: Path) -> None:
    artifact_root = tmp_path / "repo"
    relative_path = "docs/reverse-engineering/fixtures/retail-demo-transcript.json"
    expected_sha256 = _write_artifact(artifact_root, relative_path, b"retail demo transcript")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            "--hash-artifact",
            relative_path,
            "--artifact-root",
            str(artifact_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["artifact_root"] == str(artifact_root.resolve())
    assert summary["artifact_count"] == 1
    assert summary["artifacts"] == [
        {
            "path": relative_path,
            "size": len(b"retail demo transcript"),
            "sha256": expected_sha256,
        }
    ]


def test_capture_evidence_artifact_hashing_rejects_root_escape(tmp_path: Path) -> None:
    artifact_root = tmp_path / "repo"
    outside = tmp_path / "outside.json"
    outside.write_text("not under repo", encoding="utf-8")

    with pytest.raises(CaptureEvidenceError, match="escapes the artifact root"):
        hash_capture_evidence_artifacts([outside], artifact_root=artifact_root)


def test_capture_evidence_bundle_template_is_non_claiming_and_row_scoped() -> None:
    template = capture_evidence_bundle_template(["xor_golden_datagrams"])

    assert template["format"] == "quake_live_capture_evidence_bundle"
    assert template["protocol"] == 91
    assert template["provenance"]["capture_type"] == "retail_packet_capture"
    assert len(template["closure_targets"]) == 1
    target = template["closure_targets"][0]
    assert target["row_id"] == "xor_golden_datagrams"
    assert target["status"] == "not_claimed"
    assert target["artifacts"] == []
    assert {artifact["format"] for artifact in target["artifact_templates"]} == {
        "quake_live_capture_diff_report",
        "quake_live_packet_byte_capture",
    }

    summary = validate_capture_evidence_bundle_dict(template)
    assert summary["closure_target_count"] == 1
    assert summary["submitted_closure_target_count"] == 0
    assert summary["artifact_count"] == 0


def test_capture_evidence_bundle_template_rejects_unknown_rows() -> None:
    with pytest.raises(CaptureEvidenceError, match="template row_id is not recognized"):
        capture_evidence_bundle_template(["not_a_residual_row"])


def test_capture_evidence_bundle_cli_prints_row_scoped_template() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            "--print-template",
            "--template-row",
            "compressed_connect_capture_diff",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    template = json.loads(result.stdout)
    assert template["format"] == "quake_live_capture_evidence_bundle"
    assert [target["row_id"] for target in template["closure_targets"]] == [
        "compressed_connect_capture_diff"
    ]
    assert template["closure_targets"][0]["status"] == "not_claimed"
    assert {artifact["format"] for artifact in template["closure_targets"][0]["artifact_templates"]} == {
        "quake_live_capture_diff_report",
        "quake_live_packet_byte_capture",
    }


def test_capture_evidence_bundle_cli_reports_unknown_template_rows() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.trace.capture_evidence",
            "--print-template",
            "--template-row",
            "not_a_residual_row",
        ],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capture evidence validation failed:" in result.stderr
    assert "template row_id is not recognized" in result.stderr


def _fragment_queue_timing_report() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "format": "quake_live_fragment_queue_timing",
        "capture_id": "retail-fragment-queue-unit",
        "provenance": {
            "source": "retail-qzdm6",
            "capture_type": "retail_packet_capture",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "Steam protocol 91",
        },
        "fragment_reassembly": [
            {
                "sequence": 77,
                "fragmentStart": 0,
                "fragmentLength": 1300,
                "accumulatedLength": 1300,
                "accepted": False,
                "reassembledPayloadHash": None,
            },
            {
                "sequence": 77,
                "fragmentStart": 1300,
                "fragmentLength": 24,
                "accumulatedLength": 1324,
                "accepted": True,
                "reassembledPayloadHash": "1" * 64,
            },
        ],
        "queued_followup": [
            {
                "queuedMessageSequence": 78,
                "storedEncoded": False,
                "encodedOnPop": True,
                "queueEmptyAfterPop": True,
                "datagramHash": "2" * 64,
            }
        ],
    }


def test_fragment_queue_timing_validator_accepts_retail_timing_report() -> None:
    summary = validate_fragment_queue_timing_dict(
        _fragment_queue_timing_report(),
        require_retail_provenance=True,
    )

    assert summary["capture_id"] == "retail-fragment-queue-unit"
    assert summary["fragment_event_count"] == 2
    assert summary["full_fragment_count"] == 1
    assert summary["terminal_fragment_count"] == 1
    assert summary["queued_followup_count"] == 1
    assert summary["queue_empty_after_pop_count"] == 1


def test_fragment_queue_timing_validator_rejects_wrong_fragment_and_queue_timing() -> None:
    full_fragment_accepted = _fragment_queue_timing_report()
    full_fragment_accepted["fragment_reassembly"][0]["accepted"] = True
    with pytest.raises(FragmentTimingError, match="full FRAGMENT_SIZE fragments must not be accepted"):
        validate_fragment_queue_timing_dict(full_fragment_accepted)

    stored_encoded = _fragment_queue_timing_report()
    stored_encoded["queued_followup"][0]["storedEncoded"] = True
    with pytest.raises(FragmentTimingError, match="must be stored unencoded"):
        validate_fragment_queue_timing_dict(stored_encoded)

    not_empty_at_end = _fragment_queue_timing_report()
    not_empty_at_end["queued_followup"][0]["queueEmptyAfterPop"] = False
    with pytest.raises(FragmentTimingError, match="last queued follow-up event must empty the queue"):
        validate_fragment_queue_timing_dict(not_empty_at_end)


def test_fragment_queue_timing_validator_requires_retail_provenance_for_closure() -> None:
    report = _fragment_queue_timing_report()
    report.pop("provenance")

    with pytest.raises(FragmentTimingError, match="requires provenance metadata"):
        validate_fragment_queue_timing_dict(report, require_retail_provenance=True)

    bad_type = _fragment_queue_timing_report()
    bad_type["provenance"]["capture_type"] = "local_generated_packet_capture"
    with pytest.raises(FragmentTimingError, match="capture_type is not recognized"):
        validate_fragment_queue_timing_dict(bad_type, require_retail_provenance=True)


def _invalid_lc_probe_report() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "format": "quake_live_invalid_lc_probe",
        "probe_id": "invalid-lc-entity-59-retail-unit",
        "protocol": 91,
        "provenance": {
            "source": "retail-malicious-packet-lab",
            "capture_type": "controlled_retail_probe",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "Steam protocol 91",
        },
        "malicious_input": {
            "field_table": "entityStateFields",
            "field_count": 58,
            "lc": 59,
            "packet_sha256": "3" * 64,
        },
        "retail_observation": {
            "classification": "crash",
            "observed_message": "retail process terminated while walking entityStateFields[59]",
            "artifacts": [
                {
                    "type": "crash_dump",
                    "sha256": "4" * 64,
                    "description": "retail crash dump from controlled invalid-lc probe",
                }
            ],
        },
        "source_observation": {
            "classification": "err_drop",
            "error_message": "MSG_ReadDeltaEntity: invalid field count 59",
        },
    }


def test_invalid_lc_probe_validator_accepts_controlled_retail_report() -> None:
    summary = validate_invalid_lc_probe_dict(
        _invalid_lc_probe_report(),
        require_retail_provenance=True,
    )

    assert summary["probe_id"] == "invalid-lc-entity-59-retail-unit"
    assert summary["protocol"] == 91
    assert summary["field_table"] == "entityStateFields"
    assert summary["field_count"] == 58
    assert summary["lc"] == 59
    assert summary["retail_classification"] == "crash"
    assert summary["artifact_count"] == 1


def test_invalid_lc_probe_validator_rejects_non_malicious_lc_and_wrong_source_guard() -> None:
    in_range_lc = _invalid_lc_probe_report()
    in_range_lc["malicious_input"]["lc"] = 58
    in_range_lc["source_observation"]["error_message"] = "MSG_ReadDeltaEntity: invalid field count 58"
    with pytest.raises(InvalidLcProbeError, match="lc must exceed"):
        validate_invalid_lc_probe_dict(in_range_lc)

    wrong_source = _invalid_lc_probe_report()
    wrong_source["source_observation"]["classification"] = "accepted"
    with pytest.raises(InvalidLcProbeError, match="source classification must be err_drop"):
        validate_invalid_lc_probe_dict(wrong_source)

    wrong_error = _invalid_lc_probe_report()
    wrong_error["source_observation"]["error_message"] = "MSG_ReadDeltaPlayerstate: invalid field count 59"
    with pytest.raises(InvalidLcProbeError, match="source error_message does not match"):
        validate_invalid_lc_probe_dict(wrong_error)


def test_invalid_lc_probe_validator_requires_retail_provenance_and_hashed_artifacts() -> None:
    missing_provenance = _invalid_lc_probe_report()
    missing_provenance.pop("provenance")
    with pytest.raises(InvalidLcProbeError, match="requires provenance metadata"):
        validate_invalid_lc_probe_dict(missing_provenance, require_retail_provenance=True)

    missing_artifact = _invalid_lc_probe_report()
    missing_artifact["retail_observation"]["artifacts"] = []
    with pytest.raises(InvalidLcProbeError, match="requires at least one hashed artifact"):
        validate_invalid_lc_probe_dict(missing_artifact, require_retail_provenance=True)

    bad_type = _invalid_lc_probe_report()
    bad_type["provenance"]["capture_type"] = "local_source_probe"
    with pytest.raises(InvalidLcProbeError, match="capture_type is not recognized"):
        validate_invalid_lc_probe_dict(bad_type, require_retail_provenance=True)


def _snapshot_decode_specs() -> tuple[dict[str, Any], dict[str, Any]]:
    playerstate_spec = {
        "source_of_truth": {
            "entries": [
                {
                    "index": 49,
                    "field": "jumpTime",
                    "bits": 32,
                    "wire_kind": "unsigned_int",
                },
                {
                    "index": 57,
                    "field": "upmove",
                    "bits": 8,
                    "wire_kind": "signed_byte_unsigned_wire",
                },
            ]
        }
    }
    entitystate_spec = {
        "source_of_truth": {
            "entries": [
                {
                    "index": 33,
                    "field": "generic1",
                    "source_alias": "retailEventData",
                    "bits": 8,
                    "wire_kind": "unsigned_int",
                },
                {
                    "index": 57,
                    "field": "location",
                    "bits": 8,
                    "wire_kind": "unsigned_int",
                },
            ]
        }
    }
    return playerstate_spec, entitystate_spec


def _snapshot_decode_report() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "format": "quake_live_snapshot_field_decode",
        "capture_id": "retail-snapshot-decode-unit",
        "protocol": 91,
        "provenance": {
            "source": "retail-qzdm6",
            "capture_type": "protocol91_demo_transcript",
            "capture_date_utc": "2026-06-05T00:00:00Z",
            "retail_build": "Steam protocol 91",
        },
        "field_tables": [
            {
                "name": "playerStateFields",
                "field_count": 58,
                "decode_hash": "5" * 64,
                "observed_fields": [
                    {
                        "field": "jumpTime",
                        "index": 49,
                        "bits": 32,
                        "wire_kind": "unsigned_int",
                        "value_hash": "6" * 64,
                    },
                    {
                        "field": "upmove",
                        "index": 57,
                        "bits": 8,
                        "wire_kind": "signed_byte_unsigned_wire",
                        "value_hash": "7" * 64,
                    },
                ],
            },
            {
                "name": "entityStateFields",
                "field_count": 58,
                "decode_hash": "8" * 64,
                "observed_fields": [
                    {
                        "field": "retailEventData",
                        "index": 33,
                        "bits": 8,
                        "wire_kind": "unsigned_int",
                        "value_hash": "9" * 64,
                    },
                    {
                        "field": "location",
                        "index": 57,
                        "bits": 8,
                        "wire_kind": "unsigned_int",
                        "value_hash": "a" * 64,
                    },
                ],
            },
        ],
        "snapshots": [
            {
                "messageNum": 7,
                "serverTime": 1234,
                "deltaNum": -1,
                "packetEntityCount": 2,
                "playerStateHash": "b" * 64,
                "entityStateHash": "c" * 64,
                "packetEntitiesHash": "d" * 64,
            }
        ],
    }


def test_snapshot_field_decode_validator_accepts_player_and_entity_decode_report() -> None:
    playerstate_spec, entitystate_spec = _snapshot_decode_specs()

    summary = validate_snapshot_field_decode_dict(
        _snapshot_decode_report(),
        playerstate_spec=playerstate_spec,
        entitystate_spec=entitystate_spec,
        require_retail_provenance=True,
    )

    assert summary["capture_id"] == "retail-snapshot-decode-unit"
    assert summary["protocol"] == 91
    assert summary["field_table_count"] == 2
    assert summary["observed_field_count"] == 4
    assert summary["snapshot_count"] == 1


def test_snapshot_field_decode_validator_rejects_field_table_drift() -> None:
    playerstate_spec, entitystate_spec = _snapshot_decode_specs()

    wrong_player_index = _snapshot_decode_report()
    wrong_player_index["field_tables"][0]["observed_fields"][0]["index"] = 21
    with pytest.raises(SnapshotDecodeError, match="index does not match spec"):
        validate_snapshot_field_decode_dict(
            wrong_player_index,
            playerstate_spec=playerstate_spec,
            entitystate_spec=entitystate_spec,
        )

    unknown_field = _snapshot_decode_report()
    unknown_field["field_tables"][1]["observed_fields"][0]["field"] = "missingRetailField"
    with pytest.raises(SnapshotDecodeError, match="is not in the retail spec"):
        validate_snapshot_field_decode_dict(
            unknown_field,
            playerstate_spec=playerstate_spec,
            entitystate_spec=entitystate_spec,
        )

    missing_table = _snapshot_decode_report()
    missing_table["field_tables"] = missing_table["field_tables"][:1]
    with pytest.raises(SnapshotDecodeError, match="field_tables missing"):
        validate_snapshot_field_decode_dict(missing_table)


def test_snapshot_field_decode_validator_requires_retail_provenance_and_snapshots() -> None:
    report = _snapshot_decode_report()
    report.pop("provenance")
    with pytest.raises(SnapshotDecodeError, match="requires provenance metadata"):
        validate_snapshot_field_decode_dict(report, require_retail_provenance=True)

    bad_type = _snapshot_decode_report()
    bad_type["provenance"]["capture_type"] = "local_snapshot_decode"
    with pytest.raises(SnapshotDecodeError, match="capture_type is not recognized"):
        validate_snapshot_field_decode_dict(bad_type, require_retail_provenance=True)

    empty_snapshots = _snapshot_decode_report()
    empty_snapshots["snapshots"] = []
    with pytest.raises(SnapshotDecodeError, match="snapshots must not be empty"):
        validate_snapshot_field_decode_dict(empty_snapshots)


@pytest.mark.parametrize(
    ("demo", "message"),
    [
        (b"\x01\x00\x00", "truncated demo record header"),
        (_demo_record(1, b"abc")[:-1], "truncated demo payload"),
        (
            (1).to_bytes(4, "little", signed=True)
            + (-2).to_bytes(4, "little", signed=True),
            "invalid negative demo message length",
        ),
        (
            (1).to_bytes(4, "little", signed=True)
            + (16385).to_bytes(4, "little", signed=True),
            "exceeds MAX_MSGLEN",
        ),
    ],
)
def test_demo_transcript_rejects_invalid_envelopes(demo: bytes, message: str) -> None:
    with pytest.raises(DemoTranscriptError, match=message):
        parse_demo_bytes(demo)
