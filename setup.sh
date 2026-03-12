#!/usr/bin/env bash
set -euo pipefail

FORGE_ROOT="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }

errors=0

echo "=== forge setup ==="
echo

# 1. OS check
echo "[1/6] OS check"
if grep -qi microsoft /proc/version 2>/dev/null; then
    ok "WSL2 detected"
else
    ok "Linux detected"
fi

# 2. Required commands
echo "[2/6] Required commands"
for cmd in python3 claude gh git; do
    if command -v "$cmd" &>/dev/null; then
        case "$cmd" in
            python3) ver=$(python3 --version 2>&1) ;;
            claude)  ver=$(claude --version 2>&1) ;;
            gh)      ver=$(gh --version 2>&1 | head -1) ;;
            git)     ver=$(git --version 2>&1) ;;
        esac
        ok "$cmd ($ver)"
    else
        fail "$cmd not found"
        errors=$((errors + 1))
    fi
done

# 3. Sandbox dependencies (bubblewrap, socat)
echo "[3/6] Sandbox dependencies"
for cmd in bwrap socat; do
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd"
    else
        warn "$cmd not found — sudo apt-get install bubblewrap socat"
        errors=$((errors + 1))
    fi
done

# 4. Configuration files
echo "[4/6] Configuration files"
if [ -f "$FORGE_ROOT/config/forge.env" ]; then
    ok "config/forge.env"

    for key in FORGE_TEAM_ID LINEAR_API_KEY FORGE_LOG_DIR FORGE_LOCK_DIR FORGE_WORKTREE_DIR; do
        val=$(grep "^${key}=" "$FORGE_ROOT/config/forge.env" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
        if [ -z "$val" ]; then
            fail "  $key is not set"
            errors=$((errors + 1))
        fi
    done
else
    warn "config/forge.env not found — copying from example"
    cp "$FORGE_ROOT/config/forge.env.example" "$FORGE_ROOT/config/forge.env"
    ok "Created config/forge.env (please fill in the values)"
    errors=$((errors + 1))
fi

if [ -f "$FORGE_ROOT/config/repos.conf" ]; then
    ok "config/repos.conf"
else
    warn "config/repos.conf not found — copying from example"
    cp "$FORGE_ROOT/config/repos.conf.example" "$FORGE_ROOT/config/repos.conf"
    ok "Created config/repos.conf (please configure repositories)"
fi

# 5. Create directories
echo "[5/6] Create directories"
for dir_key in FORGE_LOG_DIR FORGE_LOCK_DIR FORGE_WORKTREE_DIR; do
    dir=$(grep "^${dir_key}=" "$FORGE_ROOT/config/forge.env" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    if [ -n "$dir" ]; then
        mkdir -p "$dir"
        ok "$dir"
    fi
done

# 6. Linear MCP connection check
echo "[6/6] Linear MCP connection"
if claude mcp list 2>/dev/null | grep -q linear; then
    ok "linear-server MCP configured"
else
    warn "linear-server MCP not found — configure with: claude mcp add"
    errors=$((errors + 1))
fi

echo
if [ "$errors" -eq 0 ]; then
    echo -e "${GREEN}Setup complete${NC}"
else
    echo -e "${YELLOW}${errors} issue(s) found. Please review above${NC}"
    exit 1
fi
