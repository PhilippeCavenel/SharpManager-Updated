#!/bin/bash
# Double-cliquer depuis le Finder sur un Mac Apple Silicon équipé de Python 3
# (avec Tkinter) et des outils en ligne de commande Xcode.
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  echo "La compilation doit se faire sur le Mac mini M4 (macOS arm64)."
  exit 1
fi
PYTHON_CMD=""
# Homebrew's python3 can take precedence in PATH while lacking tkinter.
# Prefer the python.org framework installation when it is present.
for candidate in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 python3; do
  if "$candidate" -c 'import tkinter' >/dev/null 2>&1; then
    PYTHON_CMD="$candidate"
    break
  fi
done
if [[ -z "$PYTHON_CMD" ]]; then
  echo "Python 3 avec Tkinter est requis : installer Python pour macOS depuis python.org."
  exit 1
fi
if ! xcrun --find clang >/dev/null 2>&1; then
  echo "Installer les outils Xcode : xcode-select --install"
  exit 1
fi
"$PYTHON_CMD" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
make -C PocketTools clean all CC=clang
.venv/bin/pyinstaller --noconfirm --clean --windowed --name SharpManager-PC1403-V5-Flux \
  --target-arch arm64 --add-binary 'PocketTools/bas2img:PocketTools' \
  --add-binary 'PocketTools/bin2wav:PocketTools' \
  --add-binary 'PocketTools/wav2bin:PocketTools' app.py
echo
echo "Application prête : $(pwd)/dist/SharpManager-PC1403-V5-Flux.app"
echo "Copier ce fichier dans Applications, puis ouvrir avec clic droit > Ouvrir."
read -r -p 'Appuyer sur Entrée pour fermer…' _
