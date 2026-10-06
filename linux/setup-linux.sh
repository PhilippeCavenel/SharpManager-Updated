#!/usr/bin/env bash
# Linux setup added 6 October 2026. See LICENSE-SharpManager.txt.
set -euo pipefail
app_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_command="${SHARP_PYTHON:-python3}"

if [[ "$(uname -s)" != Linux ]]; then
    echo "Use the macOS or Windows version on this operating system." >&2
    exit 1
fi
for command_name in "$python_command" make cc; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Missing $command_name. On Ubuntu install: python3 python3-venv python3-tk gcc make" >&2
        exit 1
    fi
done
if ! "$python_command" -c 'import tkinter' >/dev/null 2>&1; then
    echo "Tkinter is missing. On Ubuntu: sudo apt install python3-tk" >&2
    exit 1
fi
if ! "$python_command" -m venv "$app_dir/.venv"; then
    echo "Cannot create the virtual environment. On Ubuntu: sudo apt install python3-venv" >&2
    exit 1
fi
"$app_dir/.venv/bin/python" -m pip install -r "$app_dir/requirements.txt"
make -C "$app_dir/PocketTools" all
echo "Setup complete. Start SharpManager with: $app_dir/run-linux.sh"
