# projekt_io
odpalanie - najpierw pip install -r requirements.txt (oraz requirements2.txt)
z cmd z poziomu katalogu głównego - python -m main

konieczne wpisanie komendy z poziomu /app w command line: winget install "FFmpeg (Essentials Build)"
sprawdź czy zostało pobrane - po wpisaniu komendy zamknij cmd i otwórz nowe
wejdź do poziomu aplikacji - /app najdalej i wpisz ffmpeg
jeęli pojawiają się informacje o rozszerzeniu - działa
//możliwy błąd do poprawy - ffmpeg czasem stwarza problemy i potrzebuje zmiany ścieżki - linijka 67 pliku recording.py w folderze backend - zamiast 'ffmpeg' trzeba będzie wpisać 'ffmpeg/bin/ffmpeg' (nie wiem od czego to zależy)
