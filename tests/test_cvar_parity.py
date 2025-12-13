import pytest

from tools.hlil import cvar_parity


def test_hlil_cvar_parity():
    hlil_entries = cvar_parity.extract_hlil_registrations()
    source_entries = cvar_parity.extract_source_registrations()

    if not hlil_entries:
        pytest.skip("No HLIL cvar/dvar registrations found in reference dumps")

    report = cvar_parity.compare_registrations(hlil_entries, source_entries)

    errors = []
    for category, entries in report.items():
        if entries:
            errors.append(f"{category}: {sorted(entries.keys())}")

    if errors:
        pytest.fail("; ".join(errors))
