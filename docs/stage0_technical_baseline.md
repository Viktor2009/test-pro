# Этап 0 — технический baseline (зафиксировано)

Документ фиксирует решения этапа 0 из
`language_learning_module_implementation_plan.md`: стек, границы модулей,
контракты, качество кода и персистентность.

## 1. Роли компонентов

| Слой | Ответственность | Реализация (сейчас) |
|------|-----------------|---------------------|
| Desktop UI | Экраны, кнопки, визуализация прогресса | **часть 1 (этап 8):** `python -m lang_learn gui` (tkinter, `lang_learn.gui`); см. `docs/stage8_gui.md`. |
| Python backend / domain | Контракты провайдеров, схемы данных, учебная логика | пакет `lang_learn` в `src/lang_learn/` |
| Speech | STT/TTS через абстракции | `contracts/` + адаптеры в `providers/` |
| Persistence | Прогресс, попытки, контент | `db/schema.sql`; `lang_learn.persistence` (`SqliteProgressRepository`, `MemoryProgressRepository`) |

## 2. Стек (зафиксировано на этапе 0)

- **Язык:** Python **3.10+** (целевая версия для инструментов — 3.10; локально допустимы новее).
- **Модели данных:** Pydantic v2.
- **Качество:** Ruff (линт + формат, заменяет отдельный flake8 для этого репозитория),
  Mypy (в т.ч. плагин `pydantic.mypy`), Pytest; те же шаги в CI (GitHub Actions).
- **Десктоп-оболочка (по плану этап 8):** отдельное решение; рекомендуемые варианты для Windows:
  - **PySide6 / Qt** — нативный UI, хорошая интеграция с аудиоустройствами;
  - альтернатива: **Flet** (Flutter) или тонкий локальный UI + тот же Python-пакет.
  До выбора конкретного UI весь сценарий проверяется через CLI, тесты и будущие
  интеграционные тесты аудио.

## 3. API-контракты (модули)

Реализованы как ABC в `src/lang_learn/contracts/`:

- `STTProvider`, `TTSProvider`, `LLMProvider`
- `ProgressRepository`, `LessonEngine`

DTO — в `src/lang_learn/schemas/` (в т.ч. `schemas/persistence.py` под строки БД).

## 4. База данных

- **СУБД (этап 0–1):** **SQLite** — один файл, без отдельного сервера, удобно для
  стационарного приложения и тестов.
- **Схема:** декларативный DDL в `db/schema.sql` (таблицы из плана: пользователи,
  профили, уроки, сценарии, попытки, отчёты по произношению, очередь повторений,
  журнал сессий).

Реализация `ProgressRepository` — raw SQL в `persistence/sqlite_progress.py` (ORM не используется).

## 5. Quality gates (локально и CI)

```text
ruff check src tests
ruff format --check src tests
mypy src/lang_learn
pytest tests
```

Скрипты: `scripts/run_tests.ps1`, `scripts/run_tests.sh`.

## 6. Структура репозитория (актуальная)

```text
src/lang_learn/     # домен: contracts, schemas, learning, persistence, providers,
                    # audio_io, services, data, cli.py
db/schema.sql       # DDL SQLite
docs/               # план, baseline, stage1–stage6
.github/workflows/  # CI
```

## 7. Критерий завершения этапа 0

- [x] Зафиксированы стек и границы Python-модуля vs UI.
- [x] Интерфейсы провайдеров и ядра объявлены в коде.
- [x] Базовые Pydantic-схемы и модели строк БД (черновик).
- [x] Ruff / Mypy / Pytest настроены и гоняются в CI.
- [x] Подготовлена схема БД (`db/schema.sql`).
