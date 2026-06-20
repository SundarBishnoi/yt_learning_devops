#!/bin/bash

# Clear system execution paths so cron can run tools reliably
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Print current timestamp alongside the log message
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Check: Look for active, interactive SSH login bash streams belonging to ubuntu
# This ignores dead ghost sockets and targets actual live window sessions
ACTIVE_TERMINALS=$(ps aux | grep 'sshd: ubuntu@' | grep -v grep | wc -l)

if [ "$ACTIVE_TERMINALS" -eq 0 ]; then
    echo "[$TIMESTAMP] No active interactive SSH windows found (Count: $ACTIVE_TERMINALS). Shutting down." >> /var/log/auto-stop.log
    /sbin/shutdown -h now
else
    echo "[$TIMESTAMP] Interactive VS Code session is live (Count: $ACTIVE_TERMINALS). Keeping instance awake." >> /var/log/auto-stop.log
    
    # 🧹 Log Housekeeping: Keep only the last 50 lines
    if [ -f /var/log/auto-stop.log ]; then
        CLEANED_LOGS=$(tail -n 50 /var/log/auto-stop.log)
        echo "$CLEANED_LOGS" > /var/log/auto-stop.log
    fi
fi

