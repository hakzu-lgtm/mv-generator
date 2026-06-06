#!/bin/bash
echo "==================================="
echo " Google Cloud 로그인"
echo "==================================="
echo
echo "브라우저가 열리면 본인 Google 계정으로 로그인하세요."
echo

if ! command -v gcloud &> /dev/null; then
    echo "[오류] gcloud를 찾을 수 없습니다."
    echo "Google Cloud CLI 설치: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

gcloud auth application-default login

echo
read -p "Google Cloud Project ID 입력 (예: my-project-123456): " PID
if [ -z "$PID" ]; then
    echo "Project ID가 비어 있습니다. 다시 실행하세요."
    exit 1
fi

echo
echo "프로젝트 설정 중..."
gcloud auth application-default set-quota-project "$PID"

echo
echo "Vertex AI API 활성화 중... (처음에만 1~2분 소요)"
gcloud services enable aiplatform.googleapis.com --project="$PID"

echo
echo "==================================="
echo " 로그인 완료!"
echo " 이제 bash start.sh 를 실행하세요."
echo "==================================="
