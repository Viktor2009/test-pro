# Этап 1 — аудио-ядро (TTS / STT / микрофон)

## Установка

Минимальный пакет (`pydantic`) не включает аудио-зависимости. Для этапа 1:

```powershell
pip install -e ".[audio]"
```

или `pip install -r requirements-audio.txt`.

Первый запуск **faster-whisper** скачивает веса выбранной модели (например `tiny`).

## CLI

```text
python -m lang_learn devices
python -m lang_learn speak --text "Hello" --lang en-US
python -m lang_learn record --seconds 3 --out sample.wav
python -m lang_learn transcribe --wav sample.wav --lang en
```

- **devices** — список устройств PortAudio (вход/выход).
- **speak** — TTS через **pyttsx3** (WAV), по умолчанию воспроизведение через **sounddevice**.
- **record** — запись моно PCM16 WAV с микрофона.
- **transcribe** — STT через **faster-whisper** (локально).

Флаги **`--no-play`** и **`--out`** у `speak` позволяют только сохранить файл без воспроизведения.

## Программный API

- Провайдеры: `lang_learn.providers.pyttsx3_tts.Pyttsx3TTSProvider`,
  `lang_learn.providers.faster_whisper_stt.FasterWhisperSTTProvider`.
- Сервис: `lang_learn.services.audio_cycle.AudioCycleService`
  (`speak_text`, `transcribe_audio`, `record_and_transcribe`).
- I/O: `lang_learn.audio_io` (`MicrophoneRecorder`, `play_wav_bytes`,
  `list_audio_devices`, утилиты WAV).

## Частые сбои (Windows)

- **`PortAudioError: Error querying device -1`** при `record`: у системы нет
  валидного «микрофона по умолчанию» или драйвер не отдаёт вход. В коде
  выполняется обход: явный индекс default или первое устройство с входом;
  если не найдено — `RuntimeError` с подсказкой. Вручную выберите индекс:
  `python -m lang_learn devices`, затем
  `python -m lang_learn record --seconds 3 --out x.wav --device N`.
- Проверьте доступ приложения к микрофону в параметрах Windows.

## Ограничения этапа 1

- **TTS**: pyttsx3 выдаёт **WAV**; выбор голоса/языка зависит от установленных
  голосов ОС.
- **STT**: faster-whisper принимает **WAV моно 16-bit** в `STTRequest`.
- Нет полноценного desktop UI — только CLI и вызовы из кода.
