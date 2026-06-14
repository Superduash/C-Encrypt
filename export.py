from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT / "cencrypt.txt"

INCLUDE_EXTENSIONS = {
    ".py",
    ".bat",
    ".cmd",
    ".ps1",
    ".txt",
    ".json",
    ".md",
}

EXCLUDE_DIR_NAMES = {"cstorage", "__pycache__", ".git", ".venv", "venv", "env", ".kiro"}
EXCLUDE_NAME_PATTERNS = ("sample", "test", "tests", "example")
EXCLUDE_FILE_NAMES = {"export.py", "cencrypt.txt", "IMPLEMENTATION_COMPLETE.md", "QUICK_START.txt"}


def should_skip_path(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    if path.name.lower() in EXCLUDE_FILE_NAMES or path == OUTPUT_FILE:
        return True

    if any(part.lower() in EXCLUDE_DIR_NAMES for part in relative_parts[:-1]):
        return True

    lower_name = path.name.lower()
    if any(pattern in lower_name for pattern in EXCLUDE_NAME_PATTERNS):
        return True

    if path.is_dir():
        return True

    return path.suffix.lower() not in INCLUDE_EXTENSIONS


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if should_skip_path(path):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix().lower())


def export_files() -> Path:
    exported_files = iter_source_files()
    sections: list[str] = []

    for path in exported_files:
        relative_path = path.relative_to(ROOT).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="utf-8", errors="replace")

        sections.append(f"===== {relative_path} =====\n{content.rstrip()}\n")

    OUTPUT_FILE.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return OUTPUT_FILE


if __name__ == "__main__":
    output_path = export_files()
    print(f"Exported {output_path}")