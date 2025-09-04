#!/usr/bin/env python3
"""
Script de build final pour MEVEM - Version simple sans WebSocket temps réel
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_simple_app():
    """Créer une version simplifiée de l'app pour PyInstaller"""
    
    simple_app_content = '''#!/usr/bin/env python3
"""
Version simplifiée de MEVEM pour PyInstaller
"""

import json
import threading
import time
import webbrowser
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import os
import sys
import serial.tools.list_ports
from main import CalibratedSensorDecoder
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mevem_secret_2024'

# Instance globale du décodeur
decoder = None
current_measurement = []
measurement_active = False
measurement_thread = None
selected_port = None
averaging_window = 25  # Nombre de valeurs pour la moyenne
angle_accumulator = []  # Accumulateur pour les angles
force_accumulator = []  # Accumulateur pour les forces

def get_available_ports():
    """Obtenir la liste des ports série disponibles"""
    ports = []
    try:
        available_ports = serial.tools.list_ports.comports()
        for port in available_ports:
            # Tester l'accès au port
            access_status = check_port_access(port.device)
            
            ports.append({
                'device': port.device,
                'description': port.description,
                'manufacturer': port.manufacturer or 'Inconnu',
                'accessible': access_status['accessible'],
                'error': access_status.get('error', '')
            })
    except Exception as e:
        print(f"Erreur lors de la recherche des ports: {e}")
    
    return ports

def check_port_access(port):
    """Vérifier l'accès à un port série"""
    try:
        # Essayer d'ouvrir le port brièvement
        test_conn = serial.Serial(port, timeout=0.1)
        test_conn.close()
        return {'accessible': True}
    except serial.SerialException as e:
        error_msg = str(e)
        if 'Permission denied' in error_msg:
            return {
                'accessible': False,
                'error': 'Permission refusée - Ajoutez votre utilisateur au groupe dialout'
            }
        elif 'Device or resource busy' in error_msg:
            return {
                'accessible': False,
                'error': 'Port occupé par une autre application'
            }
        else:
            return {
                'accessible': False,
                'error': f'Erreur: {error_msg}'
            }
    except Exception as e:
        return {
            'accessible': False,
            'error': f'Erreur inconnue: {str(e)}'
        }

def initialize_decoder(port=None):
    """Initialiser le décodeur de capteurs"""
    global decoder
    try:
        if port:
            # Utiliser le port spécifié
            decoder = CalibratedSensorDecoder(port=port, baudrate=115200)
            if decoder.connect():
                print(f"✅ Connecté au port {port}")
                decoder.disconnect()  # Déconnecter pour l'instant
                return True
            else:
                return False
        else:
            # Auto-détection
            ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', 'COM3', 'COM4', 'COM5']
            
            for port in ports:
                try:
                    decoder = CalibratedSensorDecoder(port=port, baudrate=115200)
                    if decoder.connect():
                        print(f"✅ Connecté au port {port}")
                        decoder.disconnect()  # Déconnecter pour l'instant
                        return True
                except Exception as e:
                    continue
            
            print("⚠️ Aucun port série trouvé, utilisation du mode démo")
            decoder = CalibratedSensorDecoder(port='/dev/null', baudrate=115200)
            return False
    except Exception as e:
        print(f"❌ Erreur initialisation décodeur: {e}")
        return False

def measurement_worker():
    """Worker thread pour la mesure en continu - VERSION SIMPLIFIÉE"""
    global current_measurement, measurement_active, decoder
    global averaging_window, angle_accumulator, force_accumulator
    
    if not decoder.connect():
        print("Impossible de se connecter au capteur")
        return
    
    buffer = ""
    start_time = time.time()
    
    # Réinitialiser les accumulateurs
    angle_accumulator = []
    force_accumulator = []
    
    try:
        while measurement_active:
            try:
                if decoder.serial_conn and decoder.serial_conn.in_waiting > 0:
                    bytes_to_read = min(decoder.serial_conn.in_waiting, 1024)
                    chunk = decoder.serial_conn.read(bytes_to_read)
                    
                    if chunk:
                        buffer += chunk.decode('utf-8', errors='ignore')
                        
                        while '\\n' in buffer:
                            line, buffer = buffer.split('\\n', 1)
                            parsed = decoder.parse_line(line)
                            
                            if parsed:
                                for data in parsed:
                                    # Accumuler les valeurs
                                    angle_accumulator.append({
                                        'angle': data['angle_deg'],
                                        'raw_angle': data['raw_angle']
                                    })
                                    force_accumulator.append({
                                        'force': data['force_kg'],
                                        'raw_force': data['raw_force']
                                    })
                                    
                                    # Si on a assez de valeurs, calculer la moyenne
                                    if len(angle_accumulator) >= averaging_window:
                                        avg_angle = sum([item['angle'] for item in angle_accumulator]) / len(angle_accumulator)
                                        avg_force = sum([item['force'] for item in force_accumulator]) / len(force_accumulator)
                                        avg_raw_angle = sum([item['raw_angle'] for item in angle_accumulator]) / len(angle_accumulator)
                                        avg_raw_force = sum([item['raw_force'] for item in force_accumulator]) / len(force_accumulator)
                                        
                                        measurement_point = {
                                            'timestamp': time.time() - start_time,
                                            'angle': round(avg_angle, 2),
                                            'force': round(avg_force, 3),
                                            'raw_angle': int(avg_raw_angle),
                                            'raw_force': int(avg_raw_force),
                                            'samples_count': len(angle_accumulator)
                                        }
                                        
                                        current_measurement.append(measurement_point)
                                        print(f"📊 Point: Angle={avg_angle:.2f}° Force={avg_force:.3f}kg")
                                        
                                        # Vider les accumulateurs
                                        angle_accumulator = []
                                        force_accumulator = []
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"⚠️ Erreur dans measurement_worker: {e}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"❌ Erreur critique dans measurement_worker: {e}")
    finally:
        decoder.disconnect()
        measurement_active = False

# Routes API (sans SocketIO)
@app.route('/')
def index():
    return render_template('index_simple.html')

@app.route('/api/ports/list')
def list_ports():
    ports = get_available_ports()
    return jsonify({
        'ports': ports,
        'current_port': decoder.port if decoder else None
    })

@app.route('/api/ports/select', methods=['POST'])
def select_port():
    global decoder, selected_port, measurement_active
    
    data = request.get_json()
    port = data.get('port')
    
    if not port:
        return jsonify({'error': 'Port non spécifié'}), 400
    
    if measurement_active:
        measurement_active = False
        time.sleep(0.5)
    
    success = initialize_decoder(port)
    if success:
        selected_port = port
        return jsonify({
            'success': True, 
            'message': f'Port {port} sélectionné',
            'port': port
        })
    else:
        return jsonify({
            'error': f'Impossible de se connecter au port {port}'
        }), 400

@app.route('/api/calibration/status')
def get_calibration_status():
    global decoder
    if not decoder:
        return jsonify({'error': 'Décodeur non initialisé'}), 500
    
    return jsonify({
        'angle_calibrated': decoder.calibration['angle']['calibrated'],
        'force_calibrated': decoder.calibration['force']['calibrated'],
        'calibration_data': decoder.calibration
    })

@app.route('/api/measurement/start', methods=['POST'])
def start_measurement():
    global measurement_active, measurement_thread, current_measurement
    
    if measurement_active:
        return jsonify({'error': 'Une mesure est déjà en cours'}), 400
    
    current_measurement = []
    measurement_active = True
    measurement_thread = threading.Thread(target=measurement_worker, daemon=True)
    measurement_thread.start()
    
    return jsonify({'success': True, 'message': 'Mesure démarrée'})

@app.route('/api/measurement/stop', methods=['POST'])
def stop_measurement():
    global measurement_active
    
    measurement_active = False
    
    return jsonify({
        'success': True, 
        'message': 'Mesure arrêtée',
        'data_points': len(current_measurement)
    })

@app.route('/api/measurement/data')
def get_measurement_data():
    return jsonify({
        'data': current_measurement,
        'active': measurement_active,
        'points': len(current_measurement)
    })

@app.route('/api/measurement/clear', methods=['POST'])
def clear_measurement():
    global current_measurement, measurement_active
    
    if measurement_active:
        measurement_active = False
        time.sleep(0.5)
    
    current_measurement = []
    return jsonify({'success': True, 'message': 'Mesure effacée'})

@app.route('/api/averaging/get')
def get_averaging_window():
    global averaging_window
    return jsonify({
        'averaging_window': averaging_window,
        'min_value': 1,
        'max_value': 100
    })

@app.route('/api/averaging/set', methods=['POST'])
def set_averaging_window():
    global averaging_window, angle_accumulator, force_accumulator
    
    data = request.get_json()
    new_window = data.get('window', 25)
    
    if not isinstance(new_window, int) or new_window < 1 or new_window > 100:
        return jsonify({'error': 'La fenêtre doit être un entier entre 1 et 100'}), 400
    
    averaging_window = new_window
    angle_accumulator = []
    force_accumulator = []
    
    return jsonify({
        'success': True, 
        'message': f'Fenêtre de moyennage définie à {new_window} valeurs',
        'averaging_window': averaging_window
    })

@app.route('/api/measurement/export/excel', methods=['POST'])
def export_to_excel():
    if not current_measurement:
        return jsonify({'error': 'Aucune donnée à exporter'}), 400
    
    try:
        df = pd.DataFrame(current_measurement)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Mesures MEVEM', index=False)
            
            metadata_df = pd.DataFrame({
                'Information': ['Date de mesure', 'Nombre de points', 'Durée (s)', 'Angle min (°)', 'Angle max (°)', 'Force min (kg)', 'Force max (kg)'],
                'Valeur': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    len(current_measurement),
                    round(max([p['timestamp'] for p in current_measurement]) if current_measurement else 0, 2),
                    round(min([p['angle'] for p in current_measurement]) if current_measurement else 0, 2),
                    round(max([p['angle'] for p in current_measurement]) if current_measurement else 0, 2),
                    round(min([p['force'] for p in current_measurement]) if current_measurement else 0, 3),
                    round(max([p['force'] for p in current_measurement]) if current_measurement else 0, 3)
                ]
            })
            metadata_df.to_excel(writer, sheet_name='Métadonnées', index=False)
        
        output.seek(0)
        filename = f"mevem_mesure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur export Excel: {str(e)}'}), 500

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    print("🌾 MEVEM - Mesure de la verse du maïs")
    print("=" * 50)
    
    if not initialize_decoder():
        print("⚠️ Mode démo activé")
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("🚀 Démarrage du serveur web...")
    print("📱 Interface disponible sur: http://127.0.0.1:5000")
    print("🔄 Ctrl+C pour arrêter")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\\n⏹️ Arrêt de l'application")
        global measurement_active
        measurement_active = False
        sys.exit(0)

if __name__ == '__main__':
    main()
'''
    
    return simple_app_content

def build_final():
    """Build final avec l'app simplifiée"""
    print("🔨 Construction de MEVEM - Version finale...")
    
    base_dir = Path(__file__).parent
    
    # Créer l'app simplifiée
    simple_app_content = create_simple_app()
    simple_app_file = base_dir / "app_simple.py"
    
    with open(simple_app_file, 'w') as f:
        f.write(simple_app_content)
    
    # Build avec PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=mevem",
        "--onefile",
        "--add-data=templates:templates",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl", 
        "--hidden-import=serial",
        "--hidden-import=serial.tools.list_ports",
        str(simple_app_file)
    ]
    
    try:
        result = subprocess.run(cmd, cwd=base_dir, check=True)
        
        print("✅ Build final terminé!")
        
        # Créer distribution finale
        dist_final = base_dir / "dist_final"
        if dist_final.exists():
            shutil.rmtree(dist_final)
        dist_final.mkdir()
        
        # Copier l'exécutable
        shutil.copy2(base_dir / "dist" / "mevem", dist_final / "mevem")
        os.chmod(dist_final / "mevem", 0o755)
        
        # Script de lancement
        launcher = """#!/bin/bash
echo "🌾 Démarrage de MEVEM - CRC Limagrain..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
"$DIR/mevem"
"""
        
        with open(dist_final / "start_mevem.sh", "w") as f:
            f.write(launcher)
        os.chmod(dist_final / "start_mevem.sh", 0o755)
        
        # README
        readme = """MEVEM - Mesure de la verse du maïs
Centre de recherche de Chappes (CRC) Limagrain

Version exécutable standalone - Fonctionne sans installation Python

Instructions:
1. Connectez votre capteur USB série
2. Lancez ./start_mevem.sh ou ./mevem
3. L'interface web s'ouvre automatiquement
4. Configurez le port série dans l'interface
5. Calibrez puis mesurez

Note: Cette version utilise un rafraîchissement manuel au lieu du temps réel.
"""
        
        with open(dist_final / "README.txt", "w") as f:
            f.write(readme)
        
        # Nettoyer
        simple_app_file.unlink()
        
        print(f"📁 MEVEM final créé dans: {dist_final}")
        print("🎉 Prêt à utiliser !")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = build_final() 
    sys.exit(0 if success else 1)