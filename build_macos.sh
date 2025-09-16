#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m pip install --upgrade pip
pip3 install -r requirements.txt pyinstaller

EXTRA_ARGS=()
if pyinstaller --help | grep -q "--target-arch"; then
  ARCH_VALUE="${PYINSTALLER_ARCH:-universal2}"
  EXTRA_ARGS=(--target-arch "$ARCH_VALUE")
else
  echo "PyInstaller does not support --target-arch on this platform; building default architecture."
fi

pyinstaller --noconfirm --clean \
  --add-data "office_toolkit:office_toolkit" \
  --name "OfficeEfficiencyToolkit" \
  "${EXTRA_ARGS[@]}" \
  run_app.py

rm -f OfficeEfficiencyToolkit-macos.zip
if command -v ditto >/dev/null 2>&1; then
  ditto -c -k --sequesterRsrc --keepParent "dist/OfficeEfficiencyToolkit" "OfficeEfficiencyToolkit-macos.zip"
else
  (cd dist && zip -r "../OfficeEfficiencyToolkit-macos.zip" "OfficeEfficiencyToolkit")
fi

echo
printf '%s\n' "Build complete. Launch the binary from dist/OfficeEfficiencyToolkit or use the ZIP archive."
