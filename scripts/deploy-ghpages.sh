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
touch "$TMP/.nojekyll"
cd "$TMP"
git init -q
git checkout -q -b gh-pages
git add -A
git -c user.name="CornishOllie" -c user.email="o.bridges@urbanchain.co.uk" commit -q -m "Deploy $(date -u +%Y-%m-%dT%H:%MZ)"
git push -f "$REPO_URL" gh-pages

echo "Deployed → https://cornishollie.github.io/jollyfollies/"
rm -rf "$TMP"
