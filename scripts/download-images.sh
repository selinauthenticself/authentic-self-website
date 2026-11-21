#!/usr/bin/env bash
# Copies every image the site uses from Squarespace into src/assets/images/,
# so the site no longer depends on Squarespace. Images already saved are skipped.
# Run from the project folder:  bash scripts/download-images.sh
set -euo pipefail
cd "$(dirname "$0")/.."
CDN="https://images.squarespace-cdn.com/content/v1/6724c7a0bca70a27ee2e67bd/"
grep -rhoE '\{\{IMG\}\}[^"'"'"')]+' src build.py | sed 's/{{IMG}}//' | sort -u | while read -r p; do
  out="src/assets/images/$p"
  [ -f "$out" ] && continue
  mkdir -p "$(dirname "$out")"
  echo "Downloading $p"
  curl -fsSL "${CDN}${p}?format=2500w" -o "$out"
done
# Images listed in EXTRA_IMAGES in build.py
python3 - <<'PY'
import re, subprocess, pathlib
src = pathlib.Path("build.py").read_text()
block = src[src.index("EXTRA_IMAGES = {"):src.index("}", src.index("EXTRA_IMAGES = {"))]
for url, local in re.findall(r'"(https://[^"]+)":\s*"([^"]+)"', block):
    out = pathlib.Path("src/assets/images") / local
    if out.exists():
        continue
    out.parent.mkdir(parents=True, exist_ok=True)
    print("Downloading", local)
    subprocess.run(["curl", "-fsSL", url, "-o", str(out)], check=True)
PY
echo "Done. Build with: python3 build.py --local-images"
