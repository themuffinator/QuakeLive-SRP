from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
G_ACTIVE_PATH = REPO_ROOT / "src" / "code" / "game" / "g_active.c"


def test_scoreboard_spectators_consume_usercmd_time_without_moving() -> None:
	source = G_ACTIVE_PATH.read_text(encoding="utf-8")
	marker = "if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD ) {"
	start = source.index(marker)
	end = source.index("\n\t\t}", start)
	scoreboard_block = source[start:end]

	assert "client->ps.pm_flags |= PMF_NO_MOVE;" in scoreboard_block
	assert "SpectatorThink( ent, ucmd );" in scoreboard_block
	assert "client->ps.pm_flags &= ~PMF_NO_MOVE;" in scoreboard_block
	assert scoreboard_block.index("client->ps.pm_flags |= PMF_NO_MOVE;") < scoreboard_block.index("SpectatorThink( ent, ucmd );")
	assert scoreboard_block.index("SpectatorThink( ent, ucmd );") < scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;")
	assert scoreboard_block.index("client->ps.pm_flags &= ~PMF_NO_MOVE;") < scoreboard_block.index("return;")
