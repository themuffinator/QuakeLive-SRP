"""Validate fragmented-message and queued-follow-up timing reports."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .demo_transcript import RETAIL_CAPTURE_TYPES, RETAIL_PROVENANCE_KEYS


FRAGMENT_SIZE = 1300
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


class FragmentTimingError(ValueError):
    """Raised when a fragment/queue timing report is malformed."""


def _non_negative_int(value: object, context: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise FragmentTimingError(f"{context} must be a non-negative integer")
    return value


def _require_bool(value: object, context: str) -> bool:
    if not isinstance(value, bool):
        raise FragmentTimingError(f"{context} must be a boolean")
    return value


def _require_hash(value: object, context: str) -> str:
    if not isinstance(value, str) or not SHA256_HEX_RE.match(value):
        raise FragmentTimingError(f"{context} must be a lowercase SHA-256 hex string")
    return value


def _validate_retail_provenance(report: Mapping[str, Any]) -> None:
    provenance = report.get("provenance")
    if not isinstance(provenance, Mapping):
        raise FragmentTimingError("retail fragment timing report requires provenance metadata")
    missing = [
        key
        for key in RETAIL_PROVENANCE_KEYS
        if not isinstance(provenance.get(key), str) or not provenance.get(key)
    ]
    if missing:
        raise FragmentTimingError(
            f"retail fragment timing provenance missing required keys: {', '.join(missing)}"
        )
    if provenance.get("capture_type") not in RETAIL_CAPTURE_TYPES:
        raise FragmentTimingError("retail fragment timing provenance capture_type is not recognized")


def validate_fragment_queue_timing_dict(
    report: Mapping[str, Any],
    *,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a committed fragmented-message plus queued-follow-up timing report."""

    if report.get("schema_version") != 1:
        raise FragmentTimingError("fragment timing schema_version must be 1")
    if report.get("format") != "quake_live_fragment_queue_timing":
        raise FragmentTimingError("fragment timing format must be quake_live_fragment_queue_timing")

    capture_id = report.get("capture_id")
    if not isinstance(capture_id, str) or not capture_id:
        raise FragmentTimingError("fragment timing capture_id must be a non-empty string")

    fragments = report.get("fragment_reassembly")
    followups = report.get("queued_followup")
    if not isinstance(fragments, list):
        raise FragmentTimingError("fragment_reassembly must be a list")
    if not isinstance(followups, list):
        raise FragmentTimingError("queued_followup must be a list")
    if not fragments:
        raise FragmentTimingError("fragment_reassembly must contain at least one event")
    if not followups:
        raise FragmentTimingError("queued_followup must contain at least one event")

    if require_retail_provenance:
        _validate_retail_provenance(report)

    expected_starts_by_sequence: dict[int, int] = {}
    full_fragment_count = 0
    terminal_fragment_count = 0
    accepted_fragment_count = 0

    for index, event in enumerate(fragments):
        if not isinstance(event, Mapping):
            raise FragmentTimingError(f"fragment event {index} must be an object")

        sequence = _non_negative_int(event.get("sequence"), f"fragment event {index} sequence")
        fragment_start = _non_negative_int(
            event.get("fragmentStart"),
            f"fragment event {index} fragmentStart",
        )
        fragment_length = _non_negative_int(
            event.get("fragmentLength"),
            f"fragment event {index} fragmentLength",
        )
        accumulated_length = _non_negative_int(
            event.get("accumulatedLength"),
            f"fragment event {index} accumulatedLength",
        )
        accepted = _require_bool(event.get("accepted"), f"fragment event {index} accepted")

        expected_start = expected_starts_by_sequence.get(sequence, 0)
        if fragment_start != expected_start:
            raise FragmentTimingError(
                f"fragment event {index} fragmentStart must equal previous accumulatedLength"
            )
        if accumulated_length != fragment_start + fragment_length:
            raise FragmentTimingError(
                f"fragment event {index} accumulatedLength must equal fragmentStart + fragmentLength"
            )

        if fragment_length == FRAGMENT_SIZE:
            if accepted:
                raise FragmentTimingError("full FRAGMENT_SIZE fragments must not be accepted")
            full_fragment_count += 1
        elif fragment_length < FRAGMENT_SIZE:
            if not accepted:
                raise FragmentTimingError("terminal short fragments must be accepted")
            _require_hash(
                event.get("reassembledPayloadHash"),
                f"fragment event {index} reassembledPayloadHash",
            )
            terminal_fragment_count += 1
            accepted_fragment_count += 1
        else:
            raise FragmentTimingError(
                f"fragment event {index} fragmentLength must not exceed FRAGMENT_SIZE"
            )

        expected_starts_by_sequence[sequence] = accumulated_length

    if full_fragment_count == 0:
        raise FragmentTimingError("fragment timing report must include a nonterminal full fragment")
    if terminal_fragment_count == 0:
        raise FragmentTimingError("fragment timing report must include a terminal short fragment")

    queue_empty_after_pop_count = 0
    for index, event in enumerate(followups):
        if not isinstance(event, Mapping):
            raise FragmentTimingError(f"queued follow-up event {index} must be an object")

        _non_negative_int(
            event.get("queuedMessageSequence"),
            f"queued follow-up event {index} queuedMessageSequence",
        )
        stored_encoded = _require_bool(
            event.get("storedEncoded"),
            f"queued follow-up event {index} storedEncoded",
        )
        encoded_on_pop = _require_bool(
            event.get("encodedOnPop"),
            f"queued follow-up event {index} encodedOnPop",
        )
        queue_empty_after_pop = _require_bool(
            event.get("queueEmptyAfterPop"),
            f"queued follow-up event {index} queueEmptyAfterPop",
        )
        if stored_encoded:
            raise FragmentTimingError("queued follow-up messages must be stored unencoded")
        if not encoded_on_pop:
            raise FragmentTimingError("queued follow-up messages must be encoded on pop")
        if queue_empty_after_pop:
            queue_empty_after_pop_count += 1
        _require_hash(event.get("datagramHash"), f"queued follow-up event {index} datagramHash")

    if not _require_bool(followups[-1].get("queueEmptyAfterPop"), "last queued follow-up queueEmptyAfterPop"):
        raise FragmentTimingError("last queued follow-up event must empty the queue")

    return {
        "capture_id": capture_id,
        "fragment_event_count": len(fragments),
        "full_fragment_count": full_fragment_count,
        "terminal_fragment_count": terminal_fragment_count,
        "accepted_fragment_count": accepted_fragment_count,
        "queued_followup_count": len(followups),
        "queue_empty_after_pop_count": queue_empty_after_pop_count,
    }
