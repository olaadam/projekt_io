from flask import Blueprint, Flask, jsonify, render_template, request
from .calendar_integration import get_calendar_events
import pygetwindow as gw
from threading import Thread
import time
from .recording import record_window, is_recording


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
def stop_recording():
    """Zatrzymaj nagrywanie."""
    global is_recording
    if is_recording:
        is_recording = False  # Zatrzymaj nagrywanie
        return jsonify({"message": "Nagrywanie zatrzymane."})
    return jsonify({"message": "Brak aktywnego nagrywania."}), 400


if __name__ == "__main__":
    main.run(debug=True)