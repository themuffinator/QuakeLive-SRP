from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = REPO_ROOT / "src" / "code" / "game"


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_ready_latch_declared_and_helpers_present() -> None:
    local_h = _read("src/code/game/g_local.h")
    client_c = _read("src/code/game/g_client.c")

    assert "readyUpLatch" in local_h
    assert "G_ClientIsReady( const gclient_t *client )" in client_c
    assert "G_SetClientReadyState( gclient_t *client, qboolean ready )" in client_c
    assert "G_SyncClientReadyState( gclient_t *client )" in client_c


def test_readyup_commands_use_latch_and_retail_gate_strings() -> None:
    cmds_c = _read("src/code/game/g_cmds.c")
    main_c = _read("src/code/game/g_main.c")

    assert "Cannot ready up until more players are present." in cmds_c
    assert "Players cannot ready up until both teams are present." in cmds_c
    assert "Players cannot ready up until both teams are fully present." in cmds_c
    assert "G_ClientIsReady( ent->client )" in cmds_c
    assert "G_SetClientReadyState( ent->client, qtrue );" in cmds_c
    assert "G_SetClientReadyState( ent->client, qfalse );" in cmds_c
    assert "G_ClientIsReady( cl )" in main_c


def test_onsameteam_preserves_matching_spectators() -> None:
    team_c = _read("src/code/game/g_team.c")

    assert "team1 == TEAM_SPECTATOR && team2 == TEAM_SPECTATOR" in team_c
