import subprocess
from pathlib import Path
from typing import Dict, List

README_FILE = "README.md"

# Folder → aspect ratio mapping
FOLDERS: Dict[str, str] = {
    "Horizontal": "Wide",
    "Vertical": "Potrait",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Safety valves
MAX_IMAGES_PER_SECTION = 20  # prevent README bloat
SORT_BY = "name"  # "name" or "modified"


def collect_images(folder: str) -> List[Path]:
    base = Path(folder)
    if not base.exists():
        return []

    images = [
        p
        for p in base.rglob("*")
        if p.suffix.lower() in IMAGE_EXTENSIONS and p.is_file()
    ]

    if SORT_BY == "modified":
        images.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        images.sort(key=lambda p: p.name.lower())

    return images[:MAX_IMAGES_PER_SECTION]


def generate_preview_section() -> str:
    lines = ["### Preview\n"]

    for folder, ratio in FOLDERS.items():
        images = collect_images(folder)
        if not images:
            continue

        lines.append(f"#### {ratio}\n")
        for img in images:
            rel_path = img.as_posix()
            lines.append(f"![{img.name}](./{rel_path})\n")
        lines.append("\n")

    return "".join(lines)


def update_readme():
    readme = Path(README_FILE)
    if not readme.exists():
        raise FileNotFoundError("README.md not found")

    content = readme.read_text(encoding="utf-8")

    start = content.find("### Preview")
    end = content.find("### Source")

    if start == -1 or end == -1 or start >= end:
        raise ValueError(
            "README.md must contain '### Preview' followed by '### Source'"
        )

    new_content = content[:start] + generate_preview_section() + content[end:]
    readme.write_text(new_content, encoding="utf-8")

    print("README.md updated (scalable mode).")


def run_git_commands():
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "up"],
        ["git", "push"],
    ]

    for cmd in commands:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")

        if result.stdout.strip():
            print(result.stdout.strip())


if __name__ == "__main__":
    update_readme()
    run_git_commands()
