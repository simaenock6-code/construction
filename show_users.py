import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from app.models import Personnel

User = get_user_model()

# Mots de passe en clair des comptes créés par create_accounts.py
MOTS_DE_PASSE = {
    'chef.chantier': 'Chef@2026!',
    'resp.logistique': 'Logistique@2026!',
    'manager': 'Manager@2026!',
    'testadmin': 'testpass123',
}

print("=" * 80)
print("LISTE DES UTILISATEURS ET MOTS DE PASSE")
print("=" * 80)

for user in User.objects.all():
    personnel = getattr(user, 'personnel', None)
    fonction = personnel.fonction.nom if personnel and personnel.fonction else 'Aucune'
    chantier = personnel.chantier.location if personnel and personnel.chantier else 'Aucun'
    mot_de_passe = MOTS_DE_PASSE.get(user.username, 'N/A (inconnu)')

    print(f"\nUtilisateur: {user.username}")
    print(f"  Nom complet : {user.get_full_name() or 'N/A'}")
    print(f"  Fonction    : {fonction}")
    print(f"  Chantier    : {chantier}")
    print(f"  Superuser   : {'Oui' if user.is_superuser else 'Non'}")
    print(f"  Mot de passe: {mot_de_passe}")
    print(f"  Staff       : {'Oui' if user.is_staff else 'Non'}")
    if personnel:
        print(f"  Téléphone   : {personnel.telephone or 'N/A'}")

print("\n" + "=" * 80)
print(f"Total: {User.objects.count()} utilisateurs")