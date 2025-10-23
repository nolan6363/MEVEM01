# Filtrage du bruit initial - MEVEM

## 🎯 Problème résolu

### Bruit initial des capteurs
Lors du démarrage d'une mesure, les premiers points reçus des capteurs contiennent souvent :
- **Données instables** pendant la stabilisation des capteurs
- **Valeurs aberrantes** dues au démarrage électronique
- **Fluctuations** transitoires avant régime stable
- **Parasites** de commutation

## ⚙️ Solution implémentée

### Filtrage automatique
- **Ignorer les N premiers points** reçus lors de chaque mesure
- **Configurable** via l'interface utilisateur (0 à 50 points)
- **Valeur par défaut** : 10 points
- **Application immédiate** sur nouvelles mesures

### Interface utilisateur
- **Slider** dans "Paramètres d'acquisition"
- **Libellé** : "Ignorer le bruit : X points"
- **Bouton** "Appliquer" pour confirmer
- **Feedback** visuel avec message de confirmation

## 🔧 Fonctionnement technique

### Backend (app.py)
```python
initial_skip_points = 10  # Configurable
points_received = 0      # Compteur par mesure

# Dans measurement_worker()
if points_received <= initial_skip_points:
    print(f"🚫 Ignorer point {points_received}/{initial_skip_points}")
    continue  # Ne pas traiter ce point
```

### API REST
- **POST** `/api/skip_points/set` : Configurer le nombre
- **Validation** : 0 ≤ valeur ≤ 100
- **Retour** : Message de confirmation ou erreur

### Frontend
- **Slider** 0-50 points avec affichage temps réel
- **Event listener** pour mise à jour visuelle
- **Fonction** `applySkipPoints()` pour envoi API

## 📊 Impact sur les mesures

### Avant filtrage
```
Point 1: ❌ 127.3°, 0.001kg (bruit)
Point 2: ❌ 89.7°, -0.003kg (bruit)  
Point 3: ❌ 156.2°, 0.008kg (bruit)
...
Point 10: ❌ 92.1°, 0.002kg (bruit)
Point 11: ✅ 45.2°, 0.156kg (début mesure valide)
Point 12: ✅ 46.1°, 0.187kg (données stables)
```

### Après filtrage (skip=10)
```
Point 1-10: 🚫 IGNORÉS (bruit initial)
Point 11: ✅ 45.2°, 0.156kg (premier point conservé)
Point 12: ✅ 46.1°, 0.187kg (données stables)
```

## 🎛️ Configuration recommandée

### Selon le type de capteur
- **Capteurs rapides** : 5-10 points
- **Capteurs lents** : 10-20 points
- **Environnement bruité** : 15-25 points
- **Tests/debug** : 0 points (pas de filtrage)

### Selon la fréquence d'acquisition
- **100 Hz** : 10 points = 0.1 seconde
- **50 Hz** : 10 points = 0.2 seconde
- **25 Hz** : 10 points = 0.4 seconde

## 🔄 Réinitialisation automatique

### À chaque nouvelle mesure
- **Compteur remis à zéro** : `points_received = 0`
- **Filtrage redémarre** : Les X premiers points sont ignorés
- **Pas de cumul** entre mesures d'échantillons différents

### Fonctions concernées
- `start_measurement()` → reset compteur
- `start_listening()` → reset compteur  
- Auto-détection nouvelle mesure → reset compteur

## ✅ Avantages

### Qualité des données
- **Suppression du bruit** de démarrage
- **Mesures plus stables** dès le début
- **Graphiques plus propres** sans pics parasites
- **Statistiques plus précises** (moyenne, max, etc.)

### Facilité d'utilisation
- **Configuration simple** avec slider visuel
- **Effet immédiat** sur prochaines mesures
- **Pas d'impact** sur mesures en cours
- **Valeur persistante** pendant la session

### Flexibilité
- **Désactivable** (régler à 0)
- **Ajustable** selon conditions de mesure
- **Testable** facilement avec différentes valeurs
- **Pas de perte** si valeur trop élevée (juste délai)

## 🚨 Notes importantes

### Limitations
- **Ne filtre que le début** de chaque mesure
- **Pas de filtrage** en cours de mesure
- **Délai supplémentaire** avant premiers points valides
- **Configuration globale** (même valeur pour tous échantillons)

### Recommandations
- **Tester** avec différentes valeurs sur même échantillon
- **Observer** la stabilité des premiers points conservés
- **Ajuster** selon résultats obtenus
- **Documenter** la valeur utilisée pour reproductibilité