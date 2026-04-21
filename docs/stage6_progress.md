# Этап 6 — прогресс и персонализация (часть 1)

## Состав

- **Схема:** таблица `user_aliases` (`external_id` → `users.id`) в `db/schema.sql`.
- **Контракт:** `ProgressRepository.list_attempts`, `enqueue_review`.
- **Персистентность:** `SqliteProgressRepository`, `MemoryProgressRepository` в `lang_learn.persistence`.
- **Аналитика:** `schemas/progress_analytics.py` — `CompetencySnapshot`, `LearningKPIs`, `TravelReadinessView`, `ProgressOverview`.
- **Логика:** `learning/competency.py`, `kpi_engine.py`, `readiness.py`, `srs_planner.py`, сводка в `learning/progress_report.py`.
- **CLI:** `progress-demo` — демонстрационная запись в SQLite, печать JSON-сводки и постановка слабых осей в `review_queue`.

## Метаданные попыток

Для осмысленной аналитики в `AttemptRecord.details` можно передавать:

- `skill_axis`: `lexicon` | `comprehension` | `pronunciation` | `dialog_scenario` (иначе считается `pronunciation`);
- `scenario_slug`: slug travel-сценария для KPI «готовность к поездке»;
- опционально `lesson_id`, `scenario_id` (integer), `reference_text`, `recommendation_next`, `errors` (список → колонка `errors_json`).

## Запуск

```bash
python -m lang_learn progress-demo --db ./tmp_progress.sqlite
```

Параметры: `--schema`, `--user`, `--threshold`, `--srs-hours`.
