from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def get_gh_path() -> str:
    """Путь к gh: на Windows — поиск в стандартных путях, если нет в PATH."""
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


def run(cmd: list[str], cwd: Path) -> str:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return (p.stdout or "").strip()


def ok(cmd: list[str], cwd: Path) -> bool:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return p.returncode == 0


def main() -> None:
    project_dir = Path(r"d:\Test_pro")
    repo_name = "test-pro"
    gh = get_gh_path()

    if not ok([gh, "auth", "status"], cwd=project_dir):
        raise SystemExit(
            "Нет авторизации gh. Выполните: gh auth login -p https -w"
        )

    owner = run([gh, "api", "user", "-q", ".login"], cwd=project_dir)
    full_repo = f"{owner}/{repo_name}"

    if not (project_dir / ".git").exists():
        run(["git", "init"], cwd=project_dir)

    run(["git", "branch", "-M", "main"], cwd=project_dir)
    run(["git", "add", "."], cwd=project_dir)

    has_staged = not ok(
        ["git", "diff", "--cached", "--quiet"], cwd=project_dir
    )
    if has_staged:
        run(["git", "commit", "-m", "Initial commit"], cwd=project_dir)

    if not ok([gh, "repo", "view", full_repo], cwd=project_dir):
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
    print(f"OK: опубликовано в {full_repo}")


if __name__ == "__main__":
    main()
