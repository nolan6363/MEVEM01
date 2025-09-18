#!/usr/bin/env python3
"""
Application Flask pour MEVEM - Mesure de la verse du maïs
Interface web pour capteurs angle/force avec communication série
"""

import json
import threading
import time
import webbrowser
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import pandas as pd
import os
import sys
import serial.tools.list_ports
from main import CalibratedSensorDecoder
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mevem_secret_2024'
# Configuration SocketIO compatible PyInstaller
import os
# Configuration SocketIO - mode simple pour PyInstaller
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

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
    """Worker thread pour la mesure en continu"""
    global current_measurement, measurement_active, decoder
    global averaging_window, angle_accumulator, force_accumulator
    
    if not decoder.connect():
        socketio.emit('error', {'message': 'Impossible de se connecter au capteur'})
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
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
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
                                        
                                        # Envoyer les données en temps réel
                                        socketio.emit('measurement_data', measurement_point)
                                        
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

@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')

@app.route('/api/ports/list')
def list_ports():
    """Lister les ports série disponibles"""
    ports = get_available_ports()
    return jsonify({
        'ports': ports,
        'current_port': decoder.port if decoder else None
    })

@app.route('/api/ports/select', methods=['POST'])
def select_port():
    """Sélectionner un port série"""
    global decoder, selected_port
    
    data = request.get_json()
    port = data.get('port')
    
    if not port:
        return jsonify({'error': 'Port non spécifié'}), 400
    
    # Arrêter toute mesure en cours
    global measurement_active
    if measurement_active:
        measurement_active = False
        time.sleep(0.5)
    
    # Initialiser avec le nouveau port
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
    """Obtenir le statut de calibration"""
    global decoder
    if not decoder:
        return jsonify({'error': 'Décodeur non initialisé'}), 500
    
    return jsonify({
        'angle_calibrated': decoder.calibration['angle']['calibrated'],
        'force_calibrated': decoder.calibration['force']['calibrated'],
        'calibration_data': decoder.calibration
    })

@app.route('/api/calibration/start', methods=['POST'])
def start_calibration():
    """Démarrer la calibration"""
    global decoder
    if not decoder:
        return jsonify({'error': 'Décodeur non initialisé'}), 500
    
    try:
        # Démarrer la calibration dans un thread séparé
        threading.Thread(target=decoder.calibrate_sensor, daemon=True).start()
        return jsonify({'success': True, 'message': 'Calibration démarrée'})
    except Exception as e:
        return jsonify({'error': f'Erreur calibration: {str(e)}'}), 500

@app.route('/api/measurement/start', methods=['POST'])
def start_measurement():
    """Démarrer une mesure"""
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
    """Arrêter la mesure"""
    global measurement_active
    
    measurement_active = False
    
    return jsonify({
        'success': True, 
        'message': 'Mesure arrêtée',
        'data_points': len(current_measurement)
    })

@app.route('/api/measurement/data')
def get_measurement_data():
    """Obtenir les données de la mesure actuelle"""
    return jsonify({
        'data': current_measurement,
        'active': measurement_active,
        'points': len(current_measurement)
    })

@app.route('/api/measurement/clear', methods=['POST'])
def clear_measurement():
    """Effacer la mesure actuelle"""
    global current_measurement, measurement_active
    
    if measurement_active:
        measurement_active = False
        time.sleep(0.5)  # Laisser le temps au thread de s'arrêter
    
    current_measurement = []
    
    return jsonify({'success': True, 'message': 'Mesure effacée'})

@app.route('/api/averaging/get')
def get_averaging_window():
    """Obtenir la fenêtre de moyennage actuelle"""
    global averaging_window
    return jsonify({
        'averaging_window': averaging_window,
        'min_value': 1,
        'max_value': 100
    })

@app.route('/api/averaging/set', methods=['POST'])
def set_averaging_window():
    """Définir la fenêtre de moyennage"""
    global averaging_window, angle_accumulator, force_accumulator
    
    data = request.get_json()
    new_window = data.get('window', 10)
    
    if not isinstance(new_window, int) or new_window < 1 or new_window > 100:
        return jsonify({'error': 'La fenêtre doit être un entier entre 1 et 100'}), 400
    
    averaging_window = new_window
    
    # Vider les accumulateurs si on change pendant une mesure
    angle_accumulator = []
    force_accumulator = []
    
    return jsonify({
        'success': True, 
        'message': f'Fenêtre de moyennage définie à {new_window} valeurs',
        'averaging_window': averaging_window
    })

@app.route('/api/measurement/export/excel', methods=['POST'])
def export_to_excel():
    """Exporter les données vers Excel"""
    if not current_measurement:
        return jsonify({'error': 'Aucune donnée à exporter'}), 400

    try:
        # Récupérer les données de la requête
        data = request.get_json() if request.is_json else {}
        variety = data.get('variety', '').strip()
        sample_number = data.get('sample_number', 1)
        custom_filename = data.get('filename', '').strip()

        # Créer un DataFrame pandas
        df = pd.DataFrame(current_measurement)

        # Créer un buffer en mémoire
        output = io.BytesIO()

        # Calculer les statistiques
        forces = [p['force'] for p in current_measurement]
        angles = [p['angle'] for p in current_measurement]
        timestamps = [p['timestamp'] for p in current_measurement]

        max_force = max(forces) if forces else 0
        max_force_index = forces.index(max_force) if forces else 0
        angle_at_max_force = angles[max_force_index] if angles else 0

        # Écrire le fichier Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Mesures MEVEM', index=False)

            # Ajouter des informations de métadonnées enrichies
            metadata_info = [
                'Date de mesure', 'Variété', 'Échantillon', 'Nombre de points',
                'Durée (s)', 'Angle min (°)', 'Angle max (°)',
                'Force min (kg)', 'Force max (kg)', 'Angle à force max (°)'
            ]
            metadata_values = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                variety or 'Non spécifiée',
                sample_number,
                len(current_measurement),
                round(max(timestamps) - min(timestamps) if timestamps else 0, 2),
                round(min(angles) if angles else 0, 2),
                round(max(angles) if angles else 0, 2),
                round(min(forces) if forces else 0, 3),
                round(max_force, 3),
                round(angle_at_max_force, 2)
            ]

            metadata_df = pd.DataFrame({
                'Information': metadata_info,
                'Valeur': metadata_values
            })
            metadata_df.to_excel(writer, sheet_name='Métadonnées', index=False)

        output.seek(0)

        # Nom du fichier intelligent
        if custom_filename:
            filename = f"{custom_filename}.xlsx"
        elif variety:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{variety}_ech{sample_number}_{timestamp}.xlsx"
        else:
            filename = f"mevem_mesure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Créer le dossier de la variété si nécessaire
        if variety:
            variety_dir = os.path.join('exports', variety)
            os.makedirs(variety_dir, exist_ok=True)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': f'Erreur export Excel: {str(e)}'}), 500

@app.route('/api/calibration/save', methods=['POST'])
def save_calibration():
    """Sauvegarder une nouvelle calibration"""
    global decoder
    if not decoder:
        return jsonify({'error': 'Décodeur non initialisé'}), 500

    try:
        data = request.get_json()
        angle_data = data.get('angle', {})
        force_data = data.get('force', {})

        # Mettre à jour la calibration
        decoder.calibration['angle'].update({
            'raw_min': angle_data.get('raw_min'),
            'raw_max': angle_data.get('raw_max'),
            'real_min': angle_data.get('real_min', 0.0),
            'real_max': angle_data.get('real_max', 45.0),
            'calibrated': True
        })

        decoder.calibration['force'].update({
            'raw_min': force_data.get('raw_min'),
            'raw_max': force_data.get('raw_max'),
            'real_min': force_data.get('real_min', 0.0),
            'real_max': force_data.get('real_max', 1.0),
            'calibrated': True
        })

        # Sauvegarder la calibration
        decoder.save_calibration()

        return jsonify({
            'success': True,
            'message': 'Calibration sauvegardée avec succès'
        })

    except Exception as e:
        return jsonify({'error': f'Erreur sauvegarde calibration: {str(e)}'}), 500

@app.route('/api/sensor/read_current', methods=['POST'])
def read_current_values():
    """Lire les valeurs actuelles du capteur"""
    global decoder
    if not decoder:
        return jsonify({'error': 'Décodeur non initialisé'}), 500

    try:
        # Lire les valeurs pendant 2 secondes
        angle_value, force_value = decoder.read_current_values(duration=2)

        if angle_value is not None and force_value is not None:
            return jsonify({
                'success': True,
                'angle': round(angle_value, 1),
                'force': round(force_value, 1)
            })
        else:
            return jsonify({'error': 'Impossible de lire les valeurs du capteur'}), 500

    except Exception as e:
        return jsonify({'error': f'Erreur lecture capteur: {str(e)}'}), 500

@app.route('/api/variety/stats', methods=['POST'])
def export_variety_stats():
    """Exporter les statistiques d'une variété (compilation de 5 échantillons)"""
    try:
        data = request.get_json()
        variety = data.get('variety', '').strip()

        if not variety:
            return jsonify({'error': 'Variété non spécifiée'}), 400

        # Chercher les fichiers de la variété dans le dossier exports
        variety_dir = os.path.join('exports', variety)
        if not os.path.exists(variety_dir):
            return jsonify({'error': f'Aucune donnée trouvée pour la variété {variety}'}), 404

        # Collecter les données des échantillons
        sample_stats = []

        for i in range(1, 6):  # Échantillons 1 à 5
            # Chercher les fichiers d'échantillon (pattern : variety_ech{i}_*.xlsx)
            pattern = f"{variety}_ech{i}_"
            sample_files = [f for f in os.listdir(variety_dir) if f.startswith(pattern) and f.endswith('.xlsx')]

            if sample_files:
                # Prendre le fichier le plus récent pour cet échantillon
                latest_file = max(sample_files, key=lambda x: os.path.getctime(os.path.join(variety_dir, x)))
                file_path = os.path.join(variety_dir, latest_file)

                # Lire les métadonnées du fichier Excel
                try:
                    metadata_df = pd.read_excel(file_path, sheet_name='Métadonnées')
                    metadata_dict = dict(zip(metadata_df['Information'], metadata_df['Valeur']))

                    sample_stats.append({
                        'echantillon': i,
                        'fichier': latest_file,
                        'force_max_kg': metadata_dict.get('Force max (kg)', 0),
                        'angle_force_max_deg': metadata_dict.get('Angle à force max (°)', 0),
                        'date_mesure': metadata_dict.get('Date de mesure', ''),
                        'nb_points': metadata_dict.get('Nombre de points', 0),
                        'duree_s': metadata_dict.get('Durée (s)', 0)
                    })
                except Exception as e:
                    print(f"Erreur lecture fichier {latest_file}: {e}")

        if len(sample_stats) < 2:
            return jsonify({'error': f'Pas assez de données pour {variety} (minimum 2 échantillons requis)'}), 400

        # Créer le fichier de statistiques
        stats_df = pd.DataFrame(sample_stats)

        # Calculer les statistiques globales
        forces = [s['force_max_kg'] for s in sample_stats]
        angles = [s['angle_force_max_deg'] for s in sample_stats]

        summary_stats = {
            'Variété': variety,
            'Nombre échantillons': len(sample_stats),
            'Force max moyenne (kg)': round(sum(forces) / len(forces), 3),
            'Force max médiane (kg)': round(sorted(forces)[len(forces)//2], 3),
            'Force max min (kg)': round(min(forces), 3),
            'Force max max (kg)': round(max(forces), 3),
            'Angle moyen à force max (°)': round(sum(angles) / len(angles), 1),
            'Écart-type force (kg)': round((sum([(f - sum(forces)/len(forces))**2 for f in forces]) / len(forces))**0.5, 3),
            'Date compilation': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Créer le fichier Excel de statistiques
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Feuille de résumé
            summary_df = pd.DataFrame([summary_stats])
            summary_df.to_excel(writer, sheet_name='Résumé', index=False)

            # Feuille de détail par échantillon
            stats_df.to_excel(writer, sheet_name='Détail échantillons', index=False)

        output.seek(0)
        filename = f"{variety}_statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': f'Erreur export statistiques: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Connexion WebSocket"""
    print('Client connecté')
    emit('connected', {'message': 'Connexion établie'})

@socketio.on('disconnect')
def handle_disconnect():
    """Déconnexion WebSocket"""
    print('Client déconnecté')

def open_browser():
    """Ouvrir le navigateur automatiquement"""
    time.sleep(1.5)  # Laisser le temps au serveur de démarrer
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Fonction principale"""
    print("🌽 MEVEM - Mesure de la verse du maïs")
    print("=" * 50)

    # Créer le dossier exports s'il n'existe pas
    os.makedirs('exports', exist_ok=True)

    # Initialiser le décodeur
    if not initialize_decoder():
        print("⚠️ Mode démo activé")
    
    # Ouvrir le navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Démarrer l'application
    print("🚀 Démarrage du serveur web...")
    print("📱 Interface disponible sur: http://127.0.0.1:5000")
    print("🔄 Ctrl+C pour arrêter")
    
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt de l'application")
        global measurement_active
        measurement_active = False
        sys.exit(0)

if __name__ == '__main__':
    main()
