from django.conf import settings
from django.db import models
from django.utils import timezone

class Fonction(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code fonction")
    nom = models.CharField(max_length=100, verbose_name="Nom fonction")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Fonction"
        verbose_name_plural = "Fonctions"

    def __str__(self):
        return self.nom

class Personnel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personnel",
        verbose_name="Utilisateur",
    )
    fonction = models.ForeignKey(
        Fonction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personnels",
    )
    chantier = models.ForeignKey(
        'Emplacement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personnels",
        verbose_name="Chantier",
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    postnom = models.CharField(max_length=100, verbose_name="Postnom", blank=True)
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)
    sexe = models.CharField(
        max_length=10,
        choices=[("M", "Masculin"), ("F", "Féminin")],
        verbose_name="Sexe",
        blank=True,
    )
    datenaiss = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    lieunaiss = models.CharField(max_length=100, verbose_name="Lieu de naissance", blank=True)
    adresse = models.CharField(max_length=255, verbose_name="Adresse", blank=True)

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnels"

    def __str__(self):
        return " ".join(filter(None, [self.nom, self.postnom, self.prenom]))

class TypeDemande(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Type de demande")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Type de demande"
        verbose_name_plural = "Types de demande"

    def __str__(self):
        return self.nom

class Demande(models.Model):
    reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence",
    )
    type_demande = models.ForeignKey(
        TypeDemande,
        on_delete=models.PROTECT,
        related_name="demandes",
        verbose_name="Type de demande",
    )
    demandeur = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes",
        verbose_name="Demandeur",
    )
    date = models.DateField(verbose_name="Date de la demande")
    statut = models.CharField(
        max_length=50,
        verbose_name="Statut",
        choices=[
            ("NOUVEAU", "Nouveau"),
            ("EN_COURS", "En cours"),
            ("VALIDE", "Validé"),
            ("REFUSE", "Refusé"),
        ],
        default="NOUVEAU",
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = "REQ"
            date_code = self.date.strftime("%Y%m%d") if self.date else timezone.now().strftime("%Y%m%d")
            base = f"{prefix}-{date_code}"
            candidate = base
            suffix = 1
            while Demande.objects.filter(reference=candidate).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.reference = candidate
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Demande"
        verbose_name_plural = "Demandes"

    def __str__(self):
        return self.reference or f"Demande (non enregistrée, ID: {self.pk})"

class Article(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code article")
    nom = models.CharField(max_length=100, verbose_name="Nom article")
    description = models.TextField(blank=True, verbose_name="Description article")
    unite_mesure = models.CharField(max_length=50, verbose_name="Unité de mesure")
    seuil_minimum = models.PositiveIntegerField(
        default=10,
        verbose_name="Seuil minimum",
        help_text="Quantité minimale en stock. En dessous de ce seuil, l'article est considéré comme en stock faible.",
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.nom

    def quantite_totale(self):
        """Retourne la quantité totale disponible pour cet article sur tous les emplacements."""
        return sum(stock.quantite_disponible for stock in self.stocks.all())
    
    def quantite_par_emplacement(self, emplacement):
        """Retourne la quantité disponible pour cet article dans un emplacement spécifique."""
        stock = self.stocks.filter(emplacement=emplacement).first()
        return stock.quantite_disponible if stock else 0

    def est_suffisant(self, quantite_requise=None):
        """Indique si le stock est suffisant.

        - Si `quantite_requise` est fourni, compare la quantité totale à cette valeur.
        - Sinon utilise `seuil_minimum` de l'article.
        """
        if quantite_requise is None:
            quantite_requise = self.seuil_minimum
        return self.quantite_totale() >= quantite_requise

    def shortage(self, quantite_requise=None):
        """Renvoie la quantité manquante (0 si suffisant)."""
        if quantite_requise is None:
            quantite_requise = self.seuil_minimum
        manque = quantite_requise - self.quantite_totale()
        return max(0, manque)

    def etat_stock(self, quantite_requise=None):
        """Retourne un statut lisible du stock: 'suffisant' ou 'faible'."""
        return "suffisant" if self.est_suffisant(quantite_requise) else "faible"

class LigneDemande(models.Model):
    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Demande",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        related_name="lignes_demande",
        verbose_name="Article",
    )
    quantite = models.PositiveIntegerField(verbose_name="Quantité demandée")
    commentaire = models.CharField(max_length=255, blank=True, verbose_name="Commentaire")

    class Meta:
        verbose_name = "Ligne de demande"
        verbose_name_plural = "Lignes de demande"

    def __str__(self):
        demande_ref = self.demande.reference or "N/A"
        return f"{demande_ref} - {self.article.nom}"

class Emplacement(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code emplacement")
    location = models.CharField(max_length=200, verbose_name="Emplacement")

    class Meta:
        verbose_name = "Emplacement"
        verbose_name_plural = "Emplacements"

    def __str__(self):
        return self.location

class Stock(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name="Article",
    )
    quantite_disponible = models.PositiveIntegerField(default=0, verbose_name="Quantité disponible")
    emplacement = models.ForeignKey(
        Emplacement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stocks",
        verbose_name="Emplacement",
    )

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        constraints = [
            models.UniqueConstraint(fields=["article", "emplacement"], name="unique_stock_article_emplacement")
        ]

    def __str__(self):
        emplacement = self.emplacement.location if self.emplacement else "Sans emplacement"
        return f"{self.article.nom} - {emplacement} - {self.quantite_disponible}"

class BonEntree(models.Model):
    reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence",
    )
    date = models.DateField(verbose_name="Date du bon d'entrée")
    fournisseur = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bons_entree_fournisseur",
        verbose_name="Fournisseur"
    )
    emplacement = models.ForeignKey(
        Emplacement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bons_entree",
        verbose_name="Emplacement",
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = "BE"
            date_code = self.date.strftime("%Y%m%d") if self.date else timezone.now().strftime("%Y%m%d")
            base = f"{prefix}-{date_code}"
            candidate = base
            suffix = 1
            while BonEntree.objects.filter(reference=candidate).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.reference = candidate
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bon d'entrée"
        verbose_name_plural = "Bons d'entrée"
        ordering = ['-date']

    def __str__(self):
        return self.reference or f"Bon d'entrée (ID: {self.pk})"

class LigneBonEntree(models.Model):
    bon_entree = models.ForeignKey(
        BonEntree,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Bon d'entrée",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        related_name="lignes_bon_entree",
        verbose_name="Article",
    )
    quantite = models.PositiveIntegerField(verbose_name="Quantité entrée")
    prix_unitaire = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Prix unitaire",
    )

    class Meta:
        verbose_name = "Ligne de bon d'entrée"
        verbose_name_plural = "Lignes de bon d'entrée"

    def __str__(self):
        return f"{self.bon_entree.reference} - {self.article.nom}"

    def total_ligne(self):
        return self.quantite * self.prix_unitaire

class BonSortie(models.Model):
    reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence",
    )
    date = models.DateField(verbose_name="Date du bon de sortie")
    demande = models.ForeignKey(
        Demande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bons_sortie",
        verbose_name="Demande associée",
    )
    destinataire = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bons_sortie_destinataire",
        verbose_name="Destinataire"
    )
    emplacement = models.ForeignKey(
        Emplacement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bons_sortie",
        verbose_name="Emplacement",
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = "BS"
            date_code = self.date.strftime("%Y%m%d") if self.date else timezone.now().strftime("%Y%m%d")
            base = f"{prefix}-{date_code}"
            candidate = base
            suffix = 1
            while BonSortie.objects.filter(reference=candidate).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.reference = candidate
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bon de sortie"
        verbose_name_plural = "Bons de sortie"
        ordering = ['-date']

    def __str__(self):
        return self.reference or f"Bon de sortie (ID: {self.pk})"

class LigneBonSortie(models.Model):
    bon_sortie = models.ForeignKey(
        BonSortie,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Bon de sortie",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        related_name="lignes_bon_sortie",
        verbose_name="Article",
    )
    quantite = models.PositiveIntegerField(verbose_name="Quantité sortie")

    class Meta:
        verbose_name = "Ligne de bon de sortie"
        verbose_name_plural = "Lignes de bon de sortie"

    def __str__(self):
        return f"{self.bon_sortie.reference} - {self.article.nom}"

    def save(self, *args, **kwargs):
        # Vérifier si c'est une nouvelle instance (création)
        is_new = self.pk is None
        ancienne_quantite = 0
        
        # Si c'est une mise à jour, récupérer l'ancienne quantité pour ajuster le stock
        if not is_new:
            try:
                ancienne_ligne = LigneBonSortie.objects.get(pk=self.pk)
                ancienne_quantite = ancienne_ligne.quantite
            except LigneBonSortie.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Ajuster le stock
        if self.bon_sortie.emplacement:
            stock, created = Stock.objects.get_or_create(
                article=self.article,
                emplacement=self.bon_sortie.emplacement,
                defaults={'quantite_disponible': 0}
            )
            
            if is_new:
                # Nouvelle ligne : décrémenter
                stock.quantite_disponible = max(0, stock.quantite_disponible - self.quantite)
            else:
                # Mise à jour : ajuster la différence
                difference = self.quantite - ancienne_quantite
                if difference > 0:
                    # Quantité augmentée : décrémenter davantage
                    stock.quantite_disponible = max(0, stock.quantite_disponible - difference)
                elif difference < 0:
                    # Quantité diminuée : augmenter le stock (remettre la différence)
                    stock.quantite_disponible += abs(difference)
            
            stock.save()

    def delete(self, *args, **kwargs):
        # Avant de supprimer, remettre la quantité en stock
        if self.bon_sortie.emplacement:
            stock = Stock.objects.filter(
                article=self.article,
                emplacement=self.bon_sortie.emplacement
            ).first()
            if stock:
                stock.quantite_disponible += self.quantite
                stock.save()
        
        super().delete(*args, **kwargs)

class Devis(models.Model):
    reference = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence",
    )
    date = models.DateField(verbose_name="Date du devis")
    client = models.CharField(max_length=200, verbose_name="Client")
    demande = models.ForeignKey(
        Demande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devis",
        verbose_name="Demande associée",
    )
    validite_jours = models.PositiveIntegerField(default=30, verbose_name="Validité (jours)")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = "DEV"
            date_code = self.date.strftime("%Y%m%d") if self.date else timezone.now().strftime("%Y%m%d")
            base = f"{prefix}-{date_code}"
            candidate = base
            suffix = 1
            while Devis.objects.filter(reference=candidate).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.reference = candidate
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        ordering = ['-date']

    def __str__(self):
        return self.reference or f"Devis (ID: {self.pk})"

    def total_devis(self):
        return sum(ligne.total_ligne() for ligne in self.lignes.all())

class LigneDevis(models.Model):
    devis = models.ForeignKey(
        Devis,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Devis",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        related_name="lignes_devis",
        verbose_name="Article",
    )
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_unitaire = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Prix unitaire",
    )

    class Meta:
        verbose_name = "Ligne de devis"
        verbose_name_plural = "Lignes de devis"

    def __str__(self):
        return f"{self.devis.reference} - {self.article.nom}"

    def total_ligne(self):
        return self.quantite * self.prix_unitaire
