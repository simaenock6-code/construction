from django.contrib import admin
from .models import (
    Article,
    Demande,
    Emplacement,
    Fonction,
    LigneDemande,
    Personnel,
    Stock,
    TypeDemande,
)

@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "description")
    search_fields = ("code", "nom")

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ("user", "nom", "postnom", "prenom", "fonction", "telephone")
    search_fields = ("user__username", "nom", "postnom", "prenom")
    raw_id_fields = ("user", "fonction")

@admin.register(TypeDemande)
class TypeDemandeAdmin(admin.ModelAdmin):
    list_display = ("nom", "description")
    search_fields = ("nom",)

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ("type_demande", "demandeur", "date", "statut")
    list_filter = ("statut", "type_demande")
    search_fields = ("demandeur__nom", "demandeur__prenom")
    raw_id_fields = ("demandeur", "type_demande")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "unite_mesure")
    search_fields = ("code", "nom")

@admin.register(LigneDemande)
class LigneDemandeAdmin(admin.ModelAdmin):
    list_display = ("demande", "article", "quantite")
    raw_id_fields = ("demande", "article")

@admin.register(Emplacement)
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ("code", "location")
    search_fields = ("code", "location")

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("article", "quantite_disponible", "emplacement")
    raw_id_fields = ("article", "emplacement")
