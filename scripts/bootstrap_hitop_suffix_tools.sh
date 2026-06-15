#!/usr/bin/env bash
# Create the local virtual environment and install the HiTOP suffix tooling.
#
# This script is intentionally small and explicit. It is suitable for local
# developer setup and CI jobs that operate from the repository root.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install \
  --constraint "${ROOT_DIR}/requirements-lock.txt" \
  -e "${ROOT_DIR}[dev]"

cat <<EOF
HiTOP suffix tooling installed.

Use:
  ${VENV_DIR}/bin/hitop-suffix --help
EOF
