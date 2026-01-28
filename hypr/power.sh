#!/bin/bash

# Path to hypridle
IDLE_BINARY="hypridle"

while true; do
    # Check if AC adapter is online (1 = charging, 0 = discharging)
    # Note: Path might vary (e.g., ADP1 or ACAD). Check /sys/class/power_supply/
    STATUS=$(cat /sys/class/power_supply/ADP1/online)

    if [ "$STATUS" -eq 1 ]; then
        # It's charging: Kill hypridle if it's running
        if pgrep -x "$IDLE_BINARY" > /dev/null; then
            pkill "$IDLE_BINARY"
        fi
    else
        # Not charging: Start hypridle if it's NOT running
        if ! pgrep -x "$IDLE_BINARY" > /dev/null; then
            hypridle &
        fi
    fi

    # Wait 5 seconds before checking again to save CPU
    sleep 5
done
