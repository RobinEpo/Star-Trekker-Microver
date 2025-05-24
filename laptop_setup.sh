#!/bin/bash

# Absolute or relative paths to your Python scripts
RCVER="python/sensorsrec.py"
CTRLER="python/laptop_ctrl.py"

# Launch each script in a new Konsole window
konsole --noclose -e python3 "$RCVER" &
konsole --noclose -e python3 "$CTRLER" &
