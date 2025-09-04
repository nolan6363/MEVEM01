#!/bin/bash
# Lanceur MEVEM

# Obtenir le répertoire du script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Lancer l'application
echo "🌽 Démarrage de MEVEM..."
"$DIR/mevem"
