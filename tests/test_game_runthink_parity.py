from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_runthink_services_retail_runframe_callback() -> None:
	local_h = _read("src/code/game/g_local.h")
	main_c = _read("src/code/game/g_main.c")

	assert "(*runFrame)(gentity_t *self, float thinktime)" in local_h
	assert "if ( ent->runFrame ) {" in main_c
	assert "ent->runFrame( ent, thinktime );" in main_c


def test_trigger_push_uses_runframe_aim_refresh() -> None:
	trigger_c = _read("src/code/game/g_trigger.c")

	assert "static void AimAtTargetRunFrame( gentity_t *self, float thinktime )" in trigger_c
	assert "self->runFrame = AimAtTargetRunFrame;" in trigger_c
	assert "self->think = AimAtTarget;" in trigger_c
