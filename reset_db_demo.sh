#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "Réinitialisation de la base de données..."
rm -f db.sqlite3
echo "Supprimé : db.sqlite3"

find . -path "*/migrations/0*.py" -delete
echo "Supprimé : migrations 0*.py"

python manage.py makemigrations
python manage.py migrate
python manage.py demo_data

echo "Base réinitialisée avec succès."
