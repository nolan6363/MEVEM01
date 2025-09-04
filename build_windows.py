#!/usr/bin/env python3
"""
Script de build pour créer un exécutable Windows avec PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_windows():
    """Build l'application pour Windows"""
    print("🔨 Construction de l'exécutable Windows...")
    
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
        "--name=MEVEM",
        "--onefile",
        "--windowed",
        "--icon=static/icon.ico" if (base_dir / "static" / "icon.ico").exists() else "",
        "--add-data=templates;templates",
        "--add-data=static;static" if (base_dir / "static").exists() else "",
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
        
        print("✅ Build Windows terminé!")
        print(f"📦 Exécutable créé: {dist_dir / 'MEVEM.exe'}")
        
        # Créer un répertoire de distribution propre
        dist_final = base_dir / "dist_windows"
        if dist_final.exists():
            shutil.rmtree(dist_final)
        dist_final.mkdir()
        
        # Copier l'exécutable
        shutil.copy2(dist_dir / "MEVEM.exe", dist_final / "MEVEM.exe")
        
        # Créer un fichier README
        readme_content = """MEVEM - Mesure de la verse du maïs
=====================================

Instructions d'utilisation:
1. Connectez votre capteur USB série
2. Lancez MEVEM.exe
3. L'interface web s'ouvrira automatiquement dans votre navigateur
4. Suivez les instructions à l'écran pour calibrer puis mesurer

Résolution de problèmes:
- Si l'interface ne s'ouvre pas, allez sur http://127.0.0.1:5000
- Assurez-vous que votre capteur est bien connecté
- Vérifiez que les pilotes du capteur sont installés

Support: https://github.com/votre-repo/mevem
"""
        
        with open(dist_final / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"📁 Distribution Windows créée dans: {dist_final}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du build: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = build_windows()
    sys.exit(0 if success else 1)