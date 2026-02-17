# Test Pro

Python проект.

## Установка параметров

1. Создайте виртуальное окружение (имя без точки — `venv` или со скрытой папкой — `.venv`):
```bash
python -m venv venv
```
или
```bash
python -m venv .venv
```

2. Активируйте виртуальное окружение:
- Windows (`venv`):
```bash
venv\Scripts\activate
```
- Windows (`.venv`):
```bash
.venv\Scripts\Activate.ps1
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

Для разработки:
```bash
pip install -r requirements-dev.txt
```

## Структура проекта

```
.
├── src/                  # Исходный код проекта
│   └── test_pro/         # Основной пакет
├── tests/                # Тесты
├── scripts/              # Вспомогательные скрипты (например, publish_to_github.py)
├── requirements.txt      # Зависимости проекта
├── requirements-dev.txt  # Зависимости для разработки
├── pyproject.toml        # Конфигурация проекта
└── README.md             # Этот файл
```

## Разработка

### Запуск тестов
```bash
pytest
```

### Проверка кода
```bash
# Форматирование
black src tests

# Линтинг (достаточно ruff; flake8 опционален)
ruff check src tests

# Проверка типов
mypy src
```

## Лицензия

MIT
