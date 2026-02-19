# Каталог для разработки на Python

Шаблон каталога для создания простых и средних по сложности программ на Python. Содержит структуру проекта, зависимости и инструкции по настройке окружения.

## Структура каталога

```
Publish_Git/
├── src/
│   └── app/              # Исходный код приложения
│       ├── __init__.py
│       └── main.py       # Точка входа
├── tests/                # Тесты
│   ├── __init__.py
│   └── test_main.py
├── scripts/              # Вспомогательные скрипты
│   ├── run_tests.ps1     # Запуск тестов (Windows)
│   └── run_tests.sh      # Запуск тестов (Linux/macOS)
├── requirements.txt      # Базовые зависимости
├── requirements-dev.txt  # Зависимости для разработки
├── pyproject.toml        # Конфигурация проекта и инструментов
├── .gitignore
└── README.md             # Этот файл
```

## Требования

- **Python 3.10** или новее (рекомендуется 3.11+)
- Установленный [Python](https://www.python.org/downloads/) с добавлением в PATH

## Активация и инициализация области разработки

### 1. Перейти в каталог проекта

```powershell
cd d:\Publish_Git
```

(или путь к вашему клонированному/скопированному каталогу)

### 2. Создать виртуальное окружение

Рекомендуется использовать отдельное виртуальное окружение для каждого проекта.

**Windows (PowerShell):**

```powershell
python -m venv .venv
```

**Windows (cmd):**

```cmd
python -m venv .venv
```

**Linux / macOS:**

```bash
python3 -m venv .venv
```

Будет создана папка `.venv` с изолированным интерпретатором и pip.

### 3. Активировать виртуальное окружение

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

Если скрипты запрещены политикой, выполните один раз:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (cmd):**

```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

После активации в начале строки приглашения появится `(.venv)`.

### 4. Установить зависимости

**Только для запуска и простой разработки:**

```powershell
pip install -r requirements.txt
```

**Для полноценной разработки (тесты, линтер, типы):**

```powershell
pip install -r requirements-dev.txt
```

**Или установка проекта в режиме разработки (если используете pyproject.toml):**

```powershell
pip install -e ".[dev]"
```

### 5. Проверить, что всё работает

Запуск приложения (из корня проекта):

```powershell
python src/app/main.py
```

Либо с добавлением `src` в PYTHONPATH (чтобы работало `python -m app.main`):

```powershell
$env:PYTHONPATH = "src"
python -m app.main
```

Запуск тестов:

```powershell
pytest tests/ -v
```

Или используйте скрипты из `scripts/`:

- Windows: `.\scripts\run_tests.ps1`
- Linux/macOS: `./scripts/run_tests.sh`

## Ежедневная работа

1. Открыть каталог в редакторе (например, Cursor / VS Code).
2. Активировать виртуальное окружение в терминале (шаг 3 выше).
3. Писать код в `src/app/`, добавлять тесты в `tests/`.
4. Запускать тесты: `pytest tests/ -v`.
5. Проверять стиль и простые ошибки: `ruff check src tests`.

## Полезные команды

| Действие              | Команда                          |
|-----------------------|-----------------------------------|
| Запуск приложения     | `python -m app.main`              |
| Запуск тестов         | `pytest tests/ -v`                |
| Проверка кода (ruff)  | `ruff check src tests`            |
| Форматирование кода   | `ruff format src tests`           |
| Покрытие тестами      | `pytest tests/ --cov=app --cov-report=term-missing` |

## Деактивация окружения

В терминале, где активировано окружение:

```powershell
deactivate
```

## Дальнейшие шаги

- Переименуйте пакет `app` в `src/` под своё приложение и обновите импорты и `pyproject.toml`.
- Добавляйте новые модули в `src/app/` и тесты в `tests/`.
- При необходимости добавьте зависимости в `requirements.txt` и зафиксируйте версии.

Каталог готов к использованию как основа для ваших программ на Python.
