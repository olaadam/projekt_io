import os
import logging
import pytz
import subprocess
from datetime import datetime
from threading import Thread
import time

# Globalna zmienna dla wątku nagrywania
recording_thread = None
recording_active = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'recordings')
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi'}

def setup_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def record_window(window_title):
    """Rozpoczyna nagrywanie okna."""
    global recording_active
    recording_active = True
    while recording_active:
        logging.debug(f"Nagrywam okno: {window_title}")
        time.sleep(1)  


def start_recording_thread(window_title):
    """Uruchamia nagrywanie okna w osobnym wątku."""
    thread = Thread(target=record_window, args=(window_title,))
    thread.start()


def stop_recording():
    global recording_active
    recording_active = False
    

def save_recording(file, title=None):
    if not file or file.filename == '':
        raise ValueError('Nie przekazano żadnego pliku!')

    # Ustal tytuł pliku, jeśli nie podano
    if not title:
        tz = pytz.timezone('Europe/Warsaw')
        now = datetime.now(tz)
        date_part = now.strftime("%Y-%m-%d")
        time_part = now.strftime("%H-%M-%S")
        title = f"{date_part}_{time_part}"

    logging.debug(f'Plik: {file.filename}, Tytuł: {title}')

    # Ścieżka do pliku tymczasowego (webm)
    webm_path = os.path.join(UPLOAD_FOLDER, f"{title}.webm")
    file.save(webm_path)

    # Ścieżka do pliku końcowego (mp4)
    mp4_path = os.path.join(UPLOAD_FOLDER, f"{title}.mp4")

    # Konwersja do MP4
    try:
        subprocess.run(
            ['ffmpeg', '-i', webm_path, '-c:v', 'libx264', '-c:a', 'aac', mp4_path],
            check=True
        )
        # Usunięcie pliku .webm po konwersji
        os.remove(webm_path)
    except subprocess.CalledProcessError as e:
        logging.error(f'Błąd podczas konwersji pliku: {str(e)}')
        raise RuntimeError('Konwersja do MP4 nie powiodła się.') from e
    except Exception as e:
        logging.error(f'Nieoczekiwany błąd podczas konwersji pliku: {str(e)}')
        raise RuntimeError('Nieoczekiwany błąd podczas konwersji.') from e

    if not os.path.exists(mp4_path):
        logging.error('Plik MP4 nie został utworzony.')
        raise RuntimeError('Nie udało się utworzyć pliku MP4.')

    return mp4_path
