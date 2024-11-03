import os
import shutil
import subprocess
import time

project_dir = os.path.expanduser("~/Python/Projekte/MeinMemory")
bin_dir = os.path.expanduser("~/Python/Projekte/MeinMemory/bin")
backup_dir = os.path.expanduser("~/Python/Projekte/Backups/MeinMemory/APK")
buildozer_path = os.path.expanduser("~/Python/Projekte/MeinMemory/.venv/bin/buildozer")
win_path = os.path.expanduser("/mnt/c/Users/Bagge/Documents/Android-Studio/APKs/MeinMemory")
dropbox_path = "/mnt/f/Dropbox/Dominik/Projects/PycharmProjects/MemoryApp"

if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

apk_file = None
apk_found = 0

print("Suche bestehende APKs, um sie zu sichern.")

for file_name in os.listdir(bin_dir):
    if file_name.endswith(".apk"):
        apk_file = file_name
        # APK verschieben
        apk_path = os.path.join(bin_dir, apk_file)
        backup_apk_path = os.path.join(backup_dir, apk_file)
        shutil.move(apk_path, backup_apk_path)
        print(f"Backup erstellt: {backup_apk_path}")
        apk_found += 1

if apk_found == 0:
    print("keine APK-Datei im 'bin'-Ordner gefunden.")
elif apk_found == 1:
    print(f"Es wurde eine APK gesichert.")
else:
    print(f"Es wurden {apk_found} APKs gesichert.")

try:
    subprocess.run([buildozer_path, "android", "debug"], cwd=project_dir, check=True)
    print("Neue APK wurde erfolgreich erstellt und wird in das Windows-Verzeichnis kopiert.")

except subprocess.CalledProcessError as e:
    print(f"Fehler beim Erstellen der APK: {e}.")
except FileNotFoundError as e:
    print(f"Buildozer nicht gefunden: {e}.")


apk_found = 0

for file_name in os.listdir(bin_dir):
    if file_name.endswith(".apk"):
        apk_file = file_name
        apk_path = os.path.join(bin_dir, apk_file)

        # Für AndroidStudio auf Windows
        shutil.copy(apk_path, win_path)
        apk_found += 1
        print(f"Neue APK ({apk_file}) wurde in das Verzeichnis {win_path} kopiert.")

        # Dropbox hochladen
        shutil.copy(apk_path, dropbox_path)
        print(f"APK wurde in das Dropbox-Verzeichnis ({dropbox_path}) hochgeladen.")

if apk_found == 0:
    print("Fehler, es wurde keine neue APK-Datei gefunden.")

# Der vollständige Package-Name der installierten Dropbox-Anwendung
dropbox_package_name = "C:/Program Files/WindowsApps/"

# PowerShell-Befehl zum Beenden von Dropbox
stop_command = 'Stop-Process -Name Dropbox'

# PowerShell-Befehl zum Starten von Dropbox über explorer.exe
start_command = 'Start-Process "C:\Program Files\WindowsApps\DropboxInc.Dropbox_211.4.6008.0_x64__xbfy0k16fey96\Dropbox.exe"'

# PowerShell über subprocess steuern
print("Dropbox wird beendet...")
subprocess.run(["powershell.exe", "-Command", stop_command])

print("Warte...")
time.sleep(2)

print("Dropbox wird gestartet...")
subprocess.run(["powershell.exe", "-Command", start_command])
print("Dropbox sollte wieder laufen und die neue APK hochladen")
