# 🌽 MEVEM - Mesure de la verse du maïs

Application Flask pour mesurer la verse du maïs via capteurs USB série, avec interface web interactive et export Excel.

## ✨ Fonctionnalités

- 📡 **Communication série USB** - Lecture en temps réel des capteurs angle/force
- 📊 **Interface web moderne** - Graphique interactif force vs angle
- 🎯 **Calibration interactive** - Système de calibration guidé
- 💾 **Export Excel** - Sauvegarde des mesures avec métadonnées
- 🚀 **Auto-démarrage** - Ouverture automatique dans le navigateur
- 📦 **Exécutables standalone** - Build Windows et Linux sans installation

## 🚀 Installation rapide

### Option 1: Utiliser les exécutables (recommandé)
1. Téléchargez l'exécutable pour votre système
2. **Linux uniquement** - Configurez les permissions série (voir section ci-dessous)
3. Connectez votre capteur USB
4. Lancez l'exécutable
5. L'interface web s'ouvre automatiquement

### Option 2: Installation depuis les sources
```bash
# Cloner le projet
git clone https://github.com/votre-repo/mevem.git
cd mevem

# Installer les dépendances
make install
# ou
pip install -r requirements.txt

# Lancer l'application
make run
# ou
python app.py
```

## 🔧 Développement

### Structure du projet
```
mevem/
├── app.py              # Application Flask principale
├── main.py             # Module de communication série (existant)
├── requirements.txt    # Dépendances Python
├── Makefile           # Commandes de build et développement
├── templates/         # Templates HTML
│   └── index.html     # Interface web principale
├── build.py           # Script de build universel
├── build_windows.py   # Build Windows
└── build_linux.py     # Build Linux
```

### Commandes de développement
```bash
# Installer les dépendances
make install

# Lancer en mode développement
make run

# Construire l'exécutable
make build

# Construire pour Windows
make build-windows

# Construire pour Linux
make build-linux

# Construire pour toutes les plateformes
make build-all

# Nettoyer les fichiers temporaires
make clean
```

## 📋 Prérequis

### Système
- Python 3.8+
- Port série USB disponible
- Navigateur web moderne

### Capteurs
- Capteur d'angle (connecté via USB série)
- Capteur de force (connecté via USB série)
- Baudrate: 115200 (configurable)
- Protocoles supportés: VeTiMa, iMa, Ta

## 🎮 Utilisation

### 1. Première utilisation
1. **Connecter les capteurs** - Branchez votre dispositif USB série
2. **Lancer MEVEM** - Exécutable ou `python app.py`
3. **Interface web** - S'ouvre automatiquement sur http://127.0.0.1:5000

### 2. Calibration
1. Cliquez sur **"🎯 Calibrer capteurs"**
2. Suivez les instructions pour calibrer l'angle (0° et 45°)
3. Suivez les instructions pour calibrer la force (0kg et 1kg)
4. La calibration est sauvegardée automatiquement

### 3. Mesure
1. Cliquez sur **"🚀 Démarrer mesure"**
2. La courbe se dessine en temps réel
3. Cliquez sur **"⏹️ Arrêter mesure"** quand terminé
4. Exportez en Excel ou recommencez si nécessaire

### 4. Interface

**Panneau de contrôle:**
- 🚀 Démarrer mesure
- ⏹️ Arrêter mesure
- 🗑️ Effacer données
- 📊 Exporter Excel
- 🎯 Calibrer capteurs
- 🔄 Actualiser statut

**Affichage:**
- Graphique temps réel force vs angle
- Statistiques (durée, amplitude, force max)
- État de connexion et calibration

## 📊 Format d'export Excel

L'export génère un fichier Excel avec:
- **Feuille "Mesures MEVEM"** - Données brutes (timestamp, angle, force)
- **Feuille "Métadonnées"** - Informations de session (date, durée, statistiques)

## 🔧 Configuration

### Ports série
L'application teste automatiquement:
- Linux: `/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyACM0`
- Windows: `COM3`, `COM4`, `COM5`

### Calibration
Les paramètres de calibration sont sauvegardés dans `sensor_calibration.json`:
```json
{
  "angle": {
    "raw_min": 0,
    "raw_max": 1023,
    "real_min": 0.0,
    "real_max": 45.0,
    "calibrated": true
  },
  "force": {
    "raw_min": 0,
    "raw_max": 1023,
    "real_min": 0.0,
    "real_max": 1.0,
    "calibrated": true
  }
}
```

## 🏗️ Build des exécutables

### Build automatique
```bash
# Build pour la plateforme actuelle
make build

# Build Windows (depuis n'importe quelle plateforme)
make build-windows

# Build Linux (depuis n'importe quelle plateforme)
make build-linux

# Build toutes plateformes
make build-all
```

### Build manuel
```bash
# Windows
python build_windows.py

# Linux
python build_linux.py

# Universel
python build.py [windows|linux|all]
```

Les exécutables sont créés dans `dist_windows/` et `dist_linux/`.

## 🔧 Configuration des permissions série (Linux uniquement)

### Diagnostic automatique
```bash
# Vérifier les permissions actuelles
make check-permissions

# Ou directement
python check_permissions.py
```

### Solution rapide (recommandée)
```bash
# Ajouter l'utilisateur au groupe dialout
make fix-permissions

# Puis redémarrer votre session (logout/login)
```

### Solution manuelle
```bash
# Ajouter l'utilisateur au groupe dialout
sudo usermod -a -G dialout $USER

# Vérifier l'ajout
groups $USER

# Redémarrer la session pour appliquer les changements
```

### Sur Windows
**Aucune configuration nécessaire** - les ports COM sont directement accessibles.

## 🐛 Résolution de problèmes

### Connexion série
- **Linux**: 
  - Utilisez `make check-permissions` pour diagnostiquer
  - Assurez-vous d'être dans le groupe `dialout`
  - Vérifiez que le port n'est pas utilisé: `sudo lsof /dev/ttyUSB0`
- **Windows**: 
  - Installez les pilotes du capteur
  - Vérifiez le Gestionnaire de périphériques
- **Test**: `dmesg | grep tty` (Linux) ou Gestionnaire de périphériques (Windows)

### Interface web
- Accès manuel: http://127.0.0.1:5000
- Vérifiez que le port 5000 n'est pas utilisé
- Redémarrez l'application si problème de connexion

### Calibration
- Assurez-vous que le capteur envoie des données
- Respectez les positions exactes (0°, 45°, 0kg, 1kg)
- La calibration peut être refaite à tout moment

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 👥 Auteurs

- Développeur principal: [Votre nom]
- Module série original: `main.py` (existant)

## 🔗 Liens utiles

- [Documentation Flask](https://flask.palletsprojects.com/)
- [PyInstaller](https://pyinstaller.readthedocs.io/)
- [Chart.js](https://www.chartjs.org/)
- [Socket.IO](https://socket.io/)

---

*MEVEM - Mesure de la verse du maïs - Une solution complète pour l'agriculture de précision* 🌽