import threading
import ffmpeg
import time

# Globalna zmienna dla wątku nagrywania
recording_thread = None
recording_active = False

def record_window(window_title):
    global recording_active
    recording_active = True
    while recording_active:
        # Logika nagrywania okna (np. zrzuty ekranu, dźwięk itp.)
        time.sleep(1)  # Placeholder dla logiki nagrywania

def stop_recording():
    global recording_active
    recording_active = False
    if recording_thread:
        recording_thread.join()  # Poczekaj na zakończenie wątku


def convert_webm_to_mp4(webm_file_path, mp4_file_path):
    """
    Funkcja do konwersji pliku WebM na MP4 za pomocą FFmpeg.
    
    :param webm_file_path: Ścieżka do pliku WebM
    :param mp4_file_path: Ścieżka, gdzie zapisany będzie plik MP4
    """
    try:
        # Użycie FFmpeg do konwersji pliku
        ffmpeg.input(webm_file_path).output(mp4_file_path).run()
        print(f"Plik {webm_file_path} został pomyślnie przekonwertowany na {mp4_file_path}")
    except ffmpeg.Error as e:
        print(f"Podczas konwersji wystąpił błąd: {e}")