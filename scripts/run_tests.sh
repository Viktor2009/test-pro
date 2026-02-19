#!/usr/bin/env bash
# Запуск тестов (Linux/macOS)
# Использование: ./scripts/run_tests.sh

cd "$(dirname "$0")/.."
[ -f .venv/bin/activate ] && source .venv/bin/activate
pytest tests/ -v
