# Test Pro

Python проект.

## Установка параметров

1. Создайте виртуальное окружение в папке `.venv`:
```bash
python -m venv .venv
```

2. Активируйте виртуальное окружение:
- Windows:
```bash
.venv\Scripts\Activate.ps1
```
- Linux/Mac:
```bash
source .venv/bin/activate
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

## Обновление на GitHub

При записи изменений на GitHub «комментариями» к обновлениям служат **сообщения коммитов** (commit message): каждое изменение сохраняется с текстом коммита и отображается в истории репозитория на GitHub. Для обновления после правок выполните:
```bash
git add .
git commit -m "Краткое описание изменений 2"
git push
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
