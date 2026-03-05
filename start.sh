#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start minikube if not running
if ! minikube status | grep -q "Running"; then
  echo "Starting minikube..."
  minikube start
fi

# Build Docker images inside minikube's Docker daemon
echo "Building Docker images..."
eval $(minikube docker-env)
docker build --no-cache -f services/user_service/Dockerfile         -t user-service:latest .
docker build --no-cache -f services/product_service/Dockerfile      -t product-service:latest .
docker build --no-cache -f services/notification_service/Dockerfile -t notification-service:latest .
docker build --no-cache -f services/order_service/Dockerfile        -t order-service:latest .

# Apply k8s manifests
echo "Applying k8s manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --all -n pet --timeout=120s

# Port forward all services in background
echo "Port forwarding services..."
kubectl port-forward svc/user-service         8001:8001 -n pet &
kubectl port-forward svc/product-service      8002:8002 -n pet &
kubectl port-forward svc/notification-service 8003:8003 -n pet &
kubectl port-forward svc/order-service        8004:8004 -n pet &
kubectl port-forward svc/prometheus           9090:9090 -n pet &
kubectl port-forward svc/grafana              3000:3000 -n pet &

echo ""
echo "Services available at:"
echo "  user-service         -> http://localhost:8001/docs"
echo "  product-service      -> http://localhost:8002/docs"
echo "  notification-service -> http://localhost:8003/docs"
echo "  order-service        -> http://localhost:8004/docs"
echo ""
echo "Observability:"
echo "  Prometheus           -> http://localhost:9090"
echo "  Grafana              -> http://localhost:3000  (admin / admin)"

wait
