#!/usr/bin/env python3
"""
Script de build corrigé pour Linux avec Flask-SocketIO
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_linux_fixed():
    """Build l'application pour Linux avec les corrections Flask-SocketIO"""
    print("🔨 Construction de l'exécutable Linux (version corrigée)...")
    
    # Répertoire de base
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Nettoyer les anciens builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Créer un fichier spec temporaire
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates')],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'flask_socketio',
        'engineio',
        'socketio',
        'python_socketio',
        'python_engineio',
        'serial',
        'serial.tools.list_ports',
        'threading',
        'eventlet',
        'eventlet.wsgi',
        'dns',
        'dns.resolver',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mevem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowing_subsystem=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Écrire le fichier spec
    spec_file = base_dir / "mevem_linux.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    try:
        # Exécuter PyInstaller avec le fichier spec
        cmd = [sys.executable, "-m", "PyInstaller", str(spec_file)]
        result = subprocess.run(cmd, cwd=base_dir, check=True)
        
        print("✅ Build Linux terminé!")
        print(f"📦 Exécutable créé: {dist_dir / 'mevem'}")
        
        # Créer un répertoire de distribution propre
        dist_final = base_dir / "dist_linux_fixed"
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
echo "🌾 Démarrage de MEVEM - CRC Limagrain..."
"$DIR/mevem"
"""
        
        with open(dist_final / "start_mevem.sh", "w") as f:
            f.write(launcher_content)
        os.chmod(dist_final / "start_mevem.sh", 0o755)
        
        # Créer un fichier README
        readme_content = """MEVEM - Mesure de la verse du maïs
=====================================
Centre de recherche de Chappes (CRC) Limagrain

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
- Utilisez make check-permissions pour diagnostiquer les problèmes
- Assurez-vous que votre capteur est reconnu: dmesg | grep tty

Fonctionnalités:
- Moyennage configurable (1-100 valeurs)
- Export Excel personnalisé
- Calibration interactive
- Interface temps réel

Version: $(date +%Y-%m-%d)
"""
        
        with open(dist_final / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # Supprimer le fichier spec temporaire
        spec_file.unlink()
        
        print(f"📁 Distribution Linux créée dans: {dist_final}")
        print("\n🎉 Pour tester:")
        print(f"   cd {dist_final}")
        print("   ./start_mevem.sh")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du build: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    finally:
        # Nettoyer le fichier spec s'il existe
        if spec_file.exists():
            spec_file.unlink()

if __name__ == "__main__":
    success = build_linux_fixed()
    sys.exit(0 if success else 1)