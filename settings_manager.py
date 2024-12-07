from kivy.app import App
from kivy.utils import platform
import os
import json
import locale
from jnius import autoclass
import sys


def get_system_language():
    if platform == "android":
        auto_lang_func = autoclass("java.util.Locale")
        auto_language = auto_lang_func.getDefault().getLanguage()
        return auto_language
    else:
        auto_language = locale.getdefaultlocale()[0][:2]
        return auto_language


auto_lang = get_system_language()
supported_languages = ["en", "de"]
if auto_lang in supported_languages:
    system_lang = auto_lang
else:
    system_lang = "en"
print(f"SETTINGS SYS_LANG: {system_lang}")

# Standardwerte für die Einstellungen
default_settings = {
    "game_over_animation": "None",
    "card_flip_animation": "flip",
    "theme": "color",
    "touch_delay": 10,
    "ai_timeout": 1.2,
    "hide_cards_timeout": 1.0,
    "lang": system_lang
}


# Einstellungen-Datei speichern
def save_settings(new_setting):
    print(f"Einstellungen ({new_setting}) werden gespeichert.")
    app = App.get_running_app()
    settings_file_path = app.get_settings_file_path()
    with open(settings_file_path, 'r+') as file:
        try:
            settings = json.load(file)
            if new_setting[0] in settings:
                settings[new_setting[0]] = new_setting[1]
                print(f"Einstellungen wurden geändert. {settings}")
                file.seek(0)
                json.dump(settings, file, indent=4)
                file.truncate()
            else:
                print(f"New_Setting ({new_setting}) wurde nicht erkannt.")
        except json.JSONDecodeError:
            print("Fehler beim Laden der Einstellungen. Datei wird zurückgesetzt.")
            # Dateiinhalt zurücksetzen
            file.seek(0)
            json.dump(default_settings, file, indent=4)
            file.truncate()
            return default_settings


# Einstellungen-Datei laden
def load_settings():
    print("Einstellungen werden geladen.")
    app = App.get_running_app()
    settings_file_path = app.get_settings_file_path()

    if os.path.exists(settings_file_path):
        with open(settings_file_path, "r+") as file:  # Öffnen zum Lesen und Schreiben
            try:
                settings = json.load(file)
                # Überprüfen, ob alle Keys vorhanden sind
                for key in settings:
                    if key not in default_settings:
                        print(f"{key} nicht gefunden, wird mit 'Default-Wert' ersetzt.")
                        settings[key] = default_settings[key]

                # Datei zurück an den Anfang setzen und mit neuen Werten überschreiben
                file.seek(0)
                json.dump(settings, file, indent=4)
                file.truncate()  # Restinhalt löschen, falls die neue Datei kleiner ist

                return settings

            except json.JSONDecodeError:
                print("Fehler beim Laden der Einstellungen. Datei wird zurückgesetzt.")
                # Dateiinhalt zurücksetzen
                file.seek(0)
                json.dump(default_settings, file, indent=4)
                file.truncate()
                return default_settings
    else:
        print("Einstellungen nicht gefunden. Neue Datei wird erstellt.")
        with open(settings_file_path, "w") as file:
            json.dump(default_settings, file, indent=4)
        return default_settings


# Einstellungen zurück auf Standardwerte setzen
def reset_settings():
    print("Einstellungen werden auf Standardwerte zurückgesetzt.")
    app = App.get_running_app()
    settings_file_path = app.get_settings_file_path()
    with open(settings_file_path, "w") as file:
        json.dump(default_settings, file, indent=4)
    return default_settings
