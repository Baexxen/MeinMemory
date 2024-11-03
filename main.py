import random
import sys

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition, SwapTransition, WipeTransition, CardTransition, SlideTransition, ShaderTransition, RiseInTransition, FallOutTransition, TransitionBase
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
from random import shuffle, randint
from math import sqrt
from jnius import autoclass
import os
import logging
import time

# Highscore
from score_manager import load_best_scores, save_best_scores, update_best_scores

# Settings
from settings_manager import save_settings, load_settings, reset_settings

# Bilderlisten
from pictures_manager import save_pics_lists, load_pics_lists, reset_selected_pics_lists

# Folgende Importe werden nur in der .kv Datei verwendet. Bitte nicht löschen :)
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from custom_ui import MyScatter, MyMemoryGrid, LabelBackgroundColor, ButtonBackgroundColor

# Global variables initialization
logging.basicConfig(level=logging.DEBUG)

WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
BEIGE = (1, 0.77, 0.59, 1)
DARK_RED = (0.53, 0.09, 0.09, 1)
ORANGE = (0.95, 0.7, 0.21, 1)
LIGHT_BLUE = (0.08, 0.54, 0.64, 1)
DARK_BLUE = (0.04, 0.27, 0.32, 1)
GREY = (0.48, 0.48, 0.48, 1)

WINDOW_CLEARCOLOR_THEME = {
    "light": ORANGE,
    "dark": DARK_BLUE,
    "color": LIGHT_BLUE
}

CARD_COVER_THEME = {
    "light": "pics/Default_light.png",
    "dark": "pics/Default_dark.png",
    "color": "pics/Default.png"
}

Window.clearcolor = LIGHT_BLUE
if platform == "linux":
    Window.size = (600, 800)
    Window.left = 600
    Window.top = 150


# noinspection PyUnusedLocal
class MyMemoryApp(App):
    print("MyMemoryApp")
    white = ListProperty([1, 1, 1, 1])
    black = ListProperty([0, 0, 0, 1])
    beige = ListProperty([1, 0.77, 0.59, 1])
    dark_red = ListProperty([0.53, 0.09, 0.09, 1])
    orange = ListProperty([0.95, 0.7, 0.21, 1])
    light_blue = ListProperty([0.08, 0.54, 0.64, 1])
    dark_blue = ListProperty([0.04, 0.27, 0.32, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_difficulty = "easy"
        self.game_screen = None
        self.pics_list = []
        self.car_images = []
        self.akira_images = []
        self.bundesliga_images = []
        self.own_landscape_images = []
        self.sexy_images = []
        self.random_images = []
        self.theme = "color"
        self.theme_color = "color"
        self.button_list = []
        self.label_list = []

    def build(self):
        print("MyMemoryApp build")
        # Transitions: NoTransition, FadeTransition, SwapTransition, WipeTransition, CardTransition, SlideTransition, ShaderTransition, RiseInTransition, FallOutTransition, TransitionBase
        sm = ScreenManager(transition=NoTransition())  # Disable transition
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(StandardModeScreen(name="standard_mode"))
        sm.add_widget(TimeModeScreen(name="time_mode"))
        sm.add_widget(TimeRaceScreen(name="time_race"))
        sm.add_widget(MultiplayerScreen(name="multiplayer_mode"))
        sm.add_widget(DuellModeScreen(name="duell_mode"))
        sm.add_widget(BattleModeScreen(name="battle_mode"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(PicsSelectScreen(name="pics_select"))
        sm.current = "main_menu"
        sm.transition = SwapTransition()
        return sm

    def on_start(self):
        logging.debug("App started")
        print("MyMemoryApp on_start")
        self.icon = "pics/icon.ico"
        self.root.current = "main_menu"
        Clock.schedule_once(self.force_redraw, 0.1)  # Eventuell eine leichte Verzögerung hinzufügen
        self.game_screen = self.root.get_screen("game")
        self.load_pictures()
        Clock.schedule_once(self.load_settings, .2)

    def start_new_game(self, cards_count, game_mode="standard", difficulty="easy"):
        print(f"MyMemoryApp start new game {game_mode} {difficulty}")
        self.game_screen.current_game_mode = game_mode
        self.current_difficulty = difficulty
        self.game_screen.current_difficulty = self.current_difficulty
        self.game_screen.cards = cards_count

        self.load_active_pics_lists()
        self.game_screen.restart_game()
        self.root.current = "game"

        if game_mode == "standard":
            pass

        elif game_mode == "time_race":
            pass

        elif game_mode == "battle":
            pass

    def continue_game(self):
        settings = load_settings()
        game_screen = self.root.get_screen("game")
        game_screen.active_touches.clear()
        game_screen.touch_delay = settings["touch_delay"]
        self.root.current = "game"

    def force_redraw(self, dt):
        # Erzwinge ein erneutes Rendern des aktuellen Screens
        self.title = "MeinMemory"
        Window.size = (Window.size[0] + 1, Window.size[1] + 1)
        Window.size = (Window.size[0] - 1, Window.size[1] - 1)

    def change_theme_color(self, theme_color):
        self.theme_color = theme_color
        Window.clearcolor = WINDOW_CLEARCOLOR_THEME[theme_color]
        for button in self.button_list:
            button.change_theme(self.theme_color)
        for label in self.label_list:
            label.change_theme(self.theme_color)

    def load_settings(self, *args):
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        for button in self.button_list:
            button.change_theme(self.theme_color)
        for label in self.label_list:
            label.change_theme(self.theme_color)

    def load_active_pics_lists(self):
        self.pics_list.clear()
        lists_selected = 0
        all_pics_lists = load_pics_lists()
        if all_pics_lists["akira_images"] == "down":
            self.pics_list.extend(self.akira_images)
            lists_selected += 1
        if all_pics_lists["car_images"] == "down":
            self.pics_list.extend(self.car_images)
            lists_selected += 1
        if all_pics_lists["bundesliga_images"] == "down":
            self.pics_list.extend(self.bundesliga_images)
            lists_selected += 1
        if all_pics_lists["own_landscape_images"] == "down":
            self.pics_list.extend(self.own_landscape_images)
            lists_selected += 1
        if all_pics_lists["sexy_images"] == "down":
            self.pics_list.extend(self.sexy_images)
            lists_selected += 1
        if all_pics_lists["random_images"] == "down":
            self.pics_list.extend(self.random_images)
            lists_selected += 1

        if lists_selected == 0:
            reset_selected_pics_lists()
            self.pics_list.clear()
            self.pics_list.extend(self.akira_images)
            self.pics_list.extend(self.car_images)
            self.pics_list.extend(self.bundesliga_images)
            self.pics_list.extend(self.own_landscape_images)
            self.pics_list.extend(self.sexy_images)
            self.pics_list.extend(self.random_images)

    def load_pictures(self):
        print("MyMemoryApp: load_pictures")
        paths = {
            "pics/Akira": self.akira_images,
            "pics/Autos": self.car_images,
            "pics/Bundesliga": self.bundesliga_images,
            "pics/EigeneLandschaften": self.own_landscape_images,
            "pics/Sexy": self.sexy_images,
            "pics/Verschiedenes": self.random_images,
        }

        for path, image_list in paths.items():
            for file_name in os.listdir(path):
                if file_name.endswith(".png"):
                    full_path = os.path.join(path, file_name)
                    image_list.append(full_path)

    def get_score_file_path(self):
        return os.path.join(self.user_data_dir, "highscores.json")

    def get_settings_file_path(self):
        return os.path.join(self.user_data_dir, "settings.json")

    def get_pics_lists_file_path(self):
        return os.path.join(self.user_data_dir, "pics_lists.json")

    def exit_app(self):
        print("Es wird über 'MyMemoryApp' geschlossen.")
        self.get_running_app().stop()
        sys.exit()


class Player:
    print("Player")

    def __init__(self, name):
        self.name = name
        self.score = 0
        self.turns = 0

    def increase_score(self, points):
        self.score += points

    def increment_turns(self):
        self.turns += 1

    def reset(self):
        self.score = 0
        self.turns = 0


class AI(Player):
    print("KI")

    def __init__(self, name, difficulty="easy"):
        super().__init__(name)
        self.difficulty = difficulty
        self.card_grid = []
        self.active_cards = []  # Liste aller Karten
        self.known_cards = {}  # Set mit Karten, die schon aufgedeckt waren
        self.safe_call_cards = {}  # Set, um Karten zu speichern, die schon mehrfach aufgedeckt wurden.
        self.app = App.get_running_app()
        self.game_screen = None
        self.base_error_probability = 0
        self.error = False
        self.cols = 0
        self.base_error_probability = {"easy": 35, "medium": 15, "hard": 5, "impossible": 0}[self.difficulty]
        self.save_call_threshold = {"easy": 3, "medium": 2, "hard": 1, "impossible": 0}[self.difficulty]
        self.players_last_cards = []

    def select_first_card(self, players_last_cards):
        print(f"KI {self.difficulty} sucht erste Karte")
        self.players_last_cards = players_last_cards
        first_card = None
        self.active_cards = self.game_screen.card_list.copy()
        # ###########################################################################################################################################################################################################
        if self.difficulty == "easy":
            shuffle(self.active_cards)
            for card in self.active_cards:
                if not card.disabled and not card.flipped:  # Wähle eine zufällige Karte, die noch nicht aufgedeckt ist.
                    first_card = card
                    break
            if not first_card:
                first_card = self.find_any_card()

        # ###########################################################################################################################################################################################################
        else:
            known_pair = self.check_for_known_pair()  # Gibt es schon ein bekanntes Paar?
            if known_pair:
                first_card = known_pair[randint(0, 1)]
            else:
                # ###########################################################################################################################################################################################################
                if self.difficulty == "medium":
                    first_card = self.find_any_card()  # Wähle bevorzugt eine Karte, die nicht zuletzt vom Spieler aufgedeckt wurde.
                # ###########################################################################################################################################################################################################
                elif self.difficulty == "hard" or self.difficulty == "impossible":
                    shuffle(self.active_cards)
                    for card in self.active_cards:
                        if not card.disabled and not card.flipped:
                            if card not in self.known_cards:  # Bevorzugt eine Karte aufdecken, die noch nicht vorher aufgedeckt wurde.
                                first_card = card
                                break
                    if not first_card:
                        first_card = self.find_any_card()

        if first_card:
            return first_card
        else:
            print("'first_card' nicht gefunden.")
            return None

    def select_second_card(self, first_card):
        print(f"KI sucht zweite Karte")
        second_card = None
        self.active_cards = self.game_screen.card_list.copy()
        self.error = self.do_error()

        known_pair = self.find_match(first_card)
        print(f"Es wird nach bekanntem Paar gesucht...")
        if known_pair:
            print(f"Bekanntes Paar gefunden ({known_pair})")
            for card in known_pair:
                if not card.flipped:
                    second_card = card
                    print(f"second_card = {second_card.value}")
                    break
        else:
            if self.difficulty == "easy" or self.difficulty == "medium":
                print(f"Kein bekanntes Paar gefunden. AI:'{self.difficulty}' KI sucht zufällige Karte aus...")
                second_card = self.find_any_card()

            elif self.difficulty == "hard" or self.difficulty == "impossible":
                print(f"Kein bekanntes Paar gefunden. AI {self.difficulty} sucht Karte aus, die zuvor schon aufgedeckt wurde.")
                shuffle(self.active_cards)
                for card in self.active_cards:
                    if card != first_card and not card.disabled and not card.flipped:
                        second_card = card
                        break
                if not second_card:
                    second_card = self.find_any_card()

        if not self.error:
            if second_card:
                return second_card
            else:
                print("'second_card' nicht gefunden.")
                return self.find_any_card()  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist.
        else:
            second_card = self.find_wrong_card_nearby(first_card, second_card)  # Wenn ein Fehler gemacht werden soll, wird eine falsche Karte in der Nähe der eigentlich richtigen Karte gesucht.
            if second_card:
                return second_card
            else:
                print("'second_card' nicht gefunden.")
                return self.find_any_card()  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist.

    def remember_card(self, card):
        do_error = self.do_error()
        if not do_error or card.flip_count > self.save_call_threshold:  # KI merkt sich eine Karte nur, wenn sie keinen Fehler machen soll, oder die Karte schon öfter aufgedeckt wurde.
            print(f"KI merkt sich Karte {card.value}.")
            if card.value in self.known_cards:
                self.known_cards[card.value].add(card)  # Wenn Karte mit diesem Wert shon gespeichert ist, wird sie diesem Set hinzugefügt (falls nicht schon vorhanden)
            else:
                self.known_cards[card.value] = {card}  # Sonst wird ein neues Set angelegt.

    def find_match(self, card):
        pair_list = []  # Hilfsliste, um kein 'Set' auszugeben.
        if card.value in self.known_cards and len(self.known_cards[card.value]) == 2:  # Wenn zwei Karten mit gleichen Werten gespeichert sind ...
            print(f"Es wurde ein Paar ({card.value}) gefunden")
            for known_card in self.known_cards[card.value]:
                pair_list.append(known_card)
            return pair_list  # Werden diese als Liste, nicht als Set, ausgegeben.
        return None

    def remove_pair(self, card):
        if card.value in self.known_cards and len(self.known_cards[card.value]) == 2:
            print(f"card {card.value} aus 'KI-Gedächtnis' gelöscht")
            del self.known_cards[card.value]

    def check_for_known_pair(self):
        print("KI sucht nach bekannten Paaren")
        if len(self.players_last_cards) > 0:  # Erst prüfen, ob es ein bekanntes Kartenpaar von den Karten gibt, die der Spieler zuletzt aufgedeckt hat :-)
            for card in self.players_last_cards:
                known_pair = self.find_match(card)
                if known_pair:
                    return known_pair

        if len(self.known_cards) > 0:  # Gibt es schon bekannte Karten?
            for card in self.active_cards:  # Gibt es schon ein bekanntes Paar?
                known_pair = self.find_match(card)
                if known_pair:
                    return known_pair
        print("Es wurde kein bekanntes Paar gefunden")
        return None

    def do_error(self):
        error = randint(1, 100)
        if error > self.base_error_probability:
            print(f"KI ({self.difficulty}) macht keinen Fehler. ({error}/{self.base_error_probability})")
            return False
        else:
            print(f"KI ({self.difficulty}) macht absichtlichen Fehler. ({error}/{self.base_error_probability})")
            return True

    def find_wrong_card_nearby(self, first_card, second_card):
        print("KI sucht 'logische', falsche Karte")
        # Finde die Position der ersten Karte im 2D-Array (Spielfeld)
        second_card_index = self.game_screen.card_list.index(second_card)
        row_index = second_card_index // self.cols
        col_index = second_card_index % self.cols

        # Finde benachbarte Karten (links, rechts, oben, unten) im 2D-Spielfeld
        possible_nearby_cards = []

        if row_index > 0:  # obere Nachbarkarte
            card = self.card_grid[row_index - 1][col_index]
            if not card.disabled and card.value != first_card.value and not card.flipped:
                possible_nearby_cards.append(card)
            if col_index > 0:  # obere, linke Nachbarkarte
                card = self.card_grid[row_index - 1][col_index - 1]
                if not card.disabled and card.value != first_card.value and not card.flipped:
                    possible_nearby_cards.append(card)
            if col_index < self.cols - 1:  # obere, rechte Nachbarkarte
                card = self.card_grid[row_index - 1][col_index + 1]
                if not card.disabled and card.value != first_card.value and not card.flipped:
                    possible_nearby_cards.append(card)

        if row_index < len(self.card_grid) - 1:  # untere Nachbarkarte
            card = self.card_grid[row_index + 1][col_index]
            if not card.disabled and card.value != first_card.value and not card.flipped:
                possible_nearby_cards.append(card)
            if col_index > 0:  # untere, linke Nachbarkarte
                card = self.card_grid[row_index + 1][col_index - 1]
                if not card.disabled and card.value != first_card.value and not card.flipped:
                    possible_nearby_cards.append(card)
            if col_index < self.cols - 1:  # untere, rechte Nachbarkarte
                card = self.card_grid[row_index + 1][col_index + 1]
                if not card.disabled and card.value != first_card.value and not card.flipped:
                    possible_nearby_cards.append(card)

        if col_index > 0:  # linke Nachbarkarte
            card = self.card_grid[row_index][col_index - 1]
            if not card.disabled and card.value != first_card.value and not card.flipped:
                possible_nearby_cards.append(card)
        if col_index < self.cols - 1:  # rechte Nachbarkarte
            card = self.card_grid[row_index][col_index + 1]
            if not card.disabled and card.value != first_card.value and not card.flipped:
                possible_nearby_cards.append(card)

        # Wähle eine zufällige Nachbarkarte, die nicht die richtige Karte ist
        if possible_nearby_cards:
            shuffle(possible_nearby_cards)
            return possible_nearby_cards[0]
        return self.find_random_wrong_card(first_card)  # Falls keine passende Karte gefunden wurde, wähle eine beliebige, falsche Karte

    def find_random_wrong_card(self, first_card):
        print("Suche zufällige, falsche Karte")
        shuffle(self.active_cards)
        for card in self.active_cards:
            if not card.disabled and not card.value == first_card.value and not card == first_card:
                print(f"Falsche Karte ({card}) gefunden. First_Card = {first_card}")
                return card

        for card in self.active_cards:
            if not card.disabled and not card == first_card:
                print("Erstbeste Karte gefunden.")
                return card

    def find_any_card(self):
        shuffle(self.active_cards)
        for card in self.active_cards:  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist und nicht zuletzt vom Spieler aufgedeckt wurde.
            if not card.disabled and not card.flipped and card not in self.players_last_cards:
                return card
        for card in self.active_cards:  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist.
            if not card.disabled and not card.flipped:
                return card
        return None

    def create_card_grid(self):
        card_grid = [self.game_screen.card_list[i:i + self.cols] for i in range(0, len(self.game_screen.card_list), self.cols)]
        for row in card_grid:
            print([card.value for card in row])
        return card_grid

    def reset(self):
        self.score = 0
        self.turns = 0
        self.safe_call_cards = []
        self.known_cards.clear()
        self.game_screen = self.app.root.get_screen("game")
        self.difficulty = self.game_screen.current_difficulty
        self.base_error_probability = {"easy": 35, "medium": 15, "hard": 5, "impossible": 0}[self.difficulty]
        self.save_call_threshold = {"easy": 3, "medium": 2, "hard": 1, "impossible": 0}[self.difficulty]
        self.active_cards.clear()
        self.active_cards = self.game_screen.card_list.copy()
        self.cols = self.game_screen.cols
        self.card_grid = self.create_card_grid()


class Card(ButtonBehavior, Image):
    card_size = NumericProperty(100)
    print("Card")

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

        self.flipped = False
        self.background_normal = ""
        self.bind(card_size=self.update_size)
        self.instance = self
        self.parent = None
        self.game_screen = None
        self.flip_count = 0

    def update_size(self, instance, value):
        self.instance = instance
        self.size_hint = (None, None)
        self.size = (value, value)

    def on_touch_down(self, touch):
        return False

    def on_touch_move(self, touch):
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            super().on_touch_up(touch)
            return False

        if not self.game_screen.input_enabled:
            super().on_touch_up(touch)
            return False

        if self.disabled:
            super().on_touch_up(touch)
            return False

        if self.parent.transformed:
            super().on_touch_up(touch)
            return False

        if self.game_screen.current_player == self.game_screen.player or self.game_screen.current_player == self.game_screen.player2:
            # Flip card if conditions are met
            self.flip_count += 1
            self.game_screen.flip_card(self)
            super().on_touch_up(touch)
            return True

    def get_scatter_parent(self):
        parent = self.parent.parent
        while parent:
            if isinstance(parent, MyScatter):
                return parent
            parent = parent.parent
        return None

    def update_theme(self, theme_color):
        self.default_pic = CARD_COVER_THEME[theme_color]


# region Screens #################################################################################################
class GameScreen(Screen):
    print("GameScreen")
    layout = ObjectProperty(None)
    memory_grid = ObjectProperty(None)
    scatter = ObjectProperty(None)
    bottom_label = ObjectProperty(None)
    top_label = ObjectProperty(None)
    top_layout = ObjectProperty(None)
    scatter_layout = ObjectProperty(None)
    bottom_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        print("GameScreen init")
        self.size = Window.size
        self.player = Player("Spieler_1")
        self.player2 = Player("Spieler_2")
        self.ai = AI("KI Sepp", difficulty="easy")
        self.current_player = self.player
        self.card_list = []
        self.active_touches = set()
        self.first_flip = True
        self.elapsed_time = 0
        self.time_race_running = False
        self.bottom_label.redraw(LIGHT_BLUE, BEIGE, True, ORANGE, 3)
        self.top_label.redraw(LIGHT_BLUE, BEIGE, True, ORANGE, 3)
        self.app = App.get_running_app()
        self.bottom_label.text = "Schimmel"
        self.current_highscore = 0
        self.current_difficulty = "easy"
        self.scatter.game_screen = self
        self.game_over = True
        self.game_running = False
        self.current_game_mode = "standard"
        self.input_enabled = True
        self.cols = 4
        self.cards = 16
        self.board_size = {16: "small", 24: "medium", 36: "big"}[self.cards]
        self.ai_timeout = 1.0  # Verzögerung der AI-Aktionen (Karten aufdecken)
        self.hide_cards_timeout = 0.8  # Verzögerung beim Zudecken falsch aufgedeckter Karten
        self.touch_delay = 10  # Verzögerung bei Erkennung von 'Touch-Move'
        self.theme_color = "color"
        self.load_settings()

    def restart_game(self):
        self.board_size = {16: "small", 24: "medium", 36: "big"}[self.cards]
        self.cols = int(sqrt(self.cards))

        if self.current_game_mode == "standard":
            self.change_top_label_text(f"Einzelspieler")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "battle":
            self.change_top_label_text(f"Spiel gegen die KI\nAktueller Spieler bist du.")
        elif self.current_game_mode == "time_race":
            self.change_top_label_text("Zeitrennen")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "duell_standard":
            self.change_top_label_text(f"Duell\nAktueller Spieler ist {self.current_player.name}")

        self.memory_grid.clear_widgets()
        self.memory_grid.cols = self.cols
        card_values = list(range(1, (self.cards // 2 + 1))) * 2
        shuffle(self.app.pics_list)
        shuffle(card_values)
        self.card_list.clear()
        for value in card_values:
            card = Card(value)
            self.memory_grid.add_widget(card)
            card.parent = card.get_scatter_parent()
            card.game_screen = self
            card.source = self.app.pics_list[value - 1]
            card.pic = self.app.pics_list[value - 1]
            card.background_disabled_normal = card.pic
            card.background_down = card.pic
            card.default_pic = CARD_COVER_THEME[self.theme_color]
            self.card_list.append(card)

        self.game_over = False
        self.game_running = True
        self.player.reset()
        self.player2.reset()
        self.ai.reset()
        self.time_race_running = False
        self.first_flip = True
        self.elapsed_time = 0
        self.stop_time_count_up()
        self.update_card_pos_and_size(self.memory_grid)
        self.reset_widgets()
        if self.current_game_mode != "duell_standard":
            highscores = load_best_scores()
            current_game = f"{self.current_game_mode}_{self.current_difficulty}_{self.board_size}"
            self.current_highscore = highscores[current_game]
            self.update_time_display()
        self.update()
        self.load_settings()

    def update(self):
        print("GameScreen: update")

        count_found_cards = 0
        for card in self.card_list:
            if not card.disabled:
                if card.flipped:
                    card.source = card.pic
                else:
                    card.source = card.default_pic
            else:
                card.source = card.pic
                count_found_cards += 1
            card.text = str(card.value)

        if count_found_cards == len(self.card_list) and not self.game_over:
            self.game_over = True
            self.game_running = False
            self.top_label.text = "Game Over"

        if self.game_over:
            score = 0
            if self.current_game_mode == "standard":
                score = self.player.turns
            elif self.current_game_mode == "battle":
                score = self.player.score
            elif self.current_game_mode == "time_race":
                score = self.elapsed_time
            highscore = update_best_scores(self.current_game_mode, self.current_difficulty, self.board_size, score)
            if highscore:
                self.change_top_label_text("Neuer Highscore =)")
                self.current_highscore = score
            else:
                if self.current_game_mode == "duell_standard":
                    if self.player.score > self.player2.score:
                        self.change_top_label_text("Spieler_1 hat gewonnen :-)")
                    elif self.player.score == self.player2.score:
                        self.change_top_label_text("Unentschieden :-O")
                    else:
                        self.change_top_label_text("Spieler_2 hat gewonnen :-)")
                else:
                    self.change_top_label_text("Keine neue Bestleistung... Vielleicht nächstes Mal ;-)")
            self.update_time_display()

            self.current_player = self.player
            Clock.unschedule(self.update_time)
            self.time_race_running = False
            # self.game_over = False

        if self.current_game_mode == "standard":
            self.bottom_label.text = f"Runde: {self.player.turns}\nRekord: {self.current_highscore}"

        elif self.current_game_mode == "duell_standard":
            self.bottom_label.text = f"Runde: {self.player.turns}\nPlayer1: {self.player.score} Player2: {self.player2.score}"
        elif self.current_game_mode == "battle":
            self.bottom_label.text = f"Punkte: {self.player.score}\nRekord: {self.current_highscore}"

        elif self.current_game_mode == "time_race":
            pass

    def update_card_pos_and_size(self, *args):
        # Berechne die Kartengröße so, dass sie genau in das Grid passt
        grid_width = self.width
        grid_height = self.height * 0.8
        card_size = min(grid_width // self.cols, grid_height // (self.cards // self.cols))

        for card in self.card_list:
            card.size_hint = (None, None)
            card.size = (card_size, card_size)

    def on_touch_down(self, touch):
        self.active_touches.add(touch.uid)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.uid in self.active_touches:
            self.active_touches.remove(touch.uid)
        return super().on_touch_up(touch)

    def flip_card(self, card):
        print("flip_card")
        first_card = card
        first_card.flipped = True
        first_card.source = first_card.pic
        self.ai.remember_card(first_card)
        second_card = None

        if self.current_game_mode == "time_race":
            if self.first_flip:
                self.start_time_count_up()
                self.time_race_running = True

        for card in self.card_list:
            if card.flipped and card != first_card and not card.disabled:
                second_card = card
                print(f"Zweite Karte gefunden")
                break

        if second_card is not None:
            if first_card.value == second_card.value:
                self.input_enabled = False
                if self.current_player == self.player:
                    self.player.increment_turns()
                print("Paar gefunden")
                self.kill_cards(first_card, second_card)
                if self.current_game_mode == "battle" or self.current_game_mode == "duell_standard":
                    self.current_player.increase_score(1)
                    if self.current_player == self.ai:
                        all_found = self.all_cards_found()
                        if all_found:
                            self.game_over = True
                        else:
                            players_last_cards = [first_card, second_card]
                            Clock.schedule_once(lambda dt: self.ai_turn(players_last_cards), self.ai_timeout)

            else:
                self.input_enabled = False
                self.current_player.increment_turns()
                print("Falsche Karte aufgedeckt")
                Clock.schedule_once(lambda dt: self.hide_cards(first_card, second_card), self.hide_cards_timeout)
                if self.current_game_mode == "battle" or self.current_game_mode == "duell_standard":
                    print("Spieler wird gewechselt")
                    self.switch_player()
                    if self.current_player == self.ai:
                        players_last_cards = [first_card, second_card]
                        Clock.schedule_once(lambda dt: self.ai_turn(players_last_cards), self.ai_timeout)
        self.update()

    def kill_cards(self, first_card, second_card):
        print("kill_cards")
        for card in self.card_list:
            if card == first_card or card == second_card:
                card.disabled = True
                print(f"Karte {card.value} disabled.")
        self.input_enabled = True
        self.ai.remove_pair(first_card)

    def hide_cards(self, first_card, second_card):
        print("GameScreen: hide_cards")
        for card in self.card_list:
            if card == first_card or card == second_card:
                card.flipped = False
        self.input_enabled = True
        self.update()

    def switch_player(self):
        if self.current_game_mode != "duell_standard":
            if self.current_player == self.player:
                self.current_player = self.ai
            else:
                self.current_player = self.player
        else:
            if self.current_player == self.player:
                self.current_player = self.player2
            else:
                self.current_player = self.player
        self.change_top_label_text(f"Aktueller Spieler ist {self.current_player.name}")

    def ai_turn(self, players_last_cards):
        first_card = self.ai.select_first_card(players_last_cards)
        second_card = None
        if first_card:
            self.flip_card(first_card)
            second_card = self.ai.select_second_card(first_card)
        else:
            print("Fehler, KI konnte keine erste Karte finden.")
            self.switch_player()

        if second_card:
            Clock.schedule_once(lambda dt: self.flip_card(second_card), self.ai_timeout)
        else:
            print("Fehler, KI konnte zweite Karte nicht finden.")
            self.switch_player()

    def all_cards_found(self):
        found_cards = 0
        for card in self.card_list:
            if card.disabled:
                found_cards += 1
        if found_cards >= len(self.card_list):
            return True
        else:
            return False

    def change_top_label_text(self, text):
        self.top_label.text = text

    def reset_widgets(self):
        self.active_touches.clear()
        self.scatter.transformed = False
        self.scatter.scale = 1.0
        self.scatter_layout.do_layout()

    def start_time_count_up(self):
        Clock.schedule_interval(self.update_time, 0.1)
        self.first_flip = False

    def update_time(self, dt):
        self.elapsed_time += .1
        self.elapsed_time = round(self.elapsed_time, 1)
        self.update_time_display()

    def stop_time_count_up(self):
        Clock.unschedule(self.update_time)

    def update_time_display(self):
        if self.board_size == "small":
            self.bottom_label.text = f"Zeit: {self.elapsed_time}\nRekord: {self.current_highscore}"
        elif self.board_size == "medium":
            self.bottom_label.text = f"Zeit: {self.elapsed_time}\nRekord: {self.current_highscore}"
        elif self.board_size == "big":
            self.bottom_label.text = f"Zeit: {self.elapsed_time}\nRekord: {self.current_highscore}"

    def load_settings(self):
        settings = load_settings()
        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]
        theme = settings["theme"]
        self.theme_color = get_theme_color(theme)
        self.memory_grid.redraw(self.theme_color)
        for card in self.card_list:
            card.update_theme(self.theme_color)
        self.update()

    def on_pre_leave(self, *args):
        if self.current_game_mode == "time_race" and self.time_race_running:
            self.stop_time_count_up()
        return super().on_pre_leave()

    def on_pre_enter(self, *args):
        self.load_settings()
        self.reset_widgets()
        if self.current_game_mode == "time_race" and self.time_race_running:
            self.start_time_count_up()
        return super().on_pre_enter()


class MainMenuScreen(Screen):
    print("MainMenuScreen")
    continue_button = ObjectProperty(None)
    standard_button = ObjectProperty(None)
    time_button = ObjectProperty(None)
    multiplayer_button = ObjectProperty(None)
    settings_button = ObjectProperty(None)
    exit_button = ObjectProperty(None)

    top_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.theme = "color"
        self.theme_color = "color"
        self.button_list = [self.continue_button, self.standard_button, self.time_button, self.multiplayer_button, self.settings_button, self.exit_button]
        self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_continue_button(self, game_running):
        if game_running:
            self.continue_button.disabled = False
        else:
            self.continue_button.disabled = True
        self.continue_button.redraw()

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        app_root = app.root
        if app_root:
            game_screen = app_root.get_screen("game")
            self.update_continue_button(game_screen.game_running)
        self.redraw()


class StandardModeScreen(Screen):
    print("StandardModeScreen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class TimeModeScreen(Screen):
    print("TimeModeScreen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class TimeRaceScreen(Screen):
    print("TimeRaceScreen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class MultiplayerScreen(Screen):
    print("MultiplayerScreen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class DuellModeScreen(Screen):
    print("DuellModeScreen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class BattleModeScreen(Screen):
    print("BattleModeScreen")
    easy_button = ObjectProperty(None)
    medium_button = ObjectProperty(None)
    hard_button = ObjectProperty(None)
    impossible_button = ObjectProperty(None)
    small = ObjectProperty(None)
    medium = ObjectProperty(None)
    big = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.update_diff_buttons, 0.1)
        self.easy_button.disabled = True
        self.current_difficulty = "easy"
        self.small.disabled = True
        self.current_board_size = 16
        self.button_list = [self.easy_button, self.medium_button, self.hard_button, self.impossible_button, self.small, self.medium, self.big]
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.theme = "color"
        self.theme_color = "color"

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def init_new_game(self, mode):
        app = App.get_running_app()
        app.start_new_game(self.current_board_size, mode, self.current_difficulty)

    def update_diff_buttons(self, pushed_button=1):
        if pushed_button == 1:
            self.easy_button.disabled = True
            self.current_difficulty = "easy"
            self.medium_button.disabled = False
            self.hard_button.disabled = False
            self.impossible_button.disabled = False
        elif pushed_button == 2:
            self.easy_button.disabled = False
            self.medium_button.disabled = True
            self.current_difficulty = "medium"
            self.hard_button.disabled = False
            self.impossible_button.disabled = False
        elif pushed_button == 3:
            self.easy_button.disabled = False
            self.medium_button.disabled = False
            self.hard_button.disabled = True
            self.current_difficulty = "hard"
            self.impossible_button.disabled = False
        elif pushed_button == 4:
            self.easy_button.disabled = False
            self.medium_button.disabled = False
            self.hard_button.disabled = False
            self.impossible_button.disabled = True
            self.current_difficulty = "impossible"
        for button in self.button_list:
            button.redraw()

    def update_board_size_buttons(self, pushed_button=1):
        if pushed_button == 1:
            self.small.disabled = True
            self.current_board_size = 16
            self.medium.disabled = False
            self.big.disabled = False
        elif pushed_button == 2:
            self.small.disabled = False
            self.medium.disabled = True
            self.current_board_size = 24
            self.big.disabled = False
        elif pushed_button == 3:
            self.small.disabled = False
            self.medium.disabled = False
            self.big.disabled = True
            self.current_board_size = 36
        for button in self.button_list:
            button.redraw()

    def on_pre_enter(self, *args):
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        for button in self.button_list:
            button.change_theme(self.theme_color)


class SettingsScreen(Screen):
    print("SettingsScreen")
    top_label = ObjectProperty(None)
    theme_label = ObjectProperty(None)
    light_theme_button = ObjectProperty(None)
    dark_theme_button = ObjectProperty(None)
    system_theme_button = ObjectProperty(None)
    color_theme_button = ObjectProperty(None)
    touch_delay_label = ObjectProperty(None)
    ai_timeout_label = ObjectProperty(None)
    hide_cards_timeout_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = None
        self.game_screen = None
        self.theme = "color"  # Eigentlicher 'Theme'-Name (Unterscheidung wegen 'System-Theme')
        self.theme_color = "color"  # Tatsächliche Theme-'Farbe'
        self.touch_delay = 10
        self.ai_timeout = 1.0
        self.hide_cards_timeout = 0.8
        self.load_settings()
        self.top_label.redraw(ORANGE, WHITE, False, WHITE, 5)
        self.theme_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.touch_delay_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.ai_timeout_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.hide_cards_timeout_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.button_list = [self.light_theme_button, self.dark_theme_button, self.system_theme_button, self.color_theme_button]
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def on_pre_enter(self):
        self.load_settings()
        self.change_hide_cards_timeout_label_text()
        self.change_ai_timeout_label_text()
        self.change_touch_delay_label_text()
        self.change_button_states(self.theme)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def load_settings(self):
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)

        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]

    def change_button_states(self, theme):
        button = 0
        if theme == "light":
            self.light_theme_button.disabled = True
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
            button = 0
        elif theme == "dark":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = True
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
            button = 1
        elif theme == "system":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = True
            self.color_theme_button.disabled = False
            button = 2
        elif theme == "color":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = True
            button = 3
        self.update_theme_buttons(button)

    def update_theme_buttons(self, button_id):
        if button_id == 0:
            self.light_theme_button.disabled = True
            self.theme = "light"
            self.theme_color = "light"
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
        elif button_id == 1:
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = True
            self.theme = "dark"
            self.theme_color = "dark"
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
        elif button_id == 2:
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = True
            is_dark_theme = which_theme()
            # noinspection PySimplifyBooleanCheck
            if is_dark_theme is True:
                self.theme_color = "dark"
            elif is_dark_theme is False:
                self.theme_color = "light"
            else:
                self.theme_color = "color"
            self.theme = "system"
            self.color_theme_button.disabled = False
        elif button_id == 3:
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = True
            self.theme = "color"
            self.theme_color = "color"

        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)

        new_setting = ("theme", self.theme)
        save_settings(new_setting)

    def change_touch_delay_label_text(self):
        self.touch_delay_label.text = f"Touch-Delay: {self.touch_delay} (Standard = 10)"

    def increase_touch_delay(self):
        self.touch_delay += 1
        new_setting = ("touch_delay", self.touch_delay)
        save_settings(new_setting)

    def decrease_touch_delay(self):
        if self.touch_delay > 1:
            self.touch_delay -= 1
            new_setting = ("touch_delay", self.touch_delay)
            save_settings(new_setting)

    def change_ai_timeout_label_text(self):
        self.ai_timeout_label.text = f"AI-Timeout: {self.ai_timeout} (Standard = 1.0)\n(Muss größer sein als 'Karten verdecken')"

    def increase_ai_timeout(self):
        self.ai_timeout += 0.1  # Verzögerung der AI-Aktionen (Aufdecken von Karten)
        self.ai_timeout = round(self.ai_timeout, 1)
        new_setting = ("ai_timeout", self.ai_timeout)
        save_settings(new_setting)

    def decrease_ai_timeout(self):
        if self.ai_timeout > 0.1 and self.ai_timeout >= round((self.hide_cards_timeout + 0.1)):
            self.ai_timeout -= 0.1
            self.ai_timeout = round(self.ai_timeout, 1)
            new_setting = ("ai_timeout", self.ai_timeout)
            save_settings(new_setting)

    def change_hide_cards_timeout_label_text(self):
        self.hide_cards_timeout_label.text = f"Karten verdecken: {self.hide_cards_timeout} (Standard = 0.8)\n(Muss kleiner sein als 'AI-Timeout')"

    def increase_hide_cards_timeout(self):
        if self.hide_cards_timeout < self.ai_timeout - 0.1:  # Verzögerung vom Verdecken falsch aufgedeckter Karten
            self.hide_cards_timeout += 0.1
            self.hide_cards_timeout = round(self.hide_cards_timeout, 1)
            new_setting = ("hide_cards_timeout", self.hide_cards_timeout)
            save_settings(new_setting)

    def decrease_hide_cards_timeout(self):
        if self.hide_cards_timeout > 0.1:
            self.hide_cards_timeout -= 0.1
            self.hide_cards_timeout = round(self.hide_cards_timeout, 1)
            new_setting = ("hide_cards_timeout", self.hide_cards_timeout)
            save_settings(new_setting)


class PicsSelectScreen(Screen):
    print("PicsSelectScreen")
    akira_label = ObjectProperty()
    akira_box = ObjectProperty()
    cars_label = ObjectProperty()
    cars_box = ObjectProperty()
    bundesliga_label = ObjectProperty()
    bundesliga_box = ObjectProperty()
    own_landscapes_label = ObjectProperty()
    own_landscapes_box = ObjectProperty()
    sexy_label = ObjectProperty()
    sexy_box = ObjectProperty()
    random_label = ObjectProperty()
    random_box = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.akira_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.cars_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.bundesliga_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.own_landscapes_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.sexy_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.random_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)

        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def save_pics_lists(self):
        save_pics_lists("akira_images", self.akira_box.state)
        save_pics_lists("car_images", self.cars_box.state)
        save_pics_lists("bundesliga_images", self.bundesliga_box.state)
        save_pics_lists("own_landscape_images", self.own_landscapes_box.state)
        save_pics_lists("sexy_images", self.sexy_box.state)
        save_pics_lists("random_images", self.random_box.state)

    def load_checkbox_statuses(self):
        checkboxes = load_pics_lists()
        self.akira_box.state = checkboxes["akira_images"]
        self.cars_box.state = checkboxes["car_images"]
        self.bundesliga_box.state = checkboxes["bundesliga_images"]
        self.own_landscapes_box.state = checkboxes["own_landscape_images"]
        self.sexy_box.state = checkboxes["sexy_images"]
        self.random_box.state = checkboxes["random_images"]

    def on_pre_enter(self, *args):
        self.load_checkbox_statuses()
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()
# endregion


# region Functions #######################################################################################
def start_app():
    print("start_app")
    MyMemoryApp().run()


# noinspection PyPep8Naming
def which_theme():
    if platform == "android":
        Configuration = autoclass("android.content.res.Configuration")
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        ui_mode = activity.getResources().getConfiguration().uiMode
        dark = (ui_mode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES
        return dark
    else:
        return "not android"
# endregion


def get_theme_color(theme):
    theme_color = "color"

    if theme == "light":
        theme_color = "light"
    elif theme == "dark":
        theme_color = "dark"
    elif theme == "system":
        is_dark = which_theme()
        if is_dark is True:
            theme_color = "dark"
        elif is_dark is False:
            theme_color = "light"
        else:
            theme_color = "color"
    elif theme == "color":
        theme_color = "color"

    return theme_color


if __name__ == '__main__':
    start_app()
