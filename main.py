#!/usr/bin/env python3
"""
Décodeur de capteur avec calibration
Analyse les données angle/force avec système de calibration interactif
"""

import serial
import re
import time
import json
import csv
from datetime import datetime
from collections import deque
import threading
import queue
import os


class CalibratedSensorDecoder:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False

        # Configuration de calibration - dossier persistant
        self.config_dir = self._get_config_directory()
        os.makedirs(self.config_dir, exist_ok=True)
        self.calibration_file = os.path.join(self.config_dir, "sensor_calibration.json")
        # Calibration par défaut avec vos valeurs validées
        self.calibration = {
            'angle': {
                'raw_min': 1019.3323053199691,
                'raw_max': 705.540192926045,
                'real_min': 0.0,
                'real_max': 45.0,
                'calibrated': True
            },
            'force': {
                'raw_min': 23.444794952681388,
                'raw_max': 55.96846254927727,
                'real_min': 0.0,
                'real_max': 1.0,
                'calibrated': True
            }
        }

        # Charger calibration existante
        self.load_calibration()

        # Stockage des données
        self.data_buffer = deque(maxlen=1000)
        self.stats = {
            'total_lines': 0,
            'valid_packets': 0,
            'angles_count': 0,
            'forces_count': 0,
            'start_time': None
        }

        # Patterns regex
        self.patterns = {
            'VeTiMa': re.compile(r'VeTiMa\s*(0x[0-9A-Fa-f]{1,4})\s*(0x[0-9A-Fa-f]{1,4})'),
            'iMa': re.compile(r'iMa\s*(0x[0-9A-Fa-f]{1,4})\s*(0x[0-9A-Fa-f]{1,4})'),
            'Ta': re.compile(r'Ta\s*(0x[0-9A-Fa-f]{1,4})\s*(0x[0-9A-Fa-f]{1,4})')
        }

    def _get_config_directory(self):
        """Obtenir le répertoire de configuration de l'application"""
        import platform
        system = platform.system()

        if system == "Windows":
            # Windows: utiliser APPDATA
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(base_dir, 'MEVEM')
        else:
            # Linux/macOS: utiliser le dossier home
            return os.path.join(os.path.expanduser('~'), '.mevem')

    def load_calibration(self):
        """Charger la calibration depuis un fichier"""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    saved_cal = json.load(f)
                    self.calibration.update(saved_cal)
                print(f"✅ Calibration chargée depuis {self.calibration_file}")
            except Exception as e:
                print(f"⚠️ Erreur chargement calibration: {e}")
                print("🔧 Utilisation de la calibration par défaut")
        else:
            print("📡 Première utilisation - calibration par défaut chargée")
            print("💡 La calibration par défaut est déjà optimisée pour votre capteur")
            # Sauvegarder la calibration par défaut pour la prochaine fois
            self.save_calibration()

    def save_calibration(self):
        """Sauvegarder la calibration"""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration, f, indent=2)
            print(f"💾 Calibration sauvegardée dans {self.calibration_file}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde calibration: {e}")

    def print_calibration_status(self):
        """Afficher le statut de la calibration"""
        print("\n📏 STATUT DE LA CALIBRATION")
        print("=" * 40)

        # Angle
        angle_cal = self.calibration['angle']
        print(f"📐 ANGLE: {'✅ Calibré' if angle_cal['calibrated'] else '❌ Non calibré'}")
        if angle_cal['calibrated']:
            print(f"   {angle_cal['raw_min']} (brut) = {angle_cal['real_min']}°")
            print(f"   {angle_cal['raw_max']} (brut) = {angle_cal['real_max']}°")

        # Force
        force_cal = self.calibration['force']
        print(f"⚖️  FORCE: {'✅ Calibré' if force_cal['calibrated'] else '❌ Non calibré'}")
        if force_cal['calibrated']:
            print(f"   {force_cal['raw_min']} (brut) = {force_cal['real_min']}kg")
            print(f"   {force_cal['raw_max']} (brut) = {force_cal['real_max']}kg")

        print()

    def connect(self):
        """Connexion au port série"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                rtscts=False,
                dsrdtr=False
            )

            # Vider les buffers
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()

            print(f"✅ Connecté à {self.port} @ {self.baudrate} bauds")
            return True

        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

    def disconnect(self):
        """Déconnexion"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("🔌 Déconnecté")

    def read_current_values(self, duration=2):
        """Lire les valeurs actuelles pendant une durée donnée"""
        if not self.serial_conn or not self.serial_conn.is_open:
            if not self.connect():
                return None, None

        buffer = ""
        angle_values = []
        force_values = []

        print(f"📡 Lecture des valeurs pendant {duration}s...")
        start_time = time.time()

        while time.time() - start_time < duration:
            try:
                if self.serial_conn.in_waiting > 0:
                    bytes_to_read = min(self.serial_conn.in_waiting, 1024)
                    chunk = self.serial_conn.read(bytes_to_read)

                    if chunk:
                        buffer += chunk.decode('utf-8', errors='ignore')

                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            parsed = self.parse_line_raw(line)

                            if parsed:
                                for data in parsed:
                                    angle_values.append(data['raw_angle'])
                                    force_values.append(data['raw_force'])
                                    print(f"  📊 Angle: {data['raw_angle']} Force: {data['raw_force']}")

                time.sleep(0.01)

            except Exception as e:
                print(f"⚠️ Erreur lecture: {e}")
                time.sleep(0.1)

        if angle_values and force_values:
            # Moyenner les valeurs
            avg_angle = sum(angle_values) / len(angle_values)
            avg_force = sum(force_values) / len(force_values)
            print(f"📊 Moyennes: Angle={avg_angle:.1f} Force={avg_force:.1f}")
            return avg_angle, avg_force

        return None, None

    def parse_line_raw(self, line):
        """Parse une ligne et retourne les valeurs brutes"""
        line = line.strip()
        if not line:
            return None

        results = []

        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(line)
            for match in matches:
                try:
                    val1 = int(match[0], 16)
                    val2 = int(match[1], 16)

                    if val1 <= 0xFFFF and val2 <= 0xFFFF:  # Valeurs étendues
                        results.append({
                            'type': pattern_name,
                            'raw_angle': val2,  # Deuxième capteur = angle (CORRIGÉ)
                            'raw_force': val1  # Premier capteur = force (CORRIGÉ)
                        })

                except ValueError:
                    continue

        return results if results else None

    def calibrate_sensor(self):
        """Procédure de calibration interactive"""
        print("\n🎯 CALIBRATION DES CAPTEURS")
        print("=" * 50)

        if not self.connect():
            print("❌ Impossible de se connecter pour la calibration")
            return

        # Calibration de l'angle
        print("\n📐 CALIBRATION DE L'ANGLE")
        print("1. Placez le dispositif à 0° (position de référence)")
        input("   Appuyez sur Entrée quand c'est prêt...")

        angle_0, force_0 = self.read_current_values(3)
        if angle_0 is None:
            print("❌ Impossible de lire les valeurs à 0°")
            return

        print(f"✅ Valeur angle à 0°: {angle_0:.1f}")

        print("\n2. Placez le dispositif à 45°")
        input("   Appuyez sur Entrée quand c'est prêt...")

        angle_45, force_45 = self.read_current_values(3)
        if angle_45 is None:
            print("❌ Impossible de lire les valeurs à 45°")
            return

        print(f"✅ Valeur angle à 45°: {angle_45:.1f}")

        # Calibration de la force
        print("\n⚖️  CALIBRATION DU POIDS")
        print("1. Enlevez tout poids (capteur à vide)")
        input("   Appuyez sur Entrée quand c'est prêt...")

        angle_vide, force_vide = self.read_current_values(3)
        if force_vide is None:
            print("❌ Impossible de lire les valeurs à vide")
            return

        print(f"✅ Valeur poids à vide: {force_vide:.1f}")

        print("\n2. Placez exactement 1kg sur le capteur")
        input("   Appuyez sur Entrée quand c'est prêt...")

        angle_1kg, force_1kg = self.read_current_values(3)
        if force_1kg is None:
            print("❌ Impossible de lire les valeurs à 1kg")
            return

        print(f"✅ Valeur poids à 1kg: {force_1kg:.1f}")

        # Sauvegarder la calibration (noter l'inversion corrigée)
        self.calibration['angle'] = {
            'raw_min': angle_0,
            'raw_max': angle_45,
            'real_min': 0.0,
            'real_max': 45.0,
            'calibrated': True
        }

        self.calibration['force'] = {
            'raw_min': force_vide,
            'raw_max': force_1kg,
            'real_min': 0.0,
            'real_max': 1.0,
            'calibrated': True
        }

        self.save_calibration()

        print("\n✅ CALIBRATION TERMINÉE")
        print("📝 Note: Premier capteur = Poids, Deuxième capteur = Angle")
        self.print_calibration_status()

    def convert_raw_to_physical(self, raw_angle, raw_force):
        """Convertir les valeurs brutes en valeurs physiques"""
        # Conversion angle
        if self.calibration['angle']['calibrated']:
            angle_cal = self.calibration['angle']
            if angle_cal['raw_max'] != angle_cal['raw_min']:
                angle_ratio = (raw_angle - angle_cal['raw_min']) / (angle_cal['raw_max'] - angle_cal['raw_min'])
                angle_deg = angle_cal['real_min'] + angle_ratio * (angle_cal['real_max'] - angle_cal['real_min'])
            else:
                angle_deg = angle_cal['real_min']
        else:
            # Conversion par défaut
            angle_deg = raw_angle * 360.0 / 1023.0

        # Conversion force
        if self.calibration['force']['calibrated']:
            force_cal = self.calibration['force']
            if force_cal['raw_max'] != force_cal['raw_min']:
                force_ratio = (raw_force - force_cal['raw_min']) / (force_cal['raw_max'] - force_cal['raw_min'])
                force_kg = force_cal['real_min'] + force_ratio * (force_cal['real_max'] - force_cal['real_min'])
            else:
                force_kg = force_cal['real_min']
        else:
            # Conversion par défaut
            force_kg = raw_force * 1.0 / 1023.0

        return angle_deg, force_kg

    def parse_line(self, line):
        """Parse une ligne et retourne les valeurs converties"""
        raw_data = self.parse_line_raw(line)
        if not raw_data:
            return None

        results = []
        for data in raw_data:
            angle_deg, force_kg = self.convert_raw_to_physical(data['raw_angle'], data['raw_force'])

            results.append({
                'timestamp': datetime.now(),
                'type': data['type'],
                'raw_angle': data['raw_angle'],
                'raw_force': data['raw_force'],
                'angle_deg': angle_deg,
                'force_kg': force_kg
            })

        return results

    def monitor_sensors(self, duration=None):
        """Surveiller les capteurs en temps réel"""
        if not self.connect():
            return []

        print(f"📡 Surveillance des capteurs...")
        if duration:
            print(f"   Durée: {duration}s")
        else:
            print("   Continu (Ctrl+C pour arrêter)")

        self.print_calibration_status()

        self.running = True
        buffer = ""
        all_data = []

        try:
            start_time = time.time()

            while self.running:
                if duration and (time.time() - start_time) > duration:
                    break

                try:
                    if self.serial_conn.in_waiting > 0:
                        bytes_to_read = min(self.serial_conn.in_waiting, 1024)
                        chunk = self.serial_conn.read(bytes_to_read)

                        if chunk:
                            buffer += chunk.decode('utf-8', errors='ignore')

                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                parsed = self.parse_line(line)

                                if parsed:
                                    all_data.extend(parsed)

                                    for data in parsed:
                                        print(
                                            f"🎯 {data['type']}: 📐{data['angle_deg']:6.1f}° ⚖️{data['force_kg']:6.3f}kg (Raw: F={data['raw_force']:4d}, A={data['raw_angle']:4d})")

                    time.sleep(0.01)

                except Exception as e:
                    print(f"⚠️ Erreur: {e}")
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        finally:
            self.disconnect()

        return all_data

    def save_data(self, data, filename=None):
        """Sauvegarder les données"""
        if not data:
            return

        if not filename:
            filename = f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Type', 'Angle_deg', 'Force_kg', 'Raw_Angle', 'Raw_Force'])

                for point in data:
                    writer.writerow([
                        point['timestamp'].isoformat(),
                        point['type'],
                        f"{point['angle_deg']:.3f}",
                        f"{point['force_kg']:.4f}",
                        point['raw_angle'],
                        point['raw_force']
                    ])

            print(f"💾 Données sauvegardées dans {filename}")

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description='Décodeur de capteur avec calibration')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Port série')
    parser.add_argument('--baudrate', type=int, default=115200, help='Vitesse')
    parser.add_argument('--calibrate', action='store_true', help='Lancer la calibration')
    parser.add_argument('--duration', type=int, help='Durée de surveillance (secondes)')
    parser.add_argument('--output', help='Fichier de sortie CSV')

    args = parser.parse_args()

    # Créer le décodeur
    decoder = CalibratedSensorDecoder(port=args.port, baudrate=args.baudrate)

    # Calibration
    if args.calibrate:
        decoder.calibrate_sensor()
        return

    # Surveillance
    data = decoder.monitor_sensors(duration=args.duration)

    # Sauvegarder
    if data:
        decoder.save_data(data, args.output)

        # Statistiques
        if data:
            angles = [d['angle_deg'] for d in data]
            forces = [d['force_kg'] for d in data]
            print(f"\n📊 RÉSUMÉ: {len(data)} échantillons")
            print(f"   Angles: {min(angles):6.1f}° - {max(angles):6.1f}°")
            print(f"   Forces: {min(forces):6.3f}kg - {max(forces):6.3f}kg")


if __name__ == "__main__":
    main()