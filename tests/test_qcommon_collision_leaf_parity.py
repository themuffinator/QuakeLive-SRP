"""Focused qcommon collision-leaf parity probes for cm_patch/cm_polylib."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def collision_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("cm_collision_harness_build")
	lib_path = build_dir / shared_library_name("cm_collision_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the qcommon collision-leaf harness")

	extra_link_args: list[str] = []
	if os.name != "nt" and not compiler.is_msvc:
		extra_link_args.append("-lm")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "cm_collision_harness.c",
			REPO_ROOT / "src" / "code" / "qcommon" / "cm_polylib.c",
			REPO_ROOT / "src" / "code" / "qcommon" / "cm_patch.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code",
			REPO_ROOT / "src" / "code" / "qcommon",
			REPO_ROOT / "src" / "code" / "game",
		],
		extra_link_args=extra_link_args,
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_CM_TestLastError.argtypes = []
	lib.QLR_CM_TestLastError.restype = ctypes.c_char_p
	lib.QLR_CM_TestCapturedLog.argtypes = []
	lib.QLR_CM_TestCapturedLog.restype = ctypes.c_char_p
	lib.QLR_CM_TestCurvedPatchStats.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_CM_TestCurvedPatchStats.restype = ctypes.c_int
	lib.QLR_CM_TestFlatPatchPointTrace.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_CM_TestFlatPatchPointTrace.restype = ctypes.c_int
	lib.QLR_CM_TestFlatPatchPositionTest.argtypes = [
		ctypes.c_float,
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_CM_TestFlatPatchPositionTest.restype = ctypes.c_int
	lib.QLR_CM_TestBaseWindingClip.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_CM_TestBaseWindingClip.restype = ctypes.c_int
	lib.QLR_CM_TestConvexHullMerge.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_float),
	]
	lib.QLR_CM_TestConvexHullMerge.restype = ctypes.c_int
	lib.QLR_CM_TestCheckFacetPlane.argtypes = [
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_float),
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_int),
	]
	lib.QLR_CM_TestCheckFacetPlane.restype = ctypes.c_int
	return lib


def _assert_success(lib: ctypes.CDLL, result: int) -> None:
	assert result == 1, lib.QLR_CM_TestLastError().decode("utf-8", errors="replace")


def test_curved_patch_generation_reports_expected_planes_facets_and_bounds(
	collision_harness: ctypes.CDLL,
) -> None:
	num_planes = ctypes.c_int()
	num_facets = ctypes.c_int()
	bounds = (ctypes.c_float * 6)()

	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestCurvedPatchStats(
			ctypes.byref(num_planes), ctypes.byref(num_facets), bounds
		),
	)

	assert num_planes.value == 36
	assert num_facets.value == 4
	assert list(bounds) == pytest.approx([-17.0, -17.0, -1.0, 17.0, 17.0, 33.0])


def test_flat_patch_point_trace_matches_surface_clip_epsilon(
	collision_harness: ctypes.CDLL,
) -> None:
	fraction = ctypes.c_float()
	normal = (ctypes.c_float * 3)()
	dist = ctypes.c_float()

	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestFlatPatchPointTrace(
			ctypes.byref(fraction), normal, ctypes.byref(dist)
		),
	)

	assert fraction.value == pytest.approx((32.0 - 0.125) / 64.0, rel=1e-6)
	assert list(normal) == pytest.approx([0.0, 0.0, -1.0], rel=1e-6)
	assert dist.value == pytest.approx(0.0, abs=1e-6)


def test_flat_patch_position_test_detects_box_overlap(
	collision_harness: ctypes.CDLL,
) -> None:
	inside_hit = ctypes.c_int()
	outside_hit = ctypes.c_int()

	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestFlatPatchPositionTest(1.0, ctypes.byref(inside_hit)),
	)
	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestFlatPatchPositionTest(5.0, ctypes.byref(outside_hit)),
	)

	assert inside_hit.value == 1
	assert outside_hit.value == 0


def test_base_winding_clip_matches_expected_mark_fragment_style_bounds(
	collision_harness: ctypes.CDLL,
) -> None:
	area = ctypes.c_float()
	num_points = ctypes.c_int()
	bounds = (ctypes.c_float * 6)()

	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestBaseWindingClip(
			ctypes.byref(area), ctypes.byref(num_points), bounds
		),
	)

	assert num_points.value == 4
	assert area.value == pytest.approx(32.0, rel=1e-6)
	assert list(bounds) == pytest.approx([-4.0, -2.0, 0.0, 4.0, 2.0, 0.0], abs=1e-5)


def test_check_facet_plane_reports_expected_enter_fraction(
	collision_harness: ctypes.CDLL,
) -> None:
	enter_frac = ctypes.c_float()
	leave_frac = ctypes.c_float()
	hit = ctypes.c_int()
	result = ctypes.c_int()

	_assert_success(
		collision_harness,
		collision_harness.QLR_CM_TestCheckFacetPlane(
			ctypes.byref(enter_frac),
			ctypes.byref(leave_frac),
			ctypes.byref(hit),
			ctypes.byref(result),
		),
	)

	assert result.value == 1
	assert hit.value == 1
	assert enter_frac.value == pytest.approx((32.0 - 0.125) / 64.0, rel=1e-6)
	assert leave_frac.value == pytest.approx(1.0, abs=1e-6)
