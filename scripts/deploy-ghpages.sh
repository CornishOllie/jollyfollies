#!/usr/bin/env bash
# Build and deploy the site to the gh-pages branch (GitHub Pages).
# Usage: npm run deploy   (or: bash scripts/deploy-ghpages.sh)
#
# Why this and not GitHub Actions? The local gh OAuth token lacks the `workflow`
# scope, so .github/workflows/ can't be pushed. This deploys the built site
# directly. To switch to CI later: `gh auth refresh -s workflow`, move
# deploy/github-pages-workflow.yml to .github/workflows/, push, and set
# Settings → Pages → Source: GitHub Actions.
set -euo pipefail

REPO_URL="https://github.com/CornishOllie/jollyfollies.git"
TMP="$(mktemp -d)"

echo "Building…"
npm run build

echo "Preparing gh-pages tree…"
cp -R dist/* "$TMP"/
# The 2009 replica lives under /classic on the same branch. Build it from the
# local copy so its paths match this domain.
REPLICA="$(cd "$(dirname "$0")/../../jollyfollies-replica" && pwd)"
(cd "$REPLICA" && npx astro build --site https://jollyfollies.co.uk --base /classic --outDir "$TMP/classic")
[ -f "$TMP/classic/index.html" ] || { echo "Replica build missing, aborting"; exit 1; }
touch "$TMP/.nojekyll"
cd "$TMP"
git init -q
git checkout -q -b gh-pages
git add -A
git -c user.name="CornishOllie" -c user.email="o.bridges@urbanchain.co.uk" commit -q -m "Deploy $(date -u +%Y-%m-%dT%H:%MZ)"
git push -f "$REPO_URL" gh-pages

echo "Deployed → https://jollyfollies.co.uk/"
rm -rf "$TMP"
