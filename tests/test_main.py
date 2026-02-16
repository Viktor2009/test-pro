"""Тесты для основного модуля."""

from test_pro.main import main


def test_main() -> None:
    """Тест функции main."""
    # Пока просто проверяем, что функция выполняется без ошибок
    main()
    assert True
