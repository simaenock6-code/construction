import datetime

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Article, Demande, Emplacement, Personnel, Stock, TypeDemande


class DemandeModelTests(TestCase):
    def test_save_generates_reference(self):
        type_demande = TypeDemande.objects.create(nom="Achat")
        demande = Demande.objects.create(
            type_demande=type_demande,
            date=datetime.date.today(),
        )

        self.assertIsNotNone(demande.reference)
        self.assertTrue(demande.reference.startswith("REQ-"))


class DemandeTemplateTests(TestCase):
    def test_demande_list_has_working_create_link(self):
        response = self.client.get(reverse("demande_list"))

        self.assertContains(response, f'href="{reverse("demande_create")}"')


class ArticleTemplateTests(TestCase):
    def test_article_list_has_working_create_link(self):
        response = self.client.get(reverse("article_list"))

        self.assertContains(response, f'href="{reverse("article_create")}"')


class StockFormTests(TestCase):
    def test_stock_allows_multiple_locations_for_same_article(self):
        article = Article.objects.create(code='CEM100', nom='Ciment', unite_mesure='sac')
        emplacement_a = Emplacement.objects.create(code='LOC1', location='Entrepôt')
        emplacement_b = Emplacement.objects.create(code='LOC2', location='Chantier')

        stock_a = Stock.objects.create(article=article, emplacement=emplacement_a, quantite_disponible=10)
        stock_b = Stock.objects.create(article=article, emplacement=emplacement_b, quantite_disponible=5)

        self.assertEqual(Stock.objects.filter(article=article).count(), 2)
        self.assertTrue(Stock.objects.filter(article=article, emplacement=emplacement_a).exists())
        self.assertTrue(Stock.objects.filter(article=article, emplacement=emplacement_b).exists())
        self.assertEqual(stock_a.quantite_disponible, 10)
        self.assertEqual(stock_b.quantite_disponible, 5)


class DemoDataCommandTests(TestCase):
    def test_demo_data_creates_two_chantiers_and_users(self):
        call_command("demo_data")

        self.assertTrue(Emplacement.objects.filter(code="CHANTA").exists())
        self.assertTrue(Emplacement.objects.filter(code="CHANTB").exists())

        users = get_user_model().objects.filter(username__in=["manager", "chefchantier_a", "chefchantier_b", "responsablelog"])
        self.assertEqual(users.count(), 4)
        self.assertTrue(all(user.check_password("demo") for user in users))


class ChantiersVisibilityTests(TestCase):
    def test_chef_chantier_only_sees_data_from_his_chantier(self):
        chantier_a = Emplacement.objects.create(code="CHANTA", location="Chantier A")
        chantier_b = Emplacement.objects.create(code="CHANTB", location="Chantier B")

        user = get_user_model().objects.create_user(username="chef_a", password="demo")
        other_user = get_user_model().objects.create_user(username="chef_b", password="demo")

        personnel_a = Personnel.objects.create(user=user, nom="A", prenom="Alice", chantier=chantier_a)
        personnel_b = Personnel.objects.create(user=other_user, nom="B", prenom="Bob", chantier=chantier_b)

        type_demande = TypeDemande.objects.create(nom="Achat")
        demande_a = Demande.objects.create(type_demande=type_demande, demandeur=personnel_a, date=datetime.date.today())
        Demande.objects.create(type_demande=type_demande, demandeur=personnel_b, date=datetime.date.today())

        article = Article.objects.create(code="ART1", nom="Article test", unite_mesure="pièce")
        stock_a = Stock.objects.create(article=article, emplacement=chantier_a, quantite_disponible=10)
        Stock.objects.create(article=article, emplacement=chantier_b, quantite_disponible=5)

        self.client.force_login(user)

        response = self.client.get(reverse("demande_list"))
        self.assertEqual(list(response.context["demandes"]), [demande_a])

        response = self.client.get(reverse("stock_list"))
        self.assertEqual(list(response.context["stocks"]), [stock_a])
