"""Compare packet-byte captures against committed network byte fixtures."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .demo_transcript import DemoTranscriptError, RETAIL_CAPTURE_TYPES, RETAIL_PROVENANCE_KEYS


class CaptureDiffError(ValueError):
    """Raised when a capture diff input is malformed."""


@dataclass(frozen=True)
class PacketExpectation:
    """Expected bytes for one packet-level capture comparison."""

    fixture_id: str
    expected_hex: str
    lane: str
    source: str

    @property
    def expected_bytes(self) -> bytes:
        return _bytes_from_hex(self.expected_hex, f"expectation {self.fixture_id}")


def _bytes_from_hex(value: object, context: str) -> bytes:
    if not isinstance(value, str):
        raise CaptureDiffError(f"{context} hex value must be a string")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise CaptureDiffError(f"{context} hex value is not valid hex") from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _first_mismatch(expected: bytes, observed: bytes) -> int | None:
    for index, (expected_byte, observed_byte) in enumerate(zip(expected, observed)):
        if expected_byte != observed_byte:
            return index
    if len(expected) != len(observed):
        return min(len(expected), len(observed))
    return None


def validate_packet_capture_dict(
    capture: Mapping[str, Any],
    *,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a packet-byte capture JSON object."""

    if capture.get("schema_version") != 1:
        raise CaptureDiffError("packet capture schema_version must be 1")
    if capture.get("format") != "quake_live_packet_byte_capture":
        raise CaptureDiffError("packet capture format must be quake_live_packet_byte_capture")

    packets = capture.get("packets")
    if not isinstance(packets, list):
        raise CaptureDiffError("packet capture packets must be a list")

    seen: set[str] = set()
    aggregate_hasher = hashlib.sha256()
    for index, packet in enumerate(packets):
        if not isinstance(packet, Mapping):
            raise CaptureDiffError(f"packet {index} must be an object")
        packet_id = packet.get("id")
        if not isinstance(packet_id, str) or not packet_id:
            raise CaptureDiffError(f"packet {index} id must be a non-empty string")
        if packet_id in seen:
            raise CaptureDiffError(f"packet id repeated: {packet_id}")
        seen.add(packet_id)
        payload = _bytes_from_hex(packet.get("bytes_hex"), f"packet {packet_id}")
        declared_size = packet.get("size")
        if declared_size is not None and declared_size != len(payload):
            raise CaptureDiffError(f"packet {packet_id} size does not match bytes_hex")
        declared_hash = packet.get("sha256")
        if declared_hash is not None and declared_hash != _sha256(payload):
            raise CaptureDiffError(f"packet {packet_id} sha256 does not match bytes_hex")
        aggregate_hasher.update(payload)

    provenance = capture.get("provenance")
    if require_retail_provenance:
        if not isinstance(provenance, Mapping):
            raise DemoTranscriptError("retail packet capture requires provenance metadata")
        missing = [
            key
            for key in RETAIL_PROVENANCE_KEYS
            if not isinstance(provenance.get(key), str) or not provenance.get(key)
        ]
        if missing:
            raise DemoTranscriptError(
                f"retail packet capture provenance missing required keys: {', '.join(missing)}"
            )
        if provenance.get("capture_type") not in RETAIL_CAPTURE_TYPES:
            raise DemoTranscriptError("retail packet capture provenance capture_type is not recognized")

    return {
        "packet_count": len(packets),
        "aggregate_payload_sha256": aggregate_hasher.hexdigest(),
    }


def packet_expectations_from_xor_spec(spec: Mapping[str, Any]) -> tuple[PacketExpectation, ...]:
    expectations: list[PacketExpectation] = []
    for vector in spec.get("golden_vectors", []):
        if "encoded_datagram_hex" not in vector:
            continue
        expectations.append(
            PacketExpectation(
                fixture_id=vector["id"],
                expected_hex=vector["encoded_datagram_hex"],
                lane="xor_golden_datagram",
                source="network-xor-codec-parity-2026-06-05.json",
            )
        )
    return tuple(expectations)


def packet_expectations_from_huffman_spec(spec: Mapping[str, Any]) -> tuple[PacketExpectation, ...]:
    expectations: list[PacketExpectation] = []
    for fixture in spec.get("fixtures", []):
        if "encoded_datagram_hex" not in fixture:
            continue
        expectations.append(
            PacketExpectation(
                fixture_id=fixture["id"],
                expected_hex=fixture["encoded_datagram_hex"],
                lane="adaptive_huffman_datagram",
                source="network-adaptive-huffman-fixtures-2026-06-05.json",
            )
        )
    return tuple(expectations)


def diff_packet_capture(
    capture: Mapping[str, Any],
    expectations: Sequence[PacketExpectation] | Iterable[PacketExpectation],
    *,
    require_retail_provenance: bool = False,
) -> dict[str, Any]:
    """Compare a packet-byte capture against expected fixture bytes."""

    summary = validate_packet_capture_dict(
        capture,
        require_retail_provenance=require_retail_provenance,
    )
    packet_index = {
        packet["id"]: _bytes_from_hex(packet["bytes_hex"], f"packet {packet['id']}")
        for packet in capture["packets"]
    }

    results: list[dict[str, Any]] = []
    for expectation in expectations:
        expected = expectation.expected_bytes
        observed = packet_index.get(expectation.fixture_id)
        if observed is None:
            results.append(
                {
                    "fixture_id": expectation.fixture_id,
                    "lane": expectation.lane,
                    "source": expectation.source,
                    "status": "missing",
                    "expected_size": len(expected),
                    "observed_size": None,
                    "expected_sha256": _sha256(expected),
                    "observed_sha256": None,
                    "first_mismatch_offset": None,
                }
            )
            continue

        mismatch = _first_mismatch(expected, observed)
        results.append(
            {
                "fixture_id": expectation.fixture_id,
                "lane": expectation.lane,
                "source": expectation.source,
                "status": "match" if mismatch is None else "mismatch",
                "expected_size": len(expected),
                "observed_size": len(observed),
                "expected_sha256": _sha256(expected),
                "observed_sha256": _sha256(observed),
                "first_mismatch_offset": mismatch,
            }
        )

    status = "match"
    if any(result["status"] == "mismatch" for result in results):
        status = "mismatch"
    elif any(result["status"] == "missing" for result in results):
        status = "missing"

    return {
        "schema_version": 1,
        "format": "quake_live_capture_diff_report",
        "status": status,
        "packet_count": summary["packet_count"],
        "aggregate_payload_sha256": summary["aggregate_payload_sha256"],
        "results": results,
    }
