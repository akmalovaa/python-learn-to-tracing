#!/bin/bash

# Script to run Alembic commands in Docker container
# Usage: ./scripts/alembic.sh <alembic-command>
# Examples:
#   ./scripts/alembic.sh current
#   ./scripts/alembic.sh upgrade head
#   ./scripts/alembic.sh downgrade -1
#   ./scripts/alembic.sh revision --autogenerate -m "description"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <alembic-command>"
    echo "Examples:"
    echo "  $0 current"
    echo "  $0 upgrade head"
    echo "  $0 downgrade -1"
    echo "  $0 revision --autogenerate -m \"description\""
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Run alembic command in container
docker-compose run --rm python_app bash -c "cd otel_py_example && PYTHONPATH=/app alembic $*"
