#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
SENTINEL_START="# >>> omarchy-chess-screensaver >>>"
SENTINEL_END="# <<< omarchy-chess-screensaver <<<"

# ── 1. Remove PATH block from shell config files ──────────────────────────
_remove_from_file() {
    local rc_file="$1"
    if ! grep -qF "$SENTINEL_START" "$rc_file" 2>/dev/null; then
        return
    fi
    # Delete lines from sentinel start through sentinel end (inclusive)
    sed -i "/$(printf '%s' "$SENTINEL_START" | sed 's/[^^]/[&]/g; s/\^/\\^/g')/,/$(printf '%s' "$SENTINEL_END" | sed 's/[^^]/[&]/g; s/\^/\\^/g')/d" "$rc_file"
    # Remove the blank line that was left before the block
    sed -i '/^$/N;/^\n$/d' "$rc_file"
    echo "Removed PATH entry from $rc_file"
}

_remove_from_file "$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && _remove_from_file "$HOME/.zshrc"

# ── 2. Optionally remove .venv/ ───────────────────────────────────────────
if [ -d "$SCRIPT_DIR/.venv" ]; then
    printf "Remove .venv/ (Python virtualenv inside repo)? [y/N] "
    read -r answer
    case "$answer" in
        [yY]*)
            rm -rf "$SCRIPT_DIR/.venv"
            echo "Removed $SCRIPT_DIR/.venv"
            ;;
        *)
            echo "Keeping .venv/"
            ;;
    esac
fi

# ── 3. Summary ────────────────────────────────────────────────────────────
echo ""
echo "Uninstallation complete."
echo ""
echo "Note: uv itself was NOT removed. To remove it manually:"
echo "  rm ~/.local/bin/uv"
echo ""
echo "To fully remove the screensaver:"
echo "  rm -rf ~/repos/omarchy-chess-screensaver"
echo ""
echo "Reload your shell: source ~/.bashrc"
