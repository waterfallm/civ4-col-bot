#!/bin/bash
# Build ARM64 image on Pi and deploy to k3s
set -euo pipefail

NAMESPACE="civ4bot"
IMAGE="civ4bot:latest"
DEPLOYMENT="civ4bot"

echo "🔨 Building ARM64 Docker image: ${IMAGE}"
docker build -t "${IMAGE}" .

echo "☸️  Applying Kubernetes manifests…"
kubectl apply -f k8s/

echo "⏳ Waiting for rollout to complete…"
kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"

echo ""
echo "✅ Bot deployed at http://civ4bot.local"
echo "   Health:  curl http://civ4bot.local/healthz"
echo "   Status:  curl http://civ4bot.local/status"
echo "   Trigger: curl -X POST http://civ4bot.local/next-turn"
