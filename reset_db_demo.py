import os
import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db.sqlite3"


def run_command(command: List[str]) -> None:
    print(f"> {' '.join(command)}")
    result = subprocess.run(command, cwd=str(ROOT), shell=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    print("Réinitialisation de la base de données...")

    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Supprimé : {DB_PATH}")

    py = sys.executable
    if not py:
        py = "python"

    run_command([py, "manage.py", "migrate"])
    run_command([py, "manage.py", "demo_data"])

    print("\nBase réinitialisée avec succès.")


if __name__ == "__main__":
    main()
