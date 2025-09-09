# Documentation MEVEM

Ce dossier contient la documentation complète du système MEVEM (Mesure de la verse du maïs).

## Contenu de la documentation

### 📖 Notice d'utilisation (`notice_utilisation.tex`)

Document destiné aux utilisateurs finaux contenant :

- **Présentation générale** du système MEVEM
- **Installation et configuration** du logiciel
- **Guide de première utilisation** 
- **Procédure de calibration** détaillée avec photos
- **Réalisation des mesures** étape par étape
- **Analyse et export des données**
- **Résolution de problèmes** courants
- **Maintenance préventive et curative**
- **Caractéristiques techniques**
- **Support et garantie**

### 🔧 Documentation technique (`documentation_technique.tex`)

Document destiné aux développeurs et techniciens contenant :

- **Architecture générale** du système
- **Module de communication série** et protocoles
- **Serveur web et API REST** 
- **Traitement des données** et algorithmes
- **Interface utilisateur** et technologies web
- **Déploiement et build** multi-plateforme
- **Sécurité et performance**
- **Tests et validation**
- **Maintenance et évolution**
- **Annexes techniques** détaillées

## Compilation des documents

### Prérequis

Pour compiler les documents LaTeX, vous devez avoir installé :

- **LaTeX** (distribution complète comme TeX Live ou MiKTeX)
- **Packages LaTeX** suivants :
  - `babel` (support français)
  - `graphicx` (images)
  - `hyperref` (liens)
  - `listings` (code source)
  - `tcolorbox` (boîtes colorées)
  - `booktabs` (tableaux)
  - `longtable` (tableaux longs)

### Compilation

```bash
# Compilation de la notice d'utilisation
cd documentation
pdflatex notice_utilisation.tex
pdflatex notice_utilisation.tex  # Deux fois pour les références croisées

# Compilation de la documentation technique
pdflatex documentation_technique.tex
pdflatex documentation_technique.tex
```

### Images à ajouter

Les documents LaTeX référencent des images qui doivent être ajoutées dans le dossier `documentation/` :

#### Notice d'utilisation
- `logo_mevem.png` - Logo de l'application
- `interface_principale.png` - Capture de l'interface complète
- `calibration_0_degres.png` - Position de calibration à 0°
- `calibration_45_degres.png` - Position de calibration à 45°
- `calibration_vide.png` - Capteur de force à vide
- `calibration_1kg.png` - Calibration avec masse de 1 kg
- `mesure_en_cours.png` - Acquisition de données en temps réel

#### Documentation technique
- `logo_mevem.png` - Logo de l'application
- `architecture_systeme.png` - Schéma d'architecture générale
- `timing_diagram.png` - Diagramme de timing des communications

## Structure recommandée des images

```
documentation/
├── images/
│   ├── user_manual/
│   │   ├── interface_principale.png
│   │   ├── calibration_0_degres.png
│   │   ├── calibration_45_degres.png
│   │   ├── calibration_vide.png
│   │   ├── calibration_1kg.png
│   │   └── mesure_en_cours.png
│   └── technical/
│       ├── architecture_systeme.png
│       └── timing_diagram.png
├── logo_mevem.png
├── notice_utilisation.tex
├── documentation_technique.tex
└── README.md
```

## Versions des documents

- **Version 1.0** - Version initiale
- Basée sur l'analyse du code source MEVEM
- Compatible avec l'architecture Flask + WebSocket
- Support des capteurs VeTiMa/iMa/Ta

## Mise à jour de la documentation

Pour maintenir la documentation à jour :

1. **Modifications du code** → Mettre à jour la documentation technique
2. **Nouvelles fonctionnalités** → Mettre à jour la notice d'utilisation
3. **Corrections de bugs** → Vérifier la cohérence des deux documents
4. **Nouvelles versions** → Incrémenter le numéro de version

## Contribution

Pour contribuer à la documentation :

1. Modifier les fichiers `.tex` appropriés
2. Ajouter les images nécessaires
3. Tester la compilation LaTeX
4. Vérifier la cohérence entre les deux documents
5. Mettre à jour ce README si nécessaire

## Contact

Pour toute question sur la documentation, contactez l'équipe de développement MEVEM.