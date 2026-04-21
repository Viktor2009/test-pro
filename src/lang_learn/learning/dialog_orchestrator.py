"""Оркестрация учебного диалога: LLM → JSON → опционально TTS."""

from __future__ import annotations

from lang_learn.contracts.llm import LLMProvider
from lang_learn.contracts.tts import TTSProvider
from lang_learn.learning.dialog_parse import parse_structured_dialog
from lang_learn.learning.prompt_builder import build_dialog_messages
from lang_learn.schemas.audio import TTSRequest
from lang_learn.schemas.dialog import DialogSessionContext, DialogTurnResult
from lang_learn.schemas.llm import LLMProviderConfig, LLMRequest


class DialogOrchestrator:
    """
    Один ход диалога: промпт → LLM → валидация JSON → (опц.) синтез речи.

    При ошибке парсинга используется fallback (см. ``dialog_parse``).
    """

    def __init__(
        self,
        llm: LLMProvider,
        *,
        tts: TTSProvider | None = None,
    ) -> None:
        self._llm = llm
        self._tts = tts

    def run_turn(
        self,
        ctx: DialogSessionContext,
        llm_config: LLMProviderConfig,
    ) -> DialogTurnResult:
        """Выполнить ход диалога и вернуть структурированный результат."""
        messages = build_dialog_messages(ctx)
        cfg = llm_config.model_copy(update={"response_format_json": True})
        req = LLMRequest(
            messages=messages,
            target_language=ctx.target_language,
            config=cfg,
        )
        res = self._llm.complete(req)
        structured, fallback_used = parse_structured_dialog(res.text)
        if self._tts is not None:
            tts_req = TTSRequest(
                text=structured.assistant_reply,
                language=ctx.target_language,
            )
            tts_res = self._tts.synthesize(tts_req)
            return DialogTurnResult(
                structured=structured,
                fallback_used=fallback_used,
                raw_text=res.text,
                tts_audio=tts_res.audio,
                tts_format=tts_res.format,
            )
        return DialogTurnResult(
            structured=structured,
            fallback_used=fallback_used,
            raw_text=res.text,
        )
