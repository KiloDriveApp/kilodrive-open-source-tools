from __future__ import annotations

import re
from pathlib import Path

from .common import load_json, safe_relative_path

LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def validate(config_path: Path) -> list[str]:
    config_path = config_path.resolve()
    config = load_json(config_path)
    root = safe_relative_path(config_path.parent, config.get("root", "."))
    errors: list[str] = []
    files: list[Path] = []
    for pattern in config.get("include", ["**/*.md"]):
        files.extend(path for path in root.glob(pattern) if path.is_file())
    files = sorted(set(files))
    if not files:
        errors.append("No documentation files matched the configured include patterns")
    banned = config.get("bannedPhrases", [])
    for path in files:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        for phrase in banned:
            if phrase.lower() in text.lower():
                errors.append(f"{relative}: banned phrase {phrase!r}")
        for link in LINK.findall(text):
            target = link.split("#", 1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: broken local link {link!r}")
    for required in config.get("requiredFiles", []):
        if not safe_relative_path(root, required).is_file():
            errors.append(f"Missing required file: {required}")
    return errors
