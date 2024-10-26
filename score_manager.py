from kivy.app import App
import os
import json

# Standardwerte für die Highscores
default_scores = {
    "standard_easy_small": 777,
    "standard_easy_medium": 888,
    "standard_easy_big": 999,
    "battle_easy_small": 0,
    "battle_easy_medium": 0,
    "battle_easy_big": 0,
    "battle_medium_small": 0,
    "battle_medium_medium": 0,
    "battle_medium_big": 0,
    "battle_hard_small": 0,
    "battle_hard_medium": 0,
    "battle_hard_big": 0,
    "battle_impossible_small": 0,
    "battle_impossible_medium": 0,
    "battle_impossible_big": 0,
    "time_race_easy_small": 997,
    "time_race_easy_medium": 998,
    "time_race_easy_big": 999
}


# Highscore-Datei speichern
def save_best_scores(highscores):
    print("save_best_scores")
    app = App.get_running_app()
    score_file_path = app.get_score_file_path()
    with open(score_file_path, 'w') as file:
        json.dump(highscores, file, indent=4)


# Highscore-Datei laden
def load_best_scores():
    print("Highscores werden geladen.")
    app = App.get_running_app()
    score_file_path = app.get_score_file_path()

    if os.path.exists(score_file_path):
        with open(score_file_path, "r+") as file:  # Öffnen zum Lesen und Schreiben
            try:
                highscores = json.load(file)
                # Überprüfen, ob alle Keys vorhanden sind
                for key in default_scores:
                    if key not in highscores:
                        print(f"{key} nicht gefunden, wird mit 'Default-Wert' ersetzt.")
                        highscores[key] = default_scores[key]

                # Datei zurück an den Anfang setzen und mit neuen Werten überschreiben
                file.seek(0)
                json.dump(highscores, file, indent=4)
                file.truncate()  # Restinhalt löschen, falls die neue Datei kleiner ist

                return highscores

            except json.JSONDecodeError:
                print("Fehler beim Laden der Highscores. Datei wird zurückgesetzt.")
                # Dateiinhalt zurücksetzen
                file.seek(0)
                json.dump(default_scores, file, indent=4)
                file.truncate()
                return default_scores
    else:
        print("Highscore-Datei nicht gefunden. Neue Datei wird erstellt.")
        with open(score_file_path, "w") as file:
            json.dump(default_scores, file, indent=4)
        return default_scores


# Funktion zum Überprüfen und Aktualisieren der Highscores
def update_best_scores(game_mode, difficulty, board_size, score):
    print("Highscores werden aktualisiert.")
    if game_mode != "duell_standard":  # Bei Duell gibt es keine Highscore (bis jetzt zumindest).
        current_score = f"{game_mode}_{difficulty}_{board_size}"
        if game_mode == "time_race" or game_mode == "standard":
            comparison = "lower"  # Wenn "comparison_type" "lower" ist, ist der niedrigere Score besser.
        else:
            comparison = "higher"  # Wenn "comparison_type" "higher" ist, ist der höhere Score besser.

        highscores = load_best_scores()
        if comparison == "lower":
            if score < highscores[current_score]:
                highscores[current_score] = score
                save_best_scores(highscores)
                print(f"Neue Highscore {comparison} gespeichert.")
                return True  # Neuer Highscore
        else:
            if score > highscores[current_score]:
                highscores[current_score] = score
                save_best_scores(highscores)
                print(f"Neue Highscore {comparison} gespeichert.")
                return True  # Neuer Highscore
        return False  # Kein neuer Highscore
    return False
