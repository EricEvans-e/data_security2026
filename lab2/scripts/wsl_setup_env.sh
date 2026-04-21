#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/wsl_common.sh"

REPO_ROOT="${1:?missing repo root}"
WORKSPACE_ROOT="${2:-/home/eric/workspace/data-security-lab2}"
SUDO_PASSWORD="${3:-}"
BUNDLE_SOURCE="${4:-}"

lab2_init_paths "$REPO_ROOT" "$WORKSPACE_ROOT"
lab2_ensure_layout
lab2_install_system_packages "$SUDO_PASSWORD"
lab2_ensure_miniconda
lab2_ensure_libsnark_bundle "$BUNDLE_SOURCE"

{
    if [ -f /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        printf 'OS_PRETTY_NAME=%s\n' "$PRETTY_NAME"
    fi
    printf 'GENERATED_AT=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    printf 'HOME=%s\n' "$HOME"
    printf 'WORKSPACE_ROOT=%s\n' "$WORKSPACE_ROOT"
    printf 'CONDA_ROOT=%s\n' "$CONDA_ROOT"
    printf 'CONDA_ENV_NAME=%s\n' "$CONDA_ENV_NAME"
    printf 'CONDA_PYTHON=%s\n' "$("$CONDA_ROOT/bin/conda" run -n "$CONDA_ENV_NAME" sh -c 'command -v python' | tail -n 1)"
    printf 'PYTHON_VERSION=%s\n' "$(lab2_conda_run python --version | tail -n 1)"
    printf 'GIT=%s\n' "$(command -v git)"
    printf 'CMAKE=%s\n' "$(command -v cmake)"
    printf 'CXX=%s\n' "$(command -v c++)"
    printf 'LIBSNARK_ROOT=%s\n' "$LIBSNARK_ROOT"
} > "$ENV_DIR/environment.txt"

lab2_log "WSL environment is ready"
lab2_log "Environment summary saved to $ENV_DIR/environment.txt"
