from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils import timezone
import logging

# Configuration du logger pour les opérations critiques
logger = logging.getLogger(__name__)

User = get_user_model()


def _get_user_chantier(request):
    personnel = getattr(request.user, "personnel", None)
    if personnel and personnel.chantier:
        return personnel.chantier
    return None

from django.db.models import Count, F, Q, Sum
from .models import (
    Article, BonEntree, BonSortie, Demande, Devis, Emplacement,
    Fonction, LigneBonEntree, LigneBonSortie, LigneDemande,
    LigneDevis, Personnel, Stock, TypeDemande,
)
from .forms import (
    ArticleForm, BonEntreeForm, BonSortieForm, DemandeForm, DevisForm,
    EmplacementForm, FonctionForm, LigneBonEntreeForm, LigneBonSortieForm,
    LigneDemandeForm, LigneDevisForm, PersonnelForm, StockForm, TypeDemandeForm,
)

@login_required(login_url='login')
def dashboard(request):
    chantier = _get_user_chantier(request)
    
    # Déterminer le rôle de l'utilisateur
    personnel = getattr(request.user, "personnel", None)
    role_code = personnel.fonction.code if personnel and personnel.fonction else ""
    is_resp_logistique = role_code == "RL"

    demandes_qs = Demande.objects.all()
    stocks_qs = Stock.objects.all()
    personnels_qs = Personnel.objects.all()
    articles_qs = Article.objects.all()
    
    # Le responsable logistique voit toutes les données (pas de filtre par chantier)
    # Les chefs de chantier ne voient que leur chantier
    if not is_resp_logistique and chantier:
        demandes_qs = demandes_qs.filter(demandeur__chantier=chantier)
        stocks_qs = stocks_qs.filter(emplacement=chantier)
        personnels_qs = personnels_qs.filter(chantier=chantier)
        articles_qs = articles_qs.filter(stocks__emplacement=chantier).distinct()

    # Rôle de l'utilisateur connecté
    personnel = getattr(request.user, "personnel", None)
    role_code = personnel.fonction.code if personnel and personnel.fonction else ""
    is_chef_chantier = role_code == "CHC"
    is_resp_logistique = role_code == "RL"

    # Pagination parameters
    page = request.GET.get('page', 1)
    items_per_page = 10
    
    # Statistiques par statut de demande
    statuts_demandes = {
        "NOUVEAU": demandes_qs.filter(statut="NOUVEAU").count(),
        "EN_COURS": demandes_qs.filter(statut="EN_COURS").count(),
        "VALIDE": demandes_qs.filter(statut="VALIDE").count(),
        "REFUSE": demandes_qs.filter(statut="REFUSE").count(),
    }

    # Alertes stock faible (quantité disponible <= seuil_minimum de l'article)
    alertes_stock = stocks_qs.filter(
        quantite_disponible__lte=F("article__seuil_minimum")
    ).select_related("article", "emplacement").order_by("quantite_disponible")[:10]

    # Équipe du chantier (personnels rattachés)
    equipe_chantier = personnels_qs.select_related("fonction", "user").order_by("nom")[:10]

    # Dernières demandes avec lignes d'articles (avec pagination)
    demandes_list = demandes_qs.select_related("type_demande", "demandeur").prefetch_related("lignes__article").order_by('-date')[:items_per_page]

    # ===== Données spécifiques au Responsable Logistique =====
    bons_entree_count = BonEntree.objects.count()
    bons_sortie_count = BonSortie.objects.count()
    devis_count = Devis.objects.count()

    # Derniers bons d'entrée
    bons_entree_list = BonEntree.objects.select_related("emplacement").prefetch_related("lignes__article").order_by('-date')[:items_per_page]

    # Derniers bons de sortie
    bons_sortie_list = BonSortie.objects.select_related("demande", "emplacement").prefetch_related("lignes__article").order_by('-date')[:items_per_page]

    # Derniers devis
    devis_list = Devis.objects.select_related("demande").prefetch_related("lignes__article").order_by('-date')[:items_per_page]

    # Demandes reçues (toutes les demandes pour le responsable logistique) avec pagination
    demandes_recues = demandes_qs.select_related("type_demande", "demandeur").prefetch_related("lignes__article").order_by('-date')[:items_per_page]

    # Vérification de la disponibilité du stock pour chaque demande
    demandes_avec_stock = []
    for demande in demandes_recues:
        lignes_info = []
        stock_suffisant = True
        # Récupérer l'emplacement du demandeur (son chantier)
        emplacement_demandeur = demande.demandeur.chantier if demande.demandeur else None
        
        for ligne in demande.lignes.all():
            # Utiliser la quantité par emplacement si disponible, sinon la quantité totale
            if emplacement_demandeur:
                quantite_totale = ligne.article.quantite_par_emplacement(emplacement_demandeur)
            else:
                quantite_totale = ligne.article.quantite_totale()
            
            suffisant = quantite_totale >= ligne.quantite
            if not suffisant:
                stock_suffisant = False
            # Calculer la quantité manquante (positive si manque, 0 si suffisant)
            manque = max(0, ligne.quantite - quantite_totale)
            lignes_info.append({
                'article': ligne.article,
                'quantite': ligne.quantite,
                'disponible': quantite_totale,
                'suffisant': suffisant,
                'manque': manque,
            })
        demandes_avec_stock.append({
            'demande': demande,
            'lignes_info': lignes_info,
            'stock_suffisant': stock_suffisant,
        })

    context = {
        "chantier": chantier,
        "personnels_count": personnels_qs.count(),
        "demandes_count": demandes_qs.count(),
        "articles_count": articles_qs.count(),
        "stocks_count": stocks_qs.count(),
        "statuts_demandes": statuts_demandes,
        "alertes_stock": alertes_stock,
        "equipe_chantier": equipe_chantier,
        "demandes_list": demandes_list,
        "is_chef_chantier": is_chef_chantier,
        "is_resp_logistique": is_resp_logistique,
        "role_code": role_code,
        # Données responsable logistique
        "bons_entree_count": bons_entree_count,
        "bons_sortie_count": bons_sortie_count,
        "devis_count": devis_count,
        "bons_entree_list": bons_entree_list,
        "bons_sortie_list": bons_sortie_list,
        "devis_list": devis_list,
        "demandes_avec_stock": demandes_avec_stock,
    }
    return render(request, "app/dashboard.html", context)


# ============================================================
# UTILISATEURS
# ============================================================

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "app/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().select_related("personnel__fonction", "personnel__chantier").order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        return context


# ============================================================
# PERSONNEL CRUD
# ============================================================

class PersonnelListView(LoginRequiredMixin, ListView):
    model = Personnel
    template_name = "app/personnel_list.html"
    context_object_name = "personnels"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        chantier = _get_user_chantier(self.request)
        if chantier:
            queryset = queryset.filter(chantier=chantier)
        return queryset.select_related("user", "fonction")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        return context


class PersonnelCreateView(LoginRequiredMixin, CreateView):
    model = Personnel
    form_class = PersonnelForm
    template_name = "app/personnel_form.html"
    success_url = reverse_lazy('personnel_list')

    def form_valid(self, form):
        User = get_user_model()
        prenom = form.cleaned_data.get('prenom', '')
        nom = form.cleaned_data.get('nom', '')
        base = slugify(f"{prenom}.{nom}") or 'user'
        username = base
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{suffix}"
            suffix += 1

        password = get_random_string(10)
        user = User.objects.create(username=username, first_name=prenom, last_name=nom)
        user.set_password(password)
        user.save()

        # attach created user to Personnel before saving
        form.instance.user = user
        response = super().form_valid(form)

        # Logging de la création d'utilisateur
        logger.info(f"Création utilisateur: {user.username} pour personnel {prenom} {nom}")
        print(f"Created user for Personnel: {user.username} (password: {password})")

        return response


class PersonnelUpdateView(LoginRequiredMixin, UpdateView):
    model = Personnel
    form_class = PersonnelForm
    template_name = "app/personnel_form.html"
    success_url = reverse_lazy('personnel_list')


class PersonnelDeleteView(LoginRequiredMixin, DeleteView):
    model = Personnel
    template_name = "app/personnel_confirm_delete.html"
    success_url = reverse_lazy('personnel_list')


class PersonnelDetailView(LoginRequiredMixin, DetailView):
    model = Personnel
    template_name = "app/personnel_detail.html"
    context_object_name = "personnel"


# ============================================================
# FONCTION CRUD
# ============================================================

class FonctionListView(LoginRequiredMixin, ListView):
    model = Fonction
    template_name = "app/fonction_list.html"
    context_object_name = "fonctions"
    paginate_by = 20


class FonctionCreateView(LoginRequiredMixin, CreateView):
    model = Fonction
    form_class = FonctionForm
    template_name = "app/fonction_form.html"
    success_url = reverse_lazy('fonction_list')


class FonctionUpdateView(LoginRequiredMixin, UpdateView):
    model = Fonction
    form_class = FonctionForm
    template_name = "app/fonction_form.html"
    success_url = reverse_lazy('fonction_list')


class FonctionDeleteView(LoginRequiredMixin, DeleteView):
    model = Fonction
    template_name = "app/fonction_confirm_delete.html"
    success_url = reverse_lazy('fonction_list')


# ============================================================
# TYPE DEMANDE CRUD
# ============================================================

class TypeDemandeListView(LoginRequiredMixin, ListView):
    model = TypeDemande
    template_name = "app/typedemande_list.html"
    context_object_name = "types_demande"
    paginate_by = 20


class TypeDemandeCreateView(LoginRequiredMixin, CreateView):
    model = TypeDemande
    form_class = TypeDemandeForm
    template_name = "app/typedemande_form.html"
    success_url = reverse_lazy('typedemande_list')


class TypeDemandeUpdateView(LoginRequiredMixin, UpdateView):
    model = TypeDemande
    form_class = TypeDemandeForm
    template_name = "app/typedemande_form.html"
    success_url = reverse_lazy('typedemande_list')


class TypeDemandeDeleteView(LoginRequiredMixin, DeleteView):
    model = TypeDemande
    template_name = "app/typedemande_confirm_delete.html"
    success_url = reverse_lazy('typedemande_list')


# ============================================================
# EMPLACEMENT CRUD
# ============================================================

class EmplacementListView(LoginRequiredMixin, ListView):
    model = Emplacement
    template_name = "app/emplacement_list.html"
    context_object_name = "emplacements"
    paginate_by = 20


class EmplacementCreateView(LoginRequiredMixin, CreateView):
    model = Emplacement
    form_class = EmplacementForm
    template_name = "app/emplacement_form.html"
    success_url = reverse_lazy('emplacement_list')


class EmplacementUpdateView(LoginRequiredMixin, UpdateView):
    model = Emplacement
    form_class = EmplacementForm
    template_name = "app/emplacement_form.html"
    success_url = reverse_lazy('emplacement_list')


class EmplacementDeleteView(LoginRequiredMixin, DeleteView):
    model = Emplacement
    template_name = "app/emplacement_confirm_delete.html"
    success_url = reverse_lazy('emplacement_list')


# ============================================================
# DEMANDE CRUD
# ============================================================

class DemandeListView(LoginRequiredMixin, ListView):
    model = Demande
    template_name = "app/demande_list.html"
    context_object_name = "demandes"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        chantier = _get_user_chantier(self.request)
        if chantier:
            queryset = queryset.filter(demandeur__chantier=chantier)
        # Utiliser prefetch_related pour charger les lignes et leurs articles
        return queryset.select_related("type_demande", "demandeur").prefetch_related("lignes__article")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        context["is_resp_logistique"] = role_code == "RL"
        return context


class DemandeCreateView(LoginRequiredMixin, CreateView):
    model = Demande
    form_class = DemandeForm
    template_name = "app/demande_form.html"
    success_url = reverse_lazy('demande_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['chantier'] = _get_user_chantier(self.request)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        # Pré-remplir le demandeur avec le personnel connecté (pour un chef de chantier ou responsable logistique)
        personnel = getattr(self.request.user, "personnel", None)
        if personnel and _get_user_chantier(self.request):
            initial["demandeur"] = personnel
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        context["is_resp_logistique"] = role_code == "RL"
        # Ajouter la liste des articles pour le formulaire
        context["articles"] = Article.objects.all().order_by('nom')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Créer les lignes de demande à partir des données du formulaire
        # Récupérer toutes les clés qui contiennent 'lignes'
        lignes_data = []
        for key, value in self.request.POST.items():
            if 'lignes' in key.lower():
                lignes_data.append(value)
        
        for ligne_json in lignes_data:
            try:
                import json
                ligne = json.loads(ligne_json)
                LigneDemande.objects.create(
                    demande=self.object,
                    article_id=ligne['articleId'],
                    quantite=ligne['quantite'],
                    commentaire=ligne.get('commentaire', '')
                )
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        return response


class DemandeUpdateView(LoginRequiredMixin, UpdateView):
    model = Demande
    form_class = DemandeForm
    template_name = "app/demande_form.html"
    success_url = reverse_lazy('demande_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['chantier'] = _get_user_chantier(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        return context


class DemandeDeleteView(LoginRequiredMixin, DeleteView):
    model = Demande
    template_name = "app/demande_confirm_delete.html"
    success_url = reverse_lazy('demande_list')


# ============================================================
# LIGNE DEMANDE CRUD
# ============================================================

class LigneDemandeCreateView(LoginRequiredMixin, CreateView):
    model = LigneDemande
    form_class = LigneDemandeForm
    template_name = "app/lignedemande_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["demande"] = Demande.objects.get(pk=self.kwargs["demande_pk"])
        return context

    def form_valid(self, form):
        form.instance.demande = Demande.objects.get(pk=self.kwargs["demande_pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('demande_list')


class LigneDemandeUpdateView(LoginRequiredMixin, UpdateView):
    model = LigneDemande
    form_class = LigneDemandeForm
    template_name = "app/lignedemande_form.html"

    def get_success_url(self):
        return reverse_lazy('demande_list')


class LigneDemandeDeleteView(LoginRequiredMixin, DeleteView):
    model = LigneDemande
    template_name = "app/lignedemande_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('demande_list')


# ============================================================
# ARTICLE CRUD
# ============================================================

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "app/article_list.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        chantier = _get_user_chantier(self.request)
        if chantier:
            queryset = queryset.filter(stocks__emplacement=chantier).annotate(
                stock_chantier=Sum("stocks__quantite_disponible", filter=Q(stocks__emplacement=chantier))
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "app/article_form.html"
    success_url = reverse_lazy('article_list')


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "app/article_form.html"
    success_url = reverse_lazy('article_list')


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = "app/article_confirm_delete.html"
    success_url = reverse_lazy('article_list')


# ============================================================
# STOCK CRUD
# ============================================================

class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = "app/stock_list.html"
    context_object_name = "stocks"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Le responsable logistique voit tous les stocks (pas de filtre par chantier)
        # Les chefs de chantier ne voient que leur chantier
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        
        if role_code != "RL":  # Si ce n'est pas un responsable logistique
            chantier = _get_user_chantier(self.request)
            if chantier:
                queryset = queryset.filter(emplacement=chantier)
        return queryset.select_related("article", "emplacement")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personnel = getattr(self.request.user, "personnel", None)
        role_code = personnel.fonction.code if personnel and personnel.fonction else ""
        context["is_chef_chantier"] = role_code == "CHC"
        context["is_resp_logistique"] = role_code == "RL"
        return context


class StockCreateView(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = "app/stock_form.html"
    success_url = reverse_lazy('stock_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_update'] = False
        return kwargs


class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "app/stock_form.html"
    success_url = reverse_lazy('stock_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_update'] = True
        return kwargs


class StockDeleteView(LoginRequiredMixin, DeleteView):
    model = Stock
    template_name = "app/stock_confirm_delete.html"
    success_url = reverse_lazy('stock_list')


# ============================================================
# BON D'ENTREE CRUD
# ============================================================

class BonEntreeListView(LoginRequiredMixin, ListView):
    model = BonEntree
    template_name = "app/bonentree_list.html"
    context_object_name = "bons_entree"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related("emplacement").prefetch_related("lignes__article")


class BonEntreeCreateView(LoginRequiredMixin, CreateView):
    model = BonEntree
    form_class = BonEntreeForm
    template_name = "app/bonentree_form.html"
    success_url = reverse_lazy('bonentree_list')


class BonEntreeUpdateView(LoginRequiredMixin, UpdateView):
    model = BonEntree
    form_class = BonEntreeForm
    template_name = "app/bonentree_form.html"
    success_url = reverse_lazy('bonentree_list')


class BonEntreeDeleteView(LoginRequiredMixin, DeleteView):
    model = BonEntree
    template_name = "app/bonentree_confirm_delete.html"
    success_url = reverse_lazy('bonentree_list')


class BonEntreeDetailView(LoginRequiredMixin, DetailView):
    model = BonEntree
    template_name = "app/bonentree_detail.html"
    context_object_name = "bon_entree"


class LigneBonEntreeCreateView(LoginRequiredMixin, CreateView):
    model = LigneBonEntree
    form_class = LigneBonEntreeForm
    template_name = "app/lignebonentree_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bon_entree"] = BonEntree.objects.get(pk=self.kwargs["bonentree_pk"])
        return context

    def form_valid(self, form):
        bon_entree = BonEntree.objects.get(pk=self.kwargs["bonentree_pk"])
        form.instance.bon_entree = bon_entree
        response = super().form_valid(form)
        # Mettre à jour le stock
        article = form.instance.article
        emplacement = bon_entree.emplacement
        stock, created = Stock.objects.get_or_create(
            article=article,
            emplacement=emplacement,
            defaults={'quantite_disponible': 0}
        )
        stock.quantite_disponible += form.instance.quantite
        stock.save()
        
        # Logging de l'entrée de stock
        logger.info(f"Entrée stock: {article.nom} x{form.instance.quantite} - {bon_entree.reference}")
        
        return response

    def get_success_url(self):
        return reverse_lazy('bonentree_list')


class LigneBonEntreeUpdateView(LoginRequiredMixin, UpdateView):
    model = LigneBonEntree
    form_class = LigneBonEntreeForm
    template_name = "app/lignebonentree_form.html"

    def get_success_url(self):
        return reverse_lazy('bonentree_list')


class LigneBonEntreeDeleteView(LoginRequiredMixin, DeleteView):
    model = LigneBonEntree
    template_name = "app/lignebonentree_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('bonentree_list')


# ============================================================
# BON DE SORTIE CRUD
# ============================================================

class BonSortieListView(LoginRequiredMixin, ListView):
    model = BonSortie
    template_name = "app/bonsortie_list.html"
    context_object_name = "bons_sortie"
    paginate_by = 20

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("demande", "emplacement")
            .prefetch_related("lignes__article")
        )


class BonSortieCreateView(LoginRequiredMixin, CreateView):
    model = BonSortie
    form_class = BonSortieForm
    template_name = "app/bonsortie_form.html"
    success_url = reverse_lazy('bonsortie_list')

    def get_initial(self):
        initial = super().get_initial()
        demande_id = self.request.GET.get('demande')
        if demande_id:
            try:
                demande = Demande.objects.get(pk=demande_id)
                initial['demande'] = demande
                initial['date'] = timezone.now().date()
                # Pré-remplir le destinataire et l'emplacement avec les informations du demandeur
                if demande.demandeur:
                    initial['destinataire'] = demande.demandeur
                    # Pré-remplir l'emplacement avec le chantier du demandeur
                    if demande.demandeur.chantier:
                        initial['emplacement'] = demande.demandeur.chantier
            except Demande.DoesNotExist:
                pass
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['destinataire'].queryset = Personnel.objects.all()
        form.fields['emplacement'].queryset = Emplacement.objects.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demande_id = self.request.GET.get('demande')
        if demande_id:
            try:
                demande = Demande.objects.get(pk=demande_id)
                context['demande'] = demande
                # Générer le formset des lignes de bon de sortie pré-rempli avec la demande
                if 'lignes_formset' not in kwargs:
                    LigneBonSortieFormSet = inlineformset_factory(
                        BonSortie,
                        LigneBonSortie,
                        form=LigneBonSortieForm,
                        extra=0,
                        can_delete=False
                    )
                    initial_lignes = [
                        {'article': ligne.article.pk, 'quantite': ligne.quantite}
                        for ligne in demande.lignes.all()
                    ]
                    if self.request.POST:
                        context['lignes_formset'] = LigneBonSortieFormSet(
                            self.request.POST,
                            initial=initial_lignes
                        )
                    else:
                        context['lignes_formset'] = LigneBonSortieFormSet(
                            initial=initial_lignes
                        )
                # Passer l'emplacement (chantier du demandeur) au contexte
                if demande.demandeur and demande.demandeur.chantier:
                    context['emplacement'] = demande.demandeur.chantier
                # Passer les lignes de la demande pour l'affichage des détails
                context['lignes_demande'] = demande.lignes.all()
            except Demande.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        demande_id = self.request.GET.get('demande')
        demande = None
        if demande_id:
            try:
                demande = Demande.objects.get(pk=demande_id)
            except Demande.DoesNotExist:
                demande = None

        if demande:
            emplacement = form.instance.emplacement

            stock_insuffisant = []
            for ligne_demande in demande.lignes.all():
                article = ligne_demande.article
                quantite_requise = ligne_demande.quantite

                if emplacement:
                    stock = Stock.objects.filter(
                        article=article,
                        emplacement=emplacement
                    ).first()
                    quantite_disponible = stock.quantite_disponible if stock else 0
                else:
                    quantite_disponible = article.quantite_totale()

                if quantite_disponible < quantite_requise:
                    stock_insuffisant.append({
                        'article': article.nom,
                        'requis': quantite_requise,
                        'disponible': quantite_disponible,
                        'manque': quantite_requise - quantite_disponible,
                    })

            if stock_insuffisant:
                from django.contrib import messages
                messages.error(self.request, "Stock insuffisant pour les articles suivants :")
                for item in stock_insuffisant:
                    messages.error(
                        self.request,
                        f"• {item['article']}: requis {item['requis']}, disponible {item['disponible']}, manque {item['manque']}"
                    )
                return self.form_invalid(form)

        response = super().form_valid(form)

        lignes_formset = None
        if demande_id:
            try:
                demande = Demande.objects.get(pk=demande_id)
                LigneBonSortieFormSet = inlineformset_factory(
                    BonSortie,
                    LigneBonSortie,
                    form=LigneBonSortieForm,
                    extra=0,
                    can_delete=False,
                )
                initial_lignes = [
                    {'article': ligne.article.pk, 'quantite': ligne.quantite}
                    for ligne in demande.lignes.all()
                ]
                lignes_formset = LigneBonSortieFormSet(
                    self.request.POST,
                    instance=self.object,
                    initial=initial_lignes,
                )
            except Demande.DoesNotExist:
                pass

        if lignes_formset is not None:
            if lignes_formset.is_valid():
                lignes_formset.save()
            else:
                from django.contrib import messages
                messages.error(
                    self.request,
                    "Impossible d'enregistrer les articles du bon de sortie. Vérifiez les lignes saisies."
                )
                return self.form_invalid(form)

        if demande_id:
            try:
                demande = Demande.objects.get(pk=demande_id)
                demande.statut = "VALIDE"
                demande.save()
                logger.info(f"Demande {demande.reference} validée - Bon de sortie créé")
            except Demande.DoesNotExist:
                pass

        return response


class BonSortieUpdateView(LoginRequiredMixin, UpdateView):
    model = BonSortie
    form_class = BonSortieForm
    template_name = "app/bonsortie_form.html"
    success_url = reverse_lazy('bonsortie_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le formset des lignes de bon de sortie pour modification
        if 'lignes_formset' not in context:
            LigneBonSortieFormSet = inlineformset_factory(
                BonSortie,
                LigneBonSortie,
                form=LigneBonSortieForm,
                extra=0,
                can_delete=False
            )
            if self.request.POST:
                context['lignes_formset'] = LigneBonSortieFormSet(
                    self.request.POST,
                    instance=self.object
                )
            else:
                context['lignes_formset'] = LigneBonSortieFormSet(
                    instance=self.object
                )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        lignes_formset = context.get('lignes_formset')
        
        if lignes_formset and lignes_formset.is_valid():
            response = super().form_valid(form)
            lignes_formset.instance = self.object
            lignes_formset.save()
            return response
        else:
            return self.form_invalid(form)


class BonSortieDeleteView(LoginRequiredMixin, DeleteView):
    model = BonSortie
    template_name = "app/bonsortie_confirm_delete.html"
    success_url = reverse_lazy('bonsortie_list')


class BonSortieDetailView(LoginRequiredMixin, DetailView):
    model = BonSortie
    template_name = "app/bonsortie_detail.html"
    context_object_name = "bon_sortie"


class LigneBonSortieCreateView(LoginRequiredMixin, CreateView):
    model = LigneBonSortie
    form_class = LigneBonSortieForm
    template_name = "app/lignebonsortie_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bon_sortie"] = BonSortie.objects.get(pk=self.kwargs["bonsortie_pk"])
        return context

    def form_valid(self, form):
        bon_sortie = BonSortie.objects.get(pk=self.kwargs["bonsortie_pk"])
        form.instance.bon_sortie = bon_sortie
        response = super().form_valid(form)
        # La décrémentation du stock est maintenant gérée automatiquement par le modèle LigneBonSortie.save()
        
        # Logging de la sortie de stock
        logger.info(f"Sortie stock: {form.instance.article.nom} x{form.instance.quantite} - {bon_sortie.reference}")
        
        return response

    def get_success_url(self):
        return reverse_lazy('bonsortie_list')


class LigneBonSortieUpdateView(LoginRequiredMixin, UpdateView):
    model = LigneBonSortie
    form_class = LigneBonSortieForm
    template_name = "app/lignebonsortie_form.html"

    def get_success_url(self):
        return reverse_lazy('bonsortie_list')


class LigneBonSortieDeleteView(LoginRequiredMixin, DeleteView):
    model = LigneBonSortie
    template_name = "app/lignebonsortie_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('bonsortie_list')


# ============================================================
# DEVIS CRUD
# ============================================================

class DevisListView(LoginRequiredMixin, ListView):
    model = Devis
    template_name = "app/devis_list.html"
    context_object_name = "devis_list"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related("demande").prefetch_related("lignes__article")


class DevisCreateView(LoginRequiredMixin, CreateView):
    model = Devis
    form_class = DevisForm
    template_name = "app/devis_form.html"
    success_url = reverse_lazy('devis_list')


class DevisUpdateView(LoginRequiredMixin, UpdateView):
    model = Devis
    form_class = DevisForm
    template_name = "app/devis_form.html"
    success_url = reverse_lazy('devis_list')


class DevisDeleteView(LoginRequiredMixin, DeleteView):
    model = Devis
    template_name = "app/devis_confirm_delete.html"
    success_url = reverse_lazy('devis_list')


class DevisDetailView(LoginRequiredMixin, DetailView):
    model = Devis
    template_name = "app/devis_detail.html"
    context_object_name = "devis"


class LigneDevisCreateView(LoginRequiredMixin, CreateView):
    model = LigneDevis
    form_class = LigneDevisForm
    template_name = "app/lignedevis_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["devis"] = Devis.objects.get(pk=self.kwargs["devis_pk"])
        return context

    def form_valid(self, form):
        form.instance.devis = Devis.objects.get(pk=self.kwargs["devis_pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('devis_list')


class LigneDevisUpdateView(LoginRequiredMixin, UpdateView):
    model = LigneDevis
    form_class = LigneDevisForm
    template_name = "app/lignedevis_form.html"

    def get_success_url(self):
        return reverse_lazy('devis_list')


class LigneDevisDeleteView(LoginRequiredMixin, DeleteView):
    model = LigneDevis
    template_name = "app/lignedevis_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('devis_list')