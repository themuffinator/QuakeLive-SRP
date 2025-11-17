"""Test coverage for the deterministic match simulation harness."""

from __future__ import annotations

from pathlib import Path
import copy
import sys
from typing import Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.tests.match_sim.harness import MatchHarness, load_config, run_from_file

SCENARIO = REPO_ROOT / "tools" / "tests" / "match_sim" / "sample_scenario.json"
SCENARIO_DIR = REPO_ROOT / "tools" / "tests" / "match_sim"
ALL_SCENARIOS = [
    SCENARIO,
    SCENARIO_DIR / "overtime_scenario.json",
    SCENARIO_DIR / "complex_loadouts.json",
    SCENARIO_DIR / "factory_cvars.json",
]


def test_run_from_file_is_deterministic(tmp_path) -> None:
    """Running the same scenario with the same seed yields identical timelines."""

    result_a = run_from_file(SCENARIO, seed=4242)
    result_b = run_from_file(SCENARIO, seed=4242)

    assert result_a.config.seed == 4242
    assert result_b.config.seed == 4242
    assert result_a.to_json(indent=None) == result_b.to_json(indent=None)


def test_seed_override_changes_randomised_outputs() -> None:
    """Using different seeds should influence randomised spawn and script values."""

    config_default = load_config(SCENARIO)
    default_result = MatchHarness(config_default).run()

    config_override = load_config(SCENARIO)
    override_result = MatchHarness(config_override, seed=9090).run()

    assert default_result.config.seed == 2024
    assert override_result.config.seed == 9090

    # Randomised command parameters should diverge when the seed is overridden.
    default_move_event = default_result.frames[2].events[0]
    override_move_event = override_result.frames[2].events[0]

    assert default_move_event["bot"] == "anarki"
    assert override_move_event["bot"] == "anarki"

    default_direction = default_move_event["details"]["velocity"]
    override_direction = override_move_event["details"]["velocity"]

    assert default_direction != override_direction
    assert default_result.to_json(indent=None) != override_result.to_json(indent=None)


@pytest.mark.parametrize("scenario_path", ALL_SCENARIOS, ids=[path.stem for path in ALL_SCENARIOS])
def test_all_scenarios_produce_frames(scenario_path: Path) -> None:
    """Ensure every shipped scenario runs without errors and emits timeline frames."""

    result = run_from_file(scenario_path, seed=1337)

    assert result.frames, "Scenario should produce at least one frame"
    assert result.config.map
    assert result.config.metadata is not None

def _configure_factory_config(**overrides) -> MatchHarness:
    config = load_config(SCENARIO_DIR / "factory_cvars.json")
    factory_meta = copy.deepcopy(config.metadata.get("factory", {}))
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(factory_meta.get(key), Mapping):
            merged = copy.deepcopy(factory_meta.get(key))
            merged.update(value)
            factory_meta[key] = merged
        else:
            factory_meta[key] = value
    config.metadata["factory"] = factory_meta
    return MatchHarness(config, seed=config.seed)


@pytest.mark.parametrize(
    "active_loadout, expected_visor, expected_anarki",
    [
        (
            "practice",
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
            {"ammo": {"machinegun": 100.0, "lightning": 75.0}, "inventory": {"armor": 25, "gauntlet": 1}},
        ),
        (
            "tournament",
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
            {"ammo": {"rocket": 15.0, "rail": 5.0}, "inventory": {"armor": 50, "mega": 1}},
        ),
    ],
    ids=["practice-default", "tournament-default"],
)
def test_factory_loadout_toggle_updates_inventory(
    active_loadout: str, expected_visor: dict, expected_anarki: dict
) -> None:
    harness = _configure_factory_config(active_loadout=active_loadout)
    result = harness.run()

    first_frame = result.frames[0]
    visor_state = first_frame.bots["visor"]
    anarki_state = first_frame.bots["anarki"]

    assert visor_state["ammo"] == expected_visor["ammo"]
    assert visor_state["inventory"] == expected_visor["inventory"]

    assert anarki_state["ammo"] == expected_anarki["ammo"]
    assert anarki_state["inventory"] == expected_anarki["inventory"]


def test_factory_spawn_delays_emit_client_spawn_events() -> None:
    harness = _configure_factory_config()
    result = harness.run()

    spawn_events = [
        (event["bot"], event["details"]["warmup"], event["time"])
        for frame in result.frames
        for event in frame.events
        if event["action"] == "client_spawn"
    ]

    assert spawn_events == [
        ("visor", True, 0.5),
        ("anarki", True, 1.0),
        ("visor", False, 2.5),
        ("anarki", False, 2.7),
    ]


def _iter_spawn_events(result):
    for frame in result.frames:
        for event in frame.events:
            if event["action"] == "client_spawn":
                yield frame, event


def test_spawn_queue_limit_forces_immediate_spawns() -> None:
    harness = _configure_factory_config(spawn_queue={"max_deferred_spawns": 1})
    result = harness.run()

    spawn_events = [event for _, event in _iter_spawn_events(result)]
    immediate = [event for event in spawn_events if event["details"].get("queue_status") == "immediate"]

    assert immediate, "At least one spawn should bypass the queue when the limit is reached"
    assert all(event["details"].get("queue_limit") == 1 for event in immediate)
    assert any(abs(event["details"].get("delay", 0.0)) < 1e-6 for event in immediate)


def test_spawn_grant_items_populate_state_and_events() -> None:
    harness = _configure_factory_config(
        grant_items_on_spawn=[
            "rocket_launcher",
            {"inventory": {"mega": 1}, "ammo": {"rocket": 5}, "label": "factory_grant"},
        ]
    )
    result = harness.run()

    grant_frame = None
    grant_event = None
    for frame, event in _iter_spawn_events(result):
        if event["details"].get("grants"):
            grant_frame = frame
            grant_event = event
            break

    assert grant_event is not None, "Spawn events should record granted items"

    grants = grant_event["details"]["grants"]
    assert any("inventory" in entry for entry in grants)
    assert any(entry.get("label") == "factory_grant" for entry in grants)

    bot_state = grant_frame.bots[grant_event["bot"]]
    assert bot_state["inventory"].get("rocket_launcher") >= 1
    assert bot_state["inventory"].get("mega") >= 1
    assert bot_state["ammo"].get("rocket") >= 5.0


def _summarise_item_events(result) -> str:
    lines: list[str] = []
    for frame in result.frames:
        for event in frame.events:
            action = event["action"]
            if action not in {"drop_item", "item_respawn", "item_return"}:
                continue
            bot = event["bot"]
            details = event["details"]
            item = details.get("item")
            if action == "drop_item":
                lines.append(
                    f"{event['time']:.3f} {bot} drop {item} status={details.get('status')} bounce={details.get('bounce')}"
                )
            elif action == "item_respawn":
                lines.append(f"{event['time']:.3f} {bot} respawn {item}")
            elif action == "item_return":
                lines.append(f"{event['time']:.3f} {bot} return {item}")
    return "\n".join(lines)


def _read_expectation(name: str) -> str:
    expectation_path = REPO_ROOT / "tests" / "expectations" / name
    return expectation_path.read_text(encoding="utf-8").strip()


def test_factory_item_flags_control_drop_behaviour(tmp_path: Path) -> None:
    baseline = _configure_factory_config()
    allow_bounce = _configure_factory_config(items={"allow_bounce": True})
    no_drops = _configure_factory_config(items={"allow_drops": False})

    results = [baseline.run(), allow_bounce.run(), no_drops.run()]
    summaries = [
        _summarise_item_events(result)
        for result in results
    ]

    combined = "\n---\n".join(summaries)
    expected = _read_expectation("match_sim_factory_items.expect")
    if combined.strip() != expected.strip():
        output_path = tmp_path / "factory_items.actual"
        output_path.write_text(combined, encoding="utf-8")
        pytest.fail(
            "Item drop expectations diverged. "
            f"Captured summary written to {output_path}"
        )
