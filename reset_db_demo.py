import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db.sqlite3"


def run_command(command: List[str]) -> None:
    print(f"> {' '.join(command)}")
    result = subprocess.run(command, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def delete_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Supprimé : {DB_PATH}")


def delete_migrations() -> None:
    for path in ROOT.glob("*/migrations"):
        if path.is_dir():
            for migration_file in path.glob("0*.py"):
                migration_file.unlink()
                print(f"Supprimé : {migration_file}")


def main() -> None:
    print("Réinitialisation de la base de données...")

    delete_db()
    delete_migrations()

    py = sys.executable
    if not py:
        py = "python"

    run_command([py, "manage.py", "makemigrations"])
    run_command([py, "manage.py", "migrate"])
    run_command([py, "manage.py", "demo_data"])

    print("\nBase réinitialisée avec succès.")


if __name__ == "__main__":
    main()
