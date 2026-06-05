"""Validate controlled invalid-lc retail probe reports."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .demo_transcript import RETAIL_PROVENANCE_KEYS


SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
RETAIL_PROBE_TYPES = frozenset(
    {
        "controlled_retail_probe",
        "known_good_byte_fixture",
        "protocol91_demo_transcript",
        "retail_packet_capture",
    }
)
FIELD_TABLES = {
    "entityStateFields": {
        "field_count": 58,
        "source_error_prefix": "MSG_ReadDeltaEntity: invalid field count",
    },
    "playerStateFields": {
        "field_count": 58,
        "source_error_prefix": "MSG_ReadDeltaPlayerstate: invalid field count",
    },
}
RETAIL_OUTCOME_CLASSIFICATIONS = frozenset(
    {
        "accepted",
        "crash",
        "disconnect",
        "drop",
        "err_drop",
        "ignored",
        "rejected_packet",
    }
)
ARTIFACT_TYPES = frozenset(
    {
        "crash_dump",
        "packet_capture",
        "probe_transcript",
        "qconsole_log",
        "screenshot",
    }
)


class InvalidLcProbeError(ValueError):
    """Raised when an invalid-lc probe report is malformed."""


def _require_non_empty_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidLcProbeError(f"{context} must be a non-empty string")
    return value


def _require_positive_int(value: object, context: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise InvalidLcProbeError(f"{context} must be a positive integer")
    return value


def _require_sha256(value: object, context: str) -> str:
    if not isinstance(value, str) or not SHA256_HEX_RE.match(value):
        raise InvalidLcProbeError(f"{context} must be a lowercase SHA-256 hex string")
    return value


def _validate_retail_provenance(report: Mapping[str, Any]) -> None:
    provenance = report.get("provenance")
    if not isinstance(provenance, Mapping):
        raise InvalidLcProbeError("retail invalid-lc probe report requires provenance metadata")
    missing = [
        key
        for key in RETAIL_PROVENANCE_KEYS
        if not isinstance(provenance.get(key), str) or not provenance.get(key)
    ]
    if missing:
        raise InvalidLcProbeError(
            f"retail invalid-lc probe provenance missing required keys: {', '.join(missing)}"
        )
    if provenance.get("capture_type") not in RETAIL_PROBE_TYPES:
        raise InvalidLcProbeError("retail invalid-lc probe provenance capture_type is not recognized")


def _validate_artifacts(
    artifacts: object,
    *,
    require_artifact: bool,
    require_crash_dump: bool,
) -> int:
    if not isinstance(artifacts, list):
        raise InvalidLcProbeError("retail observation artifacts must be a list")
    if require_artifact and not artifacts:
        raise InvalidLcProbeError("retail invalid-lc closure requires at least one hashed artifact")

    crash_dump_count = 0
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            raise InvalidLcProbeError(f"retail artifact {index} must be an object")
        artifact_type = artifact.get("type")
        if artifact_type not in ARTIFACT_TYPES:
            raise InvalidLcProbeError(f"retail artifact {index} type is not recognized")
        if artifact_type == "crash_dump":
            crash_dump_count += 1
        _require_sha256(artifact.get("sha256"), f"retail artifact {index} sha256")
        _require_non_empty_string(artifact.get("description"), f"retail artifact {index} description")

    if require_crash_dump and crash_dump_count == 0:
        raise InvalidLcProbeError("retail crash classification requires a crash_dump artifact")
    return len(artifacts)


def validate_invalid_lc_probe_dict(
    report: Mapping[str, Any],
    *,
    require_retail_provenance: bool = False,
) -> Mapping[str, int | str]:
    """Validate a controlled retail invalid-lc probe report."""

    if report.get("schema_version") != 1:
        raise InvalidLcProbeError("invalid-lc probe schema_version must be 1")
    if report.get("format") != "quake_live_invalid_lc_probe":
        raise InvalidLcProbeError("invalid-lc probe format must be quake_live_invalid_lc_probe")

    probe_id = _require_non_empty_string(report.get("probe_id"), "invalid-lc probe_id")
    protocol = _require_positive_int(report.get("protocol"), "invalid-lc protocol")
    if protocol != 91:
        raise InvalidLcProbeError("invalid-lc probe protocol must be 91")

    malicious_input = report.get("malicious_input")
    if not isinstance(malicious_input, Mapping):
        raise InvalidLcProbeError("invalid-lc malicious_input must be an object")
    field_table = malicious_input.get("field_table")
    if field_table not in FIELD_TABLES:
        raise InvalidLcProbeError("invalid-lc field_table is not recognized")
    field_count = _require_positive_int(malicious_input.get("field_count"), "invalid-lc field_count")
    expected_count = FIELD_TABLES[field_table]["field_count"]
    if field_count != expected_count:
        raise InvalidLcProbeError(f"invalid-lc field_count must be {expected_count}")
    lc = _require_positive_int(malicious_input.get("lc"), "invalid-lc lc")
    if lc <= field_count:
        raise InvalidLcProbeError("invalid-lc lc must exceed the retail field table count")
    if "packet_sha256" in malicious_input:
        _require_sha256(malicious_input.get("packet_sha256"), "invalid-lc packet_sha256")

    retail_observation = report.get("retail_observation")
    if not isinstance(retail_observation, Mapping):
        raise InvalidLcProbeError("invalid-lc retail_observation must be an object")
    retail_classification = retail_observation.get("classification")
    if retail_classification not in RETAIL_OUTCOME_CLASSIFICATIONS:
        raise InvalidLcProbeError("invalid-lc retail classification is not recognized")
    _require_non_empty_string(retail_observation.get("observed_message"), "invalid-lc observed_message")
    artifact_count = _validate_artifacts(
        retail_observation.get("artifacts"),
        require_artifact=require_retail_provenance,
        require_crash_dump=retail_classification == "crash",
    )

    source_observation = report.get("source_observation")
    if not isinstance(source_observation, Mapping):
        raise InvalidLcProbeError("invalid-lc source_observation must be an object")
    if source_observation.get("classification") != "err_drop":
        raise InvalidLcProbeError("invalid-lc source classification must be err_drop")
    expected_error = f"{FIELD_TABLES[field_table]['source_error_prefix']} {lc}"
    if source_observation.get("error_message") != expected_error:
        raise InvalidLcProbeError("invalid-lc source error_message does not match the source guard")

    if require_retail_provenance:
        _validate_retail_provenance(report)

    return {
        "probe_id": probe_id,
        "protocol": protocol,
        "field_table": field_table,
        "field_count": field_count,
        "lc": lc,
        "retail_classification": retail_classification,
        "artifact_count": artifact_count,
    }
