#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
MANIFEST="${REPO_ROOT}/tools/packaging/ui_bundle_manifest.json"
BUILD_ROOT="${REPO_ROOT}/build/ui_bundle"
STAGING="${BUILD_ROOT}/staging"
ARTIFACT_ROOT="${REPO_ROOT}/artifacts/ui_bundle"
LOG_DIR="${ARTIFACT_ROOT}/logs"
METRICS_DIR="${ARTIFACT_ROOT}/metrics"
FONT_BAKE_TOOL="${REPO_ROOT}/tools/packaging/bake_fonts.py"
UI_RETAIL_OVERRIDE_TOOL="${REPO_ROOT}/scripts/ui/write_retail_ui_overrides.py"
OVERLAY_BUILD_ROOT="${BUILD_ROOT}/src_ui_retail_overlay"
OVERLAY_STAGING="${OVERLAY_BUILD_ROOT}/staging"
OVERLAY_MANIFEST_JSON="${ARTIFACT_ROOT}/ui_src_retail_overlay.json"
OVERLAY_PACKAGE_NAME="pak_ui_src_retail_overlay.pk3"
OVERLAY_PK3_PATH="${BUILD_ROOT}/${OVERLAY_PACKAGE_NAME}"

create_zip() {
	local source_dir="$1"
	local output_path="$2"

	python3 - "${source_dir}" "${output_path}" <<'PY'
import pathlib
import sys
import zipfile

source_dir = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])

output_path.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for candidate in sorted(source_dir.rglob("*")):
        if candidate.is_dir():
            continue
        archive.write(candidate, candidate.relative_to(source_dir).as_posix())
PY
}

mkdir -p "${STAGING}" "${LOG_DIR}" "${METRICS_DIR}"
rm -rf "${STAGING}" && mkdir -p "${STAGING}"
mkdir -p "${ARTIFACT_ROOT}"

rm -rf "${OVERLAY_STAGING}" && mkdir -p "${OVERLAY_STAGING}"
python3 "${UI_RETAIL_OVERRIDE_TOOL}" \
	--homepath-root "${OVERLAY_STAGING}" \
	--manifest "${OVERLAY_MANIFEST_JSON}" \
	--overlay-prefix "ui"

OVERLAY_FILE_COUNT=$(python3 - <<PY
import json
import pathlib

manifest = json.loads(pathlib.Path("${OVERLAY_MANIFEST_JSON}").read_text(encoding="utf-8"))
print(len(manifest.get("overlay_files", [])))
PY
)

rm -f "${OVERLAY_PK3_PATH}"
if [ "${OVERLAY_FILE_COUNT}" -gt 0 ]; then
	create_zip "${OVERLAY_STAGING}" "${OVERLAY_PK3_PATH}"
	cp "${OVERLAY_PK3_PATH}" "${ARTIFACT_ROOT}/${OVERLAY_PACKAGE_NAME}"
fi

PACKAGE_NAME=$(python3 - <<PY
import json
import pathlib
with open(pathlib.Path("${MANIFEST}"), 'r', encoding='utf-8') as handle:
    print(json.load(handle)['package'])
PY
)

copy_log="${LOG_DIR}/manifest_copy.log"
python3 - <<PY
import json
import pathlib
import shutil
import sys

manifest = json.loads(pathlib.Path("${MANIFEST}").read_text())
staging = pathlib.Path("${STAGING}")
log_path = pathlib.Path("${copy_log}")
repo_root = pathlib.Path("${REPO_ROOT}")
logs = []
copied_paths = []


def resolve_path(path: str) -> pathlib.Path:
    candidate = pathlib.Path(path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate


def copy_file(source: pathlib.Path, destination: pathlib.Path) -> None:
    if not source.is_file():
        raise SystemExit(f"Missing source file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    logs.append(f"Copied {source} -> {destination}")
    copied_paths.append(destination.relative_to(staging).as_posix())

for entry in manifest.get('files', []):
    if 'source_dir' in entry:
        source_dir = resolve_path(entry['source_dir'])
        if not source_dir.is_dir():
            raise SystemExit(f"Manifest source_dir is missing: {source_dir}")
        include = entry.get('include', ['**/*'])
        matched = False
        for pattern in include:
            for candidate in source_dir.glob(pattern):
                if candidate.is_dir():
                    continue
                rel = candidate.relative_to(source_dir)
                destination = staging / entry['destination'] / rel
                copy_file(candidate, destination)
                matched = True
        if not matched:
            raise SystemExit(
                f"No files matched manifest include patterns {include} under {source_dir}"
            )
        continue

    source = resolve_path(entry['source'])
    destination = staging / entry['destination']
    copy_file(source, destination)

audit = manifest.get('audit', {})
errors = []
for rel_path in audit.get('required_paths', []):
    target = staging / rel_path
    if not target.exists():
        errors.append(f"Missing required path in staging: {rel_path}")
for pattern in audit.get('required_globs', []):
    matches = [p for p in staging.glob(pattern) if p.is_file()]
    if not matches:
        errors.append(f"No files matched audit glob '{pattern}' in staging")

if errors:
    for line in errors:
        print(line, file=sys.stderr)
    sys.exit("Asset validation failed; required inputs are missing or misplaced")

log_path.write_text('\n'.join(logs) + '\n', encoding='utf-8')
PY

BAKE_LOG="${LOG_DIR}/font_bake.log"
METRICS_JSON="${METRICS_DIR}/font_metrics.json"
python3 "${FONT_BAKE_TOOL}" --manifest "${MANIFEST}" --output "${STAGING}" --log "${BAKE_LOG}" --metrics "${METRICS_JSON}"

PK3_PATH="${BUILD_ROOT}/${PACKAGE_NAME}"
rm -f "${PK3_PATH}"
create_zip "${STAGING}" "${PK3_PATH}"
cp "${PK3_PATH}" "${ARTIFACT_ROOT}/${PACKAGE_NAME}"

cat <<MSG
UI bundle complete.
  package: ${PK3_PATH}
  src/ui retail overlay: ${OVERLAY_PK3_PATH}
  src/ui overlay manifest: ${OVERLAY_MANIFEST_JSON}
  manifest log: ${LOG_DIR}/manifest_copy.log
  font bake log: ${BAKE_LOG}
  font metrics: ${METRICS_JSON}
MSG
