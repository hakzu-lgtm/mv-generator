#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "   MV Generator - Music Video Maker"
echo "============================================"
echo

# --- Check required programs ---
echo "[Check] Verifying installed programs..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "[ERROR] Python not found."
    echo "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js not found."
    echo "Install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
if ! command -v ffmpeg &>/dev/null; then
    echo "[WARN] FFmpeg not found. Video export may fail."
fi
if ! command -v gcloud &>/dev/null; then
    echo "[WARN] gcloud not found. Run: bash auth.sh"
fi
echo "[OK] Checks done."
echo

PYTHON=$(command -v python3 || command -v python)

# --- Install backend deps ---
echo "[1/3] Installing backend packages..."
cd "$SCRIPT_DIR/backend"
$PYTHON -m pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[ERROR] Backend install failed."
    exit 1
fi
cd "$SCRIPT_DIR"

# --- Install frontend deps if missing ---
echo "[2/3] Checking frontend packages..."
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "Installing frontend packages (first run - may take a few minutes)..."
    cd "$SCRIPT_DIR/frontend"
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Frontend install failed."
        exit 1
    fi
    cd "$SCRIPT_DIR"
else
    echo "[OK] Frontend packages already installed."
fi
echo

# --- Launch servers ---
echo "[3/3] Starting servers..."

open_browser() {
    sleep 8
    if command -v open &>/dev/null; then
        open http://localhost:5173
    elif command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:5173
    fi
}

if command -v osascript &>/dev/null; then
    # macOS: open separate Terminal windows
    osascript -e "tell app \"Terminal\" to do script \"echo '=== MV-Backend ===' && cd '$SCRIPT_DIR/backend' && $PYTHON -m uvicorn main:app --port 8000\""
    sleep 6
    osascript -e "tell app \"Terminal\" to do script \"echo '=== MV-Frontend ===' && cd '$SCRIPT_DIR/frontend' && npm run dev\""
    open_browser &
    echo
    echo "============================================"
    echo " App is running at http://localhost:5173"
    echo " Keep the Terminal windows open."
    echo " To stop: bash stop.sh"
    echo "============================================"
elif command -v gnome-terminal &>/dev/null; then
    # Linux GNOME
    gnome-terminal --title="MV-Backend"  -- bash -c "echo '=== MV-Backend ===' && cd '$SCRIPT_DIR/backend' && $PYTHON -m uvicorn main:app --port 8000; exec bash"
    sleep 6
    gnome-terminal --title="MV-Frontend" -- bash -c "echo '=== MV-Frontend ===' && cd '$SCRIPT_DIR/frontend' && npm run dev; exec bash"
    open_browser &
    echo
    echo "============================================"
    echo " App is running at http://localhost:5173"
    echo " To stop: bash stop.sh"
    echo "============================================"
else
    # Fallback: background processes with log files
    echo "Starting in background mode (no GUI terminal detected)..."
    cd "$SCRIPT_DIR/backend"
    $PYTHON -m uvicorn main:app --port 8000 > "$SCRIPT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "[OK] Backend PID=$BACKEND_PID  (log: backend.log)"
    sleep 6

    cd "$SCRIPT_DIR/frontend"
    npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo "[OK] Frontend PID=$FRONTEND_PID  (log: frontend.log)"

    echo "$BACKEND_PID $FRONTEND_PID" > "$SCRIPT_DIR/.server_pids"

    open_browser &

    echo
    echo "============================================"
    echo " App is running at http://localhost:5173"
    echo " Logs: backend.log / frontend.log"
    echo " To stop: bash stop.sh"
    echo "============================================"

    wait $BACKEND_PID
fi
