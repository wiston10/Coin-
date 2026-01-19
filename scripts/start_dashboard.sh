#!/usr/bin/env bash
# Start the dashboard in background and capture logs + pid
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/run_dashboard.pid"
mkdir -p "$LOG_DIR"
cd "$ROOT_DIR"
nohup python3 run_gui.py > "$LOG_DIR/dashboard.log" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Started dashboard (PID=$PID). Logs: $LOG_DIR/dashboard.log"
