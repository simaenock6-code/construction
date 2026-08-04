"""
Tests unitaires pour l'application de gestion de chantiers.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import (
    Fonction, Personnel, Emplacement, TypeDemande, Article,
    Demande, LigneDemande, Stock, BonEntree, LigneBonEntree,
    BonSortie, LigneBonSortie, Devis, LigneDevis
)

User = get_user_model()


class ModelTests(TestCase):
    """Tests des modèles de données."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Créer des fonctions
        self.fonction_rl = Fonction.objects.create(
            code="RL",
            nom="Responsable Logistique",
            description="Responsable de la logistique"
        )
        self.fonction_chc = Fonction.objects.create(
            code="CHC",
            nom="Chef de Chantier",
            description="Chef de chantier"
        )
        
        # Créer des emplacements
        self.emplacement1 = Emplacement.objects.create(
            code="EMP001",
            location="Chantier A"
        )
        self.emplacement2 = Emplacement.objects.create(
            code="EMP002",
            location="Chantier B"
        )
        
        # Créer des utilisateurs et personnels
        self.user_rl = User.objects.create_user(
            username="rl_test",
            password="test123",
            first_name="Jean",
            last_name="Dupont"
        )
        self.personnel_rl = Personnel.objects.create(
            user=self.user_rl,
            fonction=self.fonction_rl,
            nom="Dupont",
            prenom="Jean",
            telephone="0123456789"
        )
        
        self.user_chc = User.objects.create_user(
            username="chc_test",
            password="test123",
            first_name="Marie",
            last_name="Martin"
        )
        self.personnel_chc = Personnel.objects.create(
            user=self.user_chc,
            fonction=self.fonction_chc,
            chantier=self.emplacement1,
            nom="Martin",
            prenom="Marie",
            telephone="0987654321"
        )
        
        # Créer un type de demande
        self.type_demande = TypeDemande.objects.create(
            nom="Matériaux",
            description="Demande de matériaux de construction"
        )
        
        # Créer des articles
        self.article1 = Article.objects.create(
            code="ART001",
            nom="Ciment",
            description="Ciment Portland",
            unite_mesure="sacs",
            seuil_minimum=10
        )
        self.article2 = Article.objects.create(
            code="ART002",
            nom="Fer à béton",
            description="Fer à béton 12mm",
            unite_mesure="barres",
            seuil_minimum=20
        )

    def test_fonction_creation(self):
        """Test de création d'une fonction."""
        self.assertEqual(self.fonction_rl.code, "RL")
        self.assertEqual(self.fonction_rl.nom, "Responsable Logistique")
        self.assertEqual(str(self.fonction_rl), "Responsable Logistique")

    def test_personnel_creation(self):
        """Test de création d'un personnel."""
        self.assertEqual(self.personnel_rl.nom, "Dupont")
        self.assertEqual(self.personnel_rl.prenom, "Jean")
        self.assertEqual(str(self.personnel_rl), "Dupont Martin")
        
    def test_personnel_str_with_postnom(self):
        """Test de l'affichage du personnel avec postnom."""
        personnel = Personnel.objects.create(
            user=User.objects.create_user("test3", "test123"),
            fonction=self.fonction_chc,
            nom="Durand",
            postnom="Pierre",
            prenom="Paul"
        )
        self.assertEqual(str(personnel), "Durand Pierre Paul")

    def test_article_quantite_totale(self):
        """Test du calcul de quantité totale d'un article."""
        # Créer des stocks
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=50
        )
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement2,
            quantite_disponible=30
        )
        
        self.assertEqual(self.article1.quantite_totale(), 80)

    def test_article_quantite_par_emplacement(self):
        """Test du calcul de quantité par emplacement."""
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=50
        )
        
        self.assertEqual(
            self.article1.quantite_par_emplacement(self.emplacement1),
            50
        )
        self.assertEqual(
            self.article1.quantite_par_emplacement(self.emplacement2),
            0
        )

    def test_article_est_suffisant(self):
        """Test de la vérification de stock suffisant."""
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=50
        )
        
        self.assertTrue(self.article1.est_suffisant(30))
        self.assertTrue(self.article1.est_suffisant())  # Utilise seuil_minimum
        self.assertFalse(self.article1.est_suffisant(100))

    def test_article_shortage(self):
        """Test du calcul de quantité manquante."""
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=5
        )
        
        self.assertEqual(self.article1.shortage(10), 5)
        self.assertEqual(self.article1.shortage(3), 0)

    def test_article_etat_stock(self):
        """Test du statut de stock."""
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=5
        )
        
        self.assertEqual(self.article1.etat_stock(), "faible")
        self.assertEqual(self.article1.etat_stock(3), "suffisant")

    def test_demande_reference_generation(self):
        """Test de la génération automatique de référence."""
        demande = Demande.objects.create(
            type_demande=self.type_demande,
            demandeur=self.personnel_chc,
            date=date.today(),
            statut="NOUVEAU"
        )
        
        self.assertIsNotNone(demande.reference)
        self.assertTrue(demande.reference.startswith("REQ-"))
        self.assertEqual(len(demande.reference), 15)  # REQ-YYYYMMDD-N

    def test_bon_entree_reference_generation(self):
        """Test de la génération automatique de référence pour bon d'entrée."""
        bon = BonEntree.objects.create(
            date=date.today(),
            emplacement=self.emplacement1
        )
        
        self.assertIsNotNone(bon.reference)
        self.assertTrue(bon.reference.startswith("BE-"))

    def test_bon_sortie_reference_generation(self):
        """Test de la génération automatique de référence pour bon de sortie."""
        bon = BonSortie.objects.create(
            date=date.today(),
            emplacement=self.emplacement1
        )
        
        self.assertIsNotNone(bon.reference)
        self.assertTrue(bon.reference.startswith("BS-"))

    def test_devis_reference_generation(self):
        """Test de la génération automatique de référence pour devis."""
        devis = Devis.objects.create(
            date=date.today(),
            client="Client Test"
        )
        
        self.assertIsNotNone(devis.reference)
        self.assertTrue(devis.reference.startswith("DEV-"))

    def test_ligne_bon_entree_total_ligne(self):
        """Test du calcul du total d'une ligne de bon d'entrée."""
        ligne = LigneBonEntree.objects.create(
            bon_entree=BonEntree.objects.create(date=date.today()),
            article=self.article1,
            quantite=10,
            prix_unitaire=15.50
        )
        
        self.assertEqual(ligne.total_ligne(), 155.00)

    def test_ligne_devis_total_ligne(self):
        """Test du calcul du total d'une ligne de devis."""
        ligne = LigneDevis.objects.create(
            devis=Devis.objects.create(date=date.today(), client="Client"),
            article=self.article1,
            quantite=5,
            prix_unitaire=20.00
        )
        
        self.assertEqual(ligne.total_ligne(), 100.00)

    def test_devis_total_devis(self):
        """Test du calcul du total d'un devis."""
        devis = Devis.objects.create(
            date=date.today(),
            client="Client Test"
        )
        LigneDevis.objects.create(
            devis=devis,
            article=self.article1,
            quantite=5,
            prix_unitaire=20.00
        )
        LigneDevis.objects.create(
            devis=devis,
            article=self.article2,
            quantite=3,
            prix_unitaire=15.00
        )
        
        self.assertEqual(devis.total_devis(), 145.00)

    def test_stock_unique_constraint(self):
        """Test de la contrainte d'unicité sur Stock (article, emplacement)."""
        Stock.objects.create(
            article=self.article1,
            emplacement=self.emplacement1,
            quantite_disponible=10
        )
        
        # Tentative de création d'un stock en double
        with self.assertRaises(Exception):
            Stock.objects.create(
                article=self.article1,
                emplacement=self.emplacement1,
                quantite_disponible=20
            )


class ViewTests(TestCase):
    """Tests des vues."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = Client()
        
        # Créer les fonctions
        self.fonction_rl = Fonction.objects.create(
            code="RL",
            nom="Responsable Logistique"
        )
        self.fonction_chc = Fonction.objects.create(
            code="CHC",
            nom="Chef de Chantier"
        )
        
        # Créer les emplacements
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        
        # Créer les utilisateurs
        self.user_rl = User.objects.create_user(
            username="rl_test",
            password="test123",
            first_name="Jean",
            last_name="Dupont"
        )
        self.personnel_rl = Personnel.objects.create(
            user=self.user_rl,
            fonction=self.fonction_rl,
            nom="Dupont",
            prenom="Jean"
        )
        
        self.user_chc = User.objects.create_user(
            username="chc_test",
            password="test123",
            first_name="Marie",
            last_name="Martin"
        )
        self.personnel_chc = Personnel.objects.create(
            user=self.user_chc,
            fonction=self.fonction_chc,
            chantier=self.emplacement,
            nom="Martin",
            prenom="Marie"
        )

    def test_dashboard_access_authenticated(self):
        """Test d'accès au dashboard avec authentification."""
        self.client.login(username="rl_test", password="test123")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dashboard.html')

    def test_dashboard_access_unauthenticated(self):
        """Test d'accès au dashboard sans authentification."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_dashboard_resp_logistique_context(self):
        """Test du contexte du dashboard pour Responsable Logistique."""
        self.client.login(username="rl_test", password="test123")
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_resp_logistique'])
        self.assertFalse(response.context['is_chef_chantier'])

    def test_dashboard_chef_chantier_context(self):
        """Test du contexte du dashboard pour Chef de Chantier."""
        self.client.login(username="chc_test", password="test123")
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_chef_chantier'])
        self.assertFalse(response.context['is_resp_logistique'])
        self.assertEqual(response.context['chantier'], self.emplacement)

    def test_personnel_list_view(self):
        """Test de la liste des personnels."""
        self.client.login(username="rl_test", password="test123")
        response = self.client.get(reverse('personnel_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/personnel_list.html')

    def test_article_list_view(self):
        """Test de la liste des articles."""
        self.client.login(username="rl_test", password="test123")
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/article_list.html')

    def test_demande_create_view_get(self):
        """Test d'affichage du formulaire de création de demande."""
        self.client.login(username="chc_test", password="test123")
        response = self.client.get(reverse('demande_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/demande_form.html')

    def test_demande_create_view_post(self):
        """Test de création d'une demande."""
        self.client.login(username="chc_test", password="test123")
        
        demande_data = {
            'type_demande': self.type_demande.id,
            'demandeur': self.personnel_chc.id,
            'date': date.today().strftime('%Y-%m-%d'),
        }
        
        response = self.client.post(
            reverse('demande_create'),
            data=demande_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Demande.objects.filter(demandeur=self.personnel_chc).exists())


class DemandeTests(TestCase):
    """Tests des demandes."""

    def setUp(self):
        """Configuration initiale."""
        self.fonction = Fonction.objects.create(code="CHC", nom="Chef de Chantier")
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        self.user = User.objects.create_user(
            username="test_user",
            password="test123",
            first_name="Jean",
            last_name="Dupont"
        )
        self.personnel = Personnel.objects.create(
            user=self.user,
            fonction=self.fonction,
            chantier=self.emplacement,
            nom="Dupont",
            prenom="Jean"
        )
        self.type_demande = TypeDemande.objects.create(
            nom="Matériaux",
            description="Demande de matériaux"
        )
        self.article = Article.objects.create(
            code="ART001",
            nom="Ciment",
            unite_mesure="sacs",
            seuil_minimum=10
        )

    def test_demande_creation_with_lignes(self):
        """Test de création d'une demande avec lignes."""
        demande = Demande.objects.create(
            type_demande=self.type_demande,
            demandeur=self.personnel,
            date=date.today(),
            statut="NOUVEAU"
        )
        
        # Créer des lignes de demande
        ligne1 = LigneDemande.objects.create(
            demande=demande,
            article=self.article,
            quantite=5,
            commentaire="Urgent"
        )
        
        self.assertEqual(demande.lignes.count(), 1)
        self.assertEqual(ligne1.article, self.article)
        self.assertEqual(ligne1.quantite, 5)

    def test_demande_str(self):
        """Test de l'affichage d'une demande."""
        demande = Demande.objects.create(
            type_demande=self.type_demande,
            demandeur=self.personnel,
            date=date.today(),
            statut="NOUVEAU"
        )
        
        # La référence est générée automatiquement
        self.assertIn("REQ-", str(demande))


class StockTests(TestCase):
    """Tests de gestion des stocks."""

    def setUp(self):
        """Configuration initiale."""
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        self.article = Article.objects.create(
            code="ART001",
            nom="Ciment",
            unite_mesure="sacs",
            seuil_minimum=10
        )

    def test_stock_creation(self):
        """Test de création d'un stock."""
        stock = Stock.objects.create(
            article=self.article,
            emplacement=self.emplacement,
            quantite_disponible=50
        )
        
        self.assertEqual(stock.quantite_disponible, 50)
        self.assertEqual(stock.article, self.article)
        self.assertEqual(stock.emplacement, self.emplacement)

    def test_stock_str(self):
        """Test de l'affichage d'un stock."""
        stock = Stock.objects.create(
            article=self.article,
            emplacement=self.emplacement,
            quantite_disponible=50
        )
        
        expected = f"{self.article.nom} - {self.emplacement.location} - 50"
        self.assertEqual(str(stock), expected)

    def test_stock_without_emplacement(self):
        """Test d'un stock sans emplacement."""
        stock = Stock.objects.create(
            article=self.article,
            quantite_disponible=30
        )
        
        self.assertEqual(str(stock), f"{self.article.nom} - Sans emplacement - 30")


class BonSortieTests(TestCase):
    """Tests des bons de sortie."""

    def setUp(self):
        """Configuration initiale."""
        self.fonction = Fonction.objects.create(code="CHC", nom="Chef de Chantier")
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        self.user = User.objects.create_user(
            username="test_user",
            password="test123"
        )
        self.personnel = Personnel.objects.create(
            user=self.user,
            fonction=self.fonction,
            chantier=self.emplacement,
            nom="Dupont",
            prenom="Jean"
        )
        self.type_demande = TypeDemande.objects.create(nom="Matériaux")
        self.article = Article.objects.create(
            code="ART001",
            nom="Ciment",
            unite_mesure="sacs",
            seuil_minimum=10
        )
        
        # Créer une demande
        self.demande = Demande.objects.create(
            type_demande=self.type_demande,
            demandeur=self.personnel,
            date=date.today(),
            statut="NOUVEAU"
        )
        
        # Créer une ligne de demande
        self.ligne_demande = LigneDemande.objects.create(
            demande=self.demande,
            article=self.article,
            quantite=5
        )
        
        # Créer du stock
        self.stock = Stock.objects.create(
            article=self.article,
            emplacement=self.emplacement,
            quantite_disponible=20
        )

    def test_bon_sortie_creation_avec_demande(self):
        """Test de création d'un bon de sortie avec demande."""
        bon = BonSortie.objects.create(
            date=date.today(),
            demande=self.demande,
            destinataire="Jean Dupont",
            emplacement=self.emplacement
        )
        
        self.assertEqual(bon.demande, self.demande)
        self.assertEqual(bon.destinataire, "Jean Dupont")
        self.assertIsNotNone(bon.reference)

    def test_ligne_bon_sortie_stock_update(self):
        """Test de la mise à jour du stock lors de création d'une ligne de bon de sortie."""
        bon = BonSortie.objects.create(
            date=date.today(),
            emplacement=self.emplacement
        )
        
        # Créer une ligne de bon de sortie
        ligne = LigneBonSortie.objects.create(
            bon_sortie=bon,
            article=self.article,
            quantite=5
        )
        
        # Vérifier que le stock a été décrémenté
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite_disponible, 15)

    def test_ligne_bon_sortie_delete_stock_update(self):
        """Test de la restauration du stock lors de suppression d'une ligne."""
        bon = BonSortie.objects.create(
            date=date.today(),
            emplacement=self.emplacement
        )
        
        ligne = LigneBonSortie.objects.create(
            bon_sortie=bon,
            article=self.article,
            quantite=5
        )
        
        # Le stock est maintenant à 15
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite_disponible, 15)
        
        # Supprimer la ligne
        ligne.delete()
        
        # Le stock doit être restauré à 20
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite_disponible, 20)


class IntegrationTests(TestCase):
    """Tests d'intégration."""

    def setUp(self):
        """Configuration initiale."""
        self.client = Client()
        
        # Créer un responsable logistique
        self.fonction_rl = Fonction.objects.create(
            code="RL",
            nom="Responsable Logistique"
        )
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        self.user_rl = User.objects.create_user(
            username="rl_test",
            password="test123",
            first_name="Jean",
            last_name="Dupont"
        )
        self.personnel_rl = Personnel.objects.create(
            user=self.user_rl,
            fonction=self.fonction_rl,
            nom="Dupont",
            prenom="Jean"
        )
        
        # Créer un chef de chantier
        self.fonction_chc = Fonction.objects.create(
            code="CHC",
            nom="Chef de Chantier"
        )
        self.user_chc = User.objects.create_user(
            username="chc_test",
            password="test123",
            first_name="Marie",
            last_name="Martin"
        )
        self.personnel_chc = Personnel.objects.create(
            user=self.user_chc,
            fonction=self.fonction_chc,
            chantier=self.emplacement,
            nom="Martin",
            prenom="Marie"
        )
        
        # Créer un type de demande et un article
        self.type_demande = TypeDemande.objects.create(nom="Matériaux")
        self.article = Article.objects.create(
            code="ART001",
            nom="Ciment",
            unite_mesure="sacs",
            seuil_minimum=10
        )

    def test_workflow_demande_to_bon_sortie(self):
        """Test du workflow complet: Demande -> Bon de sortie."""
        # 1. Chef de chantier crée une demande
        self.client.login(username="chc_test", password="test123")
        
        demande_data = {
            'type_demande': self.type_demande.id,
            'demandeur': self.personnel_chc.id,
            'date': date.today().strftime('%Y-%m-%d'),
        }
        
        response = self.client.post(
            reverse('demande_create'),
            data=demande_data,
            follow=True
        )
        
        demande = Demande.objects.first()
        self.assertEqual(demande.statut, "NOUVEAU")
        
        # 2. Créer du stock
        stock = Stock.objects.create(
            article=self.article,
            emplacement=self.emplacement,
            quantite_disponible=20
        )
        
        # 3. Ajouter une ligne de demande
        ligne = LigneDemande.objects.create(
            demande=demande,
            article=self.article,
            quantite=5
        )
        
        # 4. Responsable logistique crée un bon de sortie
        self.client.login(username="rl_test", password="test123")
        
        bon_sortie_data = {
            'date': date.today().strftime('%Y-%m-%d'),
            'demande': demande.id,
            'destinataire': 'Marie Martin',
            'emplacement': self.emplacement.id,
            'commentaire': 'Livraison chantier'
        }
        
        response = self.client.post(
            reverse('bonsortie_create') + f'?demande={demande.id}',
            data=bon_sortie_data,
            follow=True
        )
        
        # 5. Vérifications
        demande.refresh_from_db()
        self.assertEqual(demande.statut, "VALIDE")
        
        bon_sortie = BonSortie.objects.first()
        self.assertIsNotNone(bon_sortie)
        self.assertEqual(bon_sortie.demande, demande)
        
        # 6. Vérifier que le stock a été décrémenté
        stock.refresh_from_db()
        self.assertEqual(stock.quantite_disponible, 15)

    def test_workflow_bon_entree_stock(self):
        """Test du workflow: Bon d'entrée -> Mise à jour stock."""
        self.client.login(username="rl_test", password="test123")
        
        # Créer un bon d'entrée
        bon_entree_data = {
            'date': date.today().strftime('%Y-%m-%d'),
            'fournisseur': 'Fournisseur Test',
            'emplacement': self.emplacement.id,
            'commentaire': 'Livraison mensuelle'
        }
        
        response = self.client.post(
            reverse('bonentree_create'),
            data=bon_entree_data,
            follow=True
        )
        
        bon_entree = BonEntree.objects.first()
        self.assertIsNotNone(bon_entree)
        
        # Ajouter une ligne de bon d'entrée
        ligne = LigneBonEntree.objects.create(
            bon_entree=bon_entree,
            article=self.article,
            quantite=50,
            prix_unitaire=10.00
        )
        
        # Vérifier que le stock a été incrémenté
        stock = Stock.objects.get(article=self.article, emplacement=self.emplacement)
        self.assertEqual(stock.quantite_disponible, 50)


class PermissionTests(TestCase):
    """Tests des permissions et accès."""

    def setUp(self):
        """Configuration initiale."""
        self.client = Client()
        
        self.fonction_rl = Fonction.objects.create(code="RL", nom="Responsable Logistique")
        self.fonction_chc = Fonction.objects.create(code="CHC", nom="Chef de Chantier")
        
        self.emplacement1 = Emplacement.objects.create(
            code="EMP001",
            location="Chantier A"
        )
        self.emplacement2 = Emplacement.objects.create(
            code="EMP002",
            location="Chantier B"
        )
        
        # Responsable Logistique
        self.user_rl = User.objects.create_user(
            username="rl_test",
            password="test123"
        )
        self.personnel_rl = Personnel.objects.create(
            user=self.user_rl,
            fonction=self.fonction_rl,
            nom="RL",
            prenom="Test"
        )
        
        # Chef de Chantier 1
        self.user_chc1 = User.objects.create_user(
            username="chc1_test",
            password="test123"
        )
        self.personnel_chc1 = Personnel.objects.create(
            user=self.user_chc1,
            fonction=self.fonction_chc,
            chantier=self.emplacement1,
            nom="CHC1",
            prenom="Test"
        )
        
        # Chef de Chantier 2
        self.user_chc2 = User.objects.create_user(
            username="chc2_test",
            password="test123"
        )
        self.personnel_chc2 = Personnel.objects.create(
            user=self.user_chc2,
            fonction=self.fonction_chc,
            chantier=self.emplacement2,
            nom="CHC2",
            prenom="Test"
        )

    def test_chef_chantier_acces_son_chantier_only(self):
        """Test qu'un chef de chantier ne voit que son chantier."""
        # Créer des personnels dans différents chantiers
        Personnel.objects.create(
            user=User.objects.create_user("p1", "test123"),
            fonction=self.fonction_chc,
            chantier=self.emplacement1,
            nom="Personnel1",
            prenom="Test"
        )
        Personnel.objects.create(
            user=User.objects.create_user("p2", "test123"),
            fonction=self.fonction_chc,
            chantier=self.emplacement2,
            nom="Personnel2",
            prenom="Test"
        )
        
        # CHC1 se connecte
        self.client.login(username="chc1_test", password="test123")
        response = self.client.get(reverse('personnel_list'))
        
        # Vérifier qu'il ne voit que les personnels de son chantier
        personnels = response.context['personnels']
        for p in personnels:
            self.assertEqual(p.chantier, self.emplacement1)

    def test_resp_logistique_acces_tous_chantiers(self):
        """Test qu'un responsable logistique voit tous les chantiers."""
        # Créer des personnels dans différents chantiers
        Personnel.objects.create(
            user=User.objects.create_user("p1", "test123"),
            fonction=self.fonction_chc,
            chantier=self.emplacement1,
            nom="Personnel1",
            prenom="Test"
        )
        Personnel.objects.create(
            user=User.objects.create_user("p2", "test123"),
            fonction=self.fonction_chc,
            chantier=self.emplacement2,
            nom="Personnel2",
            prenom="Test"
        )
        
        # RL se connecte
        self.client.login(username="rl_test", password="test123")
        response = self.client.get(reverse('personnel_list'))
        
        # Vérifier qu'il voit tous les personnels
        personnels = response.context['personnels']
        self.assertEqual(personnels.count(), 2)


class FormTests(TestCase):
    """Tests des formulaires."""

    def setUp(self):
        """Configuration initiale."""
        self.fonction = Fonction.objects.create(
            code="CHC",
            nom="Chef de Chantier"
        )
        self.emplacement = Emplacement.objects.create(
            code="EMP001",
            location="Chantier Test"
        )
        self.user = User.objects.create_user(
            username="test_user",
            password="test123"
        )
        self.personnel = Personnel.objects.create(
            user=self.user,
            fonction=self.fonction,
            chantier=self.emplacement,
            nom="Dupont",
            prenom="Jean"
        )
        self.type_demande = TypeDemande.objects.create(nom="Matériaux")
        self.article = Article.objects.create(
            code="ART001",
            nom="Ciment",
            unite_mesure="sacs",
            seuil_minimum=10
        )

    def test_demande_form_valid(self):
        """Test de validation du formulaire de demande."""
        from .forms import DemandeForm
        
        form_data = {
            'type_demande': self.type_demande.id,
            'demandeur': self.personnel.id,
            'date': date.today(),
        }
        
        form = DemandeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_demande_form_invalid(self):
        """Test de validation du formulaire de demande avec données invalides."""
        from .forms import DemandeForm
        
        form_data = {
            'type_demande': self.type_demande.id,
            # demandeur manquant
            'date': date.today(),
        }
        
        form = DemandeForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_article_form_valid(self):
        """Test de validation du formulaire d'article."""
        from .forms import ArticleForm
        
        form_data = {
            'code': 'ART002',
            'nom': 'Nouvel Article',
            'description': 'Description test',
            'unite_mesure': 'kg',
            'seuil_minimum': 5
        }
        
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_stock_form_update_disabled_fields(self):
        """Test que les champs article et emplacement sont désactivés en mode update."""
        from .forms import StockForm
        
        stock = Stock.objects.create(
            article=self.article,
            emplacement=self.emplacement,
            quantite_disponible=10
        )
        
        form = StockForm(instance=stock, is_update=True)
        self.assertTrue(form.fields['article'].disabled)
        self.assertTrue(form.fields['emplacement'].disabled)