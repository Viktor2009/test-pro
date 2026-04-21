# Этап 4 — travel-сценарии (часть 1)

## Сделано

- **Модели** `lang_learn.schemas.travel`: лексика, фразы, вариации уровней 1–5,
  сценарий, пакет `TravelScenarioBundle`.
- **Данные** `lang_learn/data/travel/scenarios_bundle.json` — шесть тем из плана:
  аэропорт, отель, ресторан, магазин, аптека/клиника, полиция/экстренные случаи.
- **Загрузка** `load_travel_bundle()` в `learning/travel_loader.py`.
- **Сервис** `TravelScenarioService`: список сценариев, `survival_phrases(slug)`,
  `build_dialog_context(..., variation_level=, stress=)` для связки с
  `DialogOrchestrator` (этап 3).
- **Режим стресса**: укороченные реплики в контексте и подсказка уточняющих
  вопросов из выбранной вариации (текст в `session_goal`; TTS-ускорение — при
  подключении провайдера отдельно).
- **CLI**: `travel-list`, `travel-survival --slug …`, `travel-demo --slug …`.

## Дальше по этапу 4

- Больше уровней вариаций и richer-диалоги.
- Привязка к реальному LLM и сохранению сессий.
- Отдельный UX «карточки выживания» и тренажёр по списку фраз.
