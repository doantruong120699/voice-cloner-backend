# Database Setup Guide

This guide explains how to set up and use PostgreSQL with SQLAlchemy and Alembic for the Voice Cloner backend.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (or use Docker)
- Virtual environment (recommended)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Configuration

The database connection is configured via the `DATABASE_URL` environment variable. You can set it in a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voice_cloner
```

Default format: `postgresql://username:password@host:port/database_name`

## Using Docker Compose (Recommended)

The easiest way to set up PostgreSQL is using Docker Compose:

```bash
# Start PostgreSQL and the API
docker-compose up -d

# The database will be automatically configured
```

## Manual PostgreSQL Setup

1. Install PostgreSQL on your system
2. Create a database:
```sql
CREATE DATABASE voice_cloner;
```

3. Set the `DATABASE_URL` environment variable or add it to `.env`

## Running Migrations

After setting up the database, run Alembic migrations to create the tables:

```bash
# Initialize Alembic (already done, but if needed)
alembic init alembic

# Create a new migration (if you modify models)
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

## Database Models

### User Model
- `user_id` (UUID, Primary Key)
- `email` (String, Unique, Indexed)
- `name` (String, Optional)
- `picture` (Text, Optional)
- `provider` (String, Default: "google")
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Voice Model
- `voice_id` (UUID, Primary Key)
- `filename` (String)
- `file_path` (Text)
- `embedding_path` (Text, Optional)
- `duration` (Float, Optional)
- `sample_rate` (Integer, Optional)
- `name` (String, Optional)
- `description` (Text, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Storage Layer

The storage layer (`app/models/storage.py`) has been updated to use SQLAlchemy while maintaining backward compatibility. The `UserStorage` and `VoiceStorage` classes now interact with PostgreSQL instead of in-memory storage.

## Troubleshooting

### Connection Issues
- Verify PostgreSQL is running: `pg_isready` or check Docker container
- Check `DATABASE_URL` format is correct
- Ensure database exists: `psql -U postgres -l`

### Migration Issues
- Make sure database is accessible
- Check Alembic configuration in `alembic.ini` and `alembic/env.py`
- Verify all models are imported in `alembic/env.py`

### UUID Issues
- PostgreSQL must have the `uuid-ossp` extension (usually enabled by default)
- If using custom UUID generation, ensure it's compatible with PostgreSQL UUID type

## Development Tips

1. **Use database sessions properly**: The storage classes handle session management automatically, but you can also pass a session explicitly for transactions.

2. **Test migrations**: Always test migrations on a development database before applying to production.

3. **Backup before migrations**: In production, always backup your database before running migrations.

4. **Use Alembic autogenerate carefully**: Review generated migrations before applying, especially for complex schema changes.
