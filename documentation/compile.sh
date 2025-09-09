#!/bin/bash

# Script de compilation de la documentation MEVEM
# Corrige les problèmes d'encodage et compile les documents

echo "📚 Compilation de la documentation MEVEM"
echo "========================================"

# Créer le dossier de sauvegarde
mkdir -p backup

# Sauvegarder les originaux
echo "💾 Sauvegarde des documents originaux..."
cp notice_utilisation.tex backup/
cp documentation_technique.tex backup/

# Corriger l'encodage en supprimant les caractères problématiques
echo "🔧 Correction des problèmes d'encodage..."

# Pour la notice d'utilisation
sed -i 's/[àáâäã]/a/g; s/[èéêë]/e/g; s/[ìíîï]/i/g; s/[òóôöõ]/o/g; s/[ùúûü]/u/g; s/[ç]/c/g' notice_utilisation.tex
sed -i 's/[ÀÁÂÄÃ]/A/g; s/[ÈÉÊË]/E/g; s/[ÌÍÎÏ]/I/g; s/[ÒÓÔÖÕ]/O/g; s/[ÙÚÛÜ]/U/g; s/[Ç]/C/g' notice_utilisation.tex

# Pour la documentation technique
sed -i 's/[àáâäã]/a/g; s/[èéêë]/e/g; s/[ìíîï]/i/g; s/[òóôöõ]/o/g; s/[ùúûü]/u/g; s/[ç]/c/g' documentation_technique.tex
sed -i 's/[ÀÁÂÄÃ]/A/g; s/[ÈÉÊË]/E/g; s/[ÌÍÎÏ]/I/g; s/[ÒÓÔÖÕ]/O/g; s/[ÙÚÛÜ]/U/g; s/[Ç]/C/g' documentation_technique.tex

# Compilation des documents
echo "📖 Compilation de la notice d'utilisation..."
pdflatex notice_utilisation.tex
pdflatex notice_utilisation.tex  # Deux fois pour les références

echo "📖 Compilation de la documentation technique..."
pdflatex documentation_technique.tex
pdflatex documentation_technique.tex  # Deux fois pour les références

# Nettoyage des fichiers temporaires
echo "🧹 Nettoyage des fichiers temporaires..."
rm -f *.aux *.log *.out *.toc *.synctex.gz

echo "✅ Compilation terminée!"
echo "📄 Fichiers générés:"
echo "  - notice_utilisation.pdf"
echo "  - documentation_technique.pdf"
echo ""
echo "📁 Originaux sauvegardés dans le dossier backup/"