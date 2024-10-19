from kivy.app import App
import os
import json

# Standardwerte für die Einstellungen
default_pics = {
    "akira_images": "down",
    "car_images": "down",
    "bundesliga_images": "down",
    "own_landscape_images": "down",
    "tank_images": "down",
    "sexy_images": "down",
    "universe_images": "down",
    "random_images": "down"
}


# Einstellungen-Datei speichern
def save_pics_lists(updated_pics_list, state):
    print("Bilderlisten werden gespeichert.")
    app = App.get_running_app()
    pics_lists_file_path = app.get_pics_lists_file_path()
    pics_lists = load_pics_lists()
    with open(pics_lists_file_path, 'r+') as file:
        if updated_pics_list in pics_lists:
            pics_lists[updated_pics_list] = state
            print(f"Bilderlisten wurden geändert. {pics_lists}")
            json.dump(pics_lists, file, indent=4)
        else:
            print(f"Bilderliste ({updated_pics_list}) wurde nicht erkannt.")


# Einstellungen-Datei laden
def load_pics_lists():
    print("Bilderlisten werden geladen.")
    app = App.get_running_app()
    pics_lists_file_path = app.get_pics_lists_file_path()

    if os.path.exists(pics_lists_file_path):
        with open(pics_lists_file_path, "r+") as file:  # Öffnen zum Lesen und Schreiben
            try:
                pics_lists = json.load(file)
                # Überprüfen, ob alle Keys vorhanden sind
                for key in default_pics:
                    if key not in pics_lists:
                        print(f"{key} nicht gefunden, wird mit 'Default-Wert' ersetzt.")
                        pics_lists[key] = default_pics[key]

                # Datei zurück an den Anfang setzen und mit neuen Werten überschreiben
                file.seek(0)
                json.dump(pics_lists, file, indent=4)
                file.truncate()  # Restinhalt löschen, falls die neue Datei kleiner ist

                return pics_lists

            except json.JSONDecodeError:
                print("Fehler beim Laden der Einstellungen. Datei wird zurückgesetzt.")
                # Dateiinhalt zurücksetzen
                file.seek(0)
                json.dump(default_pics, file, indent=4)
                file.truncate()
                return default_pics
    else:
        print("Einstellungen nicht gefunden. Neue Datei wird erstellt.")
        with open(pics_lists_file_path, "w") as file:
            json.dump(default_pics, file, indent=4)
        return default_pics


def reset_selected_pics_lists():
    for pic_list in default_pics:
        save_pics_lists(pic_list, "down")
