#!/usr/bin/env bash
# Install (or update) the Restaurant Health Report skill for Claude Code and Codex.
#   curl -fsSL https://raw.githubusercontent.com/YangzhenRuan/restaurant-health-report/main/install.sh | bash
set -euo pipefail

REPO="YangzhenRuan/restaurant-health-report"
NAME="restaurant-health-report"
CLAUDE_SKILLS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
CODEX_SKILLS="${CODEX_HOME:-$HOME/.codex}/skills"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
echo "Downloading $REPO ..."
curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar -xz -C "$tmp"
src="$(find "$tmp" -maxdepth 3 -type d -path "*/skills/$NAME" | head -n 1)"
[ -n "$src" ] || { echo "Could not find skills/$NAME in the download." >&2; exit 1; }

for dest in "$CLAUDE_SKILLS" "$CODEX_SKILLS"; do
  mkdir -p "$dest"
  rm -rf "${dest:?}/$NAME"
  cp -R "$src" "$dest/$NAME"
  echo "Installed: $dest/$NAME"
done

echo
command -v python3 >/dev/null 2>&1 && echo "Python 3: OK" || echo "Python 3: missing. Install it from python.org (Mac: run 'python3' once and accept the developer tools prompt)."
if [ -d "/Applications/Google Chrome.app" ] || [ -d "/Applications/Microsoft Edge.app" ] || command -v google-chrome >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1; then
  echo "Chrome/Edge: OK"
else
  echo "Chrome/Edge: not found. Install Google Chrome to turn reports into PDFs."
fi
echo
echo "Done. Restart Claude Code or Codex, then ask:"
echo "  \"Make a restaurant health report for <restaurant name>, <website or address>.\""
