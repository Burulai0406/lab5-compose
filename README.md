# Lab 5: Multi-Container Docker Compose Application

## Overview

This project uses Docker Compose to run three services:

- Flask API
- PostgreSQL database
- Redis cache

## Prerequisites

- Docker Desktop
- Docker Compose

## Configuration

Create a `.env` file based on `.env.example`.
Set your database credentials and API port.
Never commit `.env` to Git.

## Start the Application

```powershell
docker compose config
docker compose up --build -d
docker compose ps
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/db-test` | Test PostgreSQL connection |
| GET | `/cache-test` | Test Redis connection |
| POST | `/users` | Create a user |
| GET | `/users` | List users |
| GET | `/users/<id>` | Get a user by ID |

API URL: `http://localhost:5000`

## Data Persistence

Named volumes `postgres_data` and `redis_data` store service data.

## Stop the Application

```powershell
docker compose down
```

This removes containers and the network but preserves named volumes.
