"""
Синхронное озвучивание коротких фрагментов через pyttsx3.

Допускается вызов из фонового потока (Windows: COM при необходимости).
"""

from __future__ import annotations

import sys
import time


def speak_pyttsx3_chunks(chunks: list[str]) -> str | None:
    """
    Озвучить последовательность строк через pyttsx3.

    Returns:
        Сообщение об ошибке (для UI) или ``None``, если воспроизведение прошло.
    """
    if not chunks:
        return "Нет фрагментов для озвучки."

    coinit = False
    try:
        if sys.platform == "win32":
            try:
                import pythoncom

                pythoncom.CoInitialize()
                coinit = True
            except ImportError:
                pass
        try:
            import pyttsx3

            engine = pyttsx3.init()
            for i, part in enumerate(chunks):
                engine.say(part)
                engine.runAndWait()
                if i < len(chunks) - 1:
                    time.sleep(0.35)
        except ImportError:
            return (
                "Нет pyttsx3. Установите зависимости: pip install -e \".[audio]\""
            )
        except (OSError, RuntimeError, AttributeError) as exc:
            return f"Озвучка: {exc}"
        return None
    finally:
        if coinit:
            try:
                import pythoncom

                pythoncom.CoUninitialize()
            except ImportError:
                pass
