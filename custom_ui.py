# Angepasste Layouts und Ähnliches
from random import randint

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from jnius import autoclass

WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
BEIGE = (1, 0.77, 0.59, 1)
DARK_RED = (0.53, 0.09, 0.09, 1)
ORANGE = (0.95, 0.7, 0.21, 1)
LIGHT_BLUE = (0.08, 0.54, 0.64, 1)
DARK_BLUE = (0.04, 0.27, 0.32, 1)
GREY = (0.48, 0.48, 0.48, 1)
DARK_GREY = (0.35, 0.35, 0.35, 1)

BUTTON_THEMES = {
        "light": {"btn_bg_color_normal": WHITE, "btn_bg_color_dis": GREY, "btn_bg_dis_normal": GREY, "btn_bg_dis_down": GREY, "btn_txt_color": ORANGE, "btn_border_color": BEIGE, "btn_txt_dis_color": DARK_GREY,
                  "btn_bg_down": GREY},
        "dark": {"btn_bg_color_normal": BLACK, "btn_bg_color_dis": GREY, "btn_bg_dis_normal": GREY, "btn_bg_dis_down": GREY, "btn_txt_color": BEIGE, "btn_border_color": BEIGE, "btn_txt_dis_color": DARK_GREY,
                 "btn_bg_down": GREY},
        "color": {"btn_bg_color_normal": LIGHT_BLUE, "btn_bg_color_dis": GREY, "btn_bg_dis_normal": GREY, "btn_bg_dis_down": GREY, "btn_txt_color": BEIGE, "btn_border_color": BEIGE, "btn_txt_dis_color": DARK_GREY,
                  "btn_bg_down": DARK_BLUE}
    }

LABEL_THEMES = {
        "light": {"bg_color_normal": WHITE, "txt_color": ORANGE, "border_color": ORANGE},
        "dark": {"bg_color_normal": BLACK, "txt_color": DARK_BLUE, "border_color": DARK_BLUE},
        "color": {"bg_color_normal": ORANGE, "txt_color": WHITE, "border_color": LIGHT_BLUE}
    }

CLEARCOLOR_THEME = {
    "light": ORANGE,
    "dark": DARK_BLUE,
    "color": LIGHT_BLUE
}


class MyScatter(ScatterPlane):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_touches = set()
        self.do_translation = True
        self.do_scale = True
        self.do_rotation = False
        self.scale_min = 0.5
        self.scale_max = 8.0
        self.start_pos = self.pos
        self.transformed = False  # Um festzustellen, ob ein Zoom/Verschieben stattgefunden hat
        self.touch_down_time = 0  # Zeit, wenn der erste Touch erkannt wurde
        self.game_screen = None
        self.touch_delay = 10
        self.theme_color = "color"
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        # self.redraw()

    def on_touch_up(self, touch):
        self.touch_down_time = 0
        self.get_settings()

        if len(self.game_screen.active_touches) == 0 and self.transformed:
            super().on_touch_up(touch)
            self.transformed = False
            return True

        return super().on_touch_up(touch)

    def on_transform_with_touch(self, touch):
        self.touch_down_time += 1
        if self.touch_down_time > self.touch_delay:
            self.transformed = True
            if self.game_screen.game_over_animation_running:
                Clock.unschedule(self.game_screen.game_over_animation_running)
                self.game_screen.game_over_animation_running = None
        return super().on_transform_with_touch(touch)

    def get_settings(self):
        self.touch_delay = self.game_screen.touch_delay

    def redraw(self):
        self.theme_color = self.game_screen.theme_color
        with self.canvas.before:
            # self.canvas.clear()
            Color(rgba=CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)


class MyMemoryGrid(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_pos = self.pos
        self.size[0] = Window.size[0]
        self.size[1] = Window.size[1] * 0.8
        self.start_size = self.size
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.theme_color = "color"

    def update_rect(self, *args):
        self.size[0] = Window.size[0]
        self.size[1] = Window.size[1] * 0.8
        self.rect.pos = self.pos
        self.rect.size = self.size
        # self.redraw()

    def reset(self, *args):
        self.pos = self.start_pos
        self.size = self.start_size

    def redraw(self):
        with self.canvas.before:
            self.theme_color = self.game_screen.theme_color
            Color(rgba=CLEARCOLOR_THEME[self.theme_color])
            self.rect = Rectangle(size=self.size, pos=self.pos)


class LabelBackgroundColor(Label):

    def __init__(self, back_color=WHITE, text_color=BLACK, border=False, border_color=BLACK, border_width=3, **kwargs):
        super().__init__(**kwargs)
        self.back_color = back_color
        self.color = text_color  # Farbe des Textes
        self.border = border
        self.border_color = border_color
        self.border_width = border_width
        self.bold = False
        # self.font_size = 16
        self.halign = "center"
        self.valign = "center"
        self.hide = False
        self.border_rect = Rectangle(size=self.size, pos=self.pos)
        Clock.schedule_once(self.add_to_label_list, .1)
        self.fading_out = False
        self.fade_out_step = 0.02  # Schrittgröße, mit der die Undurchsichtigkeit reduziert wird
        self.fade_out_delay = 0.1  # Delay, mit dem das 'Fade-Out' verzögert wird

        with self.canvas.before:
            # Rahmen zeichnen (optional)
            if self.border:
                self.border_color_instruction = Color(rgba=self.border_color)
                self.border_rect = Rectangle(size=self.size, pos=self.pos)

                # Hintergrund zeichnen
                self.back_color_instruction = Color(rgba=self.back_color)
                self.rect = Rectangle(size=(self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width), pos=(self.x + self.border_width, self.y + self.border_width))
            else:
                self.back_color_instruction = Color(rgba=self.back_color)
                self.rect = Rectangle(size=self.size, pos=self.pos)

        # Bind die Position und Größe des Labels an die Rechtecke
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        if self.border:
            self.rect.pos = (self.x + self.border_width, self.y + self.border_width)
            self.rect.size = (self.width - 2 * self.border_width, self.height - 2 * self.border_width)
            # Aktualisiere die Position und Größe des Rahmens
            self.border_rect.pos = self.pos
            self.border_rect.size = self.size
        else:
            self.rect.pos = self.pos
            self.rect.size = self.size
        self.text_size = self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width
        self.redraw()

    def redraw(self, back_color=None, text_color=None, border=None, border_color=None, border_width=None):
        if not self.hide:  # Label soll nicht versteckt werden
            if not self.blend_out:  # Label soll nicht langsam durchsichtig werden
                self.opacity = 1  # Label ist komplett undurchsichtig
            else:
                if not self.fading_out and self.opacity == 1:  # Label wird noch nicht durchsichtig gemacht und ist komplett undurchsichtig
                    self.fading_out = Clock.schedule_interval(lambda dt: self.fade_out(), self.fade_out_delay)  # Label wird schrittweise durchsichtig

            # Wenn Parameter angegeben sind, setze sie auf die neuen Werte
            if back_color is not None:
                self.back_color = back_color
            if text_color is not None:
                self.color = text_color
            if border is not None:
                self.border = border
            if border_color is not None:
                self.border_color = border_color
            if border_width is not None:
                self.border_width = border_width

            # Bereinige den Canvas, bevor du neue Instruktionen hinzufügst
            self.canvas.before.clear()

            with self.canvas.before:
                if self.border:
                    # Rahmen zeichnen
                    Color(rgba=self.border_color)
                    self.border_rect = Rectangle(size=self.size, pos=self.pos)

                    # Hintergrund zeichnen
                    Color(rgba=self.back_color)
                    self.rect = Rectangle(size=(self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width), pos=(self.x + self.border_width, self.y + self.border_width))
                else:
                    # Nur Hintergrund zeichnen
                    Color(rgba=self.back_color)
                    self.rect = Rectangle(size=self.size, pos=self.pos)
        else:  # Label wird 'versteckt'/ ist komplett durchsichtig
            self.opacity = 0

    def change_theme(self, theme):
        self.back_color = LABEL_THEMES[theme]["bg_color_normal"]
        self.border_color = LABEL_THEMES[theme]["border_color"]
        self.color = LABEL_THEMES[theme]["txt_color"]

        self.redraw()

    def add_to_label_list(self, *args):
        app = App.get_running_app()
        app.label_list.append(self)

    def fade_out(self):
        if self.fading_out and self.opacity > 0:
            self.opacity -= self.fade_out_step
            if self.opacity < 0:
                self.opacity = 0

        if self.fading_out and self.opacity == 0:
            Clock.unschedule(self.fading_out)
            self.fading_out = False


class ButtonBackgroundColor(ButtonBehavior, Label):

    def __init__(self, back_color=LIGHT_BLUE, text_color=WHITE, is_border=True, border_color=BEIGE, border_width=3, **kwargs):
        super().__init__(**kwargs)
        self.back_color = back_color
        self.color = text_color  # Farbe des Textes
        self.is_border = is_border
        self.border_color = border_color
        self.border_width = border_width
        self.border_rect = Rectangle(size=self.size, pos=self.pos)
        self.background_color_disabled = DARK_BLUE
        self.background_normal = ""
        self.background_disabled = ""
        self.background_disabled_down = ""
        self.background_down = ""
        self.background_color_down = DARK_BLUE
        self.background_color_normal = LIGHT_BLUE
        self.text_color = text_color
        self.text_disabled_color = GREY
        self.bold = False
        self.halign = "center"
        self.valign = "center"
        Clock.schedule_once(self.add_to_button_list, .1)

        with self.canvas.before:
            # Rahmen zeichnen (optional)
            if self.is_border:
                self.border_color_instruction = Color(rgba=self.border_color)
                self.border_rect = Rectangle(size=self.size, pos=self.pos)

                # Hintergrund zeichnen
                self.back_color_instruction = Color(rgba=self.back_color)
                self.rect = Rectangle(size=(self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width), pos=(self.x + self.border_width, self.y + self.border_width))
            else:
                self.back_color_instruction = Color(rgba=self.back_color)
                self.rect = Rectangle(size=self.size, pos=self.pos)

        # Bind die Position und Größe des Buttons an die Rechtecke
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        if self.is_border:
            self.rect.pos = (self.x + self.border_width, self.y + self.border_width)
            self.rect.size = (self.width - 2 * self.border_width, self.height - 2 * self.border_width)
            # Aktualisiere die Position und Größe des Rahmens
            self.border_rect.pos = self.pos
            self.border_rect.size = self.size
        else:
            self.rect.pos = self.pos
            self.rect.size = self.size

        self.text_size = self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width
        self.redraw()

    def redraw(self, back_color=None, text_color=None, is_border=None, border_color=None, border_width=None):
        # Wenn Parameter angegeben sind, setze sie auf die neuen Werte
        if back_color is not None:
            self.back_color = back_color
        if text_color is not None:
            self.text_color = text_color
        if is_border is not None:
            self.is_border = is_border
        if border_color is not None:
            self.border_color = border_color
        if border_width is not None:
            self.border_width = border_width

        # Bereinige den Canvas, bevor du neue Instruktionen hinzufügst
        self.canvas.before.clear()

        with self.canvas.before:
            if self.is_border:
                # Rahmen zeichnen
                Color(rgba=self.border_color)
                self.border_rect = Rectangle(size=self.size, pos=self.pos)

                # Hintergrund zeichnen
                if self.disabled:
                    Color(rgba=self.background_color_disabled)
                    self.color = self.text_disabled_color
                else:
                    Color(rgba=self.back_color)
                    self.color = self.text_color
                self.rect = Rectangle(size=(self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width), pos=(self.x + self.border_width, self.y + self.border_width))
            else:
                # Nur Hintergrund zeichnen
                if self.disabled:
                    Color(rgba=self.background_color_disabled)
                    self.color = self.text_disabled_color
                else:
                    Color(rgba=self.back_color)
                    self.color = self.text_color
                self.rect = Rectangle(size=self.size, pos=self.pos)

    def change_theme(self, theme):
        self.background_normal = "pics/white.png"
        self.background_disabled = ""
        self.background_disabled_down = ""
        self.background_color_down = BUTTON_THEMES[theme]["btn_bg_down"]
        self.text_disabled_color = BUTTON_THEMES[theme]["btn_txt_dis_color"]
        self.back_color = BUTTON_THEMES[theme]["btn_bg_color_normal"]
        self.background_color_normal = self.back_color
        self.border_color = BUTTON_THEMES[theme]["btn_border_color"]
        self.text_color = BUTTON_THEMES[theme]["btn_txt_color"]
        self.color = self.text_color
        self.background_color_disabled = BUTTON_THEMES[theme]["btn_bg_dis_normal"]
        self.disabled_color = BUTTON_THEMES[theme]["btn_txt_dis_color"]
        self.redraw()

    def add_to_button_list(self, *args):
        app = App.get_running_app()
        app.button_list.append(self)

    def on_release(self):
        self.back_color = self.background_color_normal
        self.redraw()
        return super().on_release()

    def on_press(self):
        self.back_color = self.background_color_down
        self.redraw()
        return super().on_press()


class Coin(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.head_image = "gfx/misc/Kopf.png"
        self.tail_image = "gfx/misc/Zahl.png"
        self.source = self.head_image
        self.keep_ratio = False
        self.allow_stretch = True
        self.pos_hint = {"x": 0.3, "top": 0.55}
        self.starting_pos = None
        self.size_hint = (0.4, 0.25)
        self.starting_size = None  # Anfangsgröße der Münze
        self.starting_width = 0
        self.is_flipping = False
        self.shrink_step = 10
        self.starting_shrink_step = self.shrink_step
        self.flips = 0
        self.flip_event = None
        self.flip_delay = 0.1
        self.shrinking = True
        self.parent_screen = None

    def start_flip(self, pick):
        if not self.is_flipping:
            self.is_flipping = True
            self.flips = randint(3, 10)  # Anzahl der Umdrehungen
            self.flip_event = Clock.schedule_interval(self.flip, self.flip_delay)
            self.starting_pos = tuple(self.pos)
            self.starting_size = tuple(self.size)
            self.starting_width = self.starting_size[0]
            self.shrink_step = self.starting_width / 4
            self.starting_shrink_step = self.shrink_step
            self.pos_hint = {}
            self.size_hint = (None, None)
            self.size = tuple(self.starting_size)
            if not self.parent_screen:
                app = App.get_running_app()
                self.parent_screen = app.root.get_screen("who_starts")
            self.parent_screen.pick = pick

    def flip(self, dt):
        # Schrumpfen der Münze
        if self.shrinking:
            if self.width > self.shrink_step:
                self.width -= self.shrink_step
                self.x += self.shrink_step / 2
            else:
                self.width = 0
                self.x = (self.starting_pos[0] + self.starting_width//2)
                self.source = self.tail_image if self.source == self.head_image else self.head_image
                self.shrinking = False
                self.shrink_step = self.starting_shrink_step
        else:  # Münze wird größer
            if self.width < self.starting_size[0]:
                self.width += self.shrink_step
                self.x -= self.shrink_step / 2
            else:
                self.width = self.starting_size[0]
                self.flips -= 1
                self.pos = tuple(self.starting_pos)
                if self.flips <= 0:
                    self.stop_flip()
                else:
                    self.shrinking = True
                    self.shrink_step = self.starting_shrink_step

    def stop_flip(self):
        Clock.unschedule(self.flip_event)
        self.flip_event = None
        self.is_flipping = False
        self.width = self.starting_size[0]
        self.pos = tuple(self.starting_pos)
        self.shrinking = True
        if self.source == self.head_image:
            coin = "head"
        else:
            coin = "tail"
        self.parent_screen.pick_side(coin)

    def disrupt_flip(self):
        if self.flip_event:
            Clock.unschedule(self.flip_event)
            self.flip_event = None
            self.is_flipping = False
            self.shrinking = True
            self.width = self.starting_size[0]
            self.pos = tuple(self.starting_pos)
            self.shrink_step = self.starting_shrink_step
