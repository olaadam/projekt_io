from flask import Blueprint, Flask, jsonify, render_template, request
from .calendar_integration import get_calendar_events
import pygetwindow as gw
from threading import Thread
import time
from .recording import record_window, stop_recording, convert_webm_to_mp4
import os
from flask import current_app, send_from_directory
from werkzeug.utils import secure_filename


main = Blueprint('main', __name__, template_folder="../frontend/templates", static_folder="../frontend/static")

# Trasa do serwowania strony głównej
@main.route("/")
def index():
    return render_template("index.html")

@main.route('/my_recordings')
def my_recordings():
    # Twoja logika obsługi strony z nagraniami
    return render_template('my_recordings.html')

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


# Trasa do zatrzymania nagrywania
@main.route("/stop_recording", methods=["POST"])
def stop_recording_route():
    """Zatrzymaj nagrywanie."""
    try:
        stop_recording()
        return jsonify({"message": "Nagrywanie zakończone pomyślnie."})
    except Exception as e:
        return jsonify({"message": f"Błąd podczas zatrzymywania nagrywania: {str(e)}"}), 500


UPLOAD_FOLDER = "recordings"
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.before_app_request
def setup_upload_folder():
    current_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


@main.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "Brak pliku w żądaniu."}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)  # Użycie current_app.config
        file.save(file_path)
        
        # Konwertowanie pliku WebM na MP4
        mp4_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{filename.rsplit('.', 1)[0]}.mp4")
        convert_webm_to_mp4(file_path, mp4_file_path)

        return jsonify({"message": "Plik zapisany i przekonwertowany na MP4!", "mp4_file": mp4_file_path})
    else:
        return jsonify({"message": "Zły typ pliku."}), 400


@main.route("/recordings")
def recordings():
    # Pobieranie listy plików z folderu uploadów
    files = os.listdir(UPLOAD_FOLDER)
    recordings = [file for file in files if file.endswith(".mp4")]  # Tylko pliki MP4
    return render_template("recordings.html", recordings=recordings)


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(main.root_path, 'uploads'), filename)


if __name__ == "__main__":
    main.run(debug=True)