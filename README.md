# Test Pro

Python проект.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
- Windows:
```bash
venv\Scripts\activate
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
├── src/              # Исходный код проекта
│   └── test_pro/     # Основной пакет
├── tests/            # Тесты
├── docs/             # Документация (опционально)
├── requirements.txt  # Зависимости проекта
├── requirements-dev.txt  # Зависимости для разработки
├── pyproject.toml    # Конфигурация проекта
└── README.md         # Этот файл
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

# Линтинг
flake8 src tests
ruff check src tests

# Проверка типов
mypy src
```

## Лицензия

MIT
