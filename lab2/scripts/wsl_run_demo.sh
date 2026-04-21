#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/wsl_common.sh"

REPO_ROOT="${1:?missing repo root}"
WORKSPACE_ROOT="${2:-/home/eric/workspace/data-security-lab2}"
X_VALUE="${3:-3}"
OUT_VALUE="${4:-35}"

lab2_init_paths "$REPO_ROOT" "$WORKSPACE_ROOT"
lab2_ensure_layout

setup_bin="$BUILD_DIR/src/zk_setup"
prove_bin="$BUILD_DIR/src/zk_prove"
verify_bin="$BUILD_DIR/src/zk_verify"

if [ ! -x "$setup_bin" ] || [ ! -x "$prove_bin" ] || [ ! -x "$verify_bin" ]; then
    lab2_log "Build artifacts missing. Run build_lab2.ps1 first."
    exit 1
fi

"$setup_bin" --artifacts-dir "$ARTIFACTS_DIR" --out "$OUT_VALUE" > "$LOGS_DIR/setup.log" 2>&1
"$prove_bin" --artifacts-dir "$ARTIFACTS_DIR" --x "$X_VALUE" --out "$OUT_VALUE" > "$LOGS_DIR/prove_valid.log" 2>&1
"$verify_bin" --artifacts-dir "$ARTIFACTS_DIR" --out "$OUT_VALUE" > "$LOGS_DIR/verify_valid.log" 2>&1

lab2_copy_workspace_results_back
lab2_log "Valid demo finished"
