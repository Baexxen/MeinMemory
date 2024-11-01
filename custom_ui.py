# Angepasste Layouts und Ähnliches
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
BEIGE = (1, 0.77, 0.59, 1)
DARK_RED = (0.53, 0.09, 0.09, 1)
ORANGE = (0.95, 0.7, 0.21, 1)
LIGHT_BLUE = (0.08, 0.54, 0.64, 1)
DARK_BLUE = (0.04, 0.27, 0.32, 1)


class MyScatter(ScatterPlane):
    print("MyScatter")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("MyScatter init")
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

        with self.canvas.before:
            Color(rgba=LIGHT_BLUE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

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
        return super().on_transform_with_touch(touch)

    def get_settings(self):
        self.touch_delay = self.game_screen.touch_delay


class MyMemoryGrid(GridLayout):
    print("MyMemoryGrid")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("MyMemoryGrid init")
        self.start_pos = self.pos
        self.size[0] = Window.size[0]
        self.size[1] = Window.size[1] * 0.8
        self.start_size = self.size

        with self.canvas.before:
            Color(rgba=LIGHT_BLUE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def reset(self, *args):
        self.pos = self.start_pos
        self.size = self.start_size


class LabelBackgroundColor(Label):
    print("LabelBackgroundColor")

    def __init__(self, back_color=WHITE, text_color=BLACK, border=True, border_color=BLACK, border_width=3, **kwargs):
        super().__init__(**kwargs)
        print("LabelBackgroundColor init")
        self.back_color = back_color
        self.color = text_color  # Farbe des Textes
        self.border = border
        self.border_color = border_color
        self.border_width = border_width
        self.border_rect = Rectangle(size=self.size, pos=self.pos)
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

    def redraw(self, back_color=None, text_color=None, border=None, border_color=None, border_width=None):
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


class ButtonBackgroundColor(ButtonBehavior, Label):
    print("ButtonBackgroundColor")

    def __init__(self, back_color=WHITE, text_color=BLACK, is_border=True, border_color=BLACK, border_width=3, **kwargs):
        super().__init__(**kwargs)
        print("LabelBackgroundColor init")
        self.back_color = back_color
        self.color = text_color  # Farbe des Textes
        self.is_border = is_border
        self.border_color = border_color
        self.border_width = border_width
        self.border_rect = Rectangle(size=self.size, pos=self.pos)
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

        # Bind die Position und Größe des Labels an die Rechtecke
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

    def redraw(self, back_color=None, text_color=None, is_border=None, border_color=None, border_width=None):
        # Wenn Parameter angegeben sind, setze sie auf die neuen Werte
        if back_color is not None:
            self.back_color = back_color
        if text_color is not None:
            self.color = text_color
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
                Color(rgba=self.back_color)
                self.rect = Rectangle(size=(self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width), pos=(self.x + self.border_width, self.y + self.border_width))
            else:
                # Nur Hintergrund zeichnen
                Color(rgba=self.back_color)
                self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)
