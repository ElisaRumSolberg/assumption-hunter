from pathlib import Path

ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}


def list_project_files(project_path: str) -> list[Path]:
    root = Path(project_path)
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix in ALLOWED_EXTENSIONS
    ]


def load_project(project_path: str) -> str:
    root = Path(project_path)
    parts = []
    for path in list_project_files(project_path):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        parts.append(f"\n--- FILE: {path.relative_to(root)} ---\n{content}\n")
    return "\n".join(parts)


def read_file(project_path: str, relative_path: str) -> str:
    return (Path(project_path) / relative_path).read_text(encoding="utf-8")
