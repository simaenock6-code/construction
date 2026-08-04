import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from app.models import Fonction, Personnel, Emplacement

User = get_user_model()

# ============================================================
# 1. Créer les fonctions si elles n'existent pas
# ============================================================
fonctions = {
    'CHC': 'Chef de chantier',
    'RL': 'Responsable logistique',
    'MGR': 'Manager',
}

for code, nom in fonctions.items():
    fonction, created = Fonction.objects.get_or_create(
        code=code,
        defaults={'nom': nom, 'description': f'Fonction {nom}'}
    )
    if created:
        print(f"Fonction créée: {code} - {nom}")
    else:
        print(f"Fonction existante: {code} - {nom}")

# ============================================================
# 2. Créer un emplacement (chantier) si nécessaire
# ============================================================
emplacement, created = Emplacement.objects.get_or_create(
    code='CH1',
    defaults={'location': 'Chantier Principal'}
)
if created:
    print(f"Emplacement créé: {emplacement}")
else:
    print(f"Emplacement existant: {emplacement}")

# ============================================================
# 3. Créer les comptes utilisateurs
# ============================================================
comptes = [
    {
        'username': 'chef.chantier',
        'password': 'Chef@2026!',
        'first_name': 'Jean',
        'last_name': 'Kabila',
        'fonction_code': 'CHC',
        'nom': 'Kabila',
        'postnom': 'Mukendi',
        'prenom': 'Jean',
        'telephone': '+243 810 000 001',
        'sexe': 'M',
        'adresse': 'Kinshasa, RDC',
    },
    {
        'username': 'resp.logistique',
        'password': 'Logistique@2026!',
        'first_name': 'Marie',
        'last_name': 'Nzuzi',
        'fonction_code': 'RL',
        'nom': 'Nzuzi',
        'postnom': 'Mbuyi',
        'prenom': 'Marie',
        'telephone': '+243 810 000 002',
        'sexe': 'F',
        'adresse': 'Kinshasa, RDC',
    },
    {
        'username': 'manager',
        'password': 'Manager@2026!',
        'first_name': 'Paul',
        'last_name': 'Ilunga',
        'fonction_code': 'MGR',
        'nom': 'Ilunga',
        'postnom': 'Kalonji',
        'prenom': 'Paul',
        'telephone': '+243 810 000 003',
        'sexe': 'M',
        'adresse': 'Kinshasa, RDC',
    },
]

for compte in comptes:
    # Vérifier si l'utilisateur existe déjà
    user = User.objects.filter(username=compte['username']).first()
    if user:
        # Mettre à jour le mot de passe et les informations
        user.set_password(compte['password'])
        user.first_name = compte['first_name']
        user.last_name = compte['last_name']
        user.is_staff = True
        user.save()
        # Vérifier si un profil personnel existe
        if hasattr(user, 'personnel'):
            print(f"PASS Compte mis à jour: {compte['username']} / {compte['password']} ({compte['fonction_code']})")
        else:
            # Créer le profil personnel
            fonction = Fonction.objects.get(code=compte['fonction_code'])
            Personnel.objects.create(
                user=user,
                fonction=fonction,
                chantier=emplacement,
                nom=compte['nom'],
                postnom=compte['postnom'],
                prenom=compte['prenom'],
                telephone=compte['telephone'],
                sexe=compte['sexe'],
                adresse=compte['adresse'],
            )
            print(f"PASS Compte mis à jour avec profil: {compte['username']} / {compte['password']} ({compte['fonction_code']})")
        continue

    # Créer l'utilisateur
    user = User.objects.create_user(
        username=compte['username'],
        password=compte['password'],
        first_name=compte['first_name'],
        last_name=compte['last_name'],
    )
    user.is_staff = True
    user.save()

    # Récupérer la fonction
    fonction = Fonction.objects.get(code=compte['fonction_code'])

    # Créer le profil personnel
    Personnel.objects.create(
        user=user,
        fonction=fonction,
        chantier=emplacement,
        nom=compte['nom'],
        postnom=compte['postnom'],
        prenom=compte['prenom'],
        telephone=compte['telephone'],
        sexe=compte['sexe'],
        adresse=compte['adresse'],
    )

    print(f"PASS Compte cree: {compte['username']} / {compte['password']} ({compte['fonction_code']})")

# ============================================================
# 4. Afficher le récapitulatif
# ============================================================
print("\n" + "=" * 60)
print("RÉCAPITULATIF DES COMPTES")
print("=" * 60)
for u in User.objects.all():
    personnel = getattr(u, 'personnel', None)
    fonction = personnel.fonction.nom if personnel and personnel.fonction else 'Aucune'
    print(f"  {u.username} | {u.get_full_name()} | {fonction} | Superuser: {u.is_superuser}")