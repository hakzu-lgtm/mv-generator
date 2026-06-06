#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Stopping MV Generator servers..."

# Kill by saved PIDs (background mode)
if [ -f "$SCRIPT_DIR/.server_pids" ]; then
    read -r BACKEND_PID FRONTEND_PID < "$SCRIPT_DIR/.server_pids"
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null && echo "[OK] Backend stopped (PID $BACKEND_PID)"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && echo "[OK] Frontend stopped (PID $FRONTEND_PID)"
    rm -f "$SCRIPT_DIR/.server_pids"
fi

# Also kill by port in case of leftover processes
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null && echo "[OK] Cleared port 8000"
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null && echo "[OK] Cleared port 5173"

echo "Done."
