# Pet Project — Microservices API

A microservices-based REST API built with FastAPI, PostgreSQL, RabbitMQ, Redis, and Kubernetes.

## Services

| Service | Port | Description |
|---|---|---|
| user-service | 8001 | User registration & JWT authentication |
| product-service | 8002 | Product management & Saga executor |
| notification-service | 8003 | Telegram notifications & notification history |
| order-service | 8004 | Order management & Saga initiator |

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

## Project Structure

```
.
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── user-db.yaml            user-service.yaml
│   ├── product-db.yaml         product-service.yaml
│   ├── notification-db.yaml    notification-service.yaml
│   ├── order-db.yaml           order-service.yaml
│   ├── rabbitmq.yaml
│   └── redis.yaml
├── services/
│   ├── user_service/           # User & auth (publishes events)
│   ├── product_service/        # Products + Saga executor
│   ├── order_service/          # Orders + Saga initiator
│   └── notification_service/   # Event consumer → Telegram
├── shared/                     # Shared library (UoW, repo, broker, cache, exceptions)
├── start.sh                    # One-command startup script
└── README.md
```
