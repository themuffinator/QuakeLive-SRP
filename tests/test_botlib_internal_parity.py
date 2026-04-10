from __future__ import annotations

import ctypes
import math
import re
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTLIB_INTERNAL_HARNESS = REPO_ROOT / "tests" / "botlib_internal_harness.c"
BOTLIB_AAS_SAMPLE = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_sample.c"
BOTLIB_AAS_MAIN = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_main.c"
BOTLIB_AAS_REACH = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_reach.c"
BOTLIB_AI_GOAL = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_goal.c"
BOTLIB_INTERFACE = REPO_ROOT / "src" / "code" / "botlib" / "be_interface.c"

PRESENCE_NORMAL = 2
PRESENCE_CROUCH = 4
PRT_FATAL = 4
TRAVELFLAG_NOTTEAM1 = 1 << 24
TRAVELFLAG_NOTTEAM2 = 2 << 24


class BotGoal(ctypes.Structure):
	_fields_ = [
		("origin", ctypes.c_float * 3),
		("areanum", ctypes.c_int),
		("mins", ctypes.c_float * 3),
		("maxs", ctypes.c_float * 3),
		("entitynum", ctypes.c_int),
		("number", ctypes.c_int),
		("flags", ctypes.c_int),
		("iteminfo", ctypes.c_int),
	]


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _vec3(*values: float) -> ctypes.Array[ctypes.c_float]:
	assert len(values) == 3
	return (ctypes.c_float * 3)(*values)


def _goal(number: int, origin: tuple[float, float, float]) -> BotGoal:
	goal = BotGoal()
	goal.origin[:] = origin
	goal.areanum = number + 100
	goal.mins[:] = (-15.0, -15.0, -24.0)
	goal.maxs[:] = (15.0, 15.0, 32.0)
	goal.entitynum = number + 200
	goal.number = number
	goal.flags = 1
	goal.iteminfo = number + 300
	return goal


@pytest.fixture(scope="session")
def botlib_internal_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("botlib_internal_harness_build")
	lib_path = build_dir / shared_library_name("botlib_internal_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the botlib internal harness")

	libraries = [] if compiler.is_msvc or lib_path.suffix == ".dll" else ["m"]

	compile_c_binary(
		compiler,
		[ BOTLIB_INTERNAL_HARNESS ],
		lib_path,
		libraries=libraries,
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_BotlibResetState.argtypes = []
	lib.QLR_BotlibResetState.restype = None
	lib.QLR_BotlibSetTime.argtypes = [ctypes.c_float]
	lib.QLR_BotlibSetTime.restype = None
	lib.QLR_BotlibSetReachabilitySettings.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
	lib.QLR_BotlibSetReachabilitySettings.restype = None
	lib.QLR_BotlibSetTravelFlagsForTeamValue.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibSetTravelFlagsForTeamValue.restype = None
	lib.QLR_BotlibPresenceTypeBoundingBoxFromArrays.argtypes = [
		ctypes.c_int,
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_BotlibPresenceTypeBoundingBoxFromArrays.restype = None
	lib.QLR_BotlibProjectPointOntoVector.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_BotlibProjectPointOntoVector.restype = None
	lib.QLR_BotlibFallDamageDistance.argtypes = []
	lib.QLR_BotlibFallDamageDistance.restype = ctypes.c_int
	lib.QLR_BotlibFallDelta.argtypes = [ctypes.c_float]
	lib.QLR_BotlibFallDelta.restype = ctypes.c_float
	lib.QLR_BotlibMaxJumpHeight.argtypes = [ctypes.c_float]
	lib.QLR_BotlibMaxJumpHeight.restype = ctypes.c_float
	lib.QLR_BotlibMaxJumpDistance.argtypes = [ctypes.c_float]
	lib.QLR_BotlibMaxJumpDistance.restype = ctypes.c_float
	lib.QLR_BotlibTravelFlagsForTeam.argtypes = [ctypes.c_int]
	lib.QLR_BotlibTravelFlagsForTeam.restype = ctypes.c_int
	lib.QLR_BotlibAllocGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibAllocGoalState.restype = ctypes.c_int
	lib.QLR_BotlibFreeGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibFreeGoalState.restype = None
	lib.QLR_BotlibResetGoalState.argtypes = [ctypes.c_int]
	lib.QLR_BotlibResetGoalState.restype = None
	lib.QLR_BotlibPushGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibPushGoal.restype = None
	lib.QLR_BotlibPopGoal.argtypes = [ctypes.c_int]
	lib.QLR_BotlibPopGoal.restype = None
	lib.QLR_BotlibEmptyGoalStack.argtypes = [ctypes.c_int]
	lib.QLR_BotlibEmptyGoalStack.restype = None
	lib.QLR_BotlibGetTopGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibGetTopGoal.restype = ctypes.c_int
	lib.QLR_BotlibGetSecondGoal.argtypes = [ctypes.c_int, ctypes.POINTER(BotGoal)]
	lib.QLR_BotlibGetSecondGoal.restype = ctypes.c_int
	lib.QLR_BotlibSetAvoidGoalTime.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float]
	lib.QLR_BotlibSetAvoidGoalTime.restype = None
	lib.QLR_BotlibAvoidGoalTime.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibAvoidGoalTime.restype = ctypes.c_float
	lib.QLR_BotlibRemoveFromAvoidGoals.argtypes = [ctypes.c_int, ctypes.c_int]
	lib.QLR_BotlibRemoveFromAvoidGoals.restype = None
	lib.QLR_BotlibLastPrintType.argtypes = []
	lib.QLR_BotlibLastPrintType.restype = ctypes.c_int
	lib.QLR_BotlibLastPrintMessage.argtypes = []
	lib.QLR_BotlibLastPrintMessage.restype = ctypes.c_char_p
	lib.QLR_BotlibResetState()
	return lib


def test_botlib_presence_type_bounding_box_matches_retail_boxes(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	mins = _vec3(0.0, 0.0, 0.0)
	maxs = _vec3(0.0, 0.0, 0.0)

	botlib_internal_harness.QLR_BotlibPresenceTypeBoundingBoxFromArrays(
		PRESENCE_NORMAL,
		mins,
		maxs,
	)
	assert tuple(mins) == pytest.approx((-15.0, -15.0, -24.0))
	assert tuple(maxs) == pytest.approx((15.0, 15.0, 32.0))

	botlib_internal_harness.QLR_BotlibPresenceTypeBoundingBoxFromArrays(
		PRESENCE_CROUCH,
		mins,
		maxs,
	)
	assert tuple(mins) == pytest.approx((-15.0, -15.0, -24.0))
	assert tuple(maxs) == pytest.approx((15.0, 15.0, 8.0))


def test_botlib_project_point_onto_vector_projects_orthogonally(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	projected = _vec3(0.0, 0.0, 0.0)

	botlib_internal_harness.QLR_BotlibProjectPointOntoVector(
		_vec3(5.0, 5.0, 0.0),
		_vec3(0.0, 0.0, 0.0),
		_vec3(10.0, 0.0, 0.0),
		projected,
	)

	assert tuple(projected) == pytest.approx((5.0, 0.0, 0.0))


def test_botlib_reachability_formula_helpers_match_expected_q3_physics(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	gravity = 800.0
	maxvelocity = 320.0
	maxjumpfallheight = 64.0
	jumpvel = 270.0

	botlib_internal_harness.QLR_BotlibResetState()
	botlib_internal_harness.QLR_BotlibSetReachabilitySettings(gravity, maxvelocity, maxjumpfallheight)

	expected_fall_distance = int(0.5 * gravity * ((math.sqrt(30 * 10000) / gravity) ** 2))
	expected_fall_delta = ((math.sqrt(abs(128.0) * 2 / gravity) * gravity) ** 2) * 0.0001
	expected_jump_height = 0.5 * gravity * ((jumpvel / gravity) ** 2)
	expected_jump_distance = maxvelocity * (math.sqrt(maxjumpfallheight / (0.5 * gravity)) + jumpvel / gravity)

	assert botlib_internal_harness.QLR_BotlibFallDamageDistance() == expected_fall_distance
	assert botlib_internal_harness.QLR_BotlibFallDelta(128.0) == pytest.approx(expected_fall_delta, rel=1e-6)
	assert botlib_internal_harness.QLR_BotlibMaxJumpHeight(jumpvel) == pytest.approx(expected_jump_height, rel=1e-6)
	assert botlib_internal_harness.QLR_BotlibMaxJumpDistance(jumpvel) == pytest.approx(expected_jump_distance, rel=1e-6)


def test_botlib_travel_flags_for_team_use_notteam_epair_convention(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	botlib_internal_harness.QLR_BotlibResetState()
	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(0, 0)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == 0

	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(1, 1)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == TRAVELFLAG_NOTTEAM1

	botlib_internal_harness.QLR_BotlibSetTravelFlagsForTeamValue(1, 2)
	assert botlib_internal_harness.QLR_BotlibTravelFlagsForTeam(7) == TRAVELFLAG_NOTTEAM2


def test_botlib_goal_state_stack_and_avoid_timer_lifecycle(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	top = BotGoal()
	second = BotGoal()

	botlib_internal_harness.QLR_BotlibResetState()
	handle = botlib_internal_harness.QLR_BotlibAllocGoalState(3)
	assert handle > 0

	first_goal = _goal(11, (100.0, 200.0, 300.0))
	second_goal = _goal(22, (-10.0, 40.0, 90.0))

	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(first_goal))
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 11
	assert tuple(top.origin) == pytest.approx((100.0, 200.0, 300.0))
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(second_goal))
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 22
	assert botlib_internal_harness.QLR_BotlibGetSecondGoal(handle, ctypes.byref(second)) == 1
	assert second.number == 11

	botlib_internal_harness.QLR_BotlibSetTime(10.0)
	botlib_internal_harness.QLR_BotlibSetAvoidGoalTime(handle, 77, 3.5)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(3.5, rel=1e-6)

	botlib_internal_harness.QLR_BotlibSetTime(11.25)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(2.25, rel=1e-6)

	botlib_internal_harness.QLR_BotlibRemoveFromAvoidGoals(handle, 77)
	assert botlib_internal_harness.QLR_BotlibAvoidGoalTime(handle, 77) == pytest.approx(0.0)

	botlib_internal_harness.QLR_BotlibPopGoal(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 1
	assert top.number == 11

	botlib_internal_harness.QLR_BotlibEmptyGoalStack(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0

	botlib_internal_harness.QLR_BotlibPushGoal(handle, ctypes.byref(first_goal))
	botlib_internal_harness.QLR_BotlibResetGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0

	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)


def test_botlib_goal_state_invalid_handle_messages_match_retail_strings(
	botlib_internal_harness: ctypes.CDLL,
) -> None:
	top = BotGoal()

	botlib_internal_harness.QLR_BotlibResetState()
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(0, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibLastPrintType() == PRT_FATAL
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == "goal state handle 0 out of range\n"

	handle = botlib_internal_harness.QLR_BotlibAllocGoalState(9)
	assert handle > 0
	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibGetTopGoal(handle, ctypes.byref(top)) == 0
	assert botlib_internal_harness.QLR_BotlibLastPrintType() == PRT_FATAL
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == f"invalid goal state {handle}\n"

	botlib_internal_harness.QLR_BotlibFreeGoalState(handle)
	assert botlib_internal_harness.QLR_BotlibLastPrintMessage().decode("utf-8") == f"invalid goal state handle {handle}\n"


def test_botlib_source_keeps_presence_bbox_and_jump_formula_helpers() -> None:
	aas_sample = BOTLIB_AAS_SAMPLE.read_text(encoding="utf-8")
	aas_main = BOTLIB_AAS_MAIN.read_text(encoding="utf-8")
	aas_reach = BOTLIB_AAS_REACH.read_text(encoding="utf-8")

	presence_block = _extract_function_block(
		aas_sample,
		"void AAS_PresenceTypeBoundingBox(int presencetype, vec3_t mins, vec3_t maxs)",
	)
	project_block = _extract_function_block(
		aas_main,
		"void AAS_ProjectPointOntoVector( vec3_t point, vec3_t vStart, vec3_t vEnd, vec3_t vProj )",
	)
	fall_distance_block = _extract_function_block(aas_reach, "int AAS_FallDamageDistance(void)")
	fall_delta_block = _extract_function_block(aas_reach, "float AAS_FallDelta(float distance)")
	max_jump_height_block = _extract_function_block(aas_reach, "float AAS_MaxJumpHeight(float phys_jumpvel)")
	max_jump_distance_block = _extract_function_block(aas_reach, "float AAS_MaxJumpDistance(float phys_jumpvel)")
	travel_flags_block = _extract_function_block(aas_reach, "int AAS_TravelFlagsForTeam(int ent)")

	assert "vec3_t boxmins[3] = {{0, 0, 0}, {-15, -15, -24}, {-15, -15, -24}};" in presence_block
	assert 'botimport.Print(PRT_FATAL, "AAS_PresenceTypeBoundingBox: unknown presence type\\n");' in presence_block
	assert "VectorNormalize( vec );" in project_block
	assert "VectorMA( vStart, DotProduct( pVec, vec ), vec, vProj );" in project_block
	assert "maxzvelocity = sqrt(30 * 10000);" in fall_distance_block
	assert "return 0.5 * gravity * t * t;" in fall_distance_block
	assert "t = sqrt(fabs(distance) * 2 / gravity);" in fall_delta_block
	assert "return delta * delta * 0.0001;" in fall_delta_block
	assert "return 0.5 * phys_gravity * (phys_jumpvel / phys_gravity) * (phys_jumpvel / phys_gravity);" in max_jump_height_block
	assert "t = sqrt(aassettings.rs_maxjumpfallheight / (0.5 * phys_gravity));" in max_jump_distance_block
	assert "return phys_maxvelocity * (t + phys_jumpvel / phys_gravity);" in max_jump_distance_block
	assert 'if (!AAS_IntForBSPEpairKey(ent, "bot_notteam", &notteam))' in travel_flags_block
	assert "return TRAVELFLAG_NOTTEAM1;" in travel_flags_block
	assert "return TRAVELFLAG_NOTTEAM2;" in travel_flags_block


def test_botlib_source_keeps_goal_state_stack_and_avoid_helpers() -> None:
	goal_source = BOTLIB_AI_GOAL.read_text(encoding="utf-8")

	state_from_handle_block = _extract_function_block(goal_source, "bot_goalstate_t *BotGoalStateFromHandle(int handle)")
	push_block = _extract_function_block(goal_source, "void BotPushGoal(int goalstate, bot_goal_t *goal)")
	top_block = _extract_function_block(goal_source, "int BotGetTopGoal(int goalstate, bot_goal_t *goal)")
	second_block = _extract_function_block(goal_source, "int BotGetSecondGoal(int goalstate, bot_goal_t *goal)")
	reset_block = _extract_function_block(goal_source, "void BotResetGoalState(int goalstate)")
	avoid_time_block = _extract_function_block(goal_source, "float BotAvoidGoalTime(int goalstate, int number)")
	set_avoid_time_block = _extract_function_block(goal_source, "void BotSetAvoidGoalTime(int goalstate, int number, float avoidtime)")
	alloc_block = _extract_function_block(goal_source, "int BotAllocGoalState(int client)")
	free_block = _extract_function_block(goal_source, "void BotFreeGoalState(int handle)")

	assert 'botimport.Print(PRT_FATAL, "goal state handle %d out of range\\n", handle);' in state_from_handle_block
	assert 'botimport.Print(PRT_FATAL, "invalid goal state %d\\n", handle);' in state_from_handle_block
	assert 'botimport.Print(PRT_ERROR, "goal heap overflow\\n");' in push_block
	assert "gs->goalstacktop++;" in push_block
	assert "Com_Memcpy(&gs->goalstack[gs->goalstacktop], goal, sizeof(bot_goal_t));" in push_block
	assert "if (!gs->goalstacktop) return qfalse;" in top_block
	assert "Com_Memcpy(goal, &gs->goalstack[gs->goalstacktop], sizeof(bot_goal_t));" in top_block
	assert "if (gs->goalstacktop <= 1) return qfalse;" in second_block
	assert "Com_Memset(gs->goalstack, 0, MAX_GOALSTACK * sizeof(bot_goal_t));" in reset_block
	assert "BotResetAvoidGoals(goalstate);" in reset_block
	assert "return gs->avoidgoaltimes[i] - AAS_Time();" in avoid_time_block
	assert "BotAddToAvoidGoals(gs, number, avoidtime);" in set_avoid_time_block
	assert "botgoalstates[i] = GetClearedMemory(sizeof(bot_goalstate_t));" in alloc_block
	assert "botgoalstates[i]->client = client;" in alloc_block
	assert 'botimport.Print(PRT_FATAL, "invalid goal state handle %d\\n", handle);' in free_block
	assert "BotFreeItemWeights(handle);" in free_block
	assert "botgoalstates[handle] = NULL;" in free_block


def test_botlib_interface_still_exports_aas_and_goal_owners() -> None:
	interface_source = BOTLIB_INTERFACE.read_text(encoding="utf-8")

	assert "aas->AAS_PresenceTypeBoundingBox = AAS_PresenceTypeBoundingBox;" in interface_source
	assert "aas->AAS_AreaTravelTimeToGoalArea = AAS_AreaTravelTimeToGoalArea;" in interface_source
	assert "ai->BotResetGoalState = BotResetGoalState;" in interface_source
	assert "ai->BotResetAvoidGoals = BotResetAvoidGoals;" in interface_source
	assert "ai->BotPushGoal = BotPushGoal;" in interface_source
	assert "ai->BotAllocGoalState = BotAllocGoalState;" in interface_source
	assert "ai->BotFreeGoalState = BotFreeGoalState;" in interface_source
