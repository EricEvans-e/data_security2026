#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/wsl_common.sh"

REPO_ROOT="${1:?missing repo root}"
WORKSPACE_ROOT="${2:-/home/eric/workspace/data-security-lab2}"

lab2_init_paths "$REPO_ROOT" "$WORKSPACE_ROOT"
lab2_ensure_layout

setup_bin="$BUILD_DIR/src/zk_setup"
prove_bin="$BUILD_DIR/src/zk_prove"
verify_bin="$BUILD_DIR/src/zk_verify"

if [ ! -x "$setup_bin" ] || [ ! -x "$prove_bin" ] || [ ! -x "$verify_bin" ]; then
    lab2_log "Build artifacts missing. Run build_lab2.ps1 first."
    exit 1
fi

"$setup_bin" --artifacts-dir "$ARTIFACTS_DIR" --out 35 > "$LOGS_DIR/setup.log" 2>&1

set +e
"$prove_bin" --artifacts-dir "$ARTIFACTS_DIR" --x 4 --out 35 > "$LOGS_DIR/prove_invalid.log" 2>&1
prove_invalid_status=$?
set -e
if [ "$prove_invalid_status" -eq 0 ]; then
    lab2_log "Expected invalid witness proof to fail, but it succeeded."
    exit 1
fi

"$prove_bin" --artifacts-dir "$ARTIFACTS_DIR" --x 3 --out 35 > "$LOGS_DIR/prove_valid.log" 2>&1

set +e
"$verify_bin" --artifacts-dir "$ARTIFACTS_DIR" --out 36 > "$LOGS_DIR/verify_wrong_out.log" 2>&1
verify_wrong_status=$?
set -e
if [ "$verify_wrong_status" -eq 0 ]; then
    lab2_log "Expected wrong-public-input verification to fail, but it succeeded."
    exit 1
fi

lab2_copy_workspace_results_back
lab2_log "Negative cases finished"
