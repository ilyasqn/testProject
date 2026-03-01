# Pet Project — Microservices API

A microservices-based REST API built with FastAPI, PostgreSQL, RabbitMQ, Redis, and Kubernetes.

## Services

| Service | Port | Description |
|---|---|---|
| user-service | 8001 | User registration & JWT authentication |
| product-service | 8002 | Products & orders management |
| notification-service | 8003 | Telegram notifications & notification history |

## Architecture

```
user-service       → PostgreSQL (user_db)
                   → RabbitMQ (publishes user_authenticated events)

product-service    → PostgreSQL (product_db)
                   → Redis (caching)
                   → RabbitMQ (publishes order events)

notification-service → PostgreSQL (notification_db)
                     → RabbitMQ (consumes events, sends Telegram notifications)
```

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Databases**: PostgreSQL 16 (separate DB per service)
- **Message Broker**: RabbitMQ 3
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
2. Build all Docker images
3. Load images into Minikube
4. Apply Kubernetes manifests
5. Wait for all pods to be ready
6. Port forward all services to localhost

## API Endpoints

### User Service — `http://localhost:8001`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/user/` | No | Register a new user |
| GET | `/api/user/` | Yes | Get all users |
| POST | `/api/jwt/tokens` | No | Login and get access + refresh tokens |
| POST | `/api/jwt/refresh_token` | No | Refresh access token |

### Product Service — `http://localhost:8002`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/products/` | No | List all products |
| GET | `/api/products/{id}` | No | Get product by ID |
| POST | `/api/products/` | Yes | Create a product |
| PUT | `/api/products/{id}` | Yes | Update a product |
| DELETE | `/api/products/{id}` | Yes | Delete a product |
| POST | `/api/orders/` | Yes | Create an order |
| GET | `/api/orders/` | Yes | List your orders |
| GET | `/api/orders/{id}` | Yes | Get order by ID |

### Notification Service — `http://localhost:8003`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications/` | No | Get all notifications |

## Interactive API Docs

Each service exposes Swagger UI:

- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Notification Service: http://localhost:8003/docs

## Authentication

The API uses JWT Bearer tokens. To authenticate:

1. Register a user via `POST /api/user/`
2. Login via `POST /api/jwt/tokens` to get `access_token` and `refresh_token`
3. Pass the `access_token` in the `Authorization: Bearer <token>` header for protected endpoints
4. Use `POST /api/jwt/refresh_token` to get a new access token when it expires

Token expiry:
- Access token: 30 minutes
- Refresh token: 24 hours

## Kubernetes

All services run in the `pet` namespace with the following setup:

- `user-service`: 4 replicas, HPA (2–8 replicas, 70% CPU target)
- `product-service`: 4 replicas, HPA (2–8 replicas, 70% CPU target)
- `notification-service`: 1 replica

### Useful Commands

```bash
# Check pod status
kubectl get pods -n pet

# View logs of a service
kubectl logs -l app=user-service -n pet

# Check all resources
kubectl get all -n pet
```

## Project Structure

```
.
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── user-service.yaml
│   ├── product-service.yaml
│   ├── notification-service.yaml
│   ├── user-db.yaml
│   ├── product-db.yaml
│   ├── notification-db.yaml
│   ├── rabbitmq.yaml
│   └── redis.yaml
├── services/
│   ├── user_service/           # User & auth service
│   ├── product_service/        # Products & orders service
│   └── notification_service/   # Notification service
├── shared/                     # Shared utilities across services
├── start.sh                    # One-command startup script
└── README.md
```
