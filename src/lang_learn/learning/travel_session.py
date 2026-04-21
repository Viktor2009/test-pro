"""Сборка контекста диалога из travel-сценария (этап 4)."""

from __future__ import annotations

from lang_learn.schemas.dialog import DialogSessionContext
from lang_learn.schemas.travel import (
    ScenarioVariation,
    TravelPhrase,
    TravelScenario,
    TravelScenarioBundle,
)


class TravelScenarioService:
    """
    Доступ к сценариям, карточке выживания и сборке ``DialogSessionContext``.

    Режим **stress** добавляет в цель сессии указание ускорить темп и
    использовать уточняющие вопросы из вариации.
    """

    def __init__(self, bundle: TravelScenarioBundle) -> None:
        self._bundle = bundle
        self._by_slug = {s.slug: s for s in bundle.scenarios}

    @classmethod
    def load_default(cls) -> TravelScenarioService:
        """Загрузить встроенный набор сценариев."""
        from lang_learn.learning.travel_loader import load_travel_bundle

        return cls(load_travel_bundle())

    def list_scenarios(self) -> tuple[TravelScenario, ...]:
        """Все сценарии в порядке файла."""
        return self._bundle.scenarios

    def get_scenario(self, slug: str) -> TravelScenario:
        """Сценарий по slug."""
        if slug not in self._by_slug:
            msg = f"Unknown scenario slug: {slug}"
            raise KeyError(msg)
        return self._by_slug[slug]

    def survival_phrases(self, slug: str) -> tuple[TravelPhrase, ...]:
        """Карточка выживания: критически важные фразы."""
        sc = self.get_scenario(slug)
        return tuple(p for p in sc.phrases if p.survival)

    def build_dialog_context(
        self,
        slug: str,
        user_latest_message: str,
        *,
        variation_level: int = 1,
        stress: bool = False,
        level_hint: str = "A1",
    ) -> DialogSessionContext:
        """Собрать контекст для ``DialogOrchestrator`` по сценарию."""
        sc = self.get_scenario(slug)
        var = _pick_variation(sc, variation_level)
        topic = f"{sc.title}: {var.title}"
        goal = _compose_session_goal(sc, var, stress=stress)
        sentences = 2 if stress else 3
        return DialogSessionContext(
            topic=topic,
            session_goal=goal,
            level_hint=level_hint,
            target_language=sc.target_language,
            user_latest_message=user_latest_message,
            max_reply_sentences=sentences,
            prior_messages=(),
        )


def _pick_variation(scenario: TravelScenario, level: int) -> ScenarioVariation:
    if not scenario.variations:
        msg = f"Scenario {scenario.slug!r} has no variations"
        raise ValueError(msg)
    capped = max(1, min(5, level))
    candidates = [v for v in scenario.variations if v.level <= capped]
    if not candidates:
        return max(scenario.variations, key=lambda v: v.level)
    return max(candidates, key=lambda v: v.level)


def _compose_session_goal(
    scenario: TravelScenario,
    variation: ScenarioVariation,
    *,
    stress: bool,
) -> str:
    lex = ", ".join(f"{x.term} — {x.gloss}" for x in scenario.lexicon[:8])
    phrases = "; ".join(f"{p.text}" for p in scenario.phrases[:6])
    parts = [
        f"Ситуация: {variation.title}.",
        variation.coach_note.strip(),
        f"Опорная лексика: {lex}.",
        f"Шаблонные фразы: {phrases}.",
        "Веди диалог как персонал или собеседник в этой ситуации.",
    ]
    if stress:
        parts.append(
            "Режим стресса: реплики короче, темп выше; задай один "
            "неожиданный уточняющий вопрос из списка вариации, если он не пуст.",
        )
        if variation.clarifying_questions:
            q = variation.clarifying_questions[0]
            parts.append(f"Пример уточнения: «{q}»")
    return " ".join(p for p in parts if p).strip()
