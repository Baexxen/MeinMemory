
import json
import os


class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "lang", f"{self.lang}.json")
            with open(path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Translation file for '{self.lang}' not found. Using default.")
            self.translations = {}

    def gettext(self, key):
        return self.translations.get(key, key)  # Fallback auf den Schlüssel

    def set_language(self, lang):
        self.lang = lang
        self.load_translations()
