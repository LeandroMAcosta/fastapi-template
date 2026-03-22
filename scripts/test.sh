#!/bin/bash
set -e

TEST_TYPE=${1:-unit}

case $TEST_TYPE in
    unit)
        uv run pytest tests/unit -v --tb=short
        ;;
    all)
        uv run pytest tests/ -v --tb=short
        ;;
    *)
        echo "Usage: ./scripts/test.sh [unit|all]"
        exit 1
        ;;
esac
