#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==================================="
echo " MV Generator - 설치"
echo "==================================="
echo

echo "[1/2] Python 패키지 설치 중..."
cd "$SCRIPT_DIR/backend"
pip install -r requirements.txt

echo
echo "[2/2] Node.js 패키지 설치 중..."
cd "$SCRIPT_DIR/frontend"
npm install

echo
echo "==================================="
echo " 설치 완료!"
echo
echo " 다음 순서로 실행하세요:"
echo "   1. bash auth.sh   (Google 계정 로그인 - 처음 한 번)"
echo "   2. bash start.sh  (앱 실행)"
echo "==================================="
