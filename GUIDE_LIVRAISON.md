# Guide : Comment le Responsable Logistique livre une demande

## Processus de livraison étape par étape

### Étape 1 : Se connecter
- **URL** : http://127.0.0.1:8000/
- **Utilisateur** : `resp.logistique`
- **Mot de passe** : `demo`

### Étape 2 : Consulter les demandes reçues
Sur le dashboard, le responsable logistique voit :
- La section **"Demandes reçues — Vérification du stock"**
- Un tableau avec toutes les demandes
- Pour chaque demande :
  - Les articles demandés
  - La disponibilité du stock (badge vert "Stock OK" ou rouge "Stock insuffisant")
  - Le statut de la demande

### Étape 3 : Vérifier le stock
Le dashboard affiche automatiquement pour chaque demande :

**Si tout le stock est disponible :**
- ✅ **Stock OK** (badge vert) : Le stock est suffisant pour tous les articles
- Bouton **"Livrer"** disponible

**Si au moins un article manque :**
- ❌ **Stock insuffisant** (badge rouge) : Au moins un article manque
- Articles en rouge avec icône d'avertissement
- Bouton **"Livrer"** masqué (pas de livraison possible)

### Étape 4 : Livrer la demande
Pour chaque demande avec stock suffisant, un bouton **"Livrer"** apparaît :

1. **Cliquer sur le bouton "Livrer"**
   - Ouvre le formulaire de bon de sortie
   - Pré-rempli automatiquement avec :
     - La demande sélectionnée
     - La date du jour
     - Le tableau des articles à livrer

2. **Remplir les informations du bon de sortie** :
   - **Date** : pré-remplie avec la date du jour
   - **Demande** : pré-remplie avec la demande source
   - **Destinataire** : nom du destinataire (ex: "Chef de chantier Jean Kabila")
   - **Emplacement** : lieu de stockage
   - **Commentaire** : observations optionnelles

3. **Vérifier les articles à livrer** :
   - Tableau récapitulatif avec :
     - Article
     - Quantité demandée
     - Stock disponible
     - Statut (Disponible/Insuffisant)

4. **Enregistrer le bon de sortie**
   - Cliquer sur **"Enregistrer le bon de sortie"**
   - Le système :
     - Crée le bon de sortie
     - **Décrémente automatiquement le stock** pour chaque article
     - **Change le statut de la demande** : NOUVEAU → VALIDÉ

### Étape 5 : Confirmation
- Redirection vers la liste des bons de sortie
- La demande apparaît maintenant avec le statut **"Validé"** sur le dashboard
- Le stock est automatiquement mis à jour

## Workflow visuel

```
Dashboard RL
    ↓
Voir les demandes reçues
    ↓
Vérifier stock (vert/rouge)
    ↓
Cliquer sur "Livrer"
    ↓
Formulaire bon de sortie (pré-rempli)
    ↓
Remplir destinataire + commentaire
    ↓
Enregistrer
    ↓
✓ Stock décrémenté
✓ Demande marquée "Validé"
```

## Points importants

### Vérification automatique du stock
- Le système vérifie **tous les articles** de la demande
- Si **un seul article** est insuffisant, tout est rouge
- Le bouton "Livrer" n'apparaît que si **tout le stock est disponible**

### Mise à jour automatique
- **Stock** : Décrémenté automatiquement
- **Demande** : Statut passe à "VALIDÉ"
- **Traçabilité** : Le bon de sortie est lié à la demande

### Cas particuliers
- **Stock insuffisant** : Le responsable logistique ne peut pas livrer
  - Il doit d'abord créer un bon d'entrée pour réapprovisionner
  - Ou contacter l'administrateur

- **Demande déjà livrée** : Le bouton n'apparaît plus (statut = VALIDÉ)

## Accès rapide depuis le dashboard

Le responsable logistique peut aussi :
- **Créer un bon d'entrée** : pour ajouter du stock
- **Vérifier le stock** : voir tous les stocks disponibles
- **Voir les bons de sortie** : historique des livraisons
- **Générer un devis** : pour les clients externes

## Exemple concret

**Demande de Jean Kabila (Chef de chantier) :**
- 10 sacs de ciment
- 5 barres de fer

**Responsable logistique :**
1. Voit la demande sur le dashboard
2. Vérifie : Stock OK (badge vert)
3. Clique sur "Livrer"
4. Remplit :
   - Destinataire : "Jean Kabila - Chantier Principal"
   - Commentaire : "Livraison pour fondation"
5. Enregistre
6. Résultat :
   - Bon de sortie créé
   - Stock : Ciment -10, Fer -5
   - Demande : Statut = VALIDÉ