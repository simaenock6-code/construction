from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard'), name='logout'),

    # Utilisateurs
    path('utilisateurs/', views.UserListView.as_view(), name='user_list'),

    # Personnel CRUD
    path('personnels/', views.PersonnelListView.as_view(), name='personnel_list'),
    path('personnels/create/', views.PersonnelCreateView.as_view(), name='personnel_create'),
    path('personnels/<int:pk>/', views.PersonnelDetailView.as_view(), name='personnel_detail'),
    path('personnels/<int:pk>/edit/', views.PersonnelUpdateView.as_view(), name='personnel_update'),
    path('personnels/<int:pk>/delete/', views.PersonnelDeleteView.as_view(), name='personnel_delete'),

    # Fonction CRUD
    path('fonctions/', views.FonctionListView.as_view(), name='fonction_list'),
    path('fonctions/create/', views.FonctionCreateView.as_view(), name='fonction_create'),
    path('fonctions/<int:pk>/edit/', views.FonctionUpdateView.as_view(), name='fonction_update'),
    path('fonctions/<int:pk>/delete/', views.FonctionDeleteView.as_view(), name='fonction_delete'),

    # TypeDemande CRUD
    path('types-demandes/', views.TypeDemandeListView.as_view(), name='typedemande_list'),
    path('types-demandes/create/', views.TypeDemandeCreateView.as_view(), name='typedemande_create'),
    path('types-demandes/<int:pk>/edit/', views.TypeDemandeUpdateView.as_view(), name='typedemande_update'),
    path('types-demandes/<int:pk>/delete/', views.TypeDemandeDeleteView.as_view(), name='typedemande_delete'),

    # Emplacement CRUD
    path('emplacements/', views.EmplacementListView.as_view(), name='emplacement_list'),
    path('emplacements/create/', views.EmplacementCreateView.as_view(), name='emplacement_create'),
    path('emplacements/<int:pk>/edit/', views.EmplacementUpdateView.as_view(), name='emplacement_update'),
    path('emplacements/<int:pk>/delete/', views.EmplacementDeleteView.as_view(), name='emplacement_delete'),

    # Demande CRUD
    path('demandes/', views.DemandeListView.as_view(), name='demande_list'),
    path('demandes/create/', views.DemandeCreateView.as_view(), name='demande_create'),
    path('demandes/<int:pk>/edit/', views.DemandeUpdateView.as_view(), name='demande_update'),
    path('demandes/<int:pk>/delete/', views.DemandeDeleteView.as_view(), name='demande_delete'),

    # LigneDemande CRUD (lié à une demande)
    path('demandes/<int:demande_pk>/lignes/create/', views.LigneDemandeCreateView.as_view(), name='lignedemande_create'),
    path('lignes/<int:pk>/edit/', views.LigneDemandeUpdateView.as_view(), name='lignedemande_update'),
    path('lignes/<int:pk>/delete/', views.LigneDemandeDeleteView.as_view(), name='lignedemande_delete'),

    # Article CRUD
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    # Stock CRUD
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stocks/create/', views.StockCreateView.as_view(), name='stock_create'),
    path('stocks/<int:pk>/edit/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stocks/<int:pk>/delete/', views.StockDeleteView.as_view(), name='stock_delete'),

    # Bon d'entrée CRUD
    path('bons-entree/', views.BonEntreeListView.as_view(), name='bonentree_list'),
    path('bons-entree/create/', views.BonEntreeCreateView.as_view(), name='bonentree_create'),
    path('bons-entree/<int:pk>/', views.BonEntreeDetailView.as_view(), name='bonentree_detail'),
    path('bons-entree/<int:pk>/edit/', views.BonEntreeUpdateView.as_view(), name='bonentree_update'),
    path('bons-entree/<int:pk>/delete/', views.BonEntreeDeleteView.as_view(), name='bonentree_delete'),
    path('bons-entree/<int:bonentree_pk>/lignes/create/', views.LigneBonEntreeCreateView.as_view(), name='lignebonentree_create'),
    path('lignes-bon-entree/<int:pk>/edit/', views.LigneBonEntreeUpdateView.as_view(), name='lignebonentree_update'),
    path('lignes-bon-entree/<int:pk>/delete/', views.LigneBonEntreeDeleteView.as_view(), name='lignebonentree_delete'),

    # Bon de sortie CRUD
    path('bons-sortie/', views.BonSortieListView.as_view(), name='bonsortie_list'),
    path('bons-sortie/create/', views.BonSortieCreateView.as_view(), name='bonsortie_create'),
    path('bons-sortie/<int:pk>/', views.BonSortieDetailView.as_view(), name='bonsortie_detail'),
    path('bons-sortie/<int:pk>/edit/', views.BonSortieUpdateView.as_view(), name='bonsortie_update'),
    path('bons-sortie/<int:pk>/delete/', views.BonSortieDeleteView.as_view(), name='bonsortie_delete'),
    path('bons-sortie/<int:bonsortie_pk>/lignes/create/', views.LigneBonSortieCreateView.as_view(), name='lignebonsortie_create'),
    path('lignes-bon-sortie/<int:pk>/edit/', views.LigneBonSortieUpdateView.as_view(), name='lignebonsortie_update'),
    path('lignes-bon-sortie/<int:pk>/delete/', views.LigneBonSortieDeleteView.as_view(), name='lignebonsortie_delete'),

    # Devis CRUD
    path('devis/', views.DevisListView.as_view(), name='devis_list'),
    path('devis/create/', views.DevisCreateView.as_view(), name='devis_create'),
    path('devis/<int:pk>/', views.DevisDetailView.as_view(), name='devis_detail'),
    path('devis/<int:pk>/edit/', views.DevisUpdateView.as_view(), name='devis_update'),
    path('devis/<int:pk>/delete/', views.DevisDeleteView.as_view(), name='devis_delete'),
    path('devis/<int:devis_pk>/lignes/create/', views.LigneDevisCreateView.as_view(), name='lignedevis_create'),
    path('lignes-devis/<int:pk>/edit/', views.LigneDevisUpdateView.as_view(), name='lignedevis_update'),
    path('lignes-devis/<int:pk>/delete/', views.LigneDevisDeleteView.as_view(), name='lignedevis_delete'),
]
