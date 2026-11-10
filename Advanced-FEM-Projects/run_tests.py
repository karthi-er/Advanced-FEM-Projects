"""Run each project's standard-library unittest suite without installation."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECTS = ("control", "fem", "rag", "cfd")


def main() -> int:
    runner = unittest.TextTestRunner(verbosity=2)
    failures = 0
    for project in PROJECTS:
        directory = ROOT / project
        suite = unittest.defaultTestLoader.discover(
            str(directory / "tests"), top_level_dir=str(directory)
        )
        print(f"\n== {project} ==", flush=True)
        result = runner.run(suite)
        failures += len(result.failures) + len(result.errors)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
