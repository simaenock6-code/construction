from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from app.models import (
    Article,
    Demande,
    Emplacement,
    Fonction,
    LigneDemande,
    Personnel,
    Stock,
    TypeDemande,
)


class Command(BaseCommand):
    help = "Créer des données de démonstration pour l’application."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("Création des données de démonstration...")

        # Fonctions
        fonctions = [
            {"code": "MGR", "nom": "Manager", "description": "Gestion générale de l’activité."},
            {"code": "CHC", "nom": "Chef de chantier", "description": "Suivi opérationnel des chantiers."},
            {"code": "RL", "nom": "Responsable logistique", "description": "Gestion des stocks et approvisionnements."},
        ]
        for data in fonctions:
            Fonction.objects.update_or_create(code=data["code"], defaults=data)
        fonctions_map = {f.code: f for f in Fonction.objects.all()}

        # Emplacements
        emplacements = [
            {"code": "SILO", "location": "Silo principal"},
            {"code": "ENTREP", "location": "Entrepôt central"},
            {"code": "CHANTA", "location": "Chantier A"}, # Chantier
            {"code": "CHANTB", "location": "Chantier B"}, # Chantier
        ]
        for data in emplacements:
            Emplacement.objects.update_or_create(code=data["code"], defaults=data)
        emplacements_map = {e.code: e for e in Emplacement.objects.all()}

        # Articles
        articles = [
            {"code": "CEM001", "nom": "Ciment", "description": "Sac de 50 kg.", "unite_mesure": "sac"},
            {"code": "FER002", "nom": "Fer à béton", "description": "Barre de 12 mm.", "unite_mesure": "kg"},
            {"code": "BRI003", "nom": "Brique", "description": "Brique pleine.", "unite_mesure": "pièce"},
        ]
        Article.objects.bulk_create(
            [Article(**data) for data in articles],
            update_conflicts=True, update_fields=["nom", "description", "unite_mesure"], unique_fields=["code"]
        )
        articles_map = {a.code: a for a in Article.objects.all()}

        # Stocks
        stock_map = {
            "CEM001": {"SILO": 120, "ENTREP": 80, "CHANTA": 40, "CHANTB": 30},
            "FER002": {"SILO": 50, "CHANTA": 30, "CHANTB": 20},
            "BRI003": {"ENTREP": 200, "CHANTA": 100, "CHANTB": 80},
        }
        stocks_to_create = []
        for article_code, locations in stock_map.items():
            for emp_code, quantity in locations.items():
                stocks_to_create.append(
                    Stock(article=articles_map[article_code], emplacement=emplacements_map[emp_code], quantite_disponible=quantity)
                )
        Stock.objects.bulk_create(
            stocks_to_create,
            update_conflicts=True, update_fields=["quantite_disponible"], unique_fields=["article", "emplacement"]
        )

        # Utilisateurs et personnels
        personnes = [
            {"username": "manager", "email": "manager@example.com", "first_name": "Manager", "last_name": "Demo", "password": "demo", "role_code": "MGR", "is_admin": True},
            {"username": "chefchantier_a", "email": "chefchantier_a@example.com", "first_name": "Chef", "last_name": "Chantier A", "password": "demo", "role_code": "CHC", "is_admin": False},
            {"username": "chefchantier_b", "email": "chefchantier_b@example.com", "first_name": "Chef", "last_name": "Chantier B", "password": "demo", "role_code": "CHC", "is_admin": False},
            {"username": "responsablelog", "email": "responsablelog@example.com", "first_name": "Responsable", "last_name": "Logistique", "password": "demo", "role_code": "RL", "is_admin": False},
        ]
        for person in personnes:
            user, created = User.objects.get_or_create(username=person["username"], defaults={
                "email": person["email"],
                "first_name": person["first_name"],
                "last_name": person["last_name"],
                "is_staff": person["is_admin"],
                "is_superuser": person["is_admin"],
            })
            if created or not user.check_password(person["password"]):
                user.set_password(person["password"])
                user.save()

            role = fonctions_map[person["role_code"]]

            chantier = None
            if person["username"] == "chefchantier_a":
                chantier = emplacements_map["CHANTA"]
            elif person["username"] == "chefchantier_b":
                chantier = emplacements_map["CHANTB"]

            Personnel.objects.update_or_create(
                user=user,
                defaults={
                    "fonction": role,
                    "chantier": chantier,
                    "nom": person["last_name"],
                    "postnom": "",
                    "prenom": person["first_name"],
                    "telephone": "+243 999 000 001",
                    "sexe": "M" if person["username"].startswith("chef") or person["username"] == "manager" else "F",
                    "datenaiss": timezone.now().date(),
                    "lieunaiss": "Kinshasa",
                    "adresse": "Avenue du Peuple 123",
                },
            )

        # Types de demandes
        types = [
            {"nom": "Achat", "description": "Demande d’achat matière première."},
            {"nom": "Maintenance", "description": "Demande de maintenance ou réparation."},
            {"nom": "Transport", "description": "Demande de transport et logistique."},
        ]
        TypeDemande.objects.bulk_create(
            [TypeDemande(**data) for data in types],
            update_conflicts=True, update_fields=["description"], unique_fields=["nom"]
        )
        types_demande_map = {td.nom: td for td in TypeDemande.objects.all()}

        # Demandes
        personnel_a = Personnel.objects.get(user__username="chefchantier_a")
        personnel_b = Personnel.objects.get(user__username="chefchantier_b")
        demandes = [
            {"type_demande": types_demande_map["Achat"], "demandeur": personnel_a, "date": timezone.now().date(), "statut": "NOUVEAU"},
            {"type_demande": types_demande_map["Maintenance"], "demandeur": personnel_b, "date": timezone.now().date(), "statut": "EN_COURS"},
        ]
        # Créer les demandes une par une pour que `save()` génère la référence unique.
        for d in demandes:
            Demande.objects.get_or_create(
                type_demande=d["type_demande"],
                demandeur=d["demandeur"],
                date=d["date"],
                statut=d["statut"],
                defaults={"reference": None},
            )

        # Lignes de demande (get_or_create pour rester idempotent en cas de re-exécution)
        articles_for_lignes = list(articles_map.values())[:2]
        for demande in Demande.objects.all():
            for article in articles_for_lignes:
                quantite = 10 if article.code == "CEM001" else 5
                LigneDemande.objects.get_or_create(
                    demande=demande,
                    article=article,
                    defaults={
                        "quantite": quantite,
                        "commentaire": "Donnée de démonstration.",
                    },
                )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées."))
