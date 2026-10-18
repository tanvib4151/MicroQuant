#!/usr/bin/env bash
set -euo pipefail
nq_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
nq_cache="${NQ_CACHE_DIR:-/tmp/neuroquant-cache}"
python3 -m venv "$nq_root/.venv"
"$nq_root/.venv/bin/python" -m pip install --cache-dir "$nq_cache/pip" -r "$nq_root/api/requirements.lock"
npm --prefix "$nq_root/web" ci --cache "$nq_cache/npm"
