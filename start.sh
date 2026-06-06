#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==================================="
echo " MV Generator 시작"
echo "==================================="
echo

echo "[1] 백엔드 서버 시작 (포트 8000)..."
if command -v osascript &> /dev/null; then
    # macOS
    osascript -e "tell app \"Terminal\" to do script \"cd '$SCRIPT_DIR/backend' && uvicorn main:app --reload --port 8000\""
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && uvicorn main:app --reload --port 8000; exec bash"
else
    cd "$SCRIPT_DIR/backend" && uvicorn main:app --reload --port 8000 &
    BACKEND_PID=$!
fi

sleep 3

echo "[2] 프론트엔드 시작 (포트 5173)..."
if command -v osascript &> /dev/null; then
    osascript -e "tell app \"Terminal\" to do script \"cd '$SCRIPT_DIR/frontend' && npm run dev\""
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/frontend' && npm run dev; exec bash"
else
    cd "$SCRIPT_DIR/frontend" && npm run dev &
    FRONTEND_PID=$!
fi

sleep 5

echo "[3] 브라우저 열기..."
if command -v open &> /dev/null; then
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
fi

echo
echo "백엔드:  http://localhost:8000"
echo "앱:      http://localhost:5173"
echo
echo "종료: Ctrl+C 또는 각 터미널 창을 닫으세요."

# 백그라운드 모드로 실행된 경우만 대기
if [ -n "$BACKEND_PID" ]; then
    wait
fi
