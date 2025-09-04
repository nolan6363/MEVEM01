#!/usr/bin/env python3
"""
Script de diagnostic des permissions série pour MEVEM
"""

import os
import sys
import grp
import pwd
import subprocess
import serial.tools.list_ports

def check_user_groups():
    """Vérifier les groupes de l'utilisateur"""
    username = pwd.getpwuid(os.getuid()).pw_name
    user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
    primary_group = grp.getgrgid(pwd.getpwuid(os.getuid()).pw_gid).gr_name
    user_groups.append(primary_group)
    
    print(f"👤 Utilisateur: {username}")
    print(f"📋 Groupes: {', '.join(user_groups)}")
    
    return 'dialout' in user_groups

def check_serial_ports():
    """Vérifier les ports série disponibles"""
    print("\n🔌 PORTS SÉRIE DÉTECTÉS:")
    print("-" * 50)
    
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("❌ Aucun port série détecté")
        return []
    
    accessible_ports = []
    
    for port in ports:
        print(f"\n📡 Port: {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Fabricant: {port.manufacturer or 'Inconnu'}")
        
        # Vérifier les permissions du fichier
        try:
            stat_info = os.stat(port.device)
            permissions = oct(stat_info.st_mode)[-3:]
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name
            
            print(f"   Permissions: {permissions}")
            print(f"   Propriétaire: {owner}:{group}")
            
        except Exception as e:
            print(f"   ❌ Erreur stat: {e}")
        
        # Tester l'accès
        try:
            test_serial = serial.Serial(port.device, timeout=0.1)
            test_serial.close()
            print(f"   ✅ ACCESSIBLE")
            accessible_ports.append(port.device)
        except serial.SerialException as e:
            if 'Permission denied' in str(e):
                print(f"   ❌ PERMISSION REFUSÉE")
            else:
                print(f"   ⚠️  Erreur: {e}")
        except Exception as e:
            print(f"   ❌ Erreur inconnue: {e}")
    
    return accessible_ports

def suggest_fixes():
    """Suggérer des solutions"""
    print("\n🛠️  SOLUTIONS RECOMMANDÉES:")
    print("-" * 50)
    
    username = pwd.getpwuid(os.getuid()).pw_name
    
    print("1️⃣  Ajouter l'utilisateur au groupe dialout:")
    print(f"   sudo usermod -a -G dialout {username}")
    print("   puis redémarrer la session (logout/login)")
    
    print("\n2️⃣  Vérifier que le groupe dialout existe:")
    print("   cat /etc/group | grep dialout")
    
    print("\n3️⃣  Solution temporaire (non recommandée):")
    print("   sudo chmod 666 /dev/ttyUSB*")
    
    print("\n4️⃣  Règle udev permanente:")
    print("   sudo nano /etc/udev/rules.d/50-usb-serial.rules")
    print("   Ajouter: SUBSYSTEM==\"tty\", GROUP=\"dialout\", MODE=\"0664\"")
    print("   puis: sudo udevadm control --reload-rules")

def main():
    """Fonction principale"""
    print("🌽 MEVEM - Diagnostic des permissions série")
    print("=" * 50)
    
    print("🐧 Plateforme:", sys.platform)
    
    # Vérifier les groupes utilisateur
    is_in_dialout = check_user_groups()
    
    if is_in_dialout:
        print("✅ Utilisateur dans le groupe dialout")
    else:
        print("❌ Utilisateur PAS dans le groupe dialout")
    
    # Vérifier les ports
    accessible_ports = check_serial_ports()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   Ports accessibles: {len(accessible_ports)}")
    print(f"   Dans groupe dialout: {'Oui' if is_in_dialout else 'Non'}")
    
    if not accessible_ports or not is_in_dialout:
        suggest_fixes()
    else:
        print("\n🎉 Tout semble correct ! MEVEM devrait fonctionner.")
    
    return 0 if accessible_ports else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)