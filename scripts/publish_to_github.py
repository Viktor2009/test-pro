"""Публикация проекта на GitHub: создание репозитория и push.

При первом запуске изменения публикуются в ветку main. При последующих
запусках создаётся ветка с именем из текущей даты и времени (например
2025-02-19_14-30-00), и изменения пушатся в неё. Комментариями служат
сообщения коммитов (commit message).
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_gh_path() -> str:
    """Возвращает путь к исполняемому файлу gh (на Windows ищет в типичных путях)."""
    if sys.platform != "win32":
        return "gh"
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get(
        "ProgramFiles(x86)", r"C:\Program Files (x86)"
    )
    localappdata = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(program_files) / "GitHub CLI" / "gh.exe",
        Path(program_files_x86) / "GitHub CLI" / "gh.exe",
        Path(localappdata) / "Programs" / "GitHub CLI" / "gh.exe",
    ]
    for p in candidates:
        if p and p.exists():
            return str(p)
    return "gh"


# Кодировка вывода дочерних процессов (gh/git), чтобы избежать ошибок на Windows.
_COMMON_ENCODING = {"encoding": "utf-8", "errors": "replace"}


def run(cmd: list[str], cwd: Path) -> str:
    """Выполняет команду, при ошибке прерывает работу. Возвращает stdout (без пробелов)."""
    p = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
        **_COMMON_ENCODING,
    )
    return (p.stdout or "").strip()


def ok(cmd: list[str], cwd: Path) -> bool:
    """Выполняет команду без вывода. Возвращает True, если код возврата 0."""
    p = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        **_COMMON_ENCODING,
    )
    return p.returncode == 0


def main() -> None:
    """Инициализирует git (если нужно), создаёт репозиторий на GitHub.

    Первый push — в ветку main. Последующие — в ветки с именем
    из текущей даты и времени (например 2025-02-19_14-30-00).
    """
    project_dir = Path(r"d:\Test_pro")
    repo_name = "test-pro1"
    gh = get_gh_path()

    if not ok([gh, "auth", "status"], cwd=project_dir):
        raise SystemExit(
            "Нет авторизации gh. Выполните: gh auth login -p https -w"
        )

    owner = run([gh, "api", "user", "-q", ".login"], cwd=project_dir)
    full_repo = f"{owner}/{repo_name}"
    repo_exists = ok([gh, "repo", "view", full_repo], cwd=project_dir)

    if not (project_dir / ".git").exists():
        run(["git", "init"], cwd=project_dir)

    run(["git", "branch", "-M", "main"], cwd=project_dir)

    if repo_exists:
        # Сначала создаём ветку с датой от main, коммит только в неё —
        # иначе коммит остаётся на локальном main и он расходится с origin/main.
        branch_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run(["git", "checkout", "-b", branch_name], cwd=project_dir)

    run(["git", "add", "."], cwd=project_dir)
    has_staged = not ok(
        ["git", "diff", "--cached", "--quiet"], cwd=project_dir
    )
    if not has_staged:
        if repo_exists:
            run(["git", "checkout", "main"], cwd=project_dir)
            run(["git", "branch", "-D", branch_name], cwd=project_dir)
        print("Нет изменений для коммита.")
        return

    if not repo_exists:
        message = "Initial commit"
        run(["git", "commit", "-m", message], cwd=project_dir)
        run(
            [
                gh,
                "repo",
                "create",
                repo_name,
                "--public",
                "--source",
                ".",
                "--remote",
                "origin",
            ],
            cwd=project_dir,
        )
        run(["git", "push", "-u", "origin", "main"], cwd=project_dir)
        print(f"OK: первый push в ветку main — {full_repo}")
    else:
        message = input("Введите сообщение коммита: ").strip() or "Update"
        run(["git", "commit", "-m", message], cwd=project_dir)
        run(["git", "push", "-u", "origin", branch_name], cwd=project_dir)
        run(["git", "checkout", "main"], cwd=project_dir)
        print(f"OK: изменения в ветке {branch_name} — {full_repo}")


if __name__ == "__main__":
    main()
