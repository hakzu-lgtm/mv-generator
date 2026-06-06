#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(command -v python3 || command -v python)

echo "============================================"
echo "   MV Generator - Install Dependencies"
echo "============================================"
echo

echo "[1/2] Installing backend packages..."
cd "$SCRIPT_DIR/backend"
$PYTHON -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Backend install failed."
    echo "Make sure Python 3.10+ is installed: https://www.python.org/downloads/"
    exit 1
fi

echo
echo "[2/2] Installing frontend packages..."
cd "$SCRIPT_DIR/frontend"
npm install
if [ $? -ne 0 ]; then
    echo "[ERROR] Frontend install failed."
    echo "Make sure Node.js 18+ is installed: https://nodejs.org/"
    exit 1
fi

echo
echo "============================================"
echo " [OK] All packages installed!"
echo
echo " Next steps:"
echo "   1. bash auth.sh   (Google login - first time only)"
echo "   2. bash run.sh    (Launch the app)"
echo "============================================"
