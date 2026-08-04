import os

base_dir = 'app/templates/app'

# ===== BON DE SORTIE TEMPLATES =====
templates = {}

templates['bonsortie_list.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Bons de sortie</h2>
    <div>
        <a href="{% url 'bonsortie_create' %}" class="btn btn-primary btn-sm">Nouveau bon de sortie</a>
        <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary btn-sm ms-2">Retour au dashboard</a>
    </div>
</div>

<div class="row g-3">
    {% for b in bons_sortie %}
    <div class="col-12 col-md-6 col-xl-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <strong class="small">{{ b.reference }}</strong>
                <span class="badge bg-light text-primary">{{ b.date|date:"d/m/Y" }}</span>
            </div>
            <div class="card-body">
                <h5 class="card-title mb-1">
                    <span class="badge bg-primary bg-opacity-10 text-primary px-3 py-2 fs-6">
                        <i class="bi bi-box-arrow-up"></i> Sortie de stock
                    </span>
                </h5>
                <div class="small text-muted mb-2">
                    {% if b.demande %}📋 {{ b.demande.reference|default:b.demande.id }}{% else %}📋 <em>Aucune demande liée</em>{% endif %}
                </div>
                <div class="small text-muted mb-2">
                    {% if b.destinataire %}👤 {{ b.destinataire }}{% else %}👤 <em>Destinataire non renseigné</em>{% endif %}
                </div>
                <div class="small text-muted mb-2">
                    📍 {{ b.emplacement.location|default:"Sans emplacement" }}
                </div>
                <div class="mb-2">
                    <div class="small text-uppercase text-muted fw-bold mb-1">Articles</div>
                    <div>
                        {% for ligne in b.lignes.all %}
                            <span class="badge bg-light text-dark border mb-1">
                                {{ ligne.article.nom }} ×{{ ligne.quantite }}
                            </span>
                        {% empty %}
                            <span class="small text-muted">—</span>
                        {% endfor %}
                    </div>
                </div>
                {% if b.commentaire %}
                <p class="small text-muted mb-2">{{ b.commentaire|truncatechars:100 }}</p>
                {% endif %}
            </div>
            <div class="card-footer d-flex gap-2">
                <a href="{% url 'bonsortie_detail' b.pk %}" class="btn btn-sm btn-outline-secondary">Voir</a>
                <a href="{% url 'lignebonsortie_create' b.pk %}" class="btn btn-sm btn-outline-primary">+ Article</a>
                <a href="{% url 'bonsortie_update' b.pk %}" class="btn btn-sm btn-outline-primary">Modifier</a>
                <a href="{% url 'bonsortie_delete' b.pk %}" class="btn btn-sm btn-outline-danger">Supprimer</a>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body text-center small text-muted py-5">
                <div class="mb-2" style="font-size:2.5rem;">📤</div>
                Aucun bon de sortie
            </div>
        </div>
    </div>
    {% endfor %}
</div>

{% if is_paginated %}
<nav class="mt-3">
  <ul class="pagination">
    {% if page_obj.has_previous %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">Préc</a></li>
    {% endif %}
    <li class="page-item active"><span class="page-link">{{ page_obj.number }}</span></li>
    {% if page_obj.has_next %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">Suiv</a></li>
    {% endif %}
  </ul>
</nav>
{% endif %}

{% endblock %}
'''

templates['bonsortie_form.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title">{% if view.object %}Modifier{% else %}Nouveau{% endif %} bon de sortie</h5>
        <form method="post">
            {% csrf_token %}
            {{ form.non_field_errors }}
            <div class="row">
                <div class="col-md-6 mb-3">{{ form.date.label_tag }}{{ form.date }}{{ form.date.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.demande.label_tag }}{{ form.demande }}{{ form.demande.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.destinataire.label_tag }}{{ form.destinataire }}{{ form.destinataire.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.emplacement.label_tag }}{{ form.emplacement }}{{ form.emplacement.errors }}</div>
                <div class="col-12 mb-3">{{ form.commentaire.label_tag }}{{ form.commentaire }}{{ form.commentaire.errors }}</div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary">Enregistrer</button>
                <a href="{% url 'bonsortie_list' %}" class="btn btn-secondary">Annuler</a>
                <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

templates['bonsortie_confirm_delete.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
  <div class="card-body">
    <h5 class="card-title">Supprimer le bon de sortie</h5>
    <p>Voulez-vous vraiment supprimer <strong>{{ object }}</strong> ?</p>
    <form method="post">{% csrf_token %}
      <button class="btn btn-danger">Supprimer</button>
      <a href="{% url 'bonsortie_list' %}" class="btn btn-secondary">Annuler</a>
      <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
    </form>
  </div>
</div>
{% endblock %}
'''

templates['bonsortie_detail.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Bon de sortie {{ bon_sortie.reference }}</h2>
    <div>
        <a href="{% url 'lignebonsortie_create' bon_sortie.pk %}" class="btn btn-primary btn-sm">+ Ajouter un article</a>
        <a href="{% url 'bonsortie_update' bon_sortie.pk %}" class="btn btn-outline-primary btn-sm">Modifier</a>
        <a href="{% url 'bonsortie_list' %}" class="btn btn-outline-secondary btn-sm ms-2">Retour</a>
    </div>
</div>

<div class="card shadow-sm mb-3">
    <div class="card-body">
        <div class="row">
            <div class="col-md-4"><strong>Référence :</strong> {{ bon_sortie.reference }}</div>
            <div class="col-md-4"><strong>Date :</strong> {{ bon_sortie.date|date:"d/m/Y" }}</div>
            <div class="col-md-4"><strong>Demande :</strong> {{ bon_sortie.demande.reference|default:"—" }}</div>
            <div class="col-md-4 mt-2"><strong>Destinataire :</strong> {{ bon_sortie.destinataire|default:"—" }}</div>
            <div class="col-md-4 mt-2"><strong>Emplacement :</strong> {{ bon_sortie.emplacement.location|default:"—" }}</div>
            <div class="col-md-4 mt-2"><strong>Commentaire :</strong> {{ bon_sortie.commentaire|default:"—" }}</div>
        </div>
    </div>
</div>

<div class="card shadow-sm">
    <div class="card-header bg-white">Articles du bon de sortie</div>
    <div class="card-body p-0">
        <table class="table table-striped mb-0">
            <thead>
                <tr>
                    <th>Article</th>
                    <th>Quantité</th>
                    <th>Unité</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for ligne in bon_sortie.lignes.all %}
                <tr>
                    <td>{{ ligne.article.nom }}</td>
                    <td>{{ ligne.quantite }}</td>
                    <td>{{ ligne.article.unite_mesure }}</td>
                    <td>
                        <a href="{% url 'lignebonsortie_update' ligne.pk %}" class="btn btn-sm btn-outline-primary">✏️</a>
                        <a href="{% url 'lignebonsortie_delete' ligne.pk %}" class="btn btn-sm btn-outline-danger">🗑️</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="4" class="text-center small text-muted py-3">Aucun article</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''

templates['lignebonsortie_form.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title">
            {% if view.object %}Modifier{% else %}Nouvelle{% endif %} ligne de bon de sortie
            {% if bon_sortie %} — {{ bon_sortie.reference }}{% endif %}
        </h5>
        <form method="post">
            {% csrf_token %}
            {{ form.non_field_errors }}
            <div class="row">
                <div class="col-md-6 mb-3">{{ form.article.label_tag }}{{ form.article }}{{ form.article.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.quantite.label_tag }}{{ form.quantite }}{{ form.quantite.errors }}</div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary">Enregistrer</button>
                <a href="{% url 'bonsortie_list' %}" class="btn btn-secondary">Annuler</a>
                <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

templates['lignebonsortie_confirm_delete.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
  <div class="card-body">
    <h5 class="card-title">Supprimer la ligne</h5>
    <p>Voulez-vous vraiment supprimer <strong>{{ object }}</strong> ?</p>
    <form method="post">{% csrf_token %}
      <button class="btn btn-danger">Supprimer</button>
      <a href="{% url 'bonsortie_list' %}" class="btn btn-secondary">Annuler</a>
      <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
    </form>
  </div>
</div>
{% endblock %}
'''

# ===== DEVIS TEMPLATES =====
templates['devis_list.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Devis</h2>
    <div>
        <a href="{% url 'devis_create' %}" class="btn btn-primary btn-sm">Nouveau devis</a>
        <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary btn-sm ms-2">Retour au dashboard</a>
    </div>
</div>

<div class="row g-3">
    {% for d in devis_list %}
    <div class="col-12 col-md-6 col-xl-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                <strong class="small">{{ d.reference }}</strong>
                <span class="badge bg-light text-dark">{{ d.date|date:"d/m/Y" }}</span>
            </div>
            <div class="card-body">
                <h5 class="card-title mb-1">
                    <span class="badge bg-warning bg-opacity-10 text-warning px-3 py-2 fs-6">
                        <i class="bi bi-file-earmark-text"></i> Devis
                    </span>
                </h5>
                <div class="small text-muted mb-2">
                    👤 {{ d.client }}
                </div>
                <div class="small text-muted mb-2">
                    {% if d.demande %}📋 {{ d.demande.reference|default:d.demande.id }}{% else %}📋 <em>Aucune demande liée</em>{% endif %}
                </div>
                <div class="small text-muted mb-2">
                    ⏳ Validité : {{ d.validite_jours }} jours
                </div>
                <div class="mb-2">
                    <div class="small text-uppercase text-muted fw-bold mb-1">Articles</div>
                    <div>
                        {% for ligne in d.lignes.all %}
                            <span class="badge bg-light text-dark border mb-1">
                                {{ ligne.article.nom }} ×{{ ligne.quantite }}
                                {% if ligne.prix_unitaire %} · {{ ligne.prix_unitaire }} FCFA{% endif %}
                            </span>
                        {% empty %}
                            <span class="small text-muted">—</span>
                        {% endfor %}
                    </div>
                </div>
                {% if d.lignes.all %}
                <div class="text-end mt-2">
                    <strong>Total : {{ d.total_devis }} FCFA</strong>
                </div>
                {% endif %}
                {% if d.commentaire %}
                <p class="small text-muted mb-2">{{ d.commentaire|truncatechars:100 }}</p>
                {% endif %}
            </div>
            <div class="card-footer d-flex gap-2">
                <a href="{% url 'devis_detail' d.pk %}" class="btn btn-sm btn-outline-secondary">Voir</a>
                <a href="{% url 'lignedevis_create' d.pk %}" class="btn btn-sm btn-outline-warning">+ Article</a>
                <a href="{% url 'devis_update' d.pk %}" class="btn btn-sm btn-outline-primary">Modifier</a>
                <a href="{% url 'devis_delete' d.pk %}" class="btn btn-sm btn-outline-danger">Supprimer</a>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-body text-center small text-muted py-5">
                <div class="mb-2" style="font-size:2.5rem;">📄</div>
                Aucun devis
            </div>
        </div>
    </div>
    {% endfor %}
</div>

{% if is_paginated %}
<nav class="mt-3">
  <ul class="pagination">
    {% if page_obj.has_previous %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">Préc</a></li>
    {% endif %}
    <li class="page-item active"><span class="page-link">{{ page_obj.number }}</span></li>
    {% if page_obj.has_next %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">Suiv</a></li>
    {% endif %}
  </ul>
</nav>
{% endif %}

{% endblock %}
'''

templates['devis_form.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title">{% if view.object %}Modifier{% else %}Nouveau{% endif %} devis</h5>
        <form method="post">
            {% csrf_token %}
            {{ form.non_field_errors }}
            <div class="row">
                <div class="col-md-6 mb-3">{{ form.date.label_tag }}{{ form.date }}{{ form.date.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.client.label_tag }}{{ form.client }}{{ form.client.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.demande.label_tag }}{{ form.demande }}{{ form.demande.errors }}</div>
                <div class="col-md-6 mb-3">{{ form.validite_jours.label_tag }}{{ form.validite_jours }}{{ form.validite_jours.errors }}</div>
                <div class="col-12 mb-3">{{ form.commentaire.label_tag }}{{ form.commentaire }}{{ form.commentaire.errors }}</div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary">Enregistrer</button>
                <a href="{% url 'devis_list' %}" class="btn btn-secondary">Annuler</a>
                <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

templates['devis_confirm_delete.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
  <div class="card-body">
    <h5 class="card-title">Supprimer le devis</h5>
    <p>Voulez-vous vraiment supprimer <strong>{{ object }}</strong> ?</p>
    <form method="post">{% csrf_token %}
      <button class="btn btn-danger">Supprimer</button>
      <a href="{% url 'devis_list' %}" class="btn btn-secondary">Annuler</a>
      <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
    </form>
  </div>
</div>
{% endblock %}
'''

templates['devis_detail.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Devis {{ devis.reference }}</h2>
    <div>
        <a href="{% url 'lignedevis_create' devis.pk %}" class="btn btn-warning btn-sm">+ Ajouter un article</a>
        <a href="{% url 'devis_update' devis.pk %}" class="btn btn-outline-primary btn-sm">Modifier</a>
        <a href="{% url 'devis_list' %}" class="btn btn-outline-secondary btn-sm ms-2">Retour</a>
    </div>
</div>

<div class="card shadow-sm mb-3">
    <div class="card-body">
        <div class="row">
            <div class="col-md-4"><strong>Référence :</strong> {{ devis.reference }}</div>
            <div class="col-md-4"><strong>Date :</strong> {{ devis.date|date:"d/m/Y" }}</div>
            <div class="col-md-4"><strong>Client :</strong> {{ devis.client }}</div>
            <div class="col-md-4 mt-2"><strong>Demande :</strong> {{ devis.demande.reference|default:"—" }}</div>
            <div class="col-md-4 mt-2"><strong>Validité :</strong> {{ devis.validite_jours }} jours</div>
            <div class="col-md-4 mt-2"><strong>Total :</strong> {{ devis.total_devis }} FCFA</div>
            <div class="col-12 mt-2"><strong>Commentaire :</strong> {{ devis.commentaire|default:"—" }}</div>
        </div>
    </div>
</div>

<div class="card shadow-sm">
    <div class="card-header bg-white">Articles du devis</div>
    <div class="card-body p-0">
        <table class="table table-striped mb-0">
            <thead>
                <tr>
                    <th>Article</th>
                    <th>Quantité</th>
                    <th>Prix unitaire</th>
                    <th>Total</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for ligne in devis.lignes.all %}
                <tr>
                    <td>{{ ligne.article.nom }}</td>
                    <td>{{ ligne.quantite }} {{ ligne.article.unite_mesure }}</td>
                    <td>{{ ligne.prix_unitaire }} FCFA</td>
                    <td>{{ ligne.total_ligne }} FCFA</td>
                    <td>
                        <a href="{% url 'lignedevis_update' ligne.pk %}" class="btn btn-sm btn-outline-primary">✏️</a>
                        <a href="{% url 'lignedevis_delete' ligne.pk %}" class="btn btn-sm btn-outline-danger">🗑️</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="text-center small text-muted py-3">Aucun article</td></tr>
                {% endfor %}
            </tbody>
            {% if devis.lignes.all %}
            <tfoot>
                <tr>
                    <td colspan="3" class="text-end fw-bold">Total général :</td>
                    <td class="fw-bold">{{ devis.total_devis }} FCFA</td>
                    <td></td>
                </tr>
            </tfoot>
            {% endif %}
        </table>
    </div>
</div>
{% endblock %}
'''

templates['lignedevis_form.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title">
            {% if view.object %}Modifier{% else %}Nouvelle{% endif %} ligne de devis
            {% if devis %} — {{ devis.reference }}{% endif %}
        </h5>
        <form method="post">
            {% csrf_token %}
            {{ form.non_field_errors }}
            <div class="row">
                <div class="col-md-6 mb-3">{{ form.article.label_tag }}{{ form.article }}{{ form.article.errors }}</div>
                <div class="col-md-3 mb-3">{{ form.quantite.label_tag }}{{ form.quantite }}{{ form.quantite.errors }}</div>
                <div class="col-md-3 mb-3">{{ form.prix_unitaire.label_tag }}{{ form.prix_unitaire }}{{ form.prix_unitaire.errors }}</div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary">Enregistrer</button>
                <a href="{% url 'devis_list' %}" class="btn btn-secondary">Annuler</a>
                <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''

templates['lignedevis_confirm_delete.html'] = '''{% extends "app/dashboard.html" %}

{% block content %}
<div class="card">
  <div class="card-body">
    <h5 class="card-title">Supprimer la ligne</h5>
    <p>Voulez-vous vraiment supprimer <strong>{{ object }}</strong> ?</p>
    <form method="post">{% csrf_token %}
      <button class="btn btn-danger">Supprimer</button>
      <a href="{% url 'devis_list' %}" class="btn btn-secondary">Annuler</a>
      <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary ms-2">Retour au dashboard</a>
    </form>
  </div>
</div>
{% endblock %}
'''

for filename, content in templates.items():
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Créé: {filepath}")

print("\nTerminé!")