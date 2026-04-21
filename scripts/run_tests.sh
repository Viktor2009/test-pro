#!/usr/bin/env  bash
# Запуск тестов (Linux/macOS)
# Использование: ./scripts/run_tests.sh

cd "$(dirname "$0")/.."
[ -f .venv/bin/activate ] && source .venv/bin/activate
ruff check src tests
ruff format --check src tests
mypy src/lang_learn
pytest tests/ -v
