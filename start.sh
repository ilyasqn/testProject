#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start minikube if not running
if ! minikube status | grep -q "Running"; then
  echo "Starting minikube..."
  minikube start
fi

# Build Docker images
echo "Building Docker images..."
docker build -f services/user_service/Dockerfile -t user-service:latest .
docker build -f services/product_service/Dockerfile -t product-service:latest .
docker build -f services/notification_service/Dockerfile -t notification-service:latest .

# Load images into minikube
echo "Loading images into minikube..."
minikube image load user-service:latest
minikube image load product-service:latest
minikube image load notification-service:latest

# Apply k8s manifests
echo "Applying k8s manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --all -n pet --timeout=120s

# Port forward all services in background
echo "Port forwarding services..."
kubectl port-forward svc/user-service 8001:8001 -n pet &
kubectl port-forward svc/product-service 8002:8002 -n pet &
kubectl port-forward svc/notification-service 8003:8003 -n pet &

echo ""
echo "Services available at:"
echo "  user-service         -> http://localhost:8001"
echo "  product-service      -> http://localhost:8002"
echo "  notification-service -> http://localhost:8003"

wait
