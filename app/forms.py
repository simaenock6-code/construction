from django import forms
from .models import (
    Article, BonEntree, BonSortie, Demande, Devis, Emplacement,
    Fonction, LigneBonEntree, LigneBonSortie, LigneDemande,
    LigneDevis, Personnel, Stock, TypeDemande,
)


class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = [
            'fonction', 'nom', 'postnom', 'prenom', 'telephone',
            'sexe', 'datenaiss', 'lieunaiss', 'adresse'
        ]
        widgets = {
            'datenaiss': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('datenaiss',):
                field.widget.attrs.setdefault('class', 'form-control')


class DemandeForm(forms.ModelForm):
    class Meta:
        model = Demande
        fields = ['type_demande', 'demandeur', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, chantier=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        if chantier:
            self.fields['demandeur'].queryset = Personnel.objects.filter(
                chantier=chantier
            ).select_related("user", "fonction")


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['code', 'nom', 'description', 'unite_mesure', 'seuil_minimum']
        widgets = {
            'seuil_minimum': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['article', 'emplacement', 'quantite_disponible']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-control'}),
            'emplacement': forms.Select(attrs={'class': 'form-control'}),
            'quantite_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        if self.is_update:
            self.fields['article'].disabled = True
            self.fields['emplacement'].disabled = True


class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['code', 'nom', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class TypeDemandeForm(forms.ModelForm):
    class Meta:
        model = TypeDemande
        fields = ['nom', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class EmplacementForm(forms.ModelForm):
    class Meta:
        model = Emplacement
        fields = ['code', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class LigneDemandeForm(forms.ModelForm):
    class Meta:
        model = LigneDemande
        fields = ['article', 'quantite', 'commentaire']
        widgets = {
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'commentaire': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class BonEntreeForm(forms.ModelForm):
    class Meta:
        model = BonEntree
        fields = ['date', 'fournisseur', 'emplacement', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'emplacement': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].queryset = Personnel.objects.all()
        self.fields['fournisseur'].widget = forms.Select(attrs={'class': 'form-control'})
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-control')


class LigneBonEntreeForm(forms.ModelForm):
    class Meta:
        model = LigneBonEntree
        fields = ['article', 'quantite', 'prix_unitaire']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class BonSortieForm(forms.ModelForm):
    class Meta:
        model = BonSortie
        fields = ['date', 'demande', 'destinataire', 'emplacement_provenance', 'emplacement', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'demande': forms.Select(attrs={'class': 'form-control'}),
            'emplacement_provenance': forms.Select(attrs={'class': 'form-control'}),
            'emplacement': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destinataire'].queryset = Personnel.objects.all()
        self.fields['destinataire'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['emplacement_provenance'].queryset = Emplacement.objects.all()
        self.fields['emplacement'].queryset = Emplacement.objects.all()
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-control')


class LigneBonSortieForm(forms.ModelForm):
    class Meta:
        model = LigneBonSortie
        fields = ['article', 'quantite']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['date', 'client', 'demande', 'validite_jours', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'client': forms.TextInput(attrs={'class': 'form-control'}),
            'demande': forms.Select(attrs={'class': 'form-control'}),
            'validite_jours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class LigneDevisForm(forms.ModelForm):
    class Meta:
        model = LigneDevis
        fields = ['article', 'quantite', 'prix_unitaire']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
