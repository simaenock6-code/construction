# Guide : Comment le Chef de Chantier crée une demande

## Processus de création de demande étape par étape

### Étape 1 : Se connecter
- **URL** : http://127.0.0.1:8000/
- **Utilisateur** : `chef.chantier`
- **Mot de passe** : `demo`

### Étape 2 : Accéder au formulaire de demande
Depuis le dashboard, le chef de chantier peut :
1. Cliquer sur le bouton **"Nouvelle demande"** dans la barre du haut
2. Ou utiliser le menu latéral : **"Créer une demande"**

### Étape 3 : Remplir les informations de base
Le formulaire contient :

1. **Type de demande** (obligatoire)
   - Sélectionner le type dans la liste déroulante
   - Exemples : "Demande de matériaux", "Demande d'équipement"

2. **Demandeur** (pré-rempli automatiquement)
   - Nom du chef de chantier connecté
   - Non modifiable

3. **Date** (pré-remplie avec la date du jour)
   - Format : JJ/MM/AAAA
   - Modifiable si nécessaire

### Étape 4 : Ajouter des articles à la demande
Section **"Articles demandés"** :

1. **Sélectionner un article**
   - Liste déroulante avec tous les articles disponibles
   - Exemple : "Ciment (sac)", "Fer à béton (barre)"

2. **Entrer la quantité**
   - Nombre entier positif
   - Exemple : 10

3. **Ajouter un commentaire** (optionnel)
   - Précisions sur la demande
   - Exemple : "Pour fondation bâtiment A"

4. **Cliquer sur "Ajouter l'article"**
   - L'article apparaît dans la liste des articles ajoutés
   - Possibilité d'ajouter plusieurs articles

5. **Répéter pour chaque article**
   - Exemple complet :
     - Ciment × 10 (commentaire: "Pour fondation")
     - Fer à béton × 5 (commentaire: "Pour armature")
     - Sable × 3 (commentaire: "Pour béton")

6. **Supprimer un article** (si erreur)
   - Cliquer sur l'icône corbeille à côté de l'article

### Étape 5 : Soumettre la demande
1. Vérifier les articles ajoutés
2. Cliquer sur **"Créer la demande"**
3. Le système :
   - Crée la demande avec référence automatique (ex: REQ-20260803-1)
   - Enregistre tous les articles avec leurs quantités
   - Redirige vers la liste des demandes

### Étape 6 : Suivre la demande
Après création, le chef de chantier peut :
- Voir la demande dans la liste avec statut **"Nouveau"**
- Retourner au dashboard pour voir les statistiques
- Attendre la validation par le responsable logistique

## Workflow visuel

```
Dashboard Chef de Chantier
    ↓
Cliquer sur "Nouvelle demande"
    ↓
Remplir Type de demande
    ↓
Ajouter des articles (sélection + quantité + commentaire)
    ↓
Vérifier la liste des articles
    ↓
Cliquer sur "Créer la demande"
    ↓
✓ Demande créée avec référence
✓ Articles enregistrés
✓ Statut: NOUVEAU
```

## Exemple concret

**Chef de chantier Jean Kabila veut demander des matériaux :**

1. Se connecte avec `chef.chantier` / `demo`
2. Clique sur "Nouvelle demande"
3. Remplit :
   - Type : "Demande de matériaux"
   - Date : 03/08/2026
4. Ajoute les articles :
   - Article 1 : Ciment × 10 (commentaire: "Pour fondation")
   - Article 2 : Fer à béton × 5 (commentaire: "Pour armature")
   - Article 3 : Sable × 3 (commentaire: "Pour béton")
5. Clique sur "Créer la demande"
6. Résultat :
   - Demande créée : REQ-20260803-1
   - 3 articles enregistrés
   - Statut : NOUVEAU

## Que se passe-t-il après ?

### Côté Responsable Logistique
1. Reçoit la demande sur son dashboard
2. Vérifie la disponibilité du stock
3. Si stock OK : clique sur "Livrer"
4. Crée un bon de sortie
5. Le statut passe à **"VALIDÉ"**

### Côté Chef de Chantier
1. Voit le statut changer sur son dashboard
2. Peut suivre l'état en temps réel
3. Reçoit les matériaux du responsable logistique

## Points importants

### Vérification avant envoi
- **Articles** : Vérifier les noms et quantités
- **Commentaires** : Ajouter des précisions si nécessaire
- **Date** : Modifier si la demande n'est pas pour aujourd'hui

### Après création
- **Référence unique** : Noter la référence (ex: REQ-20260803-1)
- **Statut NOUVEAU** : En attente de traitement
- **Pas de modification** : Contacter le responsable logistique si erreur

### Bonnes pratiques
1. **Être précis** dans les quantités
2. **Ajouter des commentaires** pour les cas particuliers
3. **Vérifier le stock** avant de demander (voir section "Vérifier le stock")
4. **Grouper les demandes** si possible pour optimiser les livraisons

## Accès rapide depuis le dashboard

Le chef de chantier peut aussi :
- **Voir ses demandes** : section "Dernières demandes du chantier"
- **Vérifier le stock** : menu "Vérifier le stock"
- **Voir son équipe** : menu "Mon équipe"
- **Consulter les articles** : menu "Articles"

## Statuts des demandes

| Statut | Signification | Action |
|--------|---------------|--------|
| NOUVEAU | Demande créée, en attente | Attendre validation RL |
| EN_COURS | En traitement par RL | Attendre livraison |
| VALIDÉ | Livrée par RL | ✓ Réceptionner les matériaux |
| REFUSE | Demandé refusé | Contacter RL pour raison |

## Support

En cas de problème :
1. Vérifier que tous les champs sont remplis
2. Vérifier que les quantités sont positives
3. Contacter le responsable logistique
4. Contacter l'administrateur si problème technique