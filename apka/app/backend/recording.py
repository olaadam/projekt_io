import threading
import time
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw

is_recording = False
record_thread = None

def record_window(window_title):
    global is_recording, record_thread

    if is_recording:
        raise Exception("Nagrywanie już w toku.")

    is_recording = True

    # Znajdź okno o podanym tytule
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
    except IndexError:
        raise Exception("Nie znaleziono okna o podanym tytule.")

    # Funkcja do nagrywania okna
    def record():
        bbox = (window.left, window.top, window.right, window.bottom)  # Współrzędne okna
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (window.width, window.height))

        while is_recording:
            img = ImageGrab.grab(bbox=bbox)  # Przechwycenie obszaru okna
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()

    record_thread = threading.Thread(target=record)
    record_thread.start()

def stop_recording():
    global is_recording
    if not is_recording:
        raise Exception("Nagrywanie nie zostało jeszcze rozpoczęte.")

    is_recording = False
    record_thread.join()  # Czekaj na zakończenie nagrywania
