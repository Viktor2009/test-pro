# Этап 3 — диалоговый ИИ (часть 1)

## Реализовано

- **Схема JSON** `lang_learn.schemas.dialog.StructuredDialogResponse`:
  `assistant_reply`, `corrections`, `new_vocabulary`, `next_action`.
- **Контекст** `DialogSessionContext` (тема, цель, уровень, целевой язык, реплика).
- **Prompt Builder** `lang_learn.learning.prompt_builder.build_dialog_messages` —
  роль учебного собеседника, тема, цель, лимит длины, контракт JSON в system.
- **Парсинг** `lang_learn.learning.dialog_parse`: чистка ```json fences```,
  `parse_structured_dialog` + fallback при невалидном JSON.
- **Оркестратор** `lang_learn.learning.dialog_orchestrator.DialogOrchestrator`:
  LLM → разбор → опционально **TTS** ответа ассистента.
- **CLI** `python -m lang_learn dialog-demo` (StubLLM).

## Дальше по этапу 3

- Реальный `LLMProvider` (OpenAI-совместимый HTTP и т.д.).
- Память диалога (`prior_messages`) из хранилища.
- Политика `next_action` в UI/сценариях.
- Сохранение сессий и телеметрия.
