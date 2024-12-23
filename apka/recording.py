import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import time
import os

def list_windows():
    """Wyświetla listę dostępnych okien."""
    windows = gw.getAllTitles()
    windows = [w for w in windows if w]  # Usuń puste tytuły
    print("Dostępne okna:")
    for idx, title in enumerate(windows):
        print(f"{idx + 1}: {title}")
    return windows

def record_window(window_title, duration, output_path="output.mp4"):
    """
    Nagrywa wybrane okno.

    :param window_title: Tytuł okna do nagrania.
    :param duration: Czas nagrywania w sekundach.
    :param output_path: Ścieżka do pliku wynikowego.
    """
    # Pobierz okno na podstawie tytułu
    window = gw.getWindowsWithTitle(window_title)
    if not window:
        print(f"Nie znaleziono okna o tytule: {window_title}")
        return
    window = window[0]

    # Pobierz współrzędne okna
    left, top, width, height = window.left, window.top, window.width, window.height
    print(f"Nagrane okno: {window_title}, wymiary: {width}x{height}")

    # Ustawienia nagrywania
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

    print(f"Nagrywanie okna przez {duration} sekund...")
    start_time = time.time()
    while time.time() - start_time < duration:
        # Zrób screenshot okna
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()
    print(f"Zakończono nagrywanie. Zapisano do {output_path}")

if __name__ == "__main__":
    # Przykład użycia
    windows = list_windows()
    selected_window = input("Wybierz okno (podaj nazwę): ")
    record_window(selected_window, duration=10, output_path="nagranie.mp4")
