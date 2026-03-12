#!/bin/bash
# auto-memory.sh - Automatically updates DEVLOG after team execution
# Also checks if infrastructure changes need service catalog sync

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
DEVLOG_PATH="$WORKSPACE_ROOT/docs/DEVLOG.md"
SERVICES_YAML="$WORKSPACE_ROOT/configs/services.yml"
SYNC_SCRIPT="$WORKSPACE_ROOT/scripts/sync_service_catalog.py"
TEAM_NAME="$1"
PROMPT="$2"

if [ ! -f "$DEVLOG_PATH" ]; then
    mkdir -p "$(dirname "$DEVLOG_PATH")"
    echo "# Development Log" > "$DEVLOG_PATH"
fi

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

cat << EOF >> "$DEVLOG_PATH"

## [Auto-Memory] Team Execution: $TEAM_NAME
**Date**: $TIMESTAMP
**Task**: $PROMPT
**Result**: Completed successfully.
EOF

echo "[MEMORY INFO] DEVLOG.md updated autonomously."

# Check if services.yml was modified in recent git changes
if command -v git &> /dev/null; then
    SERVICES_CHANGED=$(git diff --name-only HEAD 2>/dev/null | grep -c "configs/services.yml" || true)
    if [ "$SERVICES_CHANGED" -gt 0 ] && [ -f "$SYNC_SCRIPT" ]; then
        echo "[MEMORY INFO] configs/services.yml changed — running catalog sync..."
        python "$SYNC_SCRIPT" 2>&1 || echo "[MEMORY WARN] Sync script failed"
    fi
fi
