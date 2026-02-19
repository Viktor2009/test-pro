# Запуск  тестов (PowerShell)
# Использование: .\scripts\run_tests.ps1

Set-Location $PSScriptRoot\..
if (Test-Path .venv\Scripts\Activate.ps1) {
    .\.venv\Scripts\Activate.ps1
}
pytest tests/ -v
