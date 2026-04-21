#!/bin/sh
set -eu

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

lab2_log() {
    printf '[lab2] %s\n' "$*"
}

lab2_fix_home() {
    user_name="$(id -un)"
    expected_home="/home/$user_name"
    if [ -d "$expected_home" ]; then
        export HOME="$expected_home"
    fi
}

lab2_init_paths() {
    REPO_ROOT="$1"
    WORKSPACE_ROOT="$2"

    lab2_fix_home

    USER_NAME="$(id -un)"
    REPO_ROOT="$REPO_ROOT"
    WORKSPACE_ROOT="$WORKSPACE_ROOT"
    ENV_DIR="$WORKSPACE_ROOT/env"
    LIBSNARK_ROOT="$WORKSPACE_ROOT/libsnark-src/libsnark_abc-master"
    BUILD_DIR="$WORKSPACE_ROOT/build"
    ARTIFACTS_DIR="$WORKSPACE_ROOT/artifacts"
    LOGS_DIR="$WORKSPACE_ROOT/logs"
    CONDA_ROOT="$HOME/miniconda3"
    CONDA_ENV_NAME="datasec-lab2-zk"
    REPO_RESULTS_DIR="$REPO_ROOT/results"
    REPO_ARTIFACTS_DIR="$REPO_RESULTS_DIR/artifacts"
    REPO_LOGS_DIR="$REPO_RESULTS_DIR/logs"

    export HOME USER_NAME REPO_ROOT WORKSPACE_ROOT ENV_DIR LIBSNARK_ROOT BUILD_DIR ARTIFACTS_DIR LOGS_DIR CONDA_ROOT CONDA_ENV_NAME REPO_RESULTS_DIR REPO_ARTIFACTS_DIR REPO_LOGS_DIR
}

lab2_ensure_layout() {
    mkdir -p "$ENV_DIR" "$BUILD_DIR" "$ARTIFACTS_DIR" "$LOGS_DIR" "$REPO_ARTIFACTS_DIR" "$REPO_LOGS_DIR"
}

lab2_run_sudo() {
    if [ "${1:-}" = "--password" ]; then
        sudo_password="$2"
        shift 2
    else
        sudo_password=""
    fi

    if [ -n "$sudo_password" ]; then
        printf '%s\n' "$sudo_password" | sudo -S "$@"
    else
        sudo "$@"
    fi
}

lab2_install_system_packages() {
    sudo_password="${1:-}"
    lab2_log "Installing system packages in WSL"
    lab2_run_sudo --password "$sudo_password" apt-get update
    lab2_run_sudo --password "$sudo_password" apt-get install -y \
        build-essential \
        cmake \
        git \
        libgmp3-dev \
        libprocps-dev \
        python3-markdown \
        libboost-program-options-dev \
        libssl-dev \
        python3 \
        pkg-config
}

lab2_ensure_miniconda() {
    installer="$ENV_DIR/Miniconda3-latest-Linux-x86_64.sh"
    if [ ! -x "$CONDA_ROOT/bin/conda" ]; then
        lab2_log "Installing Miniconda under $CONDA_ROOT"
        rm -f "$installer"
        curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o "$installer"
        bash "$installer" -b -p "$CONDA_ROOT"
    else
        lab2_log "Miniconda already exists at $CONDA_ROOT"
    fi

    "$CONDA_ROOT/bin/conda" config --set always_yes yes --set changeps1 no >/dev/null
    "$CONDA_ROOT/bin/conda" tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main >/dev/null 2>&1 || true
    "$CONDA_ROOT/bin/conda" tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r >/dev/null 2>&1 || true
    if ! "$CONDA_ROOT/bin/conda" env list | grep -q "^$CONDA_ENV_NAME "; then
        lab2_log "Creating conda environment $CONDA_ENV_NAME"
        "$CONDA_ROOT/bin/conda" create -n "$CONDA_ENV_NAME" python=3.10 pytest
    else
        lab2_log "Conda environment $CONDA_ENV_NAME already exists"
    fi
}

lab2_conda_run() {
    "$CONDA_ROOT/bin/conda" run -n "$CONDA_ENV_NAME" "$@"
}

lab2_git() {
    git -c url."https://github.com/".insteadOf=git://github.com/ "$@"
}

lab2_ensure_libsnark_bundle() {
    bundle_source="${1:-}"
    bundle_parent="$WORKSPACE_ROOT/libsnark-src"
    mkdir -p "$bundle_parent"

    if [ ! -d "$LIBSNARK_ROOT/.git" ]; then
        rm -rf "$LIBSNARK_ROOT"
        if [ -n "$bundle_source" ] && [ -d "$bundle_source/.git" ]; then
            lab2_log "Copying libsnark_abc bundle from Windows cache"
            cp -a "$bundle_source" "$LIBSNARK_ROOT"
        else
            lab2_log "Cloning libsnark_abc bundle"
            lab2_git clone --recursive https://github.com/sec-bit/libsnark_abc.git "$LIBSNARK_ROOT"
        fi
    else
        lab2_log "Updating libsnark_abc submodules"
        lab2_git -C "$LIBSNARK_ROOT" submodule sync --recursive
        lab2_git -C "$LIBSNARK_ROOT" submodule update --init --recursive
    fi
}

lab2_sync_sources_into_bundle() {
    src_dir="$LIBSNARK_ROOT/src"
    lab2_log "Syncing lab2 C++ sources into $src_dir"
    cp "$REPO_ROOT/zk_lab/common.hpp" "$src_dir/common.hpp"
    cp "$REPO_ROOT/zk_lab/zk_setup.cpp" "$src_dir/zk_setup.cpp"
    cp "$REPO_ROOT/zk_lab/zk_prove.cpp" "$src_dir/zk_prove.cpp"
    cp "$REPO_ROOT/zk_lab/zk_verify.cpp" "$src_dir/zk_verify.cpp"
}

lab2_patch_cmakelists() {
    cmake_file="$LIBSNARK_ROOT/src/CMakeLists.txt"
    marker="# >>> lab2-zk-targets >>>"

    if grep -q "$marker" "$cmake_file"; then
        lab2_log "CMakeLists already contains lab2 target block"
        return 0
    fi

    lab2_log "Appending lab2 target block into src/CMakeLists.txt"
    {
        printf '\n%s\n' "$marker"
        printf 'add_executable(\n  zk_setup\n\n  zk_setup.cpp\n)\n'
        printf 'target_link_libraries(\n  zk_setup\n\n  snark\n)\n'
        printf 'target_include_directories(\n  zk_setup\n\n  PUBLIC\n  ${DEPENDS_DIR}/libsnark\n  ${DEPENDS_DIR}/libsnark/depends/libfqfft\n)\n\n'
        printf 'add_executable(\n  zk_prove\n\n  zk_prove.cpp\n)\n'
        printf 'target_link_libraries(\n  zk_prove\n\n  snark\n)\n'
        printf 'target_include_directories(\n  zk_prove\n\n  PUBLIC\n  ${DEPENDS_DIR}/libsnark\n  ${DEPENDS_DIR}/libsnark/depends/libfqfft\n)\n\n'
        printf 'add_executable(\n  zk_verify\n\n  zk_verify.cpp\n)\n'
        printf 'target_link_libraries(\n  zk_verify\n\n  snark\n)\n'
        printf 'target_include_directories(\n  zk_verify\n\n  PUBLIC\n  ${DEPENDS_DIR}/libsnark\n  ${DEPENDS_DIR}/libsnark/depends/libfqfft\n)\n'
        printf '# <<< lab2-zk-targets <<<\n'
    } >> "$cmake_file"
}

lab2_copy_workspace_results_back() {
    mkdir -p "$REPO_ARTIFACTS_DIR" "$REPO_LOGS_DIR"

    for file_name in pk.raw vk.raw proof.raw; do
        if [ -f "$ARTIFACTS_DIR/$file_name" ]; then
            rm -f "$REPO_ARTIFACTS_DIR/$file_name"
            cp "$ARTIFACTS_DIR/$file_name" "$REPO_ARTIFACTS_DIR/$file_name"
        fi
    done

    for log_name in setup.log prove_valid.log verify_valid.log prove_invalid.log verify_invalid.log verify_wrong_out.log build.log; do
        if [ -f "$LOGS_DIR/$log_name" ]; then
            rm -f "$REPO_LOGS_DIR/$log_name"
            cp "$LOGS_DIR/$log_name" "$REPO_LOGS_DIR/$log_name"
        fi
    done
}
