#!/bin/bash
# Nightly cleanup of dangling processes
# Run via cron: 0 3 * * * /home/rizki/clawd/scripts/cleanup-processes.sh

LOG="/home/rizki/clawd/memory/cleanup-$(date +%Y-%m-%d).log"
echo "=== Cleanup started: $(date) ===" >> "$LOG"

# Kill orphaned MCP processes (attio-mcp, etc.)
MCP_COUNT=$(pgrep -c -f "node.*mcp" 2>/dev/null) || MCP_COUNT=0
if (( MCP_COUNT > 2 )); then
    echo "Found $MCP_COUNT MCP processes, killing orphans..." >> "$LOG"
    pkill -9 -f "attio-mcp" 2>/dev/null
    pkill -9 -f "node.*mcp" 2>/dev/null
    echo "Killed MCP processes" >> "$LOG"
fi

# Check Chrome renderer count
CHROME_COUNT=$(pgrep -c -f "chrome.*renderer" 2>/dev/null) || CHROME_COUNT=0
if (( CHROME_COUNT > 10 )); then
    echo "Found $CHROME_COUNT Chrome renderers (>10), restarting browser..." >> "$LOG"
    # Stop browser via clawdbot
    source ~/.nvm/nvm.sh
    nvm use 24 > /dev/null 2>&1
    clawdbot browser stop 2>/dev/null
    sleep 2
    clawdbot browser start 2>/dev/null
    echo "Browser restarted" >> "$LOG"
fi

# Report memory
MEM_USED=$(free -h | awk '/^Mem:/ {print $3}')
MEM_TOTAL=$(free -h | awk '/^Mem:/ {print $2}')
echo "Memory: $MEM_USED / $MEM_TOTAL" >> "$LOG"

echo "=== Cleanup finished: $(date) ===" >> "$LOG"
