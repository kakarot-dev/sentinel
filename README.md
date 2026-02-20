# Sentinel

Real-time cloud cost anomaly detector. Ingests AWS billing data, detects spending anomalies, and sends alerts before costs spiral.

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Infrastructure:** Docker, GitHub Actions CI

## Development

```bash
# Start all services
docker compose up --build

# API available at http://localhost:8000
# Health check: http://localhost:8000/health

# Run tests
cd backend && pytest tests/ -v
```

## Architecture

```
AWS Cost Explorer API → Ingestion Service → PostgreSQL → Anomaly Detection → Alerts
```

## Status

🚧 Under active development
