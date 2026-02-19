"""
Тесты для основного модуля приложения.
"""

import pytest

from app.main import main


def test_main_runs_without_error(capsys: pytest.CaptureFixture[str]) -> None:
    """main() выполняется без исключений и выводит сообщение."""
    main()
    captured = capsys.readouterr()
    assert "Привет" in captured.out or "готов" in captured.out
