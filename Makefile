# Makefile pour MEVEM - Mesure de la verse du maïs

.PHONY: install dev run build build-windows build-linux clean help check-permissions fix-permissions

# Variables
PYTHON := python3
PIP := pip3
VENV := venv

# Commandes par défaut
help:
	@echo "MEVEM - Mesure de la verse du maïs"
	@echo "=================================="
	@echo ""
	@echo "Commandes disponibles:"
	@echo "  install           Installer les dépendances"
	@echo "  dev              Installer les dépendances de développement"
	@echo "  run              Lancer l'application en mode développement"
	@echo "  check-permissions Diagnostiquer les permissions série"
	@echo "  fix-permissions  Réparer les permissions série (sudo requis)"
	@echo "  build            Construire l'exécutable pour la plateforme actuelle"
	@echo "  build-windows    Construire l'exécutable Windows"
	@echo "  build-linux      Construire l'exécutable Linux"
	@echo "  build-all        Construire pour toutes les plateformes"
	@echo "  clean            Nettoyer les fichiers temporaires"
	@echo "  test             Lancer les tests (si disponibles)"

# Installation des dépendances
install:
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt

# Installation des dépendances de développement
dev: install
	@echo "🛠️ Installation des outils de développement..."
	$(PIP) install pytest flake8 black

# Diagnostic des permissions
check-permissions:
	@echo "🔍 Diagnostic des permissions série..."
	$(PYTHON) check_permissions.py

# Réparation des permissions
fix-permissions:
	@echo "🛠️ Réparation des permissions série..."
	@echo "Ajout de l'utilisateur au groupe dialout..."
	sudo usermod -a -G dialout $$USER
	@echo "✅ Utilisateur ajouté au groupe dialout"
	@echo "⚠️  Vous devez redémarrer votre session (logout/login) pour que les changements prennent effet"

# Lancement en mode développement
run:
	@echo "🚀 Lancement de MEVEM..."
	$(PYTHON) app.py

# Construction pour la plateforme actuelle
build:
	@echo "🔨 Construction de l'exécutable..."
	$(PYTHON) build.py

# Construction Windows
build-windows:
	@echo "🔨 Construction Windows..."
	$(PYTHON) build.py windows

# Construction Linux
build-linux:
	@echo "🔨 Construction Linux..."
	$(PYTHON) build.py linux

# Construction toutes plateformes
build-all:
	@echo "🔨 Construction toutes plateformes..."
	$(PYTHON) build.py all

# Tests
test:
	@echo "🧪 Lancement des tests..."
	@if [ -f "test_app.py" ]; then \
		$(PYTHON) -m pytest test_app.py -v; \
	else \
		echo "Aucun fichier de test trouvé"; \
	fi

# Nettoyage
clean:
	@echo "🧹 Nettoyage..."
	rm -rf build/
	rm -rf dist/
	rm -rf dist_windows/
	rm -rf dist_linux/
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Installation d'un environnement virtuel (optionnel)
venv:
	@echo "🐍 Création de l'environnement virtuel..."
	$(PYTHON) -m venv $(VENV)
	@echo "Activez-le avec: source $(VENV)/bin/activate"