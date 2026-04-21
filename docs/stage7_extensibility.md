# Этап 7 — расширяемость (часть 1)

## Состав

- **Feature flags:** `lang_learn.config.feature_flags` — переменные окружения
  `LANG_LEARN_FF_<ИМЯ>=1|true|yes|on` для известного набора имён (см. код).
- **Реестр провайдеров:** `plugins/registry.py`, регистрация в `plugins/bootstrap.py`
  (`stub`; опционально `pyttsx3`, `faster_whisper` при extra `[audio]`).
- **Реестр движков уроков:** `plugins/lesson_registry.py` — сейчас `pre_a0`.
- **Траектории:** `data/trajectories/bundle.json`, модели `schemas/trajectory.py`,
  сервис `learning/trajectory_service.py` (`travel`, `business`, `exam_prep`).
- **Многопользовательский задел:** `schemas/user_scope.py` (`external_user_id`,
  опциональный `tenant_id`).
- **DTO для внешнего API:** `schemas/integration_api.py` — `HttpDialogTurnRequest` /
  `HttpDialogTurnResponse` (без транспорта HTTP).

## CLI

```text
python -m lang_learn ext-demo
python -m lang_learn ext-demo --with-audio
python -m lang_learn integration-dialog --topic Shop --goal "Polite questions" --message "How much?"
```

## Расширение

- Новый LLM/STT/TTS: `ProviderRegistry.register_*` в своём bootstrap-коде приложения.
- Новый тип урока: `LessonEngineRegistry.register` + фабрика `() -> LessonEngine`.
- Новые траектории: свой JSON + `TrajectoryService(load_trajectory_bundle_bytes(...))`.
