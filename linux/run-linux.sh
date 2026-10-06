#!/usr/bin/env bash
# Linux launcher added 6 October 2026. See LICENSE-SharpManager.txt.
set -euo pipefail
app_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(uname -s)" != Linux ]]; then
    echo "Use the macOS or Windows version on this operating system." >&2
    exit 1
fi
if [[ ! -x "$app_dir/.venv/bin/python" ]]; then
    echo "Run ./setup-linux.sh first." >&2
    exit 1
fi
for tool_name in bas2img bin2wav wav2bin; do
    if [[ ! -x "$app_dir/PocketTools/$tool_name" ]]; then
        echo "Missing $tool_name. Run ./setup-linux.sh first." >&2
        exit 1
    fi
done
exec "$app_dir/.venv/bin/python" "$app_dir/app.py" "$@"
