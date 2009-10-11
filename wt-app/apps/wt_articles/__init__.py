from goopytrans import translate as gtranslate
import nltk.data

class Translator:
    """
    A container class for various translation methods
    """
    def __init__(self, name, func):
        self.name = name
        self.translate = func

    def translate(self, text, source, target):
        self.translate(text, source=source, target=target)

def google_translator():
    return Translator('Google Translator', gtranslate)


