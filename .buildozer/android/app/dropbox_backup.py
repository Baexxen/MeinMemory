import os
import shutil
import subprocess
import time

project_dir = os.path.expanduser("~/Python/Projekte/MeinMemory")
pics_dir = os.path.expanduser("~/Python/Projekte/MeinMemory/pics")
dropbox_path = "/mnt/f/Dropbox/Dominik/Projects/PycharmProjects/MemoryApp/source_backup"
dropbox_pics_path = "/mnt/f/Dropbox/Dominik/Projects/PycharmProjects/MemoryApp/source_backup/pics"

py_file = None
py_path = None
py_found = 0

for file_name in os.listdir(project_dir):
    if file_name.endswith(".py"):
        py_file = file_name
        py_path = os.path.join(project_dir, py_file)

        # Auf Dropbox kopieren
        shutil.copy(py_path, dropbox_path)
        py_found += 1
        print(f"'.py' ({py_file}) wurde in das Verzeichnis {dropbox_path} kopiert.")

if py_found == 0:
    print("Fehler, es wurde keine '.py' Datei gefunden.")

kv_file = None
kv_path = None
kv_found = 0

spec_file = None
spec_path = None
spec_found = 0

for file_name in os.listdir(project_dir):
    if file_name.endswith(".kv"):
        kv_file = file_name
        kv_path = os.path.join(project_dir, kv_file)

        # Auf Dropbox kopieren
        shutil.copy(kv_path, dropbox_path)
        kv_found += 1
        print(f"'.kv' ({kv_file}) wurde in das Verzeichnis {dropbox_path} kopiert.")

    elif file_name.endswith(".spec"):
        spec_file = file_name
        spec_path = os.path.join(project_dir, spec_file)
        shutil.copy(spec_path, dropbox_path)
        spec_found += 1
        print(f"'.spec' ({spec_file}) wurde in das Verzeichnis {dropbox_path} kopiert.")

if kv_found == 0:
    print("Fehler, es wurde keine '.kv' Datei gefunden.")
if spec_found == 0:
    print("Fehler, es wurde keine '.spec' Datei gefunden.")

png_file = None
png_path = None
png_found = 0
ico_file = None
ico_path = None
ico_found = 0

for file_name in os.listdir(pics_dir):
    if file_name.endswith(".png"):
        png_file = file_name
        png_path = os.path.join(pics_dir, png_file)
        shutil.copy(png_path, dropbox_pics_path)
        png_found += 1
        print(f"{png_file} wurde in das Verzeichnis {dropbox_pics_path} kopiert.")

    elif file_name.endswith(".ico"):
        ico_file = file_name
        ico_path = os.path.join(pics_dir, ico_file)
        shutil.copy(ico_path, dropbox_pics_path)
        ico_found += 1
        print(f"{ico_file} wurde in das Verzeichnis {dropbox_pics_path} kopiert.")

if png_found == 0:
    print("Fehler, es wurde keine '.png' Datei gefunden.")
if ico_found == 0:
    print("Fehler, es wurde keine '.ico' Datei gefunden.")

# PowerShell-Befehl zum Beenden von Dropbox
stop_command = 'Stop-Process -Name Dropbox'

# PowerShell-Befehl zum Starten von Dropbox über explorer.exe
start_command = 'Start-Process "C:/Program Files/WindowsApps/DropboxInc.Dropbox_208.4.5824.0_x64__xbfy0k16fey96/Dropbox.exe"'

# PowerShell über subprocess steuern
print("Dropbox wird beendet...")
subprocess.run(["powershell.exe", "-Command", stop_command])

print("Warte...")
time.sleep(2)

print("Dropbox wird gestartet...")
subprocess.run(["powershell.exe", "-Command", start_command])
print("Dropbox sollte wieder laufen und die py Dateien uploaden")