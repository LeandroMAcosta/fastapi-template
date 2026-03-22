#!/bin/bash
set -e
uv run ruff check --fix .
uv run ruff format .
echo "Linting and formatting done."
