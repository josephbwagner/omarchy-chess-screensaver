#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
SENTINEL_START="# >>> omarchy-chess-screensaver >>>"
SENTINEL_END="# <<< omarchy-chess-screensaver <<<"
PATH_LINE="export PATH=\"\$HOME/repos/omarchy-chess-screensaver/bin:\$PATH\""

# ── 1. Ensure uv is available ──────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "uv not found — installing via the official installer..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for the rest of this script
    export PATH="$HOME/.local/bin:$PATH"
fi

# ── 2. Install Python dependencies ────────────────────────────────────────
echo "Running uv sync to create .venv/ with dependencies..."
uv sync --project "$SCRIPT_DIR"

# ── 3. Add PATH block to shell config files ───────────────────────────────
_add_path_to_file() {
    local rc_file="$1"
    if grep -qF "$SENTINEL_START" "$rc_file" 2>/dev/null; then
        echo "PATH already configured in $rc_file — skipping."
        return
    fi
    cat >> "$rc_file" <<EOF

$SENTINEL_START
$PATH_LINE
$SENTINEL_END
EOF
    echo "Added PATH entry to $rc_file"
}

_add_path_to_file "$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && _add_path_to_file "$HOME/.zshrc"

# ── 4. Summary ────────────────────────────────────────────────────────────
echo ""
echo "Installation complete. Changes made:"
echo "  1. .venv/ created inside $SCRIPT_DIR"
echo "  2. PATH entry added to ~/.bashrc (and ~/.zshrc if present)"
echo ""
echo "Reload your shell to activate:"
echo "  source ~/.bashrc"
echo ""
echo "Then verify with:"
echo "  which omarchy-cmd-screensaver"
echo "  omarchy-cmd-screensaver --help"
