"""Сервис аудио-цикла со stub-провайдерами."""

from lang_learn.providers.stub_stt import StubSTTProvider
from lang_learn.providers.stub_tts import StubTTSProvider
from lang_learn.services.audio_cycle import AudioCycleService


def test_audio_cycle_tts_and_stt() -> None:
    svc = AudioCycleService(tts=StubTTSProvider(), stt=StubSTTProvider())
    spoken = svc.speak_text("lesson", "de-DE")
    assert spoken.audio == b""
    heard = svc.transcribe_audio(b"\x00\x01", language="de-DE")
    assert heard.text == ""
    assert heard.confidence == 0.0
