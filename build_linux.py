#!/usr/bin/env python3
"""
Script de build pour créer un exécutable Linux avec PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_linux():
    """Build l'application pour Linux"""
    print("🔨 Construction de l'exécutable Linux...")
    
    # Répertoire de base
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Nettoyer les anciens builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Commande PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=mevem",
        "--onefile",
        "--add-data=templates:templates",
        "--add-data=static:static" if (base_dir / "static").exists() else "",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=flask_socketio",
        "--hidden-import=engineio",
        "--hidden-import=socketio",
        "--hidden-import=python_socketio",
        "--hidden-import=python_engineio",
        "--hidden-import=serial",
        "--hidden-import=serial.tools.list_ports",
        "--hidden-import=threading",
        "app.py"
    ]
    
    # Filtrer les arguments vides
    cmd = [arg for arg in cmd if arg]
    
    try:
        # Exécuter PyInstaller
        result = subprocess.run(cmd, cwd=base_dir, check=True)
        
        print("✅ Build Linux terminé!")
        print(f"📦 Exécutable créé: {dist_dir / 'mevem'}")
        
        # Créer un répertoire de distribution propre
        dist_final = base_dir / "dist_linux"
        if dist_final.exists():
            shutil.rmtree(dist_final)
        dist_final.mkdir()
        
        # Copier l'exécutable
        shutil.copy2(dist_dir / "mevem", dist_final / "mevem")
        
        # Rendre l'exécutable... exécutable
        os.chmod(dist_final / "mevem", 0o755)
        
        # Créer un script de lancement
        launcher_content = """#!/bin/bash
# Lanceur MEVEM

# Obtenir le répertoire du script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Lancer l'application
echo "🌽 Démarrage de MEVEM..."
"$DIR/mevem"
"""
        
        with open(dist_final / "start_mevem.sh", "w") as f:
            f.write(launcher_content)
        os.chmod(dist_final / "start_mevem.sh", 0o755)
        
        # Créer un fichier README
        readme_content = """MEVEM - Mesure de la verse du maïs
=====================================

Instructions d'installation Linux:
1. Assurez-vous d'avoir les permissions pour accéder aux ports série
   sudo usermod -a -G dialout $USER
   (puis redémarrez votre session)

Instructions d'utilisation:
1. Connectez votre capteur USB série
2. Lancez ./mevem ou ./start_mevem.sh
3. L'interface web s'ouvrira automatiquement dans votre navigateur
4. Suivez les instructions à l'écran pour calibrer puis mesurer

Résolution de problèmes:
- Si l'interface ne s'ouvre pas, allez sur http://127.0.0.1:5000
- Vérifiez les permissions série: ls -l /dev/ttyUSB*
- Assurez-vous que votre capteur est reconnu: dmesg | grep tty

Support: https://github.com/votre-repo/mevem
"""
        
        with open(dist_final / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"📁 Distribution Linux créée dans: {dist_final}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du build: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = build_linux()
    sys.exit(0 if success else 1)