"""
Заглушки и вспомогательные реализации провайдеров.

Реальные TTS/STT этапа 1: ``pyttsx3_tts``, ``faster_whisper_stt`` (см. ``.[audio]``).
"""

from lang_learn.providers.http_chat_llm import HttpChatCompletionsLLMProvider
from lang_learn.providers.stub_llm import StubLLMProvider
from lang_learn.providers.stub_stt import StubSTTProvider
from lang_learn.providers.stub_tts import StubTTSProvider

__all__ = [
    "HttpChatCompletionsLLMProvider",
    "StubLLMProvider",
    "StubSTTProvider",
    "StubTTSProvider",
]
