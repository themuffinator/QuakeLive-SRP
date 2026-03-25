from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_pmove.c"


def test_g_pmove_reload_fallback_uses_shared_defaults() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		r"static int G_PmoveDefaultWeaponReloadTime\( weapon_t weapon \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, "G_PmoveDefaultWeaponReloadTime definition missing"

	body = match.group("body")
	assert "PM_GetDefaultSettings()" in body
	assert "defaults->weaponReloadTimes[weapon]" in body


def test_g_pmove_cache_settings_reuses_shared_extended_defaults() -> None:
	source = G_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		r"static void G_PmoveCacheSettings\( void \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, "G_PmoveCacheSettings definition missing"

	body = match.group("body")
	assert "defaults = PM_GetDefaultSettings();" in body
	assert "defaults->machinegunIronsightsScale" in body
	assert "defaults->gauntletSpeedFactor" in body
	assert "defaults->quadDamageMultiplier" in body
