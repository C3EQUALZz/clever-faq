## Mini-service **Clever-FAQ**

Backend-сервис, который обрабатывает вопросы пользователей и отвечает на них, используя базу знаний.

### Tech Stack

| Tool                  | Role                                  |
|-----------------------|---------------------------------------|
| **FastAPI**           | High‑performance async REST framework |
| **Dishka**            | IoC container (replaces FastAPI DI)   |
| **Taskiq + RabbitMQ** | Async task queue & message broker     |
| **PostgreSQL**        | Primary relational storage            |
| **Redis**             | Caching & Taskiq result backend       |
| **MinIO**             | S3‑compatible object storage          |
| **LangChain**         | Library for interacting with LLM      |
| **ChromaDB**          | Vector store                          |

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Git
- Python 3.12+ (for local development)
- Just

### Setup

```sh
git clone https://github.com/C3EQUALZz/clever-faq
cd clever-faq

cp .env.dist .env

just up
```

> [!NOTE]
> If you don't have `just` on PC, please use this command: `docker compose -f docker-compose.dev.yaml --profile api up --build -d`

### Default Endpoints

| Service                   | URL                            |
|---------------------------|--------------------------------|
| **Backend API** (Swagger) | http://localhost:8080/api/docs |
| **Grafana**               | http://localhost:3000          |
| **MinIO Console**         | http://localhost:9001          |
| **RabbitMQ UI**           | http://localhost:15672         |


### Configuration Management

Following the twelve-factor app methodology, configuration is managed via environment variables (commonly referred to as
env vars). These variables offer a flexible way to adjust settings across deployments without altering the codebase.
Unlike traditional config files, they minimize the risk of accidental inclusion in version control and provide a
universal, language- and OS-independent approach to configuration.

- Backend configuration: `src/pix_erase/setup/config/`
- Sample environment file: `.env.dist`

The configuration system leverages these env vars to define service settings.
See [Environment Variables](docs/getting-started/configuration.md) for detailed documentation.
Following the twelve-factor app methodology, configuration is managed via environment variables (commonly referred to as
env vars). These variables offer a flexible way to adjust settings across deployments without altering the codebase.
Unlike traditional config files, they minimize the risk of accidental inclusion in version control and provide a
universal, language- and OS-independent approach to configuration.

## Architectural Approach: Clean Architecture

### Core Concept

The best architecture often emerges late in development, once the codebase takes shape.

> A solid architecture postpones decisions until the last responsible moment.

### Guiding Principle

Dependency Inversion (from SOLID) drives our use of dependency injection. Dependencies flow inward, from outer tools to
inner business logic, ensuring the latter remains isolated. This splits the app into two primary layers:

1. **Inner Layer:** Business logic (use cases).
2. **External Layer:** Tools (databases, servers, brokers, external libraries).

**Inner Layer Rules** with business logic should be clean. It should:

- Not import from the outer layer.
- Rely solely on Python's standard library.
- Communicate with the outer layer via interfaces.

The business logic is agnostic to specifics like PostgreSQL or REST APIs—it interacts with abstract interfaces instead.

**External Layer Constraints** has other limitations:

- Components (e.g., HTTP servers, databases) don't directly interact with each other.
- Communication with the core layer happens through interfaces.
- Data is formatted to suit the business logic.

For instance, fetching data from a database via an HTTP request:

```raw
  HTTP → Use Case
        Use Case → Repository (e.g., Postgres)
        Use Case ← Repository
  HTTP ← Use Case
```

A more intricate flow might look like:

```raw
HTTP → Use Case
        Use Case → Repository
        Use Case ← Repository
        Use Case → External API
        Use Case ← External API
        Use Case → Message Queue
        Use Case ← Message Queue
        Use Case → Repository
        Use Case ← Repository
  HTTP ← Use Casearly identical, differing mainly in naming conventions.
```
