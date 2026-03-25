from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BG_PMOVE_PATH = REPO_ROOT / "src" / "code" / "game" / "bg_pmove.c"


def test_air_specific_accel_overrides_stay_scoped_to_airborne_move() -> None:
	source = BG_PMOVE_PATH.read_text(encoding="utf-8")
	match = re.search(
		r"static void PM_Accelerate\( vec3_t wishdir, float wishspeed, float accel \)\s*\{(?P<body>.*?)^\}",
		source,
		re.MULTILINE | re.DOTALL,
	)

	assert match is not None, "PM_Accelerate definition missing"

	body = match.group("body")
	assert "qboolean\tairborneMove = qfalse;" in body
	assert "pm->ps->pm_type == PM_NORMAL" in body
	assert "!pml.walking" in body
	assert "pm->waterlevel <= 1" in body
	assert "if ( airborneMove && ( pm_bunnyhop || pm_autohop ) )" in body
