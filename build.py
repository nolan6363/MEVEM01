#!/usr/bin/env python3
"""
Script de build universel pour MEVEM
Construit les exécutables pour Windows et Linux
"""

import sys
import platform
import subprocess
from pathlib import Path

def main():
    """Script principal de build"""
    print("🌽 MEVEM - Script de build")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    current_platform = platform.system().lower()
    
    print(f"Plateforme détectée: {current_platform}")
    
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
    else:
        target = current_platform
    
    if target in ['windows', 'win']:
        print("🔨 Construction pour Windows...")
        try:
            result = subprocess.run([sys.executable, "build_windows.py"], 
                                  cwd=base_dir, check=True)
            print("✅ Build Windows terminé!")
        except subprocess.CalledProcessError:
            print("❌ Échec du build Windows")
            return 1
            
    elif target in ['linux', 'lin']:
        print("🔨 Construction pour Linux...")
        try:
            result = subprocess.run([sys.executable, "build_linux.py"], 
                                  cwd=base_dir, check=True)
            print("✅ Build Linux terminé!")
        except subprocess.CalledProcessError:
            print("❌ Échec du build Linux")
            return 1
            
    elif target == 'all':
        print("🔨 Construction pour toutes les plateformes...")
        
        # Build Windows
        try:
            print("\n--- BUILD WINDOWS ---")
            subprocess.run([sys.executable, "build_windows.py"], 
                          cwd=base_dir, check=True)
            print("✅ Build Windows terminé!")
        except subprocess.CalledProcessError:
            print("❌ Échec du build Windows")
        
        # Build Linux
        try:
            print("\n--- BUILD LINUX ---")
            subprocess.run([sys.executable, "build_linux.py"], 
                          cwd=base_dir, check=True)
            print("✅ Build Linux terminé!")
        except subprocess.CalledProcessError:
            print("❌ Échec du build Linux")
    
    else:
        print(f"❌ Plateforme '{target}' non supportée")
        print("Plateformes disponibles: windows, linux, all")
        return 1
    
    print("\n🎉 Build terminé!")
    print("\nFichiers générés:")
    
    dist_windows = base_dir / "dist_windows"
    dist_linux = base_dir / "dist_linux"
    
    if dist_windows.exists():
        print(f"  Windows: {dist_windows}")
        for file in dist_windows.iterdir():
            print(f"    - {file.name}")
    
    if dist_linux.exists():
        print(f"  Linux: {dist_linux}")
        for file in dist_linux.iterdir():
            print(f"    - {file.name}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())