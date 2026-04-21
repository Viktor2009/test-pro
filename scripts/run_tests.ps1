# Запуск  тестов (PowerShell)
# Использование: .\scripts\run_tests.ps1

Set-Location $PSScriptRoot\..
if (Test-Path .venv\Scripts\Activate.ps1) {
    .\.venv\Scripts\Activate.ps1
}
ruff check src tests
ruff format --check src tests
mypy src/lang_learn
pytest tests/ -v
