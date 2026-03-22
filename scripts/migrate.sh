#!/bin/bash
set -e

ACTION=${1:-upgrade}

case $ACTION in
    upgrade)
        uv run alembic upgrade head
        echo "Migrations applied."
        ;;
    downgrade)
        uv run alembic downgrade -1
        echo "Downgraded one migration."
        ;;
    create)
        if [ -z "$2" ]; then
            echo "Usage: ./scripts/migrate.sh create <message>"
            exit 1
        fi
        uv run alembic revision --autogenerate -m "$2"
        echo "Migration created."
        ;;
    *)
        echo "Usage: ./scripts/migrate.sh [upgrade|downgrade|create <message>]"
        exit 1
        ;;
esac
