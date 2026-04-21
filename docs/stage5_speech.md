# Этап 5 — произношение и качество речи (часть 1)

## Реализовано

- **Схемы** `lang_learn.schemas.speech_quality`: `PronunciationScores`,
  `WordAlignmentIssue`, `PronunciationReport`, `PhraseScoreLog`.
- **Анализ** `lang_learn.learning.speech_quality.analyze_pronunciation`:
  - *intelligibility* — близость строк (SequenceMatcher по нормализованному тексту);
  - *word_accuracy* — Jaccard по множеству слов + детализация проблемных слов;
  - *fluency* — прокси по длине текста и (опционально) соотношению длительностей
    записей эталона и гипотезы в мс;
  - *composite* — взвешенная сводка; **articulation_tips** и **word_issues** для фидбека.
- **Shadowing** `lang_learn.learning.shadowing.build_shadowing_plan`: пауза после
  эталона, целевая длительность, число раундов, темп `slow|normal|fast` (числа для UI,
  без аудио-метронома в пакете).
- **До/после** `phrase_progress.record_composite_score` и `summarize_phrase_progress`.
- **CLI**: `pronunciation-report`, `shadowing-plan`, `phrase-progress`.

## Ограничения MVP

- Нет фонемного разбора и нет разметки пауз из сигнала — только текст и опционально
  длительности клипа.
- «Целевой образец» в отчёте — текст; WAV через существующий TTS вне этого вызова.

## Дальше по этапу 5

- Привязка к реальному STT + длительности записи пользователя.
- Метрики по паузам/темпу из аудио.
- UI тренажёра shadowing с таймером и визуализацией.
