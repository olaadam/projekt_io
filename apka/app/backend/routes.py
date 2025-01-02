from flask import Blueprint, Flask, jsonify, render_template, request, current_app, send_from_directory
from .calendar_integration import get_calendar_events
import pygetwindow as gw
from threading import Thread
import time
from .recording import record_window, stop_recording
import os
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import pytz
from moviepy.video.io.VideoFileClip import VideoFileClip
import subprocess
import ffmpeg

main = Blueprint('main', __name__, template_folder="../frontend/templates", static_folder="../frontend/static")

# Trasa do serwowania strony głównej
@main.route("/")
def index():
    return render_template("index.html")

@main.route('/events')
def events():
    try:
        events = get_calendar_events()
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/ms-calendar")
def ms_calendar():
    try:
        # Zastąp odpowiednimi wartościami
        client_id = "your_client_id"
        tenant_id = "your_tenant_id"
        client_secret = "your_client_secret"
        token = "access_token"

        events = get_ms_calendar_events(client_id, tenant_id, client_secret, token)
        return {"events": events}
    except Exception as e:
        return {"error": str(e)}, 400

@main.route("/list_windows", methods=["GET"])
def list_windows():
    """Zwróć listę okien."""
    windows = gw.getAllTitles()
    windows = [w for w in windows if w]
    return jsonify(windows)

@main.route("/record_window", methods=["POST"])
def record_window_route():
    """Rozpocznij nagrywanie wybranego okna."""
    data = request.get_json()
    window_title = data.get("window_title")

    if not window_title:
        return jsonify({"message": "Nie podano tytułu okna."}), 400

    # Uruchom nagrywanie w osobnym wątku
    thread = Thread(target=record_window, args=(window_title,))
    thread.start()

    return jsonify({"message": f"Rozpoczęto nagrywanie okna: {window_title}"})

@main.route("/stop_recording", methods=["POST"])
def stop_recording_route():
    """Zatrzymaj nagrywanie."""
    try:
        stop_recording()
        return jsonify({"message": "Nagrywanie zakończone pomyślnie."})
    except Exception as e:
        return jsonify({"message": f"Błąd podczas zatrzymywania nagrywania: {str(e)}"}), 500

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'recordings')
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.before_app_request
def setup_upload_folder():
    current_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(level=logging.DEBUG)

@main.route('/save', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logging.error('Brak pliku w żądaniu')
            return 'Brak pliku w żądaniu', 400
        
        file = request.files['file']
        title = request.form.get('title')
        if not title:
            tz = pytz.timezone('Europe/Warsaw')
            now = datetime.now(tz)
            date_part = now.strftime("%Y-%m-%d")  
            time_part = now.strftime("%H-%M-%S")  
            title = f"{date_part}_{time_part}"
        logging.debug(f'Plik: {file.filename}, Tytuł: {title}')
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(UPLOAD_FOLDER, f"{title}.webm")
            file.save(file_path)
            logging.info(f'Plik zapisany: {file_path}')
            return 'Plik zapisany pomyślnie', 200
        else:
            logging.error('Niedozwolony typ pliku')
            return 'Błąd: niedozwolony typ pliku', 400
    except Exception as e:
        logging.error(f'Błąd: {str(e)}')
        return f'Błąd przy zapisywaniu pliku: {str(e)}', 500

@main.route('/my_recordings')
def show_recordings():
    # Pobierz listę plików z folderu recordings
    recordings = os.listdir(UPLOAD_FOLDER)
    recordings = [f for f in recordings if f.endswith(('.mp4', '.webm', '.mov', '.avi'))]  # Filtruj tylko pliki wideo
    return render_template('my_recordings.html', recordings=recordings)

@main.route('/recordings/<filename>')
def get_recording(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return "File not found", 404

@main.route('/debug/recordings')
def debug_recordings():
    return str(os.listdir(UPLOAD_FOLDER))

@main.route('/convert/<filename>')
def convert_file(filename):
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, filename.rsplit('.', 1)[0] + '.mp4')
    file_extension = filename.split('.')[-1].lower()

    if not os.path.exists(input_path):
        logging.error(f"Plik wejściowy nie istnieje: {input_path}")
        return "File not found", 404
    if file_extension == 'mp4':
        # Jeśli plik jest MP4, nie konwertujemy go
        return send_from_directory(UPLOAD_FOLDER, filename)

    try:
        logging.info(f"Rozpoczynanie konwersji: {input_path} -> {output_path}")
        subprocess.run(['ffmpeg', '-y','-i', input_path, output_path], check=True)
        logging.info(f"Plik przekonwertowany: {output_path}")
        return send_from_directory(UPLOAD_FOLDER, os.path.basename(output_path))
    except subprocess.CalledProcessError as e:
        logging.error(f"Błąd konwersji pliku: {e}")
        return f"Błąd konwersji: {e}", 500
    except Exception as e:
        # Logowanie innych błędów
        logging.error(f"Nieoczekiwany błąd: {e}")
        return "An unexpected error occurred", 500
        
if __name__ == "__main__":
    main.run(debug=True)
