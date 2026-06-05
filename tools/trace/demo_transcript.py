"""Build text transcripts from Quake Live demo message envelopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


MAX_MSGLEN = 16384


class DemoTranscriptError(ValueError):
    """Raised when a demo file does not match the expected message envelope."""


RETAIL_CAPTURE_TYPES = frozenset(
    {
        "retail_packet_capture",
        "protocol91_demo_transcript",
        "known_good_byte_fixture",
    }
)
RETAIL_PROVENANCE_KEYS = (
    "source",
    "capture_type",
    "capture_date_utc",
    "retail_build",
)


@dataclass(frozen=True)
class DemoMessageRecord:
    """One server-message record from a Quake Live demo file."""

    index: int
    offset: int
    sequence: int
    length: int
    payload_sha256: str
    payload_hex: str
    first_byte: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "offset": self.offset,
            "sequence": self.sequence,
            "length": self.length,
            "payload_sha256": self.payload_sha256,
            "payload_hex": self.payload_hex,
            "first_byte": self.first_byte,
        }


@dataclass(frozen=True)
class DemoTranscript:
    """Text transcript for a demo envelope suitable for committed review."""

    protocol: int
    source_size: int
    message_count: int
    terminator_offset: int | None
    payload_sha256: str
    messages: tuple[DemoMessageRecord, ...]

    def to_dict(self, provenance: Mapping[str, Any] | None = None) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": 1,
            "format": "quake_live_demo_message_transcript",
            "protocol": self.protocol,
            "source_size": self.source_size,
            "message_count": self.message_count,
            "terminator_offset": self.terminator_offset,
            "payload_sha256": self.payload_sha256,
            "messages": [message.to_dict() for message in self.messages],
        }
        if provenance:
            data["provenance"] = dict(provenance)
        return data


def parse_demo_bytes(data: bytes, protocol: int = 91, max_msg_len: int = MAX_MSGLEN) -> DemoTranscript:
    """Parse a Quake Live ``.dm_91`` message envelope into a text transcript."""

    offset = 0
    records: list[DemoMessageRecord] = []
    payload_hasher = hashlib.sha256()
    terminator_offset: int | None = None

    while offset < len(data):
        if len(data) - offset < 8:
            raise DemoTranscriptError(f"truncated demo record header at offset {offset}")

        record_offset = offset
        sequence, length = struct.unpack_from("<ii", data, offset)
        offset += 8

        if sequence == -1 and length == -1:
            terminator_offset = record_offset
            if offset != len(data):
                raise DemoTranscriptError(
                    f"demo terminator at offset {record_offset} has trailing bytes"
                )
            break

        if length < 0:
            raise DemoTranscriptError(
                f"invalid negative demo message length {length} at offset {record_offset}"
            )
        if length > max_msg_len:
            raise DemoTranscriptError(
                f"demo message length {length} exceeds MAX_MSGLEN {max_msg_len}"
            )
        if len(data) - offset < length:
            raise DemoTranscriptError(
                f"truncated demo payload at offset {offset}: need {length}, have {len(data) - offset}"
            )

        payload = data[offset:offset + length]
        offset += length
        payload_hasher.update(payload)

        records.append(
            DemoMessageRecord(
                index=len(records),
                offset=record_offset,
                sequence=sequence,
                length=length,
                payload_sha256=hashlib.sha256(payload).hexdigest(),
                payload_hex=payload.hex(" "),
                first_byte=payload[0] if payload else None,
            )
        )

    if terminator_offset is None:
        raise DemoTranscriptError("demo file ended without a -1/-1 terminator")

    return DemoTranscript(
        protocol=protocol,
        source_size=len(data),
        message_count=len(records),
        terminator_offset=terminator_offset,
        payload_sha256=payload_hasher.hexdigest(),
        messages=tuple(records),
    )


def parse_demo_file(path: Path, protocol: int = 91, max_msg_len: int = MAX_MSGLEN) -> DemoTranscript:
    return parse_demo_bytes(path.read_bytes(), protocol=protocol, max_msg_len=max_msg_len)


def _decode_payload_hex(value: object, index: int) -> bytes:
    if not isinstance(value, str):
        raise DemoTranscriptError(f"message {index} payload_hex must be a string")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise DemoTranscriptError(f"message {index} payload_hex is not valid hex") from exc


def validate_demo_transcript_dict(
    data: Mapping[str, Any],
    *,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a committed demo transcript JSON object."""

    if data.get("schema_version") != 1:
        raise DemoTranscriptError("transcript schema_version must be 1")
    if data.get("format") != "quake_live_demo_message_transcript":
        raise DemoTranscriptError("transcript format must be quake_live_demo_message_transcript")

    protocol = data.get("protocol")
    if not isinstance(protocol, int) or protocol <= 0:
        raise DemoTranscriptError("transcript protocol must be a positive integer")

    source_size = data.get("source_size")
    terminator_offset = data.get("terminator_offset")
    message_count = data.get("message_count")
    messages = data.get("messages")
    if not isinstance(source_size, int) or source_size < 8:
        raise DemoTranscriptError("transcript source_size must include at least the terminator")
    if not isinstance(terminator_offset, int) or terminator_offset < 0:
        raise DemoTranscriptError("transcript terminator_offset must be a non-negative integer")
    if source_size != terminator_offset + 8:
        raise DemoTranscriptError("transcript source_size must equal terminator_offset + 8")
    if not isinstance(messages, list):
        raise DemoTranscriptError("transcript messages must be a list")
    if message_count != len(messages):
        raise DemoTranscriptError("transcript message_count does not match messages length")

    payload_hasher = hashlib.sha256()
    expected_offset = 0
    for expected_index, message in enumerate(messages):
        if not isinstance(message, Mapping):
            raise DemoTranscriptError(f"message {expected_index} must be an object")
        if message.get("index") != expected_index:
            raise DemoTranscriptError(f"message {expected_index} index mismatch")
        if message.get("offset") != expected_offset:
            raise DemoTranscriptError(f"message {expected_index} offset mismatch")
        length = message.get("length")
        if not isinstance(length, int) or length < 0 or length > MAX_MSGLEN:
            raise DemoTranscriptError(f"message {expected_index} length is invalid")

        payload = _decode_payload_hex(message.get("payload_hex"), expected_index)
        if len(payload) != length:
            raise DemoTranscriptError(f"message {expected_index} payload length mismatch")
        if hashlib.sha256(payload).hexdigest() != message.get("payload_sha256"):
            raise DemoTranscriptError(f"message {expected_index} payload_sha256 mismatch")
        first_byte = message.get("first_byte")
        expected_first = payload[0] if payload else None
        if first_byte != expected_first:
            raise DemoTranscriptError(f"message {expected_index} first_byte mismatch")

        payload_hasher.update(payload)
        expected_offset += 8 + length

    if expected_offset != terminator_offset:
        raise DemoTranscriptError("transcript terminator_offset does not follow the last message")
    aggregate = payload_hasher.hexdigest()
    if aggregate != data.get("payload_sha256"):
        raise DemoTranscriptError("transcript payload_sha256 mismatch")

    provenance = data.get("provenance")
    if require_retail_provenance:
        if not isinstance(provenance, Mapping):
            raise DemoTranscriptError("retail transcript requires provenance metadata")
        missing = [
            key
            for key in RETAIL_PROVENANCE_KEYS
            if not isinstance(provenance.get(key), str) or not provenance.get(key)
        ]
        if missing:
            raise DemoTranscriptError(
                f"retail transcript provenance missing required keys: {', '.join(missing)}"
            )
        if provenance.get("capture_type") not in RETAIL_CAPTURE_TYPES:
            raise DemoTranscriptError("retail transcript provenance capture_type is not recognized")

    return {
        "protocol": protocol,
        "source_size": source_size,
        "message_count": len(messages),
        "payload_sha256": aggregate,
    }


def _provenance_from_pairs(pairs: Iterable[str]) -> dict[str, str]:
    provenance: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise DemoTranscriptError(f"provenance entry must be key=value: {pair}")
        key, value = pair.split("=", 1)
        provenance[key] = value
    return provenance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", type=Path, help="Path to a .dm_91 demo file")
    parser.add_argument("-o", "--output", type=Path, help="Write transcript JSON to this path")
    parser.add_argument("--protocol", type=int, default=91, help="Demo protocol number")
    parser.add_argument(
        "--provenance",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Attach provenance metadata to the transcript",
    )
    args = parser.parse_args(argv)

    transcript = parse_demo_file(args.demo, protocol=args.protocol)
    payload = json.dumps(
        transcript.to_dict(_provenance_from_pairs(args.provenance)),
        indent=2,
        sort_keys=True,
    )
    payload += "\n"

    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
