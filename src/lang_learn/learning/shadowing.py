"""План тренажёра shadowing (повтор за эталоном)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Tempo = Literal["slow", "normal", "fast"]

_MS_PER_WORD = {"slow": 650, "normal": 450, "fast": 320}
_PAUSE_AFTER_REFERENCE_MS = {"slow": 900, "normal": 650, "fast": 450}


class ShadowingPlan(BaseModel):
    """Параметры одной серии повторов за диктором."""

    model_config = ConfigDict(frozen=True)

    reference_text: str = Field(min_length=1)
    tempo: Tempo = "normal"
    rounds: int = Field(default=3, ge=1, le=10)
    suggested_pause_after_reference_ms: int = Field(ge=0, le=30_000)
    suggested_target_duration_ms: int = Field(ge=0, le=600_000)
    hint: str = Field(
        default="",
        description="Краткая инструкция для пользователя.",
    )


def build_shadowing_plan(
    reference_text: str,
    *,
    tempo: Tempo = "normal",
    rounds: int = 3,
) -> ShadowingPlan:
    """
    Оценить паузу после эталона и целевую длительность по числу слов и темпу.

    Реальное аудио и метроном — на стороне UI / аудио-слоя; здесь только числа.
    """
    text = reference_text.strip()
    words = max(1, len(text.split()))
    per = _MS_PER_WORD[tempo]
    target_ms = int(words * per * 1.1)
    pause = _PAUSE_AFTER_REFERENCE_MS[tempo]
    hint = (
        f"Темп «{tempo}»: прослушайте эталон, пауза ~{pause} мс, затем повторите "
        f"{rounds} раза, стараясь уложиться примерно в {target_ms} мс на всю фразу."
    )
    return ShadowingPlan(
        reference_text=text,
        tempo=tempo,
        rounds=rounds,
        suggested_pause_after_reference_ms=pause,
        suggested_target_duration_ms=target_ms,
        hint=hint,
    )
