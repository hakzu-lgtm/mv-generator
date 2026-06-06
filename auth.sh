#!/bin/bash
echo "============================================"
echo "   Google Cloud Login (run once per PC)"
echo "============================================"
echo
echo "A browser will open. Sign in with your Google"
echo "account and click Allow."
echo
read -p "Press Enter to open the browser..."

if ! command -v gcloud &>/dev/null; then
    echo
    echo "[ERROR] gcloud not found."
    echo "Install Google Cloud CLI from:"
    echo "  https://cloud.google.com/sdk/docs/install"
    exit 1
fi

gcloud auth application-default login
if [ $? -ne 0 ]; then
    echo "[ERROR] Login failed. Please try again."
    exit 1
fi

echo
read -p "Enter your Google Cloud Project ID (e.g. my-project-123456): " PID
if [ -z "$PID" ]; then
    echo "[ERROR] Project ID cannot be empty. Please run auth.sh again."
    exit 1
fi

echo
echo "Setting quota project..."
gcloud auth application-default set-quota-project "$PID"

echo
echo "Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com --project="$PID"

echo
echo "============================================"
echo " [OK] Login complete!"
echo " You can now run: bash run.sh"
echo "============================================"
