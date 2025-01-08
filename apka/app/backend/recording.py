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

    # Ścieżka do pliku wav (audio)
    wav_path = os.path.join(UPLOAD_FOLDER, f"{title}.wav")
    # Ścieżka do pliku końcowego (mp4)
    mp4_path = os.path.join(UPLOAD_FOLDER, f"{title}.mp4")

    # Konwersja webm -> wav
    try:
        subprocess.run(
            ['ffmpeg', '-i', webm_path, '-vn', wav_path],  # '-vn' oznacza brak wideo
            check=True
        )
        logging.debug(f'Plik WAV zapisany: {wav_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Błąd podczas konwersji do WAV: {str(e)}')
        raise RuntimeError('Konwersja do WAV nie powiodła się.') from e

    # Konwersja wav -> mp4
    try:
        subprocess.run(
            ['ffmpeg', '-i', wav_path, '-i', webm_path,  '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', 
             '-c:v', 'libx264', '-c:a', 'aac', mp4_path],
            check=True
        )
        logging.debug(f'Plik MP4 zapisany: {mp4_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Błąd podczas konwersji do MP4: {str(e)}')
        raise RuntimeError('Konwersja do MP4 nie powiodła się.') from e

    # Usunięcie pliku .webm po konwersji
    os.remove(webm_path)

    if not os.path.exists(mp4_path):
        logging.error('Plik MP4 nie został utworzony.')
        raise RuntimeError('Nie udało się utworzyć pliku MP4.')

    # Zwrócenie ścieżek do plików
    return mp4_path, wav_path
