import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Changer le mot de passe de tous les utilisateurs en "demo"
users = User.objects.all()
for user in users:
    user.set_password('demo')
    user.save()
    print(f"Mot de passe changé pour: {user.username}")

print(f"\nTotal: {users.count()} utilisateur(s) mis à jour")
print("Mot de passe pour tous les utilisateurs: demo")