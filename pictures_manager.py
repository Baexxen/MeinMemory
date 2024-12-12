from kivy.app import App
import os
import json

# Standardwerte für die Einstellungen
default_pics = {
    "akira_images": "normal",
    "car_images": "down",
    "sport_images": "down",
    "own_landscape_images": "normal",
    "sexy_images": "normal",
    "random_images": "down",
    "nature_images": "down"
}


# Einstellungen-Datei speichern
def save_pics_lists(checkboxes):
    app = App.get_running_app()
    pics_lists_file_path = app.get_pics_lists_file_path()
    with open(pics_lists_file_path, 'r+') as file:
        try:
            file.seek(0)
            json.dump(checkboxes, file, indent=4)
            file.truncate()
        except json.JSONDecodeError:
            print("Fehler beim Speichern der Bilder 'json' Datei. Datei wird zurückgesetzt.")
            # Dateiinhalt zurücksetzen
            file.seek(0)
            json.dump(default_pics, file, indent=4)
            file.truncate()


# Einstellungen-Datei laden
def load_pics_lists():
    app = App.get_running_app()
    pics_lists_file_path = app.get_pics_lists_file_path()

    if os.path.exists(pics_lists_file_path):
        with open(pics_lists_file_path, "r+") as file:  # Öffnen zum Lesen und Schreiben
            try:
                error = 0
                pics_lists = json.load(file)
                # Überprüfen, ob alle Keys vorhanden sind
                for key in default_pics:
                    if key not in pics_lists:
                        print(f"{key} nicht gefunden, wird mit 'Default-Wert' ersetzt.")
                        pics_lists[key] = default_pics[key]
                        error += 1
                if error > 0:
                    file.seek(0)
                    json.dump(default_pics, file, indent=4)
                    file.truncate()
                    pics_lists = default_pics
                else:
                    file.seek(0)
                    json.dump(pics_lists, file, indent=4)
                    file.truncate()  # Restinhalt löschen, falls die neue Datei kleiner ist

                return pics_lists

            except json.JSONDecodeError:
                print("Fehler beim Laden der Bilder 'json' Datei. Datei wird zurückgesetzt.")
                # Dateiinhalt zurücksetzen
                file.seek(0)
                json.dump(default_pics, file, indent=4)
                file.truncate()
                return default_pics
    else:
        print("Bilder 'json' Datei nicht gefunden. Neue Datei wird erstellt.")
        with open(pics_lists_file_path, "w") as file:
            json.dump(default_pics, file, indent=4)
        return default_pics


def reset_selected_pics_lists():
    app = App.get_running_app()
    pics_lists_file_path = app.get_pics_lists_file_path()

    if os.path.exists(pics_lists_file_path):
        with open(pics_lists_file_path, "r+") as file:  # Öffnen zum Lesen und Schreiben
            file.seek(0)
            json.dump(default_pics, file, indent=4)
            file.truncate()

    return default_pics
