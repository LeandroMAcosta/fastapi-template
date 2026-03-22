#!/bin/bash
set -e

TEST_TYPE=${1:-unit}

case $TEST_TYPE in
    unit)
        echo "Running unit tests (no DB)..."
        uv run pytest tests/unit -v --tb=short
        ;;
    e2e)
        echo "Running e2e tests (testcontainers PostgreSQL)..."
        uv run pytest tests/e2e -v --tb=short
        ;;
    all)
        echo "Running all tests..."
        uv run pytest tests/ -v --tb=short
        ;;
    *)
        echo "Usage: ./scripts/test.sh [unit|e2e|all]"
        exit 1
        ;;
esac
