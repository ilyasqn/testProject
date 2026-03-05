# Pet Project — Microservices API

A microservices-based REST API built with FastAPI, PostgreSQL, RabbitMQ, Redis, and Kubernetes. Includes full observability with Prometheus, Loki, and Grafana.

## Services

| Service | Port | Description |
|---|---|---|
| user-service | 8001 | User registration & JWT authentication |
| product-service | 8002 | Product management & Saga executor |
| notification-service | 8003 | Telegram notifications & notification history |
| order-service | 8004 | Order management & Saga initiator |
| Prometheus | 9090 | Metrics collection (scrapes `/metrics` from all services) |
| Grafana | 3000 | Dashboards & log exploration (login: `admin` / `admin`) |
| Loki | 3100 | Log aggregation (internal, accessed via Grafana) |

## Architecture

```
user-service         → PostgreSQL (user_db)
                     → RabbitMQ (publishes: user.registered, user.authenticated)

product-service      → PostgreSQL (product_db)
                     → Redis (product caching)
                     → RabbitMQ (consumes: order.create_requested)
                                (publishes: product.created/updated/deleted, order.confirmed, order.cancelled)

order-service        → PostgreSQL (order_db)
                     → RabbitMQ (consumes: order.confirmed, order.cancelled, product.deleted)
                                (publishes: order.create_requested)

notification-service → PostgreSQL (notification_db)
                     → RabbitMQ (consumes all events, sends Telegram notifications)

all services         → Prometheus (/metrics endpoint, scraped every 15s)
Promtail (DaemonSet) → Loki (ships pod logs)
Grafana              → Prometheus + Loki (dashboards & explore)
```

### Order Saga Flow

```
POST /api/orders/
  │
  ├─ order-service  → creates order (status: pending)
  │                 → publishes order.create_requested
  │
  ├─ product-service (consumes order.create_requested)
  │                 → decrements stock, invalidates cache
  │                 → publishes order.confirmed  (stock OK)
  │                 → publishes order.cancelled  (product not found / insufficient stock)
  │
  └─ order-service  (consumes order.confirmed / order.cancelled)
                    → updates order status + total_price
```

### Product Deletion Behaviour

| Situation | Result |
|---|---|
| Order confirmed, product later deleted | Order stays **confirmed** — historical record preserved |
| Order pending when product is deleted | Order auto-**cancelled** via `product.deleted` event |
| Create order for a deleted product | Order created then immediately **cancelled** — reason: `product not found` |

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Databases**: PostgreSQL 16 (separate DB per service)
- **Message Broker**: RabbitMQ (topic exchanges, durable queues)
- **Cache**: Redis 7
- **Monitoring**: Prometheus + Grafana (metrics), Loki + Promtail (logs)
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Quick Start

```bash
./start.sh
```

This single command will:
1. Start Minikube if not running
2. Build all Docker images inside Minikube's daemon
3. Apply Kubernetes manifests
4. Wait for all pods to be ready
5. Port-forward all services to localhost

> **First run only** — run Alembic migrations for order-service:
> ```bash
> kubectl exec -n pet $(kubectl get pods -n pet -l app=order-service -o jsonpath='{.items[0].metadata.name}') \
>   -- alembic upgrade head
> ```

## API Endpoints

### User Service — `http://localhost:8001`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/user/` | No | Register a new user |
| GET | `/api/user/` | Yes | Get all users |
| POST | `/api/jwt/tokens` | No | Login — returns access + refresh tokens |
| POST | `/api/jwt/refresh_token` | No | Refresh access token |

### Product Service — `http://localhost:8002`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/products/` | No | List all products (cached) |
| GET | `/api/products/{id}` | No | Get product by ID (cached) |
| POST | `/api/products/` | Yes | Create a product |
| PUT | `/api/products/{id}` | Yes | Update a product |
| DELETE | `/api/products/{id}` | Yes | Delete a product |

### Order Service — `http://localhost:8004`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/orders/` | Yes | Create an order (starts Saga) |
| GET | `/api/orders/` | Yes | List your orders |
| GET | `/api/orders/{id}` | Yes | Get order by ID |

### Notification Service — `http://localhost:8003`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications/` | No | Get all notifications |

## Interactive API Docs

- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Order Service: http://localhost:8004/docs
- Notification Service: http://localhost:8003/docs

## Authentication

1. Register via `POST /api/user/`
2. Login via `POST /api/jwt/tokens` — returns `access_token` and `refresh_token`
3. Pass `access_token` in the `Authorization: Bearer <token>` header for protected endpoints
4. Refresh via `POST /api/jwt/refresh_token` when access token expires

Token expiry:
- Access token: 30 minutes
- Refresh token: 24 hours

## Observability

Every service exposes `/metrics` via `prometheus-fastapi-instrumentator`, scraped by Prometheus every 15s. Promtail ships pod logs to Loki. Grafana provides dashboards and log exploration.

**Key metrics** (exposed by all services):
- `http_requests_total` — request count by `handler`, `method`, `status`
- `http_request_duration_seconds` — latency histogram by handler
- `http_request_duration_highr_seconds` — high-resolution latency (accurate percentiles)
- `http_request_size_bytes` / `http_response_size_bytes` — payload sizes
- `process_resident_memory_bytes`, `process_cpu_seconds_total` — resource usage

**Logs**: query with `{namespace="pet"}` in Grafana → Explore → Loki

## Kubernetes

All services run in the `pet` namespace:

| Deployment | Replicas | HPA |
|---|---|---|
| user-service | 4 | 2–8 replicas, 70% CPU |
| product-service | 4 | 2–8 replicas, 70% CPU |
| order-service | 4 | 2–8 replicas, 70% CPU |
| notification-service | 1 | — |

### Useful Commands

```bash
# Check pod status
kubectl get pods -n pet

# View logs of a service
kubectl logs -l app=order-service -n pet --tail=50

# Check all resources
kubectl get all -n pet

# Run migrations (order-service)
kubectl exec -n pet $(kubectl get pods -n pet -l app=order-service -o jsonpath='{.items[0].metadata.name}') \
  -- alembic upgrade head
```

## Testing

Tests are written with `pytest` + `pytest-asyncio`. All dependencies (DB, Redis, RabbitMQ, Telegram) are mocked — no running infrastructure needed.

**63 tests total** across all four services:

| Service | Tests | Coverage |
|---|---|---|
| user_service | 14 | API endpoints, service logic, JWT token creation |
| product_service | 20 | API endpoints, service logic, cache behaviour, `decrement_stock` |
| order_service | 15 | API endpoints, service logic, saga event handlers |
| notification_service | 14 | API endpoint, service logic, event handler, formatters |

### Setup (one-time)

From the project root (`pet/`):

```bash
python3 -m venv .venv
.venv/bin/pip install -e shared/
.venv/bin/pip install \
  -r services/user_service/requirements.txt \
  -r services/product_service/requirements.txt \
  -r services/notification_service/requirements.txt \
  -r services/order_service/requirements.txt \
  pytest pytest-asyncio httpx pytest-mock
```

### Running Tests

Run a single service:

```bash
cd services/user_service
../../.venv/bin/python -m pytest tests/ -v
```

Run all services:

```bash
VENV=$(pwd)/.venv/bin/python
for svc in user_service product_service order_service notification_service; do
  echo "=== $svc ===" && cd services/$svc && $VENV -m pytest tests/ -v && cd ../..
done
```

### Test Structure

Each service has a `tests/` directory:

```
tests/
├── conftest.py          # shared fixtures: mock_uow, mock_service, client
├── test_api_*.py        # HTTP layer — status codes, response shape, auth enforcement
├── test_service_*.py    # Business logic — mocked UoW, event publishing, exceptions
├── test_handlers.py     # Event handlers — saga confirmed/cancelled, cascades
└── test_repo_*.py       # Repository logic — decrement_stock edge cases
```

## Project Structure

```
.
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── user-db.yaml            user-service.yaml
│   ├── product-db.yaml         product-service.yaml
│   ├── notification-db.yaml    notification-service.yaml
│   ├── order-db.yaml           order-service.yaml
│   ├── rabbitmq.yaml           redis.yaml
│   ├── prometheus.yaml         grafana.yaml
│   └── loki.yaml               promtail.yaml
├── services/
│   ├── user_service/
│   │   └── tests/              # 14 tests (api, service, auth)
│   ├── product_service/
│   │   └── tests/              # 20 tests (api, service, repo)
│   ├── order_service/
│   │   └── tests/              # 15 tests (api, service, handlers)
│   └── notification_service/
│       └── tests/              # 14 tests (api, service, handler, formatters)
├── shared/                     # Shared library (UoW, repo, broker, cache, exceptions)
├── .venv/                      # Shared virtual environment for local testing
├── start.sh                    # One-command startup script
└── README.md
```
