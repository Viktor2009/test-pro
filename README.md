# lang_learn — модуль изучения языка (Python)

Проект: TTS/STT, учебные сценарии (Pre-A0, диалог, travel), оценка речи, прогресс в SQLite.
Графический интерфейс по плану — отдельный этап 8; сейчас основная точка входа — **CLI** (`python -m lang_learn`).

## Структура каталога

```
lang_learn/
├── src/
│   └── lang_learn/       # Пакет приложения
│       ├── contracts/    # Абстракции STT/TTS/LLM, ProgressRepository, …
│       ├── schemas/      # Pydantic-модели
│       ├── providers/    # Адаптеры (stub, pyttsx3, faster-whisper, …)
│       ├── learning/     # Движки уроков, диалога, travel, речи, KPI
│       ├── persistence/  # SQLite / in-memory прогресс
│       ├── gui/          # Окно учебного диалога (tkinter, этап 8)
│       ├── audio_io/     # Запись, воспроизведение, WAV
│       ├── services/     # Аудио-цикл и др.
│       ├── data/         # JSON контента (pre_a0, travel)
│       └── cli.py        # Точка входа CLI
├── db/
│   └── schema.sql        # Схема SQLite
├── tests/                # Pytest
├── docs/                 # План, baseline, описания этапов
├── scripts/              # Вспомогательные скрипты
│   ├── run_tests.ps1     # Запуск тестов (Windows)
│   └── run_tests.sh      # Запуск тестов (Linux/macOS)
├── requirements.txt      # Базовые зависимости
├── requirements-dev.txt  # Зависимости для разработки
├── pyproject.toml        # Конфигурация проекта и инструментов
├── .gitignore
└── README.md             # Этот файл
```

## Требования

- **Python 3.10** или новее (рекомендуется 3.11+)
- Установленный [Python](https://www.python.org/downloads/) с добавлением в PATH

## Активация и инициализация области разработки

### 1. Перейти в каталог проекта

```powershell
cd c:\lang_learn
```

(или путь к вашему клонированному/скопированному каталогу)

### 2. Создать виртуальное окружение

Рекомендуется использовать отдельное виртуальное окружение для каждого проекта.

**Windows (PowerShell):**

```powershell
python -m venv .venv
```

**Windows (cmd):**

```cmd
python -m venv .venv
```

**Linux / macOS:**

```bash
python3 -m venv .venv
```

Будет создана папка `.venv` с изолированным интерпретатором и pip.

### 3. Активировать виртуальное окружение

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

Если скрипты запрещены политикой, выполните один раз:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (cmd):**

```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

После активации в начале строки приглашения появится `(.venv)`.

### 4. Установить зависимости и сам пакет

Команда `python -m lang_learn` ищет пакет `lang_learn` в окружении. Его нужно
**один раз** установить из корня репозитория в режиме разработки (тогда модуль
появится в `site-packages` и появится команда `lang-learn`):

```powershell
python -m pip install -U pip
pip install -r requirements.txt
pip install -e .
```

Для полноценной разработки (тесты, линтер, типы):

```powershell
pip install -e ".[dev]"
```

**Важно (Windows):** после активации `.venv` запускайте **`python`**, а не
`py -3`: лаунчер `py` может выбрать **глобальный** Python 3.13, где пакет не
установлен, и вы увидите `No module named lang_learn`.

**Без `pip install -e .`** можно временно задать путь к исходникам и запустить GUI:

```powershell
.\scripts\run_gui.ps1
```

### 4.1. Секреты в файле `.env` (для передачи пользователю)

При каждом запуске `python -m lang_learn …` и GUI автоматически читаются файлы
`.env` (библиотека `python-dotenv`):

1. `%LOCALAPPDATA%\lang_learn\.env` (Windows) или каталог данных приложения по
   аналогии XDG на Linux/macOS — **удобно для установленной копии**;
2. `.env` в **текущем рабочем каталоге** — при запуске из клона репозитория;
   значения из этого файла перекрывают одноимённые ключи из шага 1.

Скопируйте в репозиторий шаблон `/.env.example` → `.env` и заполните ключи.
Файл `.env` в git не коммитится (см. `.gitignore`).

Отключить загрузку (тесты): переменная `LANG_LEARN_SKIP_DOTENV=1`.

### 5. Проверить, что всё работает

Запуск приложения (после `pip install -e .`):

```powershell
python -m lang_learn
```

То же через установленный скрипт:

```powershell
lang-learn
```

Запуск GUI:

```powershell
python -m lang_learn gui
```

или `lang-learn gui`.

Запуск тестов:

```powershell
pytest tests/ -v
```

Или используйте скрипты из `scripts/`:

- Windows: `.\scripts\run_tests.ps1`
- Linux/macOS: `./scripts/run_tests.sh`

## Ежедневная работа

1. Открыть каталог в редакторе (например, Cursor / VS Code).
2. Активировать виртуальное окружение в терминале (шаг 3 выше).
3. Писать код в `src/lang_learn/`, добавлять тесты в `tests/`.
4. Запускать тесты: `pytest tests/ -v`.
5. Проверять стиль и простые ошибки: `ruff check src tests`.

## Если появилось «No module named lang_learn»

1. Убедитесь, что активировано виртуальное окружение (в начале строки `(.venv)`).
2. Выполните из корня проекта: `pip install -e .`
3. Используйте **`python -m lang_learn`**, а не `py -3 -m lang_learn` (см. шаг 4).
4. Либо запустите GUI скриптом: `.\scripts\run_gui.ps1`

## Полезные команды

| Действие              | Команда                          |
|-----------------------|-----------------------------------|
| Запуск приложения     | `python -m lang_learn` или `lang-learn` |
| Запуск GUI (tkinter)  | `python -m lang_learn gui` или `lang-learn gui` |
| Запуск тестов         | `pytest tests/ -v`                |
| Проверка кода (ruff)  | `ruff check src tests`            |
| Форматирование кода   | `ruff format src tests`           |
| Статическая типизация | `mypy src/lang_learn` (как в CI)   |
| Покрытие тестами      | `pytest tests/ --cov=lang_learn --cov-report=term-missing` |

## Деактивация окружения

В терминале, где активировано окружение:

```powershell
deactivate
```

## Дальнейшие шаги

- Технический baseline этапа 0: `docs/stage0_technical_baseline.md`.
- Аудио этапа 1 (TTS/STT, CLI): `docs/stage1_audio.md`, extra `pip install -e ".[audio]"`.
- Pre-A0 этапа 2 (часть 1): `docs/stage2_prea0.md`, команда `python -m lang_learn prea0-demo`.
- Диалог этапа 3 (часть 1): `docs/stage3_dialog.md`, команда `python -m lang_learn dialog-demo`.
- Travel этапа 4 (часть 1): `docs/stage4_travel.md`, команды `travel-list`, `travel-survival`, `travel-demo`.
- Произношение этапа 5 (часть 1): `docs/stage5_speech.md`, команды `pronunciation-report`, `shadowing-plan`, `phrase-progress`.
- Прогресс этапа 6 (часть 1): `docs/stage6_progress.md`, команда `python -m lang_learn progress-demo`.
- Расширяемость этапа 7 (часть 1): `docs/stage7_extensibility.md`, команды `ext-demo`, `integration-dialog`.
- GUI этапа 8 (часть 1): `docs/stage8_gui.md`, команда `python -m lang_learn gui` (tkinter).
- Полный план этапов: `docs/language_learning_module_implementation_plan.md`.
- Добавляйте новые модули в `src/lang_learn/` и тесты в `tests/`.
- При необходимости добавьте зависимости в `requirements.txt` и зафиксируйте версии.