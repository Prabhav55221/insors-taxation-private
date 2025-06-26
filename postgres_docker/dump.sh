#!/bin/bash
# setup_database.sh

set -e

echo "Setting up Insors PostgreSQL Database..."

DOCKER_DIR="/Users/prabhavsingh/Documents/Insors/insors-taxation-private/docker"
DUMP_FILE="/Users/prabhavsingh/Documents/Insors/insors-taxation-private/dumps/postgres_localhost-2025_06_25_11_44_12-dump.sql"

if [ ! -d "$DOCKER_DIR" ]; then
    echo "Error: Docker directory not found: $DOCKER_DIR"
    exit 1
fi

if [ ! -f "$DUMP_FILE" ]; then
    echo "Error: Dump file not found: $DUMP_FILE"
    exit 1
fi

cd "$DOCKER_DIR"

echo "Checking if PostgreSQL is running..."
if docker-compose ps postgres | grep -q "Up"; then
    echo "PostgreSQL is already running"
else
    echo "Starting PostgreSQL..."
    docker-compose up -d postgres
    
    echo "Waiting for PostgreSQL to be ready..."
    until docker-compose exec postgres pg_isready -U insors_demo -d insors_db; do
        echo "Still waiting..."
        sleep 2
    done
fi

echo "PostgreSQL is ready"

echo "Loading dump file..."
cat "$DUMP_FILE" | docker-compose exec -T postgres psql -U insors_demo -d insors_db

echo "Database setup complete"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5433"
echo "  Database: insors_db"
echo "  Username: insors_demo"
echo "  Password: p@ssW0rd!"