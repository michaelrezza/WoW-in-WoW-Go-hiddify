#!/bin/bash

LOG_FILE="logs/restart-log.txt"
WARP_SCRIPT="scripts/warp-go.sh"
MAX_RETRIES=5
RETRY_DELAY=10

mkdir -p logs

for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "🔄 Attempt #$i to restart WARP..." | tee -a "$LOG_FILE"

    if bash "$WARP_SCRIPT"; then
        echo "✅ WARP successfully executed on attempt $i" | tee -a "$LOG_FILE"
        exit 0
    fi

    echo "❌ Execution failed! Waiting for $RETRY_DELAY seconds before retrying..." | tee -a "$LOG_FILE"
    sleep "$RETRY_DELAY"
done

echo "🚨 All attempts failed! Please check the logs for details." | tee -a "$LOG_FILE"
exit 1