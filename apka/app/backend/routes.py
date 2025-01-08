from flask import Blueprint, Flask, jsonify, render_template, current_app, request, send_from_directory
from .calendar_integration import get_calendar_events
import pygetwindow as gw
from .recording import record_window, start_recording_thread, stop_recording, save_recording, setup_upload_folder
import os
from werkzeug.utils import secure_filename

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


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'recordings')
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi'}

@main.route("/record_window", methods=["POST"])
def record_window_route():
    setup_upload_folder()
    data = request.get_json()
    window_title = data.get("window_title")

    if not window_title:
        return jsonify({"message": "Nie podano tytułu okna."}), 400

    # Uruchom nagrywanie w osobnym wątku
    start_recording_thread(window_title)

    return jsonify({"message": f"Rozpoczęto nagrywanie okna: {window_title}"})


@main.route("/stop_recording", methods=["POST"])
def stop_recording_route():
    try:
        stop_recording()
        return jsonify({"message": "Nagrywanie zakończone pomyślnie."})
    except Exception as e:
        return jsonify({"message": f"Błąd podczas zatrzymywania nagrywania: {str(e)}"}), 500


@main.route('/save', methods=['POST'])
def save_recording_route():
    """Zapisz nagranie i przekonwertuj na MP4."""
    try:
        file = request.files['file']
        title = request.form.get('title', 'recording')
        mp4_path = save_recording(file, title)
        return render_template('index.html', message="Nagranie zapisane!", path=mp4_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Nieoczekiwany błąd.', 'details': str(e)}), 500


@main.route('/my_recordings')
def show_recordings():
    setup_upload_folder()
    # Pobierz listę plików z folderu recordings
    recordings = os.listdir(UPLOAD_FOLDER)
    recordings = [f for f in recordings if f.endswith(('.mp4'))]  # Filtruj tylko pliki wideo
    recordings = [os.path.splitext(f)[0] for f in recordings]
    return render_template('my_recordings.html', recordings=recordings)


@main.route('/recordings/<filename>')
def get_recording(filename):
    try:
        file_extension = '.mp4'
        return send_from_directory(UPLOAD_FOLDER, filename + file_extension)
    except FileNotFoundError:
        return "File not found", 404


@main.route('/debug/recordings')
def debug_recordings():
    return str(os.listdir(UPLOAD_FOLDER))


if __name__ == "__main__":
    main.run(debug=True)
