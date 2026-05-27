#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_ROOT="${REPO_ROOT}/src-re/prototypes"
INCLUDE_ROOT="${REPO_ROOT}/src-re/include"

HOST_SYSTEM="${QLR_RE_PLATFORM:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
case "${HOST_SYSTEM}" in
  linux*)
    PLATFORM_NAME="linux"
    SHLIB_EXT="so"
    CC_DEFAULT="gcc"
    LDFLAGS_DEFAULT="-shared"
    ;;
  darwin*|macos*)
    PLATFORM_NAME="macos"
    SHLIB_EXT="dylib"
    CC_DEFAULT="cc"
    LDFLAGS_DEFAULT="-dynamiclib"
    ;;
  *)
    echo "Unsupported clean-room build host: ${HOST_SYSTEM}" >&2
    exit 1
    ;;
esac

BUILD_ROOT="${QLR_RE_BUILD_ROOT:-${BUILD_ROOT:-${REPO_ROOT}/build/re/${PLATFORM_NAME}}}"
[[ "${BUILD_ROOT}" = /* ]] || BUILD_ROOT="${REPO_ROOT}/${BUILD_ROOT}"

CC="${QLR_RE_CC:-${CC:-$CC_DEFAULT}}"
CFLAGS_DEFAULT="-std=c99 -Wall -Wextra -O2 -fPIC"
CFLAGS="${QLR_RE_CFLAGS:-${CFLAGS:-$CFLAGS_DEFAULT}}"
LDFLAGS="${QLR_RE_LDFLAGS:-${LDFLAGS:-$LDFLAGS_DEFAULT}}"

mkdir -p "$BUILD_ROOT"

if ! command -v "$CC" >/dev/null 2>&1; then
  echo "Compiler '$CC' not found in PATH" >&2
  exit 1
fi

build_module() {
  local name="$1"
  shift
  local output="${BUILD_ROOT}/${name}.${SHLIB_EXT}"
  echo "[clean-room] Building ${name} -> ${output}"
  "$CC" \
    $CFLAGS \
    -I"${SRC_ROOT}/common" \
    -I"${INCLUDE_ROOT}" \
    "$@" \
    $LDFLAGS \
    -o "$output"
}

build_module qlr_client_frame \
  -I"${SRC_ROOT}/c_client" \
  "${SRC_ROOT}/c_client/cl_frame.c" \
  "${SRC_ROOT}/common/native_shim.c"

build_module qlr_game_frame \
  -I"${SRC_ROOT}/g_gameplay" \
  "${SRC_ROOT}/g_gameplay/g_frame.c" \
  "${SRC_ROOT}/common/native_shim.c"

echo "Clean-room ${PLATFORM_NAME} shared objects stored under ${BUILD_ROOT}"
