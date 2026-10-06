#!/usr/bin/env bash
# Optional Linux bundle added 6 October 2026. See LICENSE-SharpManager.txt.
set -euo pipefail
app_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$app_dir/setup-linux.sh"
if ! command -v objdump >/dev/null 2>&1; then
    echo "objdump is missing. On Ubuntu: sudo apt install binutils" >&2
    exit 1
fi
"$app_dir/.venv/bin/python" -m pip install -r "$app_dir/requirements-build.txt"
# Custom Python installations may keep Tcl/Tk shared libraries beside Python
# instead of in the system linker path. Make that directory visible while
# PyInstaller resolves native dependencies; the bundle collects them itself.
python_lib_dirs="$("$app_dir/.venv/bin/python" -c 'from pathlib import Path; import sys, sysconfig; candidates = [Path(sys.base_prefix) / "lib", Path(sysconfig.get_config_var("LIBDIR") or "/nonexistent")]; print(":".join(dict.fromkeys(str(p) for p in candidates if p.is_dir())))')"
if [[ -n "$python_lib_dirs" ]]; then
    export LD_LIBRARY_PATH="$python_lib_dirs${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
cd "$app_dir"
"$app_dir/.venv/bin/python" -m PyInstaller --noconfirm --clean --onedir \
    --name SharpManager-Linux --hidden-import serial.tools.list_ports_linux \
    --add-data "$app_dir/PocketTools/bas2img:PocketTools" \
    --add-data "$app_dir/PocketTools/bin2wav:PocketTools" \
    --add-data "$app_dir/PocketTools/wav2bin:PocketTools" \
    --add-data "$app_dir/PocketTools/NOTICE.txt:PocketTools" \
    --add-data "$app_dir/LICENSE-SharpManager.txt:." \
    --add-data "$app_dir/../NOTICE:." app.py
echo "Bundle created: $app_dir/dist/SharpManager-Linux/SharpManager-Linux"
echo "Keep the whole SharpManager-Linux directory, including _internal."
