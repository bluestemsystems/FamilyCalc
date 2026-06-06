#!/bin/bash
# ============================================================
#  Build "Family Calculator.app" for macOS.
#  Requires: Python 3 + PyInstaller  (pip install pyinstaller)
#  Produces: mac/dist/Family Calculator.app  and  mac/FamilyCalc-Mac.zip
#  Note: the .app is built for THIS Mac's architecture (Apple Silicon
#        vs Intel). Build on the kind of Mac you want to distribute to.
# ============================================================
set -e
cd "$(dirname "$0")"                  # the mac/ folder
ROOT="$(cd .. && pwd)"                # repo root (holds the shared index.html)

# --target-arch universal2 makes one app that runs on both Intel and Apple
# Silicon. It requires a universal2 Python (the python.org framework build is).
python3 -m PyInstaller --noconfirm --windowed \
  --name "Family Calculator" \
  --icon AppIcon.icns \
  --osx-bundle-identifier com.bluestem.familycalc \
  --target-arch universal2 \
  --add-data "$ROOT/index.html:." \
  server.py

# The .app must be ad-hoc signed to launch. PyInstaller's auto-sign can choke on
# stray resource forks / Finder info, so scrub all of that first, then re-sign.
APP="dist/Family Calculator.app"
dot_clean -m dist 2>/dev/null || true
find "$APP" -type f -name '._*' -delete 2>/dev/null || true
xattr -cr "$APP"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP" && echo "signature OK"

# Zip the .app for distribution. Strip resource forks / extended attributes so
# the signature isn't flagged as "detritus" after download + unzip.
rm -f FamilyCalc-Mac.zip
( cd dist && ditto -c -k --keepParent --norsrc --noextattr "Family Calculator.app" ../FamilyCalc-Mac.zip )

echo
echo "============================================================"
echo "  Built:  mac/dist/Family Calculator.app"
echo "  Zip:    mac/FamilyCalc-Mac.zip   (this is what you distribute)"
echo "============================================================"
