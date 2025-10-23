# Navigation des échantillons - Nouvelles fonctionnalités

## 🎯 Interface de navigation

### Barre de navigation au-dessus du graphique
- **5 boutons numérotés** (1 à 5) représentant chaque échantillon
- **États visuels** :
  - 🔴 : Pas encore fait
  - 🔄 : En cours (échantillon actuel)
  - ✅ : Terminé (données sauvegardées)

### Interactions
- **Clic gauche** : Met en avant l'échantillon sélectionné
- **Clic droit** : Menu contextuel avec options
  - 👁️ Voir cet échantillon (même action que clic gauche)
  - 🗑️ Supprimer et refaire

## 🔄 Auto-remplacement intelligent

### Détection de nouvelle mesure
Quand une nouvelle mesure est détectée sur un échantillon déjà fait :
- ⚠️ **Alerte** : "Remplacement de l'échantillon X par une nouvelle mesure"
- 🗑️ **Suppression automatique** de l'ancienne mesure
- 🔄 **Démarrage automatique** de la nouvelle mesure
- 🔄 **Reconstruction** de l'affichage sans l'ancienne mesure

### Avantages
- Plus besoin de supprimer manuellement
- Workflow fluide pour corriger une mesure
- Impossible d'avoir des doublons

## 👁️ Mise en avant vs isolation

### Avant (isolement)
- Clic sur bouton → affichage SEUL de cet échantillon
- Autres mesures complètement cachées
- Vue "tunnel" peu pratique pour la comparaison

### Après (mise en avant)
- Clic sur bouton → **mise en avant** de cet échantillon
- Autres mesures restent visibles mais **très transparentes**
- Échantillon sélectionné affiché normalement
- **Meilleure comparaison visuelle**

## 🎨 Retour visuel

### Bouton sélectionné
- **Surbrillance bleue** autour du bouton
- **Légère augmentation** de taille (scale 1.05)
- **Ombre bleue** pour indiquer la sélection

### Graphique
- **Titre dynamique** : "Échantillon X mis en avant"
- **Bouton retour** : "↩️ Vue globale" (dans le titre)
- **Statistiques** : Affichage des stats de l'échantillon sélectionné

## 🔧 Gestion des données

### Structure des données
```javascript
sampleData = {
  1: [...], // Données échantillon 1
  2: [...], // Données échantillon 2
  // etc.
}
```

### Logique d'affichage
```javascript
// Mode normal
Dataset 0: Tous échantillons terminés (transparent)
Dataset 1: Mesure en cours

// Mode "mise en avant"
Dataset 0: Autres échantillons (très transparent)
Dataset 1: Échantillon sélectionné + mesure en cours
```

### Reconstruction intelligente
- `rebuildPreviousMeasurements()` : Reconstruit l'affichage après suppression
- `updateSampleVisualization()` : Gère l'affichage selon le mode
- `updateSampleButtonsHighlight()` : Gère la surbrillance des boutons

## 🗑️ Suppression d'échantillon

### Comportement intelligent
1. **Suppression** des données de l'échantillon
2. **Reconstruction** de l'affichage
3. **Repositionnement** du curseur si nécessaire :
   - Si échantillon supprimé ≤ échantillon courant → curseur sur l'échantillon supprimé
   - **Relance automatique** de l'écoute
4. **Vue globale** si on était en train de voir l'échantillon supprimé

### Exemple de workflow
```
État : Échantillons 1,2,3 terminés, on est sur le 4
Action : Supprimer échantillon 2
Résultat : Curseur sur échantillon 2, écoute active
→ Prêt à refaire l'échantillon 2
```

## 🏃‍♂️ Workflow utilisateur simplifié

### Correction d'un échantillon
1. **Clic droit** sur le bouton de l'échantillon à corriger
2. **Cliquer** "🗑️ Supprimer et refaire"
3. **Confirmer** la suppression
4. ✅ **Automatiquement** : curseur repositionné, écoute active
5. **Presser** le bouton sur la machine → nouvelle mesure

### Comparaison visuelle
1. **Clic gauche** sur un échantillon → mise en avant
2. **Comparaison** visuelle avec les autres (transparents)
3. **Clic** "↩️ Vue globale" → retour normal

### Navigation fluide
- **Aucune interruption** du workflow principal
- **Vue contextuelle** sans perdre l'ensemble
- **Actions rapides** via menu contextuel