from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "audit-retail-dependencies.ps1"
RETAIL_TOOLCHAIN_AUDIT_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "audit-retail-toolchain.ps1"
VALIDATE_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "validate-windows-native.ps1"
ASSERT_DLL_EXPORTS_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "assert-dll-exports.ps1"
RETAIL_DEPENDENCY_DOC_PATH = REPO_ROOT / "docs" / "platform" / "retail-dependencies.md"
TOOLCHAIN_MATRIX_PATH = REPO_ROOT / "docs" / "platform" / "toolchain-matrix.md"
WINDOWS_BUILD_DOC_PATH = REPO_ROOT / "docs" / "build" / "windows.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
WINDOWS_RUNTIME_GUIDE_PATH = REPO_ROOT / "docs" / "platform" / "windows-32bit-runtime.md"
TOOLCHAIN_CI_PATH = REPO_ROOT / "docs" / "toolchain-ci.md"
NIGHTLY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "nightly-build.yml"
INSTALL_TOOLSET_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "install-vs-toolset.ps1"
VERIFY_TOOLSET_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "verify-vs-toolchain.ps1"
BUILD_WINDOWS_DLLS_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "build-windows-dlls.ps1"
NIGHTLY_BUILD_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "nightly_build.py"
QUAKELIVE_SOLUTION_PATH = REPO_ROOT / "src" / "code" / "quakelive.sln"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
PLATFORM_CONFIG_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_config.h"
PLATFORM_SERVICES_PATH = REPO_ROOT / "src" / "common" / "platform" / "platform_services.c"
SV_CLIENT_PATH = REPO_ROOT / "src" / "code" / "server" / "sv_client.c"
UI_OWNERDRAW_INDEX_PATH = REPO_ROOT / "docs" / "reverse-engineering" / "ui-ownerdrawtype-parity-index.md"
REPO_WIDE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "repo-wide-parity-audit-2026-04-21.md"
)
OUTSTANDING_WORK_CHECKLIST_PATH = (
	REPO_ROOT / "docs" / "plans" / "2026-06-05-outstanding-work-checklist.md"
)
WINDOWS_NATIVE_PREFLIGHT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "windows-native-validation-preflight-2026-06-05.json"
)
WINDOWS_NATIVE_PREFLIGHT_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "windows-native-validation-preflight-2026-06-05.md"
)
RUNTIME_BUILD_EVIDENCE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "runtime-build-evidence-refresh-2026-06-05.json"
)
RUNTIME_BUILD_EVIDENCE_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "runtime-build-evidence-refresh-2026-06-05.md"
)
RETAIL_MODULE_LATEST_EVIDENCE_PATH = (
	REPO_ROOT / "artifacts" / "module_validation" / "logs" / "retail_module_runtime_evidence_latest.json"
)
RESIDUAL_POLICY_SPOT_CHECK_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "residual-policy-spot-check-2026-06-05.json"
)
RESIDUAL_POLICY_SPOT_CHECK_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "residual-policy-spot-check-2026-06-05.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
	return json.loads(_read_text(path))


def test_retail_dependency_runtime_stage_is_wired_and_documented() -> None:
	audit_script = _read_text(AUDIT_SCRIPT_PATH)
	validate_script = _read_text(VALIDATE_SCRIPT_PATH)
	retail_dependency_doc = _read_text(RETAIL_DEPENDENCY_DOC_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)
	windows_build_doc = _read_text(WINDOWS_BUILD_DOC_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	windows_runtime_guide = _read_text(WINDOWS_RUNTIME_GUIDE_PATH)
	toolchain_ci = _read_text(TOOLCHAIN_CI_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)

	assert "[string]$RuntimeRoot = ''" in audit_script
	assert "[switch]$SkipSteamInstall" in audit_script
	assert "Expected retail DLLs missing from ${Label}:" in audit_script
	assert "Extra DLLs present in ${Label} but absent from the reference retail payload:" in audit_script
	assert "Retail-hash-optional DLL slots:" in audit_script
	assert "'baseq3\\cgamex86.dll'" in audit_script
	assert "'baseq3\\qagamex86.dll'" in audit_script
	assert "'baseq3\\uix86.dll'" in audit_script
	assert 'throw \'No audit target was supplied. Provide -RuntimeRoot when using -SkipSteamInstall.\'' in audit_script

	assert "function Initialize-RetailRuntimeStage" in validate_script
	assert 'build\\win32\\$ConfigurationName\\retail-runtime' in validate_script
	assert "& $dependencyAudit -RepoRoot $RepoRoot -RuntimeRoot $retailRuntimeRoot -SkipSteamInstall -Strict:$true" in validate_script
	assert 'Write-Host "Validated staged retail runtime root: $retailRuntimeRoot"' in validate_script
	assert 'Write-Host "Retail launcher payload is not fully staged under' in validate_script
	assert 'Write-Warning "Retail launcher payload is not fully staged under' not in validate_script

	assert "build\\win32\\<Config>\\retail-runtime\\" in retail_dependency_doc
	assert "build\\win32\\<Config>\\bin\\" in retail_dependency_doc
	assert "strict retail payload boundary" in retail_dependency_doc
	assert "pwsh tools\\ci\\audit-retail-dependencies.ps1 -RuntimeRoot build\\win32\\Release\\retail-runtime -SkipSteamInstall -Strict" in retail_dependency_doc

	assert "retail-runtime" in toolchain_matrix
	assert "audit-retail-dependencies.ps1 -RuntimeRoot build\\win32\\Release\\retail-runtime -SkipSteamInstall -Strict" in toolchain_matrix
	assert "Expand local/runtime guards so parity builds fail fast when extra non-retail runtime DLLs are introduced alongside the launcher payload." not in toolchain_matrix

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in windows_build_doc
	assert "retail-runtime" in windows_build_doc

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in windows_native_pipeline
	assert "build\\win32\\<Config>\\retail-runtime\\" in windows_native_pipeline

	assert "build\\win32\\Release\\retail-runtime" in windows_runtime_guide

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in toolchain_ci
	assert "retail-runtime" in toolchain_ci

	assert "### Task A6f: Add a strict staged retail-runtime DLL audit for native Windows validation [COMPLETED]" in implementation_plan
	assert "The retail native validation lane now also stages" in audit
	assert "The retail native validation lane now also stages" in repo_wide_audit


def test_hosted_nightly_uses_preinstalled_vs2022_toolset() -> None:
	nightly_workflow = _read_text(NIGHTLY_WORKFLOW_PATH)
	install_toolset = _read_text(INSTALL_TOOLSET_SCRIPT_PATH)
	verify_toolset = _read_text(VERIFY_TOOLSET_SCRIPT_PATH)
	validate_script = _read_text(VALIDATE_SCRIPT_PATH)
	build_windows_dlls = _read_text(BUILD_WINDOWS_DLLS_SCRIPT_PATH)
	nightly_build = _read_text(NIGHTLY_BUILD_SCRIPT_PATH)
	quakelive_solution = _read_text(QUAKELIVE_SOLUTION_PATH)
	toolchain_ci = _read_text(TOOLCHAIN_CI_PATH)

	assert "NIGHTLY_PLATFORM_TOOLSET: v143" in nightly_workflow
	assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in nightly_workflow
	assert "NODE_NO_WARNINGS" not in nightly_workflow
	assert "actions/checkout@v6" in nightly_workflow
	assert "actions/setup-python@v6" in nightly_workflow
	assert "actions/upload-artifact@v7" in nightly_workflow
	assert "actions/download-artifact@v8" in nightly_workflow
	assert "actions/checkout@v4" not in nightly_workflow
	assert "actions/setup-python@v5" not in nightly_workflow
	assert "actions/upload-artifact@v4" not in nightly_workflow
	assert "actions/download-artifact@v4" not in nightly_workflow
	assert "Prepare nightly metadata" in nightly_workflow
	assert "QL_POSIX_PACKAGE_VERSION" in nightly_workflow
	assert "-DisableOptionalCodecs" in nightly_workflow
	assert "Publish Windows build logs" in nightly_workflow
	assert "Publish nightly GitHub release" in nightly_workflow
	assert "contents: write" in nightly_workflow
	assert "release_tag: ${{ steps.version.outputs.release_tag }}" in nightly_workflow
	assert "release_title: ${{ steps.version.outputs.release_title }}" in nightly_workflow
	assert "--asset-output-root artifacts/nightly/release-assets" in nightly_workflow
	assert "gh release create" in nightly_workflow
	assert "gh release upload" in nightly_workflow
	assert "--latest" in nightly_workflow
	assert "--latest=false" not in nightly_workflow
	assert "--prerelease" not in nightly_workflow
	assert "prerelease=false" in nightly_workflow
	assert "nightly-release-manifest.json" in nightly_workflow
	assert "SHA256SUMS.txt" in nightly_workflow
	assert "release-notes.md" in nightly_workflow
	assert "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" in install_toolset
	assert "[ValidateSet('v100', 'v141', 'v143')]" in install_toolset
	assert "'v143' { return 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }" in install_toolset

	assert "[ValidateSet('v100', 'v141', 'v143')]" in verify_toolset
	assert "DisplayName = 'Visual Studio 2022 (v143)'" in verify_toolset
	assert "'v143' {" in verify_toolset
	assert "ComponentId = 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64'" in verify_toolset

	assert "[string]$PlatformToolset = 'v143'" in validate_script
	assert "[string]$ProjectToolset = 'v141'" in validate_script
	assert "[switch]$DisableOptionalCodecs" in validate_script
	assert "-DisableOptionalCodecs:$DisableOptionalCodecs" in validate_script
	assert "'v143' { 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }" in build_windows_dlls
	assert "$PlatformToolset -in @('v141', 'v143')" in build_windows_dlls
	assert "[string]$BuildLogRoot = ''" in build_windows_dlls
	assert "'/p:QLEnableOgg=0'" in build_windows_dlls
	assert "'/p:QLEnablePng=0'" in build_windows_dlls
	assert "'/p:QLEnableFreeType=0'" in build_windows_dlls
	assert "msbuild-${safeConfiguration}-${safePlatform}-${safeToolset}.log" in build_windows_dlls
	assert 'package.add_argument("--toolset", default="v143")' in nightly_build
	assert 'subparsers.add_parser("release-manifest"' in nightly_build
	assert 'subparsers.add_parser("release-notes"' in nightly_build
	assert "RELEASE_PACKAGE_SUFFIXES" in nightly_build
	assert "def is_release_package" in nightly_build
	assert "def stage_release_asset" in nightly_build
	assert "{A8EAC38E-C7DA-42F8-811D-77FD092B9D19}.Release|x86.Build.0 = Release|Win32" in quakelive_solution
	assert "{94DFC7CA-ABB9-47A9-8F5A-372FCD4F47A7}.Release|x86.Build.0 = Release|Win32" in quakelive_solution
	assert "{C7006958-AB86-451D-BAAD-73F4B5DFBBD5}.Release|x86.Build.0 = Release|Win32" in quakelive_solution
	assert "{CE8AF870-8957-407E-BDBC-3E022FAA8BB6}.Release|x86.Build.0 = Release|Win32" in quakelive_solution
	assert "build/re/windows" not in nightly_build
	assert "clean-room" not in nightly_build
	assert '"nightly-release-manifest.json"' in nightly_build
	assert '"SHA256SUMS.txt"' in nightly_build
	assert "hosted-compatible `v143` toolset" in toolchain_ci


def test_a6_windows_native_validation_preflight_blocker_is_captured() -> None:
	toolchain_audit = _read_text(RETAIL_TOOLCHAIN_AUDIT_SCRIPT_PATH)
	validate_script = _read_text(VALIDATE_SCRIPT_PATH)
	preflight = _read_json(WINDOWS_NATIVE_PREFLIGHT_PATH)
	preflight_note = _read_text(WINDOWS_NATIVE_PREFLIGHT_NOTE_PATH)
	outstanding_checklist = _read_text(OUTSTANDING_WORK_CHECKLIST_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)

	assert "[string]$RepoRoot = ''" in toolchain_audit
	assert "$ToolchainAuditScriptRoot = $PSScriptRoot" in toolchain_audit
	assert "Unable to determine repository root. Provide -RepoRoot explicitly." in toolchain_audit
	assert "[string]$RepoRoot = ''" in validate_script
	assert "$NativeValidationScriptRoot = $PSScriptRoot" in validate_script
	assert "Join-Path $NativeValidationScriptRoot 'audit-retail-toolchain.ps1'" in validate_script
	assert "Join-Path $NativeValidationScriptRoot 'build-windows-dlls.ps1'" in validate_script

	assert preflight["schema_version"] == 1
	assert preflight["last_updated"] == "2026-06-05"
	assert preflight["task"] == "A6"
	assert preflight["status"] == "blocked_before_build"
	assert preflight["runtime_launch_required"] is False
	assert preflight["game_launch_required"] is False
	assert preflight["tooling_fix"]["changes_strict_retail_target"] is False
	assert preflight["tooling_fix"]["files"] == [
		"tools/ci/audit-retail-toolchain.ps1",
		"tools/ci/validate-windows-native.ps1",
	]

	commands = {command["id"]: command for command in preflight["commands"]}
	assert set(commands) == {
		"strict_retail_toolchain_audit",
		"retail_native_validation_wrapper",
	}
	assert commands["strict_retail_toolchain_audit"]["exit_code"] == 1
	assert commands["retail_native_validation_wrapper"]["exit_code"] == 1
	assert "expected 'v100', found 'v141'" in commands["strict_retail_toolchain_audit"]["failure"]
	assert "src/code/game/qagamex86.vcxproj uses PlatformToolset='v141'" in commands["retail_native_validation_wrapper"]["verified_before_failure"]

	blocker = preflight["blockers"][0]
	assert blocker["id"] == "strict_retail_project_toolset_mismatch"
	assert blocker["expected"] == "v100"
	assert blocker["actual"] == "v141"
	assert blocker["first_failing_project"] == "src/code/quakelive_steam.vcxproj"
	assert blocker["effect"].startswith("Strict retail native validation stops before")
	assert preflight["checklist_effect"]["preflight_blocker_captured"] is True
	assert preflight["checklist_effect"]["native_windows_build_validation_closed"] is False
	assert preflight["checklist_effect"]["latest_runtime_alias_promotion_allowed"] is False
	assert preflight["parity_estimate"]["repo_wide_before_percent"] == 99
	assert preflight["parity_estimate"]["repo_wide_after_percent"] == 99

	assert "Status: captured strict-retail blocker; superseded for Task A6 by" in preflight_note
	assert "Both commands now infer the repository root from their script path" in preflight_note
	assert "No strict retail native build, staged runtime dependency audit, export audit" in preflight_note
	assert "strict VC10 staged-runtime evidence cannot be claimed" in preflight_note

	assert "- [x] Task A6: Capture the current Windows native validation preflight blocker" in outstanding_checklist
	assert "- [x] Task A6: Re-run native Windows build validation where the required" in outstanding_checklist
	assert "docs/reverse-engineering/windows-native-validation-preflight-2026-06-05.md" in outstanding_checklist

	assert "Earlier 2026-06-05 preflight, now superseded by the A6 refresh ledger:" in implementation_plan
	assert "strict VC10 blocker documented" in implementation_plan
	assert "2026-06-05 A6 native Windows preflight captured" in audit
	assert "both stop before build because the strict retail audit" in audit
	assert "A 2026-06-05 native Windows preflight is now captured" in repo_wide_audit
	assert "current checked-in project files report `v141`" in repo_wide_audit
	assert "Reconcile the strict retail native validation policy before claiming fresh" in toolchain_matrix


def test_a6_runtime_build_evidence_refresh_closes_available_freshness_gap() -> None:
	assert_dll_exports = _read_text(ASSERT_DLL_EXPORTS_SCRIPT_PATH)
	evidence = _read_json(RUNTIME_BUILD_EVIDENCE_PATH)
	evidence_note = _read_text(RUNTIME_BUILD_EVIDENCE_NOTE_PATH)
	retail_module_latest = _read_json(RETAIL_MODULE_LATEST_EVIDENCE_PATH)
	outstanding_checklist = _read_text(OUTSTANDING_WORK_CHECKLIST_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)
	function_gap_audit = _read_text(
		REPO_ROOT / "docs" / "reverse-engineering" / "function-parity-gap-audit-2026-04-24.md"
	)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)

	assert "Sort-Object LastWriteTimeUtc -Descending" in assert_dll_exports
	assert evidence["task"] == "A6"
	assert evidence["status"] == "completed_available_evidence_refresh_with_strict_retail_toolchain_gap_documented"
	assert evidence["repo_wide_parity_estimate"] == {"before": 99, "after": 99}

	retail_latest = evidence["runtime_evidence"]["retail_module_latest"]
	assert retail_latest["path"] == "artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json"
	assert retail_latest["source_artifact"].endswith("retail_module_runtime_evidence_20260602.json")
	assert retail_latest["promoted_latest"] is True
	assert retail_latest["missing_log_markers"] == 0
	assert retail_latest["warnings"] == 0
	assert retail_latest["map_runtime"]["map"] == "bloodrun"
	assert retail_latest["map_runtime"]["active_seen"] is True
	assert retail_latest["map_runtime"]["renderer_owner_blocker"] == ""

	assert retail_module_latest["missing_log_markers"] == []
	assert retail_module_latest["warnings"] == []
	assert retail_module_latest["map_runtime"]["server_seen"] is True
	assert retail_module_latest["map_runtime"]["active_seen"] is True
	assert retail_module_latest["map_runtime"]["retail_ui_load_seen"] is True
	assert retail_module_latest["map_runtime"]["retail_cgame_load_seen"] is True
	assert retail_module_latest["map_runtime"]["retail_qagame_load_seen"] is True
	assert "Going from CS_PRIMED to CS_ACTIVE" in retail_module_latest["verified_log_markers"]

	modern = evidence["build_validation"]["modern_native_validation"]
	assert modern["status"] == "partial_pass_timeout_after_build"
	assert modern["build_result"]["toolset"] == "v143"
	assert modern["build_result"]["warnings"] == 0
	assert modern["build_result"]["errors"] == 0
	assert modern["direct_export_audit"]["status"] == "passed"
	assert "build/win32/Release/modules/qagamex86/qagamex86.dll" in modern["direct_export_audit"]["validated_outputs"]
	assert evidence["build_validation"]["strict_retail_v100_validation"]["status"] == "blocked"
	assert "expects v100" in evidence["build_validation"]["strict_retail_v100_validation"]["reason"]

	assert "Status: completed for evidence available on this workstation" in evidence_note
	assert "The validation wrapper timed out after the successful build" in evidence_note
	assert "strict retail VC10 evidence" in evidence_note

	assert "- [x] Task A6: Refresh archived build/runtime evidence on current toolchains." in outstanding_checklist
	assert "- [x] Task A6: Promote stable `latest` runtime-evidence aliases only after" in outstanding_checklist
	assert "- [x] Task A6: Refresh the remaining retail-module runtime freshness evidence." in outstanding_checklist
	assert "docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.md" in outstanding_checklist

	assert "### Task A6: Refresh build/runtime evidence for the repo-wide ledger [COMPLETED 2026-06-05]" in implementation_plan
	assert "Visual Studio 2022 `v143` availability" in implementation_plan
	assert "prefers the newest" in implementation_plan
	assert "uninspected A6 freshness gap" in implementation_plan
	assert "latest alias now points at the clean `20260602`" in audit
	assert "modern-host `v143` `Release|x86` outputs" in audit
	assert "Current status: **Closed as an active repo-wide gap; strict retail VC10 evidence remains a documented local-toolchain boundary**" in repo_wide_audit
	assert "Documented validation boundary" in function_gap_audit
	assert "The 2026-06-05 A6 refresh verified the local Visual Studio 2022 `v143`" in toolchain_matrix


def test_residual_policy_spot_check_keeps_ongoing_guardrails_visible() -> None:
	platform_config = _read_text(PLATFORM_CONFIG_PATH)
	platform_services = _read_text(PLATFORM_SERVICES_PATH)
	sv_client = _read_text(SV_CLIENT_PATH)
	ownerdraw_index = _read_text(UI_OWNERDRAW_INDEX_PATH)
	spot_check = _read_json(RESIDUAL_POLICY_SPOT_CHECK_PATH)
	spot_check_note = _read_text(RESIDUAL_POLICY_SPOT_CHECK_NOTE_PATH)
	outstanding_checklist = _read_text(OUTSTANDING_WORK_CHECKLIST_PATH)

	assert "#define QL_BUILD_ONLINE_SERVICES 0" in platform_config
	assert "#if !QL_BUILD_ONLINE_SERVICES" in platform_config
	assert "#define QL_BUILD_STEAMWORKS 0" in platform_config
	assert "#define QL_BUILD_OPEN_STEAM 0" in platform_config
	assert "table.auth.provider = \"Build-disabled (QL_BUILD_ONLINE_SERVICES=0)\";" in platform_services
	assert "table.matchmaking.provider = \"Build-disabled (QL_BUILD_ONLINE_SERVICES=0)\";" in platform_services
	assert "#if !( QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES )" in sv_client

	assert "Last updated: 2026-05-28" in ownerdraw_index
	assert "| Checked | 36 |" in ownerdraw_index
	assert "| Partial | 1 | `542` |" in ownerdraw_index
	assert "| Needs check | 0 | None |" in ownerdraw_index
	assert "| Retail no-op/source legacy | 8 |" in ownerdraw_index
	assert "| No-op/missing | 1 | `530` |" in ownerdraw_index
	assert "Complete `UI_KEYBINDSTATUS` from partial coverage to full parity." in ownerdraw_index

	assert spot_check["schema_version"] == 1
	assert spot_check["last_updated"] == "2026-06-05"
	assert spot_check["status"] == "dated_spot_check_complete"
	assert spot_check["runtime_launch_required"] is False
	assert spot_check["game_launch_required"] is False
	assert spot_check["online_services"]["spot_check_result"] == "No policy drift found in the default source path."
	assert spot_check["online_services"]["remaining_boundary"].startswith("Opt-in Steamworks/open-adapter lanes")
	assert spot_check["ownerdraw"]["counts"] == {
		"checked": 36,
		"partial": 1,
		"needs_check": 0,
		"retail_noop_source_legacy": 8,
		"noop_missing": 1,
		"sentinel": 1,
	}
	assert spot_check["ownerdraw"]["src_ui_read_only_respected"] is True
	assert spot_check["checklist_effect"]["dated_online_services_spot_check_captured"] is True
	assert spot_check["checklist_effect"]["dated_ownerdraw_spot_check_captured"] is True
	assert spot_check["checklist_effect"]["ongoing_guardrails_closed"] is False
	assert spot_check["parity_estimate"]["repo_wide_before_percent"] == 99
	assert spot_check["parity_estimate"]["repo_wide_after_percent"] == 99

	assert "Status: dated spot-check complete; ongoing guardrails remain open." in spot_check_note
	assert "No default-policy drift was found." in spot_check_note
	assert "The UI ownerdraw parity index was reviewed before new UI work." in spot_check_note
	assert "Repo-wide parity estimate remains **99% -> 99%**." in spot_check_note

	assert "- [ ] Keep Quake Live-only online-service replacements behind" in outstanding_checklist
	assert "- [x] 2026-06-05 spot-check: default online-service policy still routes through" in outstanding_checklist
	assert "- [ ] Check the ownerdraw parity indexes before starting new UI work" in outstanding_checklist
	assert "- [x] 2026-06-05 spot-check: `ui-ownerdrawtype-parity-index.md` was reviewed;" in outstanding_checklist
	assert "docs/reverse-engineering/residual-policy-spot-check-2026-06-05.md" in outstanding_checklist
