from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))



from tools.tests.match_sim.harness import run_from_file

SCENARIO = Path(__file__).resolve().parent.parent / "tools" / "tests" / "match_sim" / "special_modes_demo.json"


def _collect_events(scenario: Path):
    result = run_from_file(scenario, seed=8080)
    events = []
    for frame in result.frames:
        events.extend(frame.events)
    return events


def test_special_mode_metadata_emits_round_transitions() -> None:
    events = _collect_events(SCENARIO)
    round_states = [event["state"] for event in events if event.get("type") == "round_state"]
    assert round_states[:3] == ["warmup", "live", "complete"]


def test_freeze_tick_and_thaw_events_present() -> None:
    events = _collect_events(SCENARIO)
    freeze_events = [event for event in events if event.get("type") == "freeze_tick"]
    thaw_events = [event for event in events if event.get("type") == "thaw"]
    assert freeze_events, "Freeze tick events should be emitted"
    assert thaw_events == [{"type": "thaw", "bot": "athena"}]


def test_infected_and_respawn_markers_are_generated() -> None:
    events = _collect_events(SCENARIO)
    infected = [event for event in events if event.get("type") == "infected_bonus"]
    respawn = [event for event in events if event.get("type") == "respawn_gate"]
    assert infected == [{"type": "infected_bonus", "bonus": 2}]
    assert respawn == [{"type": "respawn_gate", "interval": 1750}]
