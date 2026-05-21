#!/usr/bin/env python3
"""Post-generation hook: rename env.template -> .env so the project is ready to run.

The env.template file is fully rendered by cookiecutter (with the chosen
database/cache/broker variables) — we just give it the conventional name
applications expect.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    project_dir = Path.cwd()
    src = project_dir / "env.template"
    dst = project_dir / ".env"

    if not src.exists():
        print(f"[post_gen_project] env.template not found at {src}; nothing to do.")
        return 0

    try:
        shutil.copyfile(src, dst)
        print(f"[post_gen_project] Created .env at {dst}")
    except OSError as exc:
        print(f"[post_gen_project] Failed to create .env: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
