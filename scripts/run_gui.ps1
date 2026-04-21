# Запуск GUI без предварительного pip install -e .
# Использует интерпретатор из PATH (активируйте .venv и вызывайте: .\scripts\run_gui.ps1)
# Секреты: при запуске через "python -m lang_learn gui" подхватывается .env автоматически.
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = (Join-Path $ProjectRoot "src")
Set-Location $ProjectRoot
& python -m lang_learn gui
