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
        self.who_starts_screen = None
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
        self.root.current = "main_menu"
        Clock.schedule_once(self.force_redraw, 0.1)  # Eventuell eine leichte Verzögerung hinzufügen
        self.game_screen = self.root.get_screen("game")
        self.load_pictures()
        Clock.schedule_once(self.load_settings, .2)
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
        self.get_running_app().stop()
        sys.exit()


class Player:

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
        return card_grid

    def reset(self):
        self.score = 0
        self.turns = 0
        self.safe_call_cards = []
        self.known_cards.clear()
        self.game_screen = self.app.root.get_screen("game")
        self.difficulty = self.game_screen.current_difficulty
        self.name = {"easy": "Sepp", "medium": "Maja", "hard": "Juniper", "impossible": "Jasmin"}[self.difficulty]
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
        self.flip_step = 8  # Schrittweite für Flip von Card
        self.pos_step = self.zoom_step // 2  # Schrittweite für die Position von Card
        self.starting_pos = (0, 0)
        self.pic = None
        self.flip_animation = "flip"

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
        # Startet das Zoom-Event
        self.zoom_event = Clock.schedule_interval(lambda dt: self.zoom(), 0.01)

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
                self.shrink_event = Clock.schedule_interval(lambda dt: self.shrink(), 0.01)
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
                self.shrink_event = Clock.schedule_interval(lambda dt: self.shrink(), 0.01)

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
                    self.game_screen.update()

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
        self.default_pic = CARD_COVER_THEME[theme_color]


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

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.size = Window.size
        self.player = Player("Spieler 1")
        self.player2 = Player("Spieler 2")
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

    def restart_game(self):
        self.load_settings()
        self.game_over_label.hide = True
        if self.game_over_animation_running:
            Clock.unschedule(self.game_over_animation_running)
            self.game_over_animation_running = None
        if not self.who_starts_screen:
            self.get_who_starts_screen()
        if self.current_game_mode == "standard":
            self.top_label.font_size = FONT_SIZE_LARGE
            self.change_top_label_text(f"Einzelspieler")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "battle":
            self.change_top_label_text(f"Spiel gegen {self.ai.name}\nAktueller Spieler: {self.current_player.name}.")
            self.who_starts_screen.init_settings(self.current_game_mode, self.current_difficulty, self.board_size)
            self.app.root.current = "who_starts"
        elif self.current_game_mode == "time_race":
            self.change_top_label_text("Zeitrennen")
            self.current_difficulty = "easy"
        elif self.current_game_mode == "duell_standard":
            self.change_top_label_text(f"Duell\nAktueller Spieler: {self.current_player.name}")
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
            card.game_screen = self
            card.flip_animation = self.card_flip_animation
            card.source = self.app.pics_list[value - 1]
            card.pic = self.app.pics_list[value - 1]
            card.background_disabled_normal = card.pic
            card.background_down = card.pic
            if DEBUGGING:
                card.default_pic = card.pic
            else:
                card.default_pic = CARD_COVER_THEME[self.theme_color]
            self.card_list.append(card)

        self.game_over = False
        self.game_running = True
        self.time_race_running = False
        self.first_flip = True
        self.elapsed_time = 0
        self.stop_time_count_up()
        self.update_card_pos_and_size()
        self.reset_widgets()
        self.game_over_label.hide = True
        self.game_over_label.font_size = FONT_SIZE_LARGE
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

    def update(self):
        print("GameScreen: update")

        count_found_cards = 0
        for card in self.card_list:
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
                if card.flipped and not card.shrink_event and not card.zoom_event:
                    card.source = card.pic
                count_found_cards += 1
            card.text = str(card.value)

        if count_found_cards == len(self.card_list) and not self.game_over:
            self.game_over = True
            self.game_running = False
            self.top_label.text = "Game Over"

        if self.game_over:
            score = 0
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
                highscore_valid = True

            if highscore_valid:
                highscore = update_best_scores(self.current_game_mode, self.current_difficulty, self.board_size, score)
                if highscore:
                    self.change_top_label_text("Neuer Highscore =)")
                    self.current_highscore = score
                    if self.current_game_mode != "time_race":
                        self.game_over_label.text = f"Neuer Highscore =)\nPunkte: {score}"
                    else:
                        self.game_over_label.text = f"Neuer Highscore =)\nBenötigte Zeit: {score} Sekunden"
                    self.game_over_label.hide = False
                    self.game_over_label.opacity = 1
                    self.game_over_label.redraw()
                    self.start_game_over_animation()
                else:
                    if self.current_game_mode == "duell_standard":
                        if self.player.score > self.player2.score:
                            self.change_top_label_text("Spieler_1 hat gewonnen :-)")
                            game_over_label_text = f"{self.player.name} hat gewonnen :-)"
                        elif self.player.score == self.player2.score:
                            self.change_top_label_text("Unentschieden :-O")
                            game_over_label_text = "Unentschieden :-O"
                        else:
                            self.change_top_label_text("Spieler_2 hat gewonnen :-)")
                            game_over_label_text = f"{self.player2.name} hat gewonnen :-)"
                    else:
                        self.change_top_label_text("Keine neue Bestleistung... Vielleicht nächstes Mal ;-)")
                        game_over_label_text = "Keine neue Bestleistung... Vielleicht nächstes Mal ;-)"

                    self.game_over_label.text = game_over_label_text
                    self.game_over_label.hide = False
                    self.game_over_label.opacity = 1
                    self.game_over_label.redraw()
                    self.start_game_over_animation()
            self.update_time_display()

            self.current_player = self.player
            Clock.unschedule(self.update_time)
            self.time_race_running = False

        if self.current_game_mode == "standard":
            self.bottom_label.text = f"Runde: {self.player.turns}\nRekord: {self.current_highscore}"

        elif self.current_game_mode == "duell_standard":
            self.bottom_label.text = f"Runde: {self.player.turns}\n{self.player.name}: {self.player.score}\n{self.player2.name}: {self.player2.score}"
        elif self.current_game_mode == "battle":
            self.bottom_label.text = f"Punkte: {self.player.score}\nRekord: {self.current_highscore}"

        elif self.current_game_mode == "time_race":
            pass

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
        # first_card.source = first_card.pic
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
        self.game_over_animation = settings["game_over_animation"]
        self.card_flip_animation = settings["card_flip_animation"]
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
        for card in self.card_list:
            card.flip_animation = self.card_flip_animation
        self.reset_widgets()
        if self.current_game_mode == "time_race" and self.time_race_running:
            self.start_time_count_up()
        return super().on_pre_enter()

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    def init_new_game(self, mode):
        app = App.get_running_app()
        app.start_new_game(self.current_board_size, mode, self.current_difficulty)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.theme_color = app.theme_color
        self.redraw()


class BattleModeScreen(Screen):

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
        self.current_board_size = "small"
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
            self.current_board_size = "small"
            self.medium.disabled = False
            self.big.disabled = False
        elif pushed_button == 2:
            self.small.disabled = False
            self.medium.disabled = True
            self.current_board_size = "medium"
            self.big.disabled = False
        elif pushed_button == 3:
            self.small.disabled = False
            self.medium.disabled = False
            self.big.disabled = True
            self.current_board_size = "big"
        for button in self.button_list:
            button.redraw()

    def on_pre_enter(self, *args):
        settings = load_settings()
        self.theme = settings["theme"]
        self.theme_color = get_theme_color(self.theme)
        for button in self.button_list:
            button.change_theme(self.theme_color)


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

    def on_pre_enter(self):
        self.load_settings()
        self.change_hide_cards_timeout_label_text()
        self.change_ai_timeout_label_text()
        self.change_touch_delay_label_text()
        self.change_button_states(self.theme, self.game_over_animation)

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
        self.card_flip_animation = settings["card_flip_animation"]
        self.game_over_animation = settings["game_over_animation"]
        self.touch_delay = settings["touch_delay"]
        self.ai_timeout = settings["ai_timeout"]
        self.hide_cards_timeout = settings["hide_cards_timeout"]

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
        self.touch_delay_label.text = f"Touch-Delay: {self.touch_delay} (Standard = 10)\nTrägheit der 'Touch-Erkennung'"

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
        self.ai_timeout_label.text = f"KI-Verzögerung: {self.ai_timeout} (Standard = 1.0)\n(Muss größer sein als 'Karten verdecken')\nDauer für Aktionen der KI"

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
        self.checkbox_list = [self.akira_box, self.cars_box, self.bundesliga_box, self.own_landscapes_box, self.sexy_box, self.random_box]
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
        pics_selected = 0
        if self.akira_box.state == "down":
            pics_selected += 1
        if self.cars_box.state == "down":
            pics_selected += 1
        if self.bundesliga_box.state == "down":
            pics_selected += 1
        if self.own_landscapes_box.state == "down":
            pics_selected += 1
        if self.sexy_box.state == "down":
            pics_selected += 1
        if self.random_box.state == "down":
            pics_selected += 1

        if pics_selected > 0:
            save_pics_lists("akira_images", self.akira_box.state)
            save_pics_lists("car_images", self.cars_box.state)
            save_pics_lists("bundesliga_images", self.bundesliga_box.state)
            save_pics_lists("own_landscape_images", self.own_landscapes_box.state)
            save_pics_lists("sexy_images", self.sexy_box.state)
            save_pics_lists("random_images", self.random_box.state)
        else:
            self.akira_box.state = "down"
            save_pics_lists("akira_images", self.akira_box.state)
            save_pics_lists("car_images", self.cars_box.state)
            save_pics_lists("bundesliga_images", self.bundesliga_box.state)
            save_pics_lists("own_landscape_images", self.own_landscapes_box.state)
            save_pics_lists("sexy_images", self.sexy_box.state)
            save_pics_lists("random_images", self.random_box.state)

            self.load_checkbox_statuses()

    def load_checkbox_statuses(self):
        checkboxes = load_pics_lists()
        self.akira_box.state = checkboxes["akira_images"]
        self.cars_box.state = checkboxes["car_images"]
        self.bundesliga_box.state = checkboxes["bundesliga_images"]
        self.own_landscapes_box.state = checkboxes["own_landscape_images"]
        self.sexy_box.state = checkboxes["sexy_images"]
        self.random_box.state = checkboxes["random_images"]

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
        self.load_checkbox_statuses()
        settings = load_settings()
        theme = settings["theme"]
        self.theme_color = get_theme_color(theme)
        self.update_checkbox_theme()
        self.redraw()


class WhoStartsScreen(Screen):
    top_label = ObjectProperty(None)
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
        self.redraw()

    def redraw(self):
        print(f"WhoStartsScreen: redraw")
        with self.canvas.before:
            Color(rgba=WINDOW_CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)

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
        self.top_label.text = f"{self.game_screen.current_player.name} beginnt das Spiel :)"
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
