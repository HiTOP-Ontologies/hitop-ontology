#!/usr/bin/env bash
# Run the local quality checks for the HiTOP suffix tooling.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
  echo "Missing .venv. Run scripts/bootstrap_hitop_suffix_tools.sh first." >&2
  exit 1
fi

# Keep this gate compact and deterministic: syntax/import checks, regression
# tests, and public documentation examples must all pass before a release.
"${PYTHON}" -m compileall -q "${ROOT_DIR}/src" "${ROOT_DIR}/scripts" "${ROOT_DIR}/validation"
"${PYTHON}" -m unittest discover -s "${ROOT_DIR}/validation" -v
"${PYTHON}" "${ROOT_DIR}/scripts/validate_hitop_suffix_docs.py"
