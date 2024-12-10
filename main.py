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
from kivy.metrics import sp
from random import shuffle, randint
from math import sqrt
from jnius import autoclass
from PIL import Image as PILImage, ImageDraw
import os
import logging
import time
import locale

# Translator
from translator import Translator

# Custom UI
from custom_ui import MyScatter, MyMemoryGrid, LabelBackgroundColor, ButtonBackgroundColor

# Highscore
from score_manager import load_best_scores, save_best_scores, update_best_scores, reset_highscores

# Settings
from settings_manager import save_settings, load_settings, reset_settings, get_system_language

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


# Global variables initialization
logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("PIL").setLevel(logging.WARNING)

WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
BEIGE = (1, 0.77, 0.59, 1)
DARK_RED = (0.53, 0.09, 0.09, 1)
ORANGE = (0.95, 0.7, 0.21, 1)
LIGHT_BLUE = (0.08, 0.54, 0.64, 1)
DARK_BLUE = (0.04, 0.27, 0.32, 1)
GREY = (0.48, 0.48, 0.48, 1)
DARK_GREY = (0.35, 0.35, 0.35, 1)

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
BOARD_SIZES = {
    "small": 16,
    "medium": 24,
    "big": 30
}
Window.clearcolor = LIGHT_BLUE

DEBUGGING = False

if platform == "linux":
    Window.size = (600, 800)
    Window.left = 600
    Window.top = 150
    DEBUGGING = False

FONT_SIZE_NORMAL = sp(Window.size[0] * 0.02)
FONT_SIZE_LARGE = sp(Window.size[0] * 0.03)


# noinspection PyUnusedLocal
class MyMemoryApp(App):
    white = ListProperty([1, 1, 1, 1])
    black = ListProperty([0, 0, 0, 1])
    beige = ListProperty([1, 0.77, 0.59, 1])
    dark_red = ListProperty([0.53, 0.09, 0.09, 1])
    orange = ListProperty([0.95, 0.7, 0.21, 1])
    light_blue = ListProperty([0.08, 0.54, 0.64, 1])
    dark_blue = ListProperty([0.04, 0.27, 0.32, 1])
    normal_font = FONT_SIZE_NORMAL
    large_font = FONT_SIZE_LARGE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_difficulty = "easy"
        self.game_screen = None
        self.main_menu = None
        self.who_starts_screen = None
        self.pics_list = []
        self.car_images = []
        self.akira_images = []
        self.sport_images = []
        self.own_landscape_images = []
        self.sexy_images = []
        self.random_images = []
        self.nature_images = []
        self.theme = "color"
        self.theme_color = "color"
        self.button_list = []
        self.label_list = []
        self.sys_lang = get_system_language()
        supported_languages = ["en", "de"]
        if self.sys_lang in supported_languages:
            self.lang = self.sys_lang
        else:
            self.lang = "en"
        self.translator = Translator(lang=self.lang)  # Standardsprache ist Englisch

    def build(self):
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
        sm.add_widget(WhoStartsScreen(name="who_starts"))

        sm.current = "main_menu"
        sm.transition = SwapTransition()
        return sm

    def on_start(self):
        logging.debug("App started")
        self.icon = "pics/icon.ico"
        # self.root.current = "main_menu"
        # Clock.schedule_once(self.force_redraw, 0.1)  # Eventuell eine leichte Verzögerung hinzufügen
        self.game_screen = self.root.get_screen("game")
        self.main_menu = self.root.get_screen("main_menu")
        self.load_pictures()
        Clock.schedule_once(self.load_settings, 0.2)
        self.who_starts_screen = self.root.get_screen("who_starts")

    def start_new_game(self, board_size="small", game_mode="standard", difficulty="easy"):
        print(f"MyMemoryApp start new game {game_mode} {difficulty}")
        self.game_screen.current_game_mode = game_mode
        self.current_difficulty = difficulty
        self.game_screen.current_difficulty = self.current_difficulty
        self.game_screen.cards = BOARD_SIZES[board_size]
        self.game_screen.board_size = board_size
        self.load_active_pics_lists()
        self.game_screen.restart_game()
        # if game_mode == "battle" or game_mode == "duell_standard":
        #    self.who_starts_screen.init_settings(game_mode, difficulty, board_size)
        #    self.root.current = "who_starts"
        # else:
        if game_mode != "battle" and game_mode != "duell_standard":
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
        self.lang = settings["lang"]
        self.translator = Translator(lang=self.lang)
        self.main_menu.redraw()
        self.root.current = "main_menu"

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
        if all_pics_lists["sport_images"] == "down":
            self.pics_list.extend(self.sport_images)
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
        if all_pics_lists["nature_images"] == "down":
            self.pics_list.extend(self.nature_images)
            lists_selected += 1

        if lists_selected == 0:
            all_pics_lists = reset_selected_pics_lists()
            if all_pics_lists["akira_images"] == "down":
                self.pics_list.extend(self.akira_images)
                lists_selected += 1
            if all_pics_lists["car_images"] == "down":
                self.pics_list.extend(self.car_images)
                lists_selected += 1
            if all_pics_lists["sport_images"] == "down":
                self.pics_list.extend(self.sport_images)
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
            if all_pics_lists["nature_images"] == "down":
                self.pics_list.extend(self.nature_images)
                lists_selected += 1

            if lists_selected == 0:
                self.exit_app()

    def load_pictures(self):
        paths = {
            "pics/Akira": self.akira_images,
            "pics/Autos": self.car_images,
            "pics/Sport": self.sport_images,
            "pics/EigeneLandschaften": self.own_landscape_images,
            "pics/Sexy": self.sexy_images,
            "pics/Verschiedenes": self.random_images,
            "pics/Natur": self.nature_images
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
        self.get_running_app().stop()
        sys.exit()


class Player:

    def __init__(self, name):
        self.name = name
        self.score = 0
        self.turns = 0
        self.app = None

    def increase_score(self, points):
        self.score += points

    def increment_turns(self):
        self.turns += 1

    def reset(self):
        self.score = 0
        self.turns = 0
        if not self.app:
            self.app = App.get_running_app()
        if self.name == "Spieler_1":
            self.name = self.app.translator.gettext("player_1_name")
        elif self.name == "Spieler_2":
            self.name = self.app.translator.gettext("player_2_name")


class AI(Player):

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
        self.error = False
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
                        if not card.disabled:
                            if card not in self.known_cards:  # Bevorzugt eine Karte aufdecken, die noch nicht vorher aufgedeckt wurde.
                                first_card = card
                                break
                    if not first_card:
                        first_card = self.find_any_card()

        if first_card:
            self.remember_card(first_card)
            return first_card
        else:
            print("'first_card' nicht gefunden.")
            return None

    def select_second_card(self, first_card):
        print(f"KI sucht zweite Karte")
        self.error = False
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
                self.remember_card(second_card)
                return second_card
            else:
                print("'second_card' nicht gefunden.")
                return self.find_any_card()  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist.
        else:
            second_card = self.find_wrong_card_nearby(first_card, second_card)  # Wenn ein Fehler gemacht werden soll, wird eine falsche Karte in der Nähe der eigentlich richtigen Karte gesucht.
            if second_card:
                self.remember_card(second_card)
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
                self.remember_card(card)
                return card
        for card in self.active_cards:  # Wähle eine zufällige Karte aus, die noch nicht aufgedeckt ist.
            if not card.disabled and not card.flipped:
                self.remember_card(card)
                return card
        return None

    def create_card_grid(self):
        card_grid = [self.game_screen.card_list[i:i + self.cols] for i in range(0, len(self.game_screen.card_list), self.cols)]
        return card_grid

    def reset(self):
        self.score = 0
        self.turns = 0
        self.safe_call_cards = []
        self.known_cards.clear()
        self.game_screen = self.app.root.get_screen("game")
        self.difficulty = self.game_screen.current_difficulty
        self.name = {"easy": "Sepp", "medium": "Guido", "hard": "Juniper", "impossible": "Jasmin"}[self.difficulty]
        self.base_error_probability = {"easy": 35, "medium": 15, "hard": 5, "impossible": 0}[self.difficulty]
        self.save_call_threshold = {"easy": 3, "medium": 2, "hard": 1, "impossible": 0}[self.difficulty]
        self.active_cards.clear()
        self.active_cards = self.game_screen.card_list.copy()
        self.cols = self.game_screen.cols
        self.card_grid = self.create_card_grid()


class Card(ButtonBehavior, Image):

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.flipped = False
        self.background_normal = ""
        self.instance = self
        self.parent = None
        self.game_screen = None
        self.flip_count = 0
        self.default_pic = "pics/Default.png"
        self.keep_ratio = False
        self.allow_stretch = True
        self.move_speed = 2.0  # Für Animation am Spielende
        self.card_size_max = None
        self.card_size_base = None
        self.card_zoom_factor = 10
        self.zoom_event = None
        self.shrink_event = None
        self.zoom_step = 2  # Schrittweite für Zoom von Card
        self.flip_step = None  # Schrittweite für Flip von Card -> wird bei 'clicked' berechnet
        self.flip_steps = 8  # Anzahl von Schritten pro 180-Grad-Flip
        self.pos_step = self.zoom_step // 2  # Schrittweite für die Position von Card
        self.animation_delay = 0.05
        self.flip_duration = self.flip_steps * self.animation_delay + 0.2
        self.starting_pos = (0, 0)
        self.pic = None
        self.pic_source = None
        self.flip_animation = "flip"
        self.source = "pics/Default.png"
        self.pic_background_color = (242, 179, 54)  # Orange
        self.theme_color = "color"

    def clicked(self):
        print(f"card_clicked: Animation: {self.flip_animation}")
        if self.zoom_event:
            Clock.unschedule(self.zoom_event)
            self.size = self.card_size_base
            self.pos = self.starting_pos
        if self.shrink_event:
            Clock.unschedule(self.shrink_event)
            self.size = self.card_size_base
            self.pos = self.starting_pos
        self.zoom_event = None
        self.shrink_event = None
        # Startet das Zoom-Event
        self.flip_step = self.card_size_base[0] / self.flip_steps
        self.zoom_event = Clock.schedule_interval(lambda dt: self.zoom(), self.animation_delay)

    def zoom(self):
        if self.flip_animation == "zoom":
            if self.size[0] < self.card_size_max[0]:
                self.size = (self.size[0] + self.zoom_step, self.size[1] + self.zoom_step)
                self.pos = (self.pos[0] - self.pos_step, self.pos[1] - self.pos_step)
            else:
                if self.zoom_event:
                    Clock.unschedule(self.zoom_event)
                    self.zoom_event = None
                if self.shrink_event:
                    Clock.unschedule(self.shrink_event)

                # Shrink-Event starten
                if self.flipped:
                    self.source = self.pic
                self.shrink_event = Clock.schedule_interval(lambda dt: self.shrink(), self.animation_delay)
        elif self.flip_animation == "flip":
            if self.width > self.zoom_step:
                self.width -= self.flip_step
                self.pos[0] += self.flip_step // 2
            else:
                self.width = 0
                self.source = self.pic if self.source == self.default_pic else self.default_pic
                if self.zoom_event:
                    Clock.unschedule(self.zoom_event)
                if self.shrink_event:
                    Clock.unschedule(self.shrink_event)
                self.shrink_event = Clock.schedule_interval(lambda dt: self.shrink(), self.animation_delay)

    def shrink(self):
        if self.flip_animation == "zoom":
            if self.size[0] > self.card_size_base[0]:
                self.size = (self.size[0] - self.zoom_step, self.size[1] - self.zoom_step)
                self.pos = (self.pos[0] + self.pos_step, self.pos[1] + self.pos_step)
            else:
                if self.shrink_event:
                    Clock.unschedule(self.shrink_event)
                    self.shrink_event = None
                self.size = self.card_size_base
                self.game_screen.update()

        elif self.flip_animation == "flip":
            if self.width < self.card_size_base[0]:
                self.width += self.flip_step
                self.pos[0] -= self.flip_step // 2
            else:
                self.width = self.card_size_base[0]
                if self.shrink_event:
                    Clock.unschedule(self.shrink_event)
                    self.shrink_event = None
                    self.size = self.card_size_base
                    self.pos = self.starting_pos
                    # self.game_screen.update()

    def on_touch_down(self, touch):
        return False

    def on_touch_move(self, touch):
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.flipped:
            super().on_touch_up(touch)
            return False

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
        if theme_color == "light":
            self.pic_background_color = (255, 196, 150)  # Beige
        elif theme_color == "dark":
            self.pic_background_color = (0, 0, 0)  # Black
        elif theme_color == "color":
            self.pic_background_color = (242, 179, 54)  # Orange
        if not DEBUGGING:
            self.default_pic = CARD_COVER_THEME[theme_color]
            if not self.flipped:
                self.source = self.default_pic

        if self.theme_color != theme_color:
            print(f"UpdateTheme Vorher; Theme_Color: {theme_color} / Self.Theme_Color: {self.theme_color}")
            self.theme_color = theme_color
            if self.card_size_base is not None:
                self.pic = self.generate_combined_image(self.pic_source, self.pic_background_color)
                if self.flipped:
                    self.source = self.pic
            print(f"UpdateTheme Nachher; Theme_Color: {theme_color} / Self.Theme_Color: {self.theme_color}")

    def generate_combined_image(self, pic_source, background_color):
        """
        Erzeugt ein zusammengesetztes Bild mit Hintergrund und skaliertem Bild.
        """
        # Zielgröße (z. B. Größe der Karte)
        card_width, card_height = self.card_size_base
        card_width = int(card_width)
        card_height = int(card_height)

        # Erstelle ein neues leeres Bild mit Hintergrundfarbe
        background = PILImage.new("RGBA", (card_width, card_height), background_color)

        # Lade das Originalbild
        original_image = PILImage.open(pic_source)
        img_width, img_height = original_image.size

        # Berechne die Skalierung, um das Seitenverhältnis beizubehalten
        scale = min(card_width / img_width, card_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # Skaliere das Originalbild
        scaled_image = original_image.resize((new_width, new_height), PILImage.LANCZOS)

        # Zentriere das Bild auf dem Hintergrund
        offset_x = (card_width - new_width) // 2
        offset_y = (card_height - new_height) // 2

        # Kombiniere das skalierte Bild mit dem Hintergrund
        background.paste(scaled_image, (offset_x, offset_y), None)

        # Speichere das Bild in einem temporären Pfad
        combined_image_path = f"pics/generated/card_{self.value}.png"
        os.makedirs(os.path.dirname(combined_image_path), exist_ok=True)
        background.save(combined_image_path)

        return combined_image_path


# region Screens #################################################################################################
class GameScreen(Screen):
    layout = ObjectProperty(None)
    memory_grid = ObjectProperty(None)
    scatter = ObjectProperty(None)
    bottom_label = ObjectProperty(None)
    top_label = ObjectProperty(None)
    top_layout = ObjectProperty(None)
    scatter_layout = ObjectProperty(None)
    bottom_layout = ObjectProperty(None)
    game_over_label = ObjectProperty(None)
    menu_btn = ObjectProperty()
    restart_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.size = Window.size
        self.player = Player("Spieler_1")
        self.player2 = Player("Spieler_2")
        self.ai = AI("Sepp", difficulty="easy")
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
        self.board_size = "small"
        self.ai_timeout = 1.0  # Verzögerung der AI-Aktionen (Karten aufdecken)
        self.hide_cards_timeout = 0.8  # Verzögerung beim Zudecken falsch aufgedeckter Karten
        self.touch_delay = 10  # Verzögerung bei Erkennung von 'Touch-Move'
        self.theme_color = "color"
        self.game_over_animation = "None"
        self.load_settings()
        self.card_size_max = None
        self.card_size_base = None
        self.card_zoom_factor = 20
        self.zoom_event = None
        self.shrink_event = None
        self.zoom_step = 2  # Schrittweite für Zoom von Card
        self.pos_step = self.zoom_step // 2  # Schrittweite für die Position von Card
        self.game_over_animation_running = None
        self.hello_there_zoom_step = 0.1
        self.who_starts_screen = None
        self.card_flip_animation = "flip"
        self.flip_duration = 0

    def restart_game(self):
        self.load_settings()
        self.flip_duration = 0
        if self.game_over_animation_running:
            Clock.unschedule(self.game_over_animation_running)
            self.game_over_animation_running = None
        if not self.who_starts_screen:
            self.get_who_starts_screen()
        if self.current_game_mode == "standard":
            self.top_label.font_size = FONT_SIZE_LARGE
            self.top_label.text = self.app.translator.gettext("single_player")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "battle":
            self.top_label.text = self.app.translator.gettext("battle_mode_top_label_start").format(ai_name=self.ai.name, current_player_name=self.current_player.name)
            self.who_starts_screen.init_settings(self.current_game_mode, self.current_difficulty, self.board_size)
            self.app.root.current = "who_starts"
        elif self.current_game_mode == "time_race":
            self.top_label.text = self.app.translator.gettext("time_race")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "duell_standard":
            self.top_label.text = self.app.translator.gettext("duell_mode_top_label_start").format(current_player_name=self.current_player.name)
            self.who_starts_screen.init_settings(self.current_game_mode, self.current_difficulty, self.board_size)
            self.app.root.current = "who_starts"

        self.memory_grid.clear_widgets()
        self.memory_grid.update_rect()
        card_values = list(range(1, (self.cards // 2 + 1))) * 2
        self.card_list = []
        self.card_size_max = None
        self.card_size_base = None
        self.app.load_active_pics_lists()
        shuffle(self.app.pics_list)
        shuffle(card_values)

        for value in card_values:
            card = Card(value)
            self.memory_grid.add_widget(card)
            card.parent = card.get_scatter_parent()
            card.theme_color = self.theme_color
            card.game_screen = self
            card.flip_animation = self.card_flip_animation
            card.source = self.app.pics_list[value - 1]
            card.pic = self.app.pics_list[value - 1]
            card.pic_source = card.pic
            card.background_disabled_normal = card.pic
            card.background_down = card.pic
            if DEBUGGING:
                card.default_pic = card.pic
            else:
                card.default_pic = CARD_COVER_THEME[card.theme_color]
            self.card_list.append(card)

        self.game_over = False
        self.game_running = True
        self.time_race_running = False
        self.first_flip = True
        self.elapsed_time = 0
        self.stop_time_count_up()
        self.update_card_pos_and_size()
        self.reset_widgets()
        if self.current_game_mode != "duell_standard":
            highscores = load_best_scores()
            current_game = f"{self.current_game_mode}_{self.current_difficulty}_{self.board_size}"
            self.current_highscore = highscores[current_game]
            self.update_time_display()
        self.player.reset()
        self.player2.reset()
        self.ai.reset()
        self.current_player = self.player
        self.update()
        self.game_over_label.blend_out = True
        self.game_over_label.hide = True
        self.game_over_label.opacity = 0
        self.game_over_label.font_size = FONT_SIZE_LARGE

    def update(self):
        print("GameScreen: update")
        count_found_cards = 0
        for card in self.card_list:
            if self.flip_duration == 0:
                self.flip_duration = card.flip_duration

            if not card.disabled:
                if card.flipped and not card.shrink_event and not card.zoom_event:
                    card.source = card.pic
                else:
                    if DEBUGGING:
                        card.source = card.pic
                    else:
                        if not card.shrink_event and not card.zoom_event:
                            card.source = card.default_pic
            else:
                if not card.shrink_event and not card.zoom_event:
                    card.source = card.pic
                if not self.game_over:
                    count_found_cards += 1

        if count_found_cards == len(self.card_list) and self.game_running and not self.game_over:
            self.game_over = True
            self.game_running = False
            self.top_label.text = self.app.translator.gettext("game_over")
            self.end_running_game()

        if self.current_game_mode == "standard":
            self.bottom_label.text = self.app.translator.gettext("bottom_standard").format(player_turns=self.player.turns, current_highscore=self.current_highscore)

        elif self.current_game_mode == "duell_standard":
            self.bottom_label.text = self.app.translator.gettext("bottom_duell").format(player_turns=self.player.turns, player_name=self.player.name, player_score=self.player.score,
                                                                                        player_2_name=self.player2.name, player_2_score=self.player2.score)
        elif self.current_game_mode == "battle":
            self.bottom_label.text = self.app.translator.gettext("bottom_battle").format(player_score=self.player.score, current_highscore=self.current_highscore)

        elif self.current_game_mode == "time_race":
            pass
        self.menu_btn.text = self.app.translator.gettext("menu")
        self.restart_btn.text = self.app.translator.gettext("restart")

    def update_card_pos_and_size(self):
        # Fenstergröße und Kartenanzahl ermitteln
        window_width, window_height = Window.size
        window_height = window_height * 0.8
        total_cards = len(self.card_list)
        cols = 4
        rows = 4
        if total_cards == BOARD_SIZES["small"]:
            cols = 4
            rows = 4
        elif total_cards == BOARD_SIZES["medium"]:
            cols = 4
            rows = 6
        elif total_cards == BOARD_SIZES["big"]:
            cols = 5
            rows = 6
        self.cols = cols
        # Berechne die Kartengröße auf Basis der Spalten und Reihen
        card_width = window_width / cols
        card_height = window_height / rows
        self.card_size_base = (card_width, card_height)
        self.card_size_max = (card_width + self.card_zoom_factor, card_height + self.card_zoom_factor)
        # Weise jeder Karte die berechnete Größe und Position zu
        for i, card in enumerate(self.card_list):
            card.size_hint = (None, None)
            card.size = (card_width, card_height)
            card.card_size_max = self.card_size_max
            card.card_size_base = self.card_size_base

            # Kartenposition auf Basis von Spalte und Reihe bestimmen
            row = i // cols
            col = i % cols
            card.pos = (col * card_width, window_height - (row + 1) * card_height)
            card.starting_pos = (col * card_width, window_height - (row + 1) * card_height)
            card.update_theme(self.theme_color)
            card.pic = card.generate_combined_image(card.pic_source, card.pic_background_color)
            card.flip_animation = self.card_flip_animation

    def on_touch_down(self, touch):
        self.active_touches.add(touch.uid)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.uid in self.active_touches:
            self.active_touches.remove(touch.uid)
        return super().on_touch_up(touch)

    def flip_card(self, card):
        print("flip_card")
        card.clicked()
        first_card = card
        first_card.flipped = True
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
                            if self.card_flip_animation == "flip":
                                Clock.schedule_once(lambda dt: self.ai_turn(players_last_cards), self.ai_timeout + self.flip_duration)
                            else:
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
                        if self.card_flip_animation == "flip":
                            Clock.schedule_once(lambda dt: self.ai_turn(players_last_cards), self.ai_timeout + self.flip_duration)
                        else:
                            Clock.schedule_once(lambda dt: self.ai_turn(players_last_cards), self.ai_timeout)
        self.update()

    def kill_cards(self, first_card, second_card):
        print("kill_cards")
        for card in self.card_list:
            if card == first_card or card == second_card:
                card.disabled = True
                card.flipped = True
                print(f"Karte {card.value} disabled.")
        self.input_enabled = True
        self.ai.remove_pair(first_card)

    def hide_cards(self, first_card, second_card):
        print("GameScreen: hide_cards")
        for card in self.card_list:
            if card == first_card or card == second_card:
                card.clicked()
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
        self.top_label.text = self.app.translator.gettext("current_player").format(current_player_name=self.current_player.name)

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
        self.bottom_label.text = self.app.translator.gettext("bottom_time_race").format(elapsed_time=self.elapsed_time, current_highscore=self.current_highscore)

    def load_settings(self):
        settings = load_settings()
        self.game_over_animation = settings["game_over_animation"]
        self.card_flip_animation = settings["card_flip_animation"]
        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]
        theme = settings["theme"]
        self.theme_color = get_theme_color(theme)
        self.memory_grid.redraw(self.theme_color)

    def on_pre_leave(self, *args):
        if self.current_game_mode == "time_race" and self.time_race_running:
            self.stop_time_count_up()
        return super().on_pre_leave()

    def on_pre_enter(self, *args):
        print("On_Pre_Enter_Game_Screen")
        self.load_settings()
        self.reset_widgets()
        self.update_card_pos_and_size()
        self.update()
        if self.current_game_mode == "time_race" and self.time_race_running:
            self.start_time_count_up()
        return super().on_pre_enter()

    def end_running_game(self):
        score = self.player.turns
        highscore_valid = False
        if self.current_game_mode == "standard":
            score = self.player.turns
            if score >= self.cards // 2:
                highscore_valid = True
        elif self.current_game_mode == "battle":
            score = self.player.score
            highscore_valid = True
        elif self.current_game_mode == "time_race":
            score = self.elapsed_time
            if score > 2:
                highscore_valid = True
        elif self.current_game_mode == "duell_standard":
            score_1 = self.player.score
            score_2 = self.player2.score
            if score_1 > score_2:
                score = score_1
            else:
                score = score_2
            highscore_valid = True

        if highscore_valid:
            highscore = update_best_scores(self.current_game_mode, self.current_difficulty, self.board_size, score)
            if highscore:
                self.top_label.text = self.app.translator.gettext("new_highscore").format(player_score=score)
                self.current_highscore = score
                if self.current_game_mode != "time_race":
                    self.game_over_label.text = self.app.translator.gettext("new_highscore").format(player_score=score)
                else:
                    self.game_over_label.text = self.app.translator.gettext("new_highscore_time_race").format(elapsed_time=score)
                self.game_over_label.hide = False
                self.game_over_label.opacity = 1
                self.game_over_label.redraw()
                self.start_game_over_animation()
            else:
                if self.current_game_mode == "duell_standard":
                    if self.player.score > self.player2.score:
                        self.top_label.text = self.app.translator.gettext("victory_player_1").format(player_1_name=self.player.name)
                        game_over_label_text = self.app.translator.gettext("victory_player_1").format(player_1_name=self.player.name)
                    elif self.player.score == self.player2.score:
                        self.top_label.text = self.app.translator.gettext("draw")
                        game_over_label_text = self.app.translator.gettext("draw")
                    else:
                        self.top_label.text = self.app.translator.gettext("victory_player_2").format(player_2_name=self.player2.name)
                        game_over_label_text = self.app.translator.gettext("victory_player_2").format(player_2_name=self.player2.name)
                else:
                    self.top_label.text = self.app.translator.gettext("no_new_highscore")
                    game_over_label_text = self.app.translator.gettext("no_new_highscore")

                self.game_over_label.text = game_over_label_text
                self.game_over_label.hide = False
                self.game_over_label.opacity = 1
                self.game_over_label.redraw()
                self.start_game_over_animation()
        self.update_time_display()

        self.current_player = self.player
        Clock.unschedule(self.update_time)
        self.time_race_running = False
        self.game_running = False

    def start_game_over_animation(self):
        if not self.game_over_animation_running:
            if self.game_over_animation == "FreeFall":
                self.game_over_animation_running = Clock.schedule_interval(lambda dt: self.free_fall(), 0.05)
            elif self.game_over_animation == "ByeBye":
                self.game_over_animation_running = Clock.schedule_interval(lambda dt: self.bye_bye(), 0.05)
            elif self.game_over_animation == "HelloThere":
                self.game_over_animation_running = Clock.schedule_interval(lambda dt: self.hello_there(), 0.05)

    def free_fall(self):
        cards_falling = 0
        for card in self.card_list:
            if card.pos[1] > - card.size[1] - (Window.size[1] * 0.1):
                card.pos[1] -= card.move_speed
                card.move_speed += 1
                cards_falling += 1
        if cards_falling == 0:
            if self.game_over_animation_running:
                Clock.unschedule(self.game_over_animation_running)
                self.game_over_animation_running = None

    def bye_bye(self):
        cards_moving = 0
        for card in self.card_list:
            if card.pos[0] > - card.size[0] - Window.size[0]:
                card.pos[0] -= card.move_speed
                card.move_speed += 1
                cards_moving += 1
        if cards_moving == 0:
            if self.game_over_animation_running:
                Clock.unschedule(self.game_over_animation_running)
                self.game_over_animation_running = None

    def hello_there(self):
        if self.scatter.scale < self.scatter.scale_max:
            self.scatter.scale += self.hello_there_zoom_step
        if self.scatter.scale > self.scatter.scale_max:
            self.scatter.scale = self.scatter.scale_max
        if self.scatter.scale == self.scatter.scale_max:
            Clock.unschedule(self.game_over_animation_running)
            print("GameOverAnimation beendet ############################################")
            self.game_over_animation_running = None

    def get_who_starts_screen(self):
        self.who_starts_screen = self.app.root.get_screen("who_starts")


class MainMenuScreen(Screen):
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
        self.app = None

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
        self.top_label.text = self.app.translator.gettext("main_menu")
        self.continue_button.text = self.app.translator.gettext("continue_game")
        self.standard_button.text = self.app.translator.gettext("standard_game")
        self.time_button.text = self.app.translator.gettext("time_mode")
        self.multiplayer_button.text = self.app.translator.gettext("multiplayer_mode")
        self.settings_button.text = self.app.translator.gettext("settings")
        self.exit_button.text = self.app.translator.gettext("exit")

    def on_pre_enter(self, *args):
        self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        app_root = self.app.root
        if app_root:
            game_screen = app_root.get_screen("game")
            self.update_continue_button(game_screen.game_running)
        self.redraw()


class StandardModeScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    small_button = ObjectProperty()
    medium_button = ObjectProperty()
    large_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
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
        self.top_label.text = self.app.translator.gettext("standard_game")
        self.back_button.text = self.app.translator.gettext("back")
        self.small_button.text = self.app.translator.gettext("small")
        self.medium_button.text = self.app.translator.gettext("medium")
        self.large_button.text = self.app.translator.gettext("large")

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        self.redraw()


class TimeModeScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    time_race_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
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
        self.top_label.text = self.app.translator.gettext("time_mode")
        self.back_button.text = self.app.translator.gettext("back")
        self.time_race_btn.text = self.app.translator.gettext("time_race")

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        self.redraw()


class TimeRaceScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    small_button = ObjectProperty()
    medium_button = ObjectProperty()
    large_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
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
        self.top_label.text = self.app.translator.gettext("time_race")
        self.back_button.text = self.app.translator.gettext("back")
        self.small_button.text = self.app.translator.gettext("small")
        self.medium_button.text = self.app.translator.gettext("medium")
        self.large_button.text = self.app.translator.gettext("large")

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        self.redraw()


class MultiplayerScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    duell_btn = ObjectProperty()
    battle_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
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
        self.top_label.text = self.app.translator.gettext("multiplayer_mode")
        self.back_button.text = self.app.translator.gettext("back")
        self.duell_btn.text = self.app.translator.gettext("duell_mode")
        self.battle_btn.text = self.app.translator.gettext("battle_mode")

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        self.redraw()


class DuellModeScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    small_button = ObjectProperty()
    medium_button = ObjectProperty()
    large_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_board_size = "small"
        self.current_difficulty = "easy"
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
        self.top_label.text = self.app.translator.gettext("duell_mode")
        self.back_button.text = self.app.translator.gettext("back")
        self.small_button.text = self.app.translator.gettext("small")
        self.medium_button.text = self.app.translator.gettext("medium")
        self.large_button.text = self.app.translator.gettext("large")

    def init_new_game(self, mode):
        app = App.get_running_app()
        app.start_new_game(self.current_board_size, mode, self.current_difficulty)

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.theme_color = self.app.theme_color
        self.redraw()


class BattleModeScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    easy_btn = ObjectProperty(None)
    medium_btn = ObjectProperty(None)
    hard_btn = ObjectProperty(None)
    impossible_btn = ObjectProperty(None)
    small_button = ObjectProperty(None)
    medium_button = ObjectProperty(None)
    large_button = ObjectProperty(None)
    start_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.update_diff_buttons, 0.1)
        self.easy_btn.disabled = True
        self.current_difficulty = "easy"
        self.small_button.disabled = True
        self.current_board_size = "small"
        self.button_list = [self.easy_btn, self.medium_btn, self.hard_btn, self.impossible_btn, self.small_button, self.medium_button, self.large_button]
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.theme = "color"
        self.theme_color = "color"
        self.app = None

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.top_label.text = self.app.translator.gettext("battle_mode")
        self.back_button.text = self.app.translator.gettext("back")
        self.small_button.text = self.app.translator.gettext("small")
        self.medium_button.text = self.app.translator.gettext("medium")
        self.large_button.text = self.app.translator.gettext("large")
        self.easy_btn.text = self.app.translator.gettext("easy")
        self.medium_btn.text = self.app.translator.gettext("medium")
        self.hard_btn.text = self.app.translator.gettext("hard")
        self.impossible_btn.text = self.app.translator.gettext("impossible")
        self.start_btn.text = self.app.translator.gettext("start_game")

    def init_new_game(self, mode):
        if not self.app:
            self.app = App.get_running_app()
        self.app.start_new_game(self.current_board_size, mode, self.current_difficulty)

    def update_diff_buttons(self, pushed_button=1):
        if pushed_button == 1:
            self.easy_btn.disabled = True
            self.current_difficulty = "easy"
            self.medium_btn.disabled = False
            self.hard_btn.disabled = False
            self.impossible_btn.disabled = False
        elif pushed_button == 2:
            self.easy_btn.disabled = False
            self.medium_btn.disabled = True
            self.current_difficulty = "medium"
            self.hard_btn.disabled = False
            self.impossible_btn.disabled = False
        elif pushed_button == 3:
            self.easy_btn.disabled = False
            self.medium_btn.disabled = False
            self.hard_btn.disabled = True
            self.current_difficulty = "hard"
            self.impossible_btn.disabled = False
        elif pushed_button == 4:
            self.easy_btn.disabled = False
            self.medium_btn.disabled = False
            self.hard_btn.disabled = False
            self.impossible_btn.disabled = True
            self.current_difficulty = "impossible"
        for button in self.button_list:
            button.redraw()

    def update_board_size_buttons(self, pushed_button=1):
        if pushed_button == 1:
            self.small_button.disabled = True
            self.current_board_size = "small"
            self.medium_button.disabled = False
            self.large_button.disabled = False
        elif pushed_button == 2:
            self.small_button.disabled = False
            self.medium_button.disabled = True
            self.current_board_size = "medium"
            self.large_button.disabled = False
        elif pushed_button == 3:
            self.small_button.disabled = False
            self.medium_button.disabled = False
            self.large_button.disabled = True
            self.current_board_size = "big"
        for button in self.button_list:
            button.redraw()

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        self.redraw()


class SettingsScreen(Screen):

    top_label = ObjectProperty(None)
    theme_label = ObjectProperty(None)
    light_theme_button = ObjectProperty(None)
    dark_theme_button = ObjectProperty(None)
    system_theme_button = ObjectProperty(None)
    color_theme_button = ObjectProperty(None)
    game_over_animation_label = ObjectProperty(None)
    no_game_over_animation_button = ObjectProperty(None)
    free_fall_game_over_animation_button = ObjectProperty(None)
    bye_bye_game_over_animation_button = ObjectProperty(None)
    hello_there_game_over_animation_button = ObjectProperty(None)
    touch_delay_label = ObjectProperty(None)
    ai_timeout_label = ObjectProperty(None)
    hide_cards_timeout_label = ObjectProperty(None)
    card_flip_animation_label = ObjectProperty(None)
    card_flip_animation_flip_button = ObjectProperty(None)
    card_flip_animation_zoom_button = ObjectProperty(None)
    lang_label = ObjectProperty(None)
    lang_btn_en = ObjectProperty(None)
    lang_btn_de = ObjectProperty(None)
    back_button = ObjectProperty()
    pic_select_btn = ObjectProperty()
    highscores_label = ObjectProperty()
    highscores_reset_btn = ObjectProperty()
    reset_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = None
        self.game_screen = None
        self.theme = "color"  # Eigentlicher 'Theme'-Name (Unterscheidung wegen 'System-Theme')
        self.theme_color = "color"  # Tatsächliche Theme-'Farbe'
        self.card_flip_animation = "flip"
        self.game_over_animation = "None"
        self.touch_delay = 10
        self.ai_timeout = 1.0
        self.hide_cards_timeout = 0.8
        self.load_settings()
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.lang = "en"

    def on_pre_enter(self):
        if not self.app:
            self.app = App.get_running_app()
        self.load_settings()
        self.change_hide_cards_timeout_label_text()
        self.change_ai_timeout_label_text()
        self.change_touch_delay_label_text()
        self.change_button_states(self.theme, self.game_over_animation)
        self.redraw()

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.top_label.text = self.app.translator.gettext("settings")
        self.theme_label.text = self.app.translator.gettext("theme")
        self.light_theme_button.text = self.app.translator.gettext("light")
        self.dark_theme_button.text = self.app.translator.gettext("dark")
        self.system_theme_button.text = self.app.translator.gettext("system")
        self.color_theme_button.text = self.app.translator.gettext("color")
        self.game_over_animation_label.text = self.app.translator.gettext("game_over_animation_label")
        self.no_game_over_animation_button.text = self.app.translator.gettext("no_animation")
        self.free_fall_game_over_animation_button.text = self.app.translator.gettext("free_fall")
        self.bye_bye_game_over_animation_button.text = self.app.translator.gettext("bye_bye")
        self.hello_there_game_over_animation_button.text = self.app.translator.gettext("hello_there")
        self.touch_delay_label.text = self.app.translator.gettext("touch_delay_label").format(touch_delay=self.touch_delay)
        self.ai_timeout_label.text = self.app.translator.gettext("ai_timeout_label").format(ai_timeout=self.ai_timeout)
        self.hide_cards_timeout_label.text = self.app.translator.gettext("hide_cards_timeout_label").format(hide_cards_timeout=self.hide_cards_timeout)
        self.card_flip_animation_label.text = self.app.translator.gettext("card_flip_animation_label")
        self.card_flip_animation_flip_button.text = self.app.translator.gettext("flip_animation_btn")
        self.card_flip_animation_zoom_button.text = self.app.translator.gettext("zoom_animation_btn")
        self.lang_label.text = self.app.translator.gettext("language")
        self.lang_btn_en.text = self.app.translator.gettext("english")
        self.lang_btn_de.text = self.app.translator.gettext("deutsch")
        self.back_button.text = self.app.translator.gettext("back")
        self.pic_select_btn.text = self.app.translator.gettext("pic_select")
        self.highscores_label.text = self.app.translator.gettext("highscores")
        self.highscores_reset_btn.text = self.app.translator.gettext("reset")
        self.reset_btn.text = self.app.translator.gettext("reset")

    def load_settings(self):
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)
        self.card_flip_animation = settings["card_flip_animation"]
        self.game_over_animation = settings["game_over_animation"]
        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]
        self.lang = settings["lang"]

    def update_lang_buttons(self, button_id):
        if button_id == 0:
            self.lang_btn_en.disabled = True
            self.lang_btn_de.disabled = False
            self.lang = "en"
            self.app.translator.set_language(self.lang)
        elif button_id == 1:
            self.lang_btn_en.disabled = False
            self.lang_btn_de.disabled = True
            self.lang = "de"
            self.app.translator.set_language(self.lang)
        new_setting = ("lang", self.lang)
        save_settings(new_setting)

        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)
        self.redraw()

    def change_button_states(self, theme, game_over_animation):
        theme_button = 0
        if theme == "light":
            self.light_theme_button.disabled = True
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
            theme_button = 0
        elif theme == "dark":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = True
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = False
            theme_button = 1
        elif theme == "system":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = True
            self.color_theme_button.disabled = False
            theme_button = 2
        elif theme == "color":
            self.light_theme_button.disabled = False
            self.dark_theme_button.disabled = False
            self.system_theme_button.disabled = False
            self.color_theme_button.disabled = True
            theme_button = 3
        self.update_theme_buttons(theme_button)
        game_over_animation_button = 0
        if game_over_animation == "None":
            game_over_animation_button = 0
        elif game_over_animation == "FreeFall":
            game_over_animation_button = 1
        elif game_over_animation == "ByeBye":
            game_over_animation_button = 2
        elif game_over_animation == "HelloThere":
            game_over_animation_button = 3
        self.update_game_over_animation_buttons(game_over_animation_button)
        card_flip_button = 0
        if self.card_flip_animation == "flip":
            card_flip_button = 0
        elif self.card_flip_animation == "zoom":
            card_flip_button = 1
        self.update_card_flip_animation_buttons(card_flip_button)
        lang_button = 0
        if self.lang == "de":
            lang_button = 1
        self.update_lang_buttons(lang_button)

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
        self.redraw()

    def update_card_flip_animation_buttons(self, button_id):
        if button_id == 0:
            self.card_flip_animation_flip_button.disabled = True
            self.card_flip_animation_zoom_button.disabled = False
            self.card_flip_animation = "flip"
        elif button_id == 1:
            self.card_flip_animation_flip_button.disabled = False
            self.card_flip_animation_zoom_button.disabled = True
            self.card_flip_animation = "zoom"

        new_setting = ("card_flip_animation", self.card_flip_animation)
        save_settings(new_setting)

        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)

    def update_game_over_animation_buttons(self, button_id):
        new_setting = ("game_over_animation", "None")
        if button_id == 0:
            self.no_game_over_animation_button.disabled = True
            self.free_fall_game_over_animation_button.disabled = False
            self.bye_bye_game_over_animation_button.disabled = False
            self.hello_there_game_over_animation_button.disabled = False
            self.game_over_animation = "None"
            new_setting = ("game_over_animation", self.game_over_animation)
        elif button_id == 1:
            self.no_game_over_animation_button.disabled = False
            self.free_fall_game_over_animation_button.disabled = True
            self.bye_bye_game_over_animation_button.disabled = False
            self.hello_there_game_over_animation_button.disabled = False
            self.game_over_animation = "FreeFall"
            new_setting = ("game_over_animation", self.game_over_animation)
        elif button_id == 2:
            self.no_game_over_animation_button.disabled = False
            self.free_fall_game_over_animation_button.disabled = False
            self.bye_bye_game_over_animation_button.disabled = True
            self.hello_there_game_over_animation_button.disabled = False
            self.game_over_animation = "ByeBye"
            new_setting = ("game_over_animation", self.game_over_animation)
        elif button_id == 3:
            self.no_game_over_animation_button.disabled = False
            self.free_fall_game_over_animation_button.disabled = False
            self.bye_bye_game_over_animation_button.disabled = False
            self.hello_there_game_over_animation_button.disabled = True
            self.game_over_animation = "HelloThere"
            new_setting = ("game_over_animation", self.game_over_animation)
        save_settings(new_setting)

        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)

    def change_touch_delay_label_text(self):
        self.touch_delay_label.text = self.app.translator.gettext("touch_delay_label").format(touch_delay=self.touch_delay)

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
        self.ai_timeout_label.text = self.app.translator.gettext("ai_timeout_label").format(ai_timeout=self.ai_timeout)

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
        self.hide_cards_timeout_label.text = self.app.translator.gettext("hide_cards_timeout_label").format(hide_cards_timeout=self.hide_cards_timeout)

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

    def reset_highscores(self):
        reset_highscores()
        self.redraw()

    def reset_settings(self):
        settings = reset_settings()  # load default settings
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        if self.app is not None:
            self.app.change_theme_color(self.theme_color)
        else:
            self.app = App.get_running_app()
            self.app.change_theme_color(self.theme_color)
        self.card_flip_animation = settings["card_flip_animation"]
        self.game_over_animation = settings["game_over_animation"]
        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]
        self.lang = settings["lang"]
        self.on_pre_enter()


class PicsSelectScreen(Screen):
    top_label = ObjectProperty()
    back_button = ObjectProperty()
    akira_label = ObjectProperty()
    akira_box = ObjectProperty()
    cars_label = ObjectProperty()
    cars_box = ObjectProperty()
    sport_label = ObjectProperty()
    sport_box = ObjectProperty()
    own_landscapes_label = ObjectProperty()
    own_landscapes_box = ObjectProperty()
    sexy_label = ObjectProperty()
    sexy_box = ObjectProperty()
    random_label = ObjectProperty()
    random_box = ObjectProperty()
    nature_label = ObjectProperty()
    nature_box = ObjectProperty()
    reset_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.akira_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.cars_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.sport_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.own_landscapes_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.sexy_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.random_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.nature_label.redraw(LIGHT_BLUE, BEIGE, True, BEIGE, 5)
        self.checkbox_list = [self.akira_box, self.cars_box, self.sport_box, self.own_landscapes_box, self.sexy_box, self.random_box, self.nature_box]
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
        self.top_label.text = self.app.translator.gettext("pic_select")
        self.back_button.text = self.app.translator.gettext("back")
        self.akira_label.text = self.app.translator.gettext("akira_label")
        self.cars_label.text = self.app.translator.gettext("cars_label")
        self.sport_label.text = self.app.translator.gettext("sport_label")
        self.own_landscapes_label.text = self.app.translator.gettext("own_landscapes_label")
        self.sexy_label.text = self.app.translator.gettext("sexy_label")
        self.random_label.text = self.app.translator.gettext("random_label")
        self.nature_label.text = self.app.translator.gettext("nature_label")

    def save_pics_lists_screen(self):
        print("Save Pics Lists")
        pics_selected = 0
        if self.akira_box.state == "down":
            pics_selected += 1
        if self.cars_box.state == "down":
            pics_selected += 1
        if self.sport_box.state == "down":
            pics_selected += 1
        if self.own_landscapes_box.state == "down":
            pics_selected += 1
        if self.sexy_box.state == "down":
            pics_selected += 1
        if self.random_box.state == "down":
            pics_selected += 1
        if self.nature_box.state == "down":
            pics_selected += 1

        if pics_selected > 0:
            checkboxes = {
                "akira_images": self.akira_box.state,
                "car_images": self.cars_box.state,
                "sport_images": self.sport_box.state,
                "own_landscape_images": self.own_landscapes_box.state,
                "sexy_images": self.sexy_box.state,
                "random_images": self.random_box.state,
                "nature_images": self.nature_box.state
            }

            print("Mindestens eine Checkbox ausgewählt")
            save_pics_lists(checkboxes)
        else:
            print("Keine Checkbox ausgewählt")
            reset_selected_pics_lists()
            self.load_checkbox_statuses()

    def load_checkbox_statuses(self):
        print("load_checkbox_statuses")
        checkboxes = load_pics_lists()
        self.akira_box.state = checkboxes["akira_images"]
        self.cars_box.state = checkboxes["car_images"]
        self.sport_box.state = checkboxes["sport_images"]
        self.own_landscapes_box.state = checkboxes["own_landscape_images"]
        self.sexy_box.state = checkboxes["sexy_images"]
        self.random_box.state = checkboxes["random_images"]
        self.nature_box.state = checkboxes["nature_images"]

    def update_checkbox_theme(self):
        for box in self.checkbox_list:
            if self.theme_color == "color":
                box.background_checkbox_normal = "gfx/misc/checkbox_unchecked_color.png"
                box.background_checkbox_down = "gfx/misc/checkbox_checked_color.png"
            elif self.theme_color == "light":
                box.background_checkbox_normal = "gfx/misc/checkbox_unchecked_light.png"
                box.background_checkbox_down = "gfx/misc/checkbox_checked_light.png"
            elif self.theme_color == "dark":
                box.background_checkbox_normal = "gfx/misc/checkbox_unchecked_dark.png"
                box.background_checkbox_down = "gfx/misc/checkbox_checked_dark.png"

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.load_checkbox_statuses()
        settings = load_settings()
        theme = settings["theme"]
        self.theme_color = get_theme_color(theme)
        self.update_checkbox_theme()
        self.redraw()

    def reset_checkboxes(self):
        checkboxes = reset_selected_pics_lists()  # Load Default Settings
        self.akira_box.state = checkboxes["akira_images"]
        self.cars_box.state = checkboxes["car_images"]
        self.sport_box.state = checkboxes["sport_images"]
        self.own_landscapes_box.state = checkboxes["own_landscape_images"]
        self.sexy_box.state = checkboxes["sexy_images"]
        self.random_box.state = checkboxes["random_images"]
        self.nature_box.state = checkboxes["nature_images"]

        self.save_pics_lists_screen()
        self.redraw()


class WhoStartsScreen(Screen):
    top_label = ObjectProperty(None)
    back_button = ObjectProperty()
    head_button = ObjectProperty(None)
    tail_button = ObjectProperty(None)
    coin = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_difficulty = "easy"
        self.current_board_size = "small"
        self.current_game_mode = "battle"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.theme = "color"
        self.theme_color = "color"
        self.head_button.background_normal = "gfx/misc/Kopf.png"
        self.tail_button.background_normal = "gfx/misc/Zahl.png"
        self.app = None
        self.game_screen = None
        self.duell_screen = None
        self.pick = None

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_pre_enter(self, *args):
        if not self.app:
            self.app = App.get_running_app()
        self.redraw()

    def redraw(self):
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.top_label.text = self.app.translator.gettext("who_starts_label")
        self.back_button.text = self.app.translator.gettext("back")
        self.head_button.text = self.app.translator.gettext("heads")
        self.tail_button.text = self.app.translator.gettext("tails")

    def init_settings(self, mode, difficulty, board_size):
        self.current_board_size = board_size
        self.current_difficulty = difficulty
        self.current_game_mode = mode
        self.top_label.text = "Wer beginnt? Wähle 'Kopf' oder 'Zahl'."
        if not self.app:
            self.app = App.get_running_app()
        if not self.game_screen:
            self.game_screen = self.app.root.get_screen("game")

    def pick_side(self, coin):
        if coin != self.pick:
            self.game_screen.switch_player()
            if self.game_screen.current_player == self.game_screen.ai:
                first_card = self.game_screen.card_list[1]
                second_card = self.game_screen.card_list[2]
                players_last_cards = (first_card, second_card)
                Clock.schedule_once(lambda dt: self.game_screen.ai_turn(players_last_cards), self.game_screen.ai_timeout + 2)
        self.top_label.text = self.app.translator.gettext("who_starts_start_message").format(current_player=self.game_screen.current_player.name)
        Clock.schedule_once(lambda dt: self.switch_to_game(), 1.5)

    def switch_to_game(self):
        self.app.root.current = "game"

    def on_leave(self, *args):
        self.coin.disrupt_flip()

# endregion


# region Functions #######################################################################################
def start_app():
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
