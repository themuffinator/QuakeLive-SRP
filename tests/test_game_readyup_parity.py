from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = REPO_ROOT / "src" / "code" / "game"


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
    start = source.rindex(marker)
    brace_start = source.index("{", start)
    depth = 0

    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]

    raise AssertionError(f"Unbalanced block for marker: {marker}")


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


def test_readyup_team_presence_truth_table_matches_retail_mapping_notes() -> None:
    cmds_c = _read("src/code/game/g_cmds.c")
    helper_block = _block_from_marker(cmds_c, "static qboolean G_GametypeRequiresBothTeamsPresent")

    for expected in (
        "case GT_TEAM:",
        "case GT_CLAN_ARENA:",
        "case GT_CTF:",
        "case GT_1FCTF:",
        "case GT_OBELISK:",
        "case GT_HARVESTER:",
        "case GT_FREEZE:",
        "case GT_DOMINATION:",
        "case GT_ATTACK_DEFEND:",
    ):
        assert expected in helper_block

    for unexpected in (
        "case GT_FFA:",
        "case GT_TOURNAMENT:",
        "case GT_RACE:",
        "case GT_RED_ROVER:",
    ):
        assert unexpected not in helper_block

    assert "return qtrue;" in helper_block
    assert "return qfalse;" in helper_block


def test_onsameteam_preserves_matching_spectators() -> None:
    team_c = _read("src/code/game/g_team.c")

    assert "team1 == TEAM_SPECTATOR && team2 == TEAM_SPECTATOR" in team_c
