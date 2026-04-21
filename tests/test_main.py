"""
Тесты точки входа CLI / модуля.
"""

import io
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from lang_learn.cli import build_parser, main


def test_parser_help_lists_subcommands() -> None:
    """Справка argparse перечисляет подкоманды (в т.ч. для CLI-режима)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        build_parser().print_help()
    help_text = buf.getvalue()
    assert "devices" in help_text
    assert "speak" in help_text
    assert "prea0-demo" in help_text
    assert "dialog-demo" in help_text
    assert "travel-list" in help_text
    assert "travel-demo" in help_text
    assert "pronunciation-report" in help_text
    assert "shadowing-plan" in help_text
    assert "phrase-progress" in help_text
    assert "progress-demo" in help_text
    assert "ext-demo" in help_text
    assert "integration-dialog" in help_text
    assert "gui" in help_text


def test_main_without_args_launches_gui() -> None:
    """Без аргументов открывается графический интерфейс (по умолчанию)."""
    with patch("lang_learn.gui.desktop_chat.run_learning_desktop") as run_gui:
        code = main([])
    assert code == 0
    run_gui.assert_called_once()


def test_main_gui_subcommand_launches_gui() -> None:
    """Явная подкоманда gui ведёт в тот же графический режим."""
    with patch("lang_learn.gui.desktop_chat.run_learning_desktop") as run_gui:
        code = main(["gui"])
    assert code == 0
    run_gui.assert_called_once()


def test_main_help_exits_zero() -> None:
    """Глобальный --help завершает процесс с кодом 0 (argparse)."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
