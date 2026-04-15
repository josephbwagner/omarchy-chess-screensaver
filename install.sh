#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
SENTINEL_START="# >>> omarchy-chess-screensaver >>>"
SENTINEL_END="# <<< omarchy-chess-screensaver <<<"
PATH_LINE="export PATH=\"$SCRIPT_DIR/bin:\$PATH\""

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

# ── 4. Add PATH to UWSM env.d (for Hyprland / UWSM) ──────────────────────
# Hyprland is launched via UWSM, which builds the session PATH by sourcing
# ~/.config/uwsm/env (and files in ~/.config/uwsm/env.d/) — NOT .bashrc or
# systemd environment.d.  Placing a drop-in here is the only reliable way to
# get the chess screensaver bin into the PATH that hypridle and the spawned
# terminal actually see.
#
# How UWSM builds the PATH (for reference):
#   1. prepare-env.sh sources /etc/profile + ~/.profile  → baseline PATH
#   2. It sources ~/.config/uwsm/env  → Omarchy adds its bin/
#   3. It sources files in ~/.config/uwsm/env.d/  → our drop-in adds chess bin
#   4. The resulting PATH is always-exported into the systemd user manager,
#      overwriting anything set in ~/.config/environment.d/ or .bashrc.
UWSM_ENV_D_DIR="$HOME/.config/uwsm/env.d"
UWSM_ENV_D_FILE="$UWSM_ENV_D_DIR/omarchy-chess-screensaver.sh"
mkdir -p "$UWSM_ENV_D_DIR"
if [ -f "$UWSM_ENV_D_FILE" ]; then
    echo "UWSM env.d entry already exists — skipping."
else
    cat > "$UWSM_ENV_D_FILE" <<EOF
# Added by omarchy-chess-screensaver install.sh
# Prepends the chess screensaver bin/ so it shadows omarchy's built-in
# omarchy-cmd-screensaver when UWSM builds the Hyprland session PATH.
export PATH="$SCRIPT_DIR/bin:\$PATH"
EOF
    echo "Added PATH entry to $UWSM_ENV_D_FILE"
fi

# ── 5. Summary ────────────────────────────────────────────────────────────
echo ""
echo "Installation complete. Changes made:"
echo "  1. .venv/ created inside $SCRIPT_DIR"
echo "  2. PATH entry added to ~/.bashrc (and ~/.zshrc if present)"
echo "  3. PATH entry added to ~/.config/uwsm/env.d/omarchy-chess-screensaver.sh"
echo ""
echo "Reload your shell to activate the interactive shell change:"
echo "  source ~/.bashrc"
echo ""
echo "Then verify with:"
echo "  which omarchy-cmd-screensaver"
echo "  omarchy-cmd-screensaver --help"
echo ""
echo "Log out and back in for the Hyprland session to pick up the new PATH."
