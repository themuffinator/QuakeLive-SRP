from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

ALIASES_PATH = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
ROUND_58_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_58.md"
ROUND_59_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "quakelive_steam_mapping_round_59.md"
QSHARED_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "qshared-retail-helper-parity-audit-2026-04-17.md"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "qcommon-validation.yml"
BUILD_PIPELINE_PATH = REPO_ROOT / "docs" / "build-pipeline.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
QSHARED_H_PATH = REPO_ROOT / "src" / "code" / "game" / "q_shared.h"
QSHARED_C_PATH = REPO_ROOT / "src" / "code" / "game" / "q_shared.c"
QMATH_C_PATH = REPO_ROOT / "src" / "code" / "game" / "q_math.c"


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def test_qshared_alias_ledger_covers_recovered_math_and_info_helpers() -> None:
	aliases = _read_text(ALIASES_PATH)
	round_58 = _read_text(ROUND_58_PATH)
	round_59 = _read_text(ROUND_59_PATH)

	assert '"sub_4D7990": "Q_random"' in aliases
	assert '"sub_4D7D10": "Q_rsqrt"' in aliases
	assert '"sub_4D7D60": "Q_fabs"' in aliases
	assert '"sub_4D8280": "Q_log2"' in aliases
	assert '"sub_4D8940": "Com_Clamp"' in aliases
	assert '"sub_4D8F40": "Q_strncpyz"' in aliases
	assert '"sub_4D9160": "Com_sprintf"' in aliases
	assert '"sub_4D9260": "Info_ValueForKey"' in aliases
	assert '"sub_4D9380": "Info_NextPair"' in aliases
	assert '"sub_4D9500": "Info_RemoveKey_Big"' in aliases
	assert '"sub_4D97E0": "Info_SetValueForKey_Big"' in aliases

	assert "- `sub_4D7990 -> Q_random`" in round_58
	assert "- `sub_4D7D10 -> Q_rsqrt`" in round_58
	assert "- `sub_4D7D60 -> Q_fabs`" in round_58
	assert "- `sub_4D8280 -> Q_log2`" in round_58
	assert "- `sub_4D8940 -> Com_Clamp`" in round_58
	assert "- `sub_4D9160 -> Com_sprintf`" in round_58

	assert "- `sub_4D9260 -> Info_ValueForKey`" in round_59
	assert "- `sub_4D9380 -> Info_NextPair`" in round_59
	assert "- `sub_4D9500 -> Info_RemoveKey_Big`" in round_59
	assert "- `sub_4D97E0 -> Info_SetValueForKey_Big`" in round_59


def test_qshared_header_matches_recovered_helper_names_and_swap_contracts() -> None:
	q_shared_h = _read_text(QSHARED_H_PATH)

	assert "void Info_RemoveKey_Big( char *s, const char *key );" in q_shared_h
	assert "Info_RemoveKey_big" not in q_shared_h

	assert "static ID_INLINE int BigLong(int l) { return LongSwap(l); }" in q_shared_h
	assert "static ID_INLINE float BigFloat(const float *l) { return FloatSwap(l); }" in q_shared_h
	assert "static int BigLong(int l) { return LongSwap(l); }" in q_shared_h
	assert "static float BigFloat(const float *l) { return FloatSwap(l); }" in q_shared_h


def test_qshared_source_retains_recovered_math_and_info_helper_bodies() -> None:
	q_shared_c = _read_text(QSHARED_C_PATH)
	q_math_c = _read_text(QMATH_C_PATH)

	assert "float\tQ_random( int *seed ) {" in q_math_c
	assert "*seed = (69069 * *seed + 1);" in q_math_c
	assert "float Q_rsqrt( float number )" in q_math_c
	assert "0x5f3759df" in q_math_c
	assert "float Q_fabs( float f ) {" in q_math_c
	assert "int Q_log2( int val ) {" in q_math_c
	assert "float Com_Clamp( float min, float max, float value ) {" in q_shared_c
	assert 'Com_Error( ERR_DROP, "Info_RemoveKey_Big: oversize infostring" );' in q_shared_c
	assert "void Info_RemoveKey_Big( char *s, const char *key ) {" in q_shared_c
	assert "void Info_SetValueForKey_Big( char *s, const char *key, const char *value ) {" in q_shared_c
	assert "Info_RemoveKey_Big (s, key);" in q_shared_c
	assert "int QDECL Com_sprintf( char *dest, int size, const char *fmt, ...)" in q_shared_c


def test_qshared_audit_and_validation_lane_track_the_shared_helper_surface() -> None:
	audit = _read_text(QSHARED_AUDIT_PATH)
	workflow = _read_text(WORKFLOW_PATH)
	build_pipeline = _read_text(BUILD_PIPELINE_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)

	assert "src/code/game/q_shared.c" in audit
	assert "src/code/game/q_shared.h" in audit
	assert "src/code/game/q_math.c" in audit
	assert "QS-G01" in audit
	assert "QS-G02" in audit
	assert "**Parity estimate:** **before 99% -> after 100%**" in audit

	assert "tests/test_qshared_retail_parity.py" in workflow
	assert "src/code/game/q_math.c" in workflow
	assert "qshared-retail-helper-parity-audit-2026-04-17.md" in workflow

	assert "tests/test_qshared_retail_parity.py" in build_pipeline
	assert "tests/test_qshared_retail_parity.py" in windows_native_pipeline
