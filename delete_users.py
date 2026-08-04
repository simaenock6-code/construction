import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from app.models import Personnel

User = get_user_model()

# Supprimer tous les utilisateurs sauf le superuser admin
users = User.objects.all()
deleted = 0
kept = []

for user in users:
    if user.is_superuser:
        kept.append(user.username)
        continue
    # Supprimer le personnel associé d'abord
    try:
        if hasattr(user, 'personnel'):
            user.personnel.delete()
    except Exception:
        pass
    user.delete()
    deleted += 1

print(f"Utilisateurs supprimés: {deleted}")
print(f"Utilisateurs conservés: {kept}")
print(f"Total restant: {User.objects.count()}")