#!/usr/bin/env bash
# End-to-end smoke test on a synthetic stock-WordPress site: crawl -> build_source -> astro build -> verify ->
# SEO inventory/check -> assets -> audits. Needs python3, node and npm (Astro is installed into a temp project).
# Usage: bash test-fixture/smoke.sh        (from reference-implementation/)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"; PORT="${PORT:-8765}"; SERVER=
trap 'kill $SERVER 2>/dev/null || true; rm -rf "$WORK"' EXIT
cd "$WORK" && mkdir -p fixture proj/docs
cp "$HERE"/test-fixture/{gen,serve}.py fixture/
(cd fixture && python3 gen.py "$PORT")
(cd fixture && exec python3 serve.py "$PORT") &
SERVER=$!; sleep 1
cd proj
cp -r "$HERE/scripts" . && cp -r "$HERE/astro/." .
echo "{ \"origin\": \"http://localhost:$PORT\", \"crawl\": { \"delaySeconds\": 0.01 }, \"hostingLayers\": [] }" > wordpress-to-astro.config.json
echo '{ "name": "smoke", "private": true, "type": "module", "dependencies": { "astro": "^5" } }' > package.json
npm install --silent
export CRAWLER_USER="Smoke Test <smoke@example.com>"
python3 scripts/crawl.py
python3 scripts/build_source.py
python3 scripts/seo_inventory.py
python3 scripts/assets_inventory.py && python3 scripts/download_assets.py && python3 scripts/assets_report.py
npx astro build
python3 scripts/verify.py
python3 scripts/seo_check.py
python3 scripts/errors_audit.py && python3 scripts/a11y_audit.py
echo "smoke test passed"
