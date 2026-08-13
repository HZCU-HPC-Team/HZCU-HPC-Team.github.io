#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
export HUGO_BIN="${HUGO_BIN:-hugo}"
export GOPROXY="https://goproxy.cn"
export GOSUMDB="off"
export GOMODCACHE="$HOME/go/pkg/mod"

python3 -m unittest tests/test_generated_site.py -v
