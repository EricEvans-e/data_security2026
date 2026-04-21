#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/wsl_common.sh"

REPO_ROOT="${1:?missing repo root}"
WORKSPACE_ROOT="${2:-/home/eric/workspace/data-security-lab2}"

lab2_init_paths "$REPO_ROOT" "$WORKSPACE_ROOT"
lab2_ensure_layout
lab2_ensure_libsnark_bundle
lab2_sync_sources_into_bundle
lab2_patch_cmakelists

lab2_log "Configuring and building libsnark bundle"
(
    cd "$LIBSNARK_ROOT"
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    cmake "$LIBSNARK_ROOT"
    cmake --build . -- -j2
) > "$LOGS_DIR/build.log" 2>&1

lab2_copy_workspace_results_back
lab2_log "Build completed. Log saved to $LOGS_DIR/build.log"
